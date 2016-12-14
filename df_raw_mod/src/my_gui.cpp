/*******************************************************************************

INTEL CORPORATION PROPRIETARY INFORMATION
This software is supplied under the terms of a license agreement or nondisclosure
agreement with Intel Corporation and may not be copied or disclosed except in
accordance with the terms of that agreement
Copyright(c) 2015-2016 Intel Corporation. All Rights Reserved.

*******************************************************************************/
#include "service/pxcsessionservice.h"
#include "pxcmetadata.h"
#include "my_gui.h"
#include "resource1.h"
#include <commctrl.h>
#include <strsafe.h>
#include <string> 

static const int NPROFILES_MAX = 100;
static const int NDEVICES_MAX = 100;

static const int IDC_STATUS = 10000;
static const int ID_DEVICEX = 21000;
static const int ID_STREAM1X = 22000;
static const int IDXM_DEVICE = 0;
static const int IDXM_MODE = 1;
static const int IDXM_SYNC = 2;

/* all stream buttons */
static const int g_stream_buttons[] = {
    IDC_STREAM1, IDC_STREAM2, IDC_STREAM3, IDC_STREAM4,
    IDC_STREAM5, IDC_STREAM6, IDC_STREAM7, IDC_STREAM8,
};

/* all controls that require resize support */
static const int g_controls[] = {
    IDC_STREAM1, IDC_STREAM2, IDC_STREAM3, IDC_STREAM4,
    IDC_STREAM5, IDC_STREAM6, IDC_STREAM7, IDC_STREAM8,
    IDC_UVMAP, IDC_INVUVMAP, IDC_PROJECTION, IDC_SCALE, IDC_MIRROR,
    IDC_DOTS, IDC_PIP, ID_START, ID_STOP
};

MyGUI::MyGUI():GUIBase(g_controls, sizeof(g_controls)/sizeof(int)), PIPRender()  {
    session = PXCSession::CreateInstance();
}

MyGUI::~MyGUI() {
    ReleaseDeviceAndCaptureManager();
    if (session) session->Release();
}

void MyGUI::OnInitDialog(HWND hwndDlg) {
    CreateStatusWindow(WS_CHILD | WS_VISIBLE, L"OK", hwndDlg, IDC_STATUS);
    GUIBase::OnInitDialog(hwndDlg, GetDlgItem(hwndDlg, IDC_MPANEL), GetDlgItem(hwndDlg, IDC_STATUS));
    SetHWND(GetDlgItem(hwndDlg, IDC_MPANEL));

    HMENU menu1 = GetMenu(hwndDlg);
    mode_menu = GetSubMenu(menu1, IDXM_MODE);
    sync_menu = GetSubMenu(menu1, IDXM_SYNC);
    RadioCheckMenuItem(sync_menu, 0);
    CheckDlgButton(hwndDlg, IDC_MIRROR, BST_CHECKED);
    CheckDlgButton(hwndDlg, IDC_SCALE, BST_CHECKED);
    PopulateDevices();
    PopulateStreams();
    CheckSelection();
}

void MyGUI::OnResize() {
    GUIBase::OnResize();

    RECT rect;
    GetClientRect(hwndDlg, &rect);

    /* Buttons & CheckBoxes */
    int offset = 0;
    for (int i = 0; i<sizeof(g_controls) / sizeof(g_controls[0]); i++) {
        SetWindowPos(GetDlgItem(hwndDlg, g_controls[i]), hwndDlg,
            rect.right - (layout[0].right - layout[3 + i].left),
            (layout[3 + i].top - layout[0].top - offset),
            (layout[3 + i].right - layout[3 + i].left), (layout[3 + i].bottom - layout[3 + i].top),
            SWP_NOZORDER);

        /* If not visible, off the size of the button for the rest controls */
        WCHAR line[256];
        GetDlgItemText(hwndDlg, g_controls[i], line, sizeof(line) / sizeof(line[0]));
        if (!wcscmp(line, L"-")) offset += layout[3 + i].bottom - layout[3 + i].top;
    }
    PIPRender::ResizePanel();
    PIPRender::UpdatePanel();
}

void MyGUI::PopulateDevices() {
    UpdateStatus(L"Scanning...");
    ReleaseDeviceAndCaptureManager();
    devices.clear();

    PXCSession::ImplDesc mdesc = {};
    mdesc.group = PXCSession::IMPL_GROUP_SENSOR;
    mdesc.subgroup = PXCSession::IMPL_SUBGROUP_VIDEO_CAPTURE;

    HMENU menu1 = CreatePopupMenu();
    if (session) {
        for (int m = 0, iitem = 0;; m++) {
            PXCSession::ImplDesc desc1;
            if (session->QueryImpl(&mdesc, m, &desc1) < PXC_STATUS_NO_ERROR) break;

            PXCCapture* capture = 0;
            if (session->CreateImpl<PXCCapture>(&desc1, &capture) < PXC_STATUS_NO_ERROR) continue;

            for (int j = 0;; j++) {
                PXCCapture::DeviceInfo dinfo;
                if (capture->QueryDeviceInfo(j, &dinfo) < PXC_STATUS_NO_ERROR) break;

                int id = ID_DEVICEX + (iitem++)*NDEVICES_MAX + j;
                devices[id] = desc1.iuid;
                pxcCHAR devName[128]; 
                memset(devName, 0, 128*sizeof(pxcCHAR)); 
                StringCbPrintf(devName, 128*sizeof(pxcCHAR), L"%s", dinfo.name); 
                AppendMenu(menu1, MF_STRING, id, devName);
            }
            capture->Release();
        }
    }
    UpdateStatus(L"OK");

    HMENU menu = GetMenu(hwndDlg);
    DeleteMenu(menu, IDXM_DEVICE, MF_BYPOSITION);
    CheckMenuRadioItem(menu1, 0, GetMenuItemCount(menu1), 0, MF_BYPOSITION);
    InsertMenu(menu, IDXM_DEVICE, MF_BYPOSITION | MF_POPUP, (UINT_PTR)menu1, L"Device");
    SetDevice(ID_DEVICEX);
}

std::wstring StreamOption2String(const PXCCapture::Device::StreamOption& streamOption)
{
    switch (streamOption)
    {
    case PXCCapture::Device::StreamOption::STREAM_OPTION_UNRECTIFIED:
        return L"RAW";
    case (PXCCapture::Device::StreamOption)0x00020000: // Depth Confidence
        return L" + Confidence";
    case PXCCapture::Device::StreamOption::STREAM_OPTION_DEPTH_PRECALCULATE_UVMAP:
    case PXCCapture::Device::StreamOption::STREAM_OPTION_STRONG_STREAM_SYNC:
    case PXCCapture::Device::StreamOption::STREAM_OPTION_ANY:
        return L"";
    default:
        return (L"(" + std::to_wstring((long double)streamOption) + L")");
    }
}

std::wstring MyGUI::Profile2String(PXCCapture::Device::StreamProfile *pinfo) {
    pxcCHAR line[256] = L"";
    if (pinfo->frameRate.min && pinfo->frameRate.max && pinfo->frameRate.min != pinfo->frameRate.max) {
        swprintf_s<sizeof(line) / sizeof(pxcCHAR)>(line, L"%s %dx%dx%d-%d %s",
            PXCImage::PixelFormatToString(pinfo->imageInfo.format),
            pinfo->imageInfo.width,
            pinfo->imageInfo.height,
            (int)pinfo->frameRate.min,
            (int)pinfo->frameRate.max,
            StreamOption2String(pinfo->options).c_str());
    }
    else {
        pxcF32 frameRate = pinfo->frameRate.min ? pinfo->frameRate.min : pinfo->frameRate.max;
        swprintf_s<sizeof(line) / sizeof(pxcCHAR)>(line, L"%s %dx%dx%d %s",
            PXCImage::PixelFormatToString(pinfo->imageInfo.format),
            pinfo->imageInfo.width,
            pinfo->imageInfo.height,
            (int)frameRate,
            StreamOption2String(pinfo->options).c_str());
    }
    return std::wstring(line);
}

void MyGUI::ReleaseDevice() {
    if (device) device->Release();
    if (capture && !captureManager) capture->Release();
    device = 0;
    capture = 0;
}

void MyGUI::ReleaseDeviceAndCaptureManager() {
    ReleaseDevice();
    if (captureManager)
    {
        captureManager->CloseStreams();
        captureManager->Release();
    }
    captureManager = 0;
}

void MyGUI::SetDevice(int ctrl) {
    if (!session) return;
    if (!captureManager) {
        ReleaseDevice();
        if (session->CreateImpl<PXCCapture>(devices[ctrl], &capture)<PXC_STATUS_NO_ERROR) return;
    }
    device = capture->CreateDevice((ctrl - ID_DEVICEX) % NDEVICES_MAX);
    if (!device) ReleaseDevice();
}

bool MyGUI::PopulateDeviceFromFile(WCHAR *file) {
    if (!file[0] || !session) return false;
    UpdateStatus(L"Scanning...");

    ReleaseDeviceAndCaptureManager();
    devices.clear();

    captureManager = session->CreateCaptureManager();
    if (!captureManager) {
        UpdateStatus(L"Failed to create CaptureManager");
        return false;
    }

    if (captureManager->SetFileName(file, false)<PXC_STATUS_NO_ERROR) {
        UpdateStatus(L"Failed to open file");
        ReleaseDeviceAndCaptureManager();
        return false;
    }

    UpdateStatus(file);
    capture = captureManager->QueryCapture();
    HMENU menu1 = CreatePopupMenu();
    for (int d = 0, iitem = 0;; d++) {
        PXCCapture::DeviceInfo dinfo;
        if (capture->QueryDeviceInfo(d, &dinfo)<PXC_STATUS_NO_ERROR) break;
        int id = ID_DEVICEX + (iitem++)*NDEVICES_MAX + d;
        devices[id] = 0;
        AppendMenu(menu1, MF_STRING, id, dinfo.name);
    }

    HMENU menu = GetMenu(hwndDlg);
    DeleteMenu(menu, IDXM_DEVICE, MF_BYPOSITION);
    CheckMenuRadioItem(menu1, 0, GetMenuItemCount(menu1), 0, MF_BYPOSITION);
    InsertMenu(menu, IDXM_DEVICE, MF_BYPOSITION | MF_POPUP, (UINT_PTR)menu1, L"Device");
    SetDevice(ID_DEVICEX);
    return true;
}

void MyGUI::PopulateStreams() {
    HMENU menu = GetMenu(hwndDlg);

    /* Remove all stream menus */
    for (;;) {
        pxcCHAR line[256];
        GetMenuString(menu, IDXM_DEVICE + 1, line, sizeof(line) / sizeof(line[0]), MF_BYPOSITION);
        if (!wcscmp(line, L"Mode")) break;
        DeleteMenu(menu, IDXM_DEVICE + 1, MF_BYPOSITION);
    }

    /* Hide all stream buttons */
    for (int i = 0; i<PXCCapture::STREAM_LIMIT; i++) {
        ShowWindow(GetDlgItem(hwndDlg, g_stream_buttons[i]), SW_HIDE);
        SetWindowText(GetDlgItem(hwndDlg, g_stream_buttons[i]), L"-");
    }

    /* Clean up */
    streams.clear();

    if (device) {
        PXCCapture::DeviceInfo dinfo;
        device->QueryDeviceInfo(&dinfo);

        int last = 0;
        for (int s = PXCCapture::STREAM_LIMIT - 1; s >= 0; s--) {
            PXCCapture::StreamType st = PXCCapture::StreamTypeFromIndex(s);
            if (!(dinfo.streams&st)) continue;
            const pxcCHAR *name = PXCCapture::StreamTypeToString(st);

            /* Create a profile menu */
            HMENU smenu = CreatePopupMenu();
            int id = ID_STREAM1X + s*NPROFILES_MAX;
            int nprofiles = device->QueryStreamProfileSetNum(st);
            for (int p = 0; p<nprofiles; p++) {
                PXCCapture::Device::StreamProfileSet profiles = {};
                if (device->QueryStreamProfileSet(st, p, &profiles) < PXC_STATUS_NO_ERROR) break;

                PXCCapture::Device::StreamProfile &profile = profiles[st];
                AppendMenu(smenu, MF_STRING, id + p, Profile2String(&profile).c_str());
                streams[id + p] = smenu;
                last = id + p;
            }

            /* Add a NONE choice and Insert the submenu */
            AppendMenu(smenu, MF_STRING, id + nprofiles, L"None");
            streams[id + nprofiles] = smenu;
            CheckMenuRadioItem(smenu, id, id + nprofiles, id + nprofiles, MF_CHECKED);
            InsertMenu(menu, IDXM_DEVICE + 1, MF_BYPOSITION | MF_POPUP, (UINT_PTR)smenu, name);

            /* Set/Unset the stream buttons */
            HWND hButton = GetDlgItem(hwndDlg, g_stream_buttons[s]);
            ShowWindow(hButton, SW_SHOW);
            SetWindowText(hButton, name);
            CheckDlgButton(hwndDlg, g_stream_buttons[s], BST_UNCHECKED);
        }
        /* Pre-select the first stream. */
        if (last) {
            /* The first profile of the last enumerated stream: Note we enumerated in the reverse order. */
            int id = ID_STREAM1X + ((last - ID_STREAM1X) / NPROFILES_MAX)*NPROFILES_MAX;
            PostMessage(hwndDlg, WM_COMMAND, id, 0);
        }
    }

    /* Redraw menu and buttons */
    DrawMenuBar(hwndDlg);
    OnResize();
    InvalidateRect(hwndDlg, 0, TRUE);
}

PXCCapture::Device::StreamProfileSet MyGUI::GetProfileSet() {
    PXCCapture::Device::StreamProfileSet profiles = {};
    if (!device) return profiles;

    PXCCapture::DeviceInfo dinfo;
    device->QueryDeviceInfo(&dinfo);
    for (int s = 0, mi = IDXM_DEVICE + 1; s<PXCCapture::STREAM_LIMIT; s++) {
        PXCCapture::StreamType st = PXCCapture::StreamTypeFromIndex(s);
        if (!(dinfo.streams&st)) continue;

        int id = ID_STREAM1X + s*NPROFILES_MAX;
        int nprofiles = device->QueryStreamProfileSetNum(st);
        for (int p = 0; p<nprofiles; p++) {
            if (!IsMenuChecked(mi, id + p)) continue;
            PXCCapture::Device::StreamProfileSet profiles1 = {};
            device->QueryStreamProfileSet(st, p, &profiles1);
            profiles[st] = profiles1[st];
        }
        mi++;
    }
    return profiles;
}


void MyGUI::CheckSelection() {
    if (!device) return;
    PXCCapture::Device::StreamProfileSet given = GetProfileSet();
    PXCCapture::DeviceInfo dinfo;
    device->QueryDeviceInfo(&dinfo);
    bool recheck = false;
    for (int s = 0, mi = IDXM_DEVICE + 1; s<PXCCapture::STREAM_LIMIT; s++) {
        PXCCapture::StreamType st = PXCCapture::StreamTypeFromIndex(s);
        if (!(dinfo.streams&st)) continue;

        int id = ID_STREAM1X + s*NPROFILES_MAX;
        int nprofiles = device->QueryStreamProfileSetNum(st);
        PXCCapture::Device::StreamProfileSet test = given;
        for (int p = 0; p<nprofiles; p++) {
            PXCCapture::Device::StreamProfileSet profiles1 = {};
            device->QueryStreamProfileSet(st, p, &profiles1);
            test[st] = profiles1[st];
            EnableMenuItem(mi, id + p, device->IsStreamProfileSetValid(&test) != 0);
        }

        bool enable = given[st].imageInfo.format != 0;
        EnableButton(g_stream_buttons[s], enable);
        if (IsButtonChecked(g_stream_buttons[s]) && !enable)
            recheck = true; // if a checked radio button is disabled, display another active stream.
        mi++;
    }

    if (recheck) {
        for (int s = 0, mi = IDXM_DEVICE + 1; s<PXCCapture::STREAM_LIMIT; s++) {
            if (!IsButtonEnabled(g_stream_buttons[s])) continue;
            StreamCheck(g_stream_buttons[s]);
            break;
        }
    }

    EnableButton(ID_START, device->IsStreamProfileSetValid(&given));
}

void MyGUI::StreamCheck(int ctrl) {
    for (int i = 0; i < (int)sizeof(g_stream_buttons) / sizeof(g_stream_buttons[0]); i++) {
        if (g_stream_buttons[i] == ctrl) {
            CheckDlgButton(hwndDlg, g_stream_buttons[i], BST_CHECKED);
            Streaming::SetPIP(Streaming::GetMain());
            Streaming::SetMain(PXCCapture::StreamTypeFromIndex(i));
        } else {
            CheckDlgButton(hwndDlg, g_stream_buttons[i], BST_UNCHECKED);
        }
    }
}


void MyGUI::OnRecord() {
    GetRecordFile(L"RSSDK clip (*.rssdk)\0*.rssdk\0All Files (*.*)\0*.*\0\0", L"rssdk");
    if (IsMenuChecked(mode_menu, ID_MODE_PLAYBACK)) {
        /* rescan streams after playback */
        PopulateDevices();
        PopulateStreams();
    }

    Streaming::SetAdaptive(false);
    if (GUIBase::file[0]) {
        RadioCheckMenuItem(mode_menu, 3);
        Streaming::SetRecord(GUIBase::file);
    }
    else {
        RadioCheckMenuItem(mode_menu, 0);
    }

    EnableButton(IDC_MIRROR, true);
    CheckSelection();
}

void MyGUI::OnPlayback() {
    Streaming::SetAdaptive(false);
    GetPlaybackFile(L"RSSDK clip (*.rssdk)\0*.rssdk\0Old format clip (*.pcsdk)\0*.pcsdk\0All Files (*.*)\0*.*\0\0");
    if (PopulateDeviceFromFile(GUIBase::file)) {
        RadioCheckMenuItem(mode_menu, 2);
        Streaming::SetPlayback(GUIBase::file);
        EnableButton(IDC_MIRROR, false);
    }
    else {
        RadioCheckMenuItem(mode_menu, 0);
        PopulateDevices();
        EnableButton(IDC_MIRROR, true);
    }
    PopulateStreams();
    CheckSelection();
}

void MyGUI::OnAdaptMode() {
    RadioCheckMenuItem(mode_menu, 1);
    EnableButton(IDC_MIRROR, true);
    SetAdaptive(true);
    PopulateDevices();
    if (device) device->SetDeviceAllowProfileChange(TRUE);
    PopulateStreams();
    GUIBase::file[0] = 0;
    CheckSelection();
}

void MyGUI::OnLiveMode() {
    if (IsMenuChecked(mode_menu, ID_MODE_PLAYBACK)) {
        /* rescan streams after playback */
        PopulateDevices();
        PopulateStreams();
    }
    RadioCheckMenuItem(mode_menu, 0);
    EnableButton(IDC_MIRROR, true);
    SetAdaptive(false);
    GUIBase::file[0] = 0;
    CheckSelection();
}

void MyGUI::OnSync(Streaming::SYNC_OPTION sync) {
    RadioCheckMenuItem(sync_menu, sync);
    Streaming::SetSynced(sync);
    CheckSelection();
}

bool MyGUI::OnDeviceMenuClick(WPARAM wParam) {
    HMENU menu1 = GetSubMenu(GetMenu(hwndDlg), IDXM_DEVICE);
    WPARAM wParam2 = LOWORD(wParam);
    if (wParam2 >= ID_DEVICEX && devices.find(wParam2) != devices.end()) {
        RadioCheckMenuItem(IDXM_DEVICE, (wParam2 - ID_DEVICEX) / NDEVICES_MAX);
        SetDevice(wParam2);
        PopulateStreams();
        CheckSelection();
        return true;
    }
    return false;
}

bool MyGUI::OnStreamMenuClick(WPARAM wParam) {
    WPARAM wParam2 = LOWORD(wParam);
    if (wParam2 >= ID_STREAM1X && streams.find(wParam2) != streams.end()) {
        RadioCheckMenuItem(streams[wParam2], (wParam2 - ID_STREAM1X) % NPROFILES_MAX);
        StreamCheck(g_stream_buttons[(wParam2 - ID_STREAM1X) / NPROFILES_MAX]);
        CheckSelection();
        return true;
    }
    return false;
}

void MyGUI::OnStreamButtonClick(WPARAM wParam) {
    WPARAM wParam2 = LOWORD(wParam);
    for (int i = 0; i < sizeof(g_stream_buttons) / sizeof(g_stream_buttons[0]); i++)
        if (wParam2 == g_stream_buttons[i]) StreamCheck(g_stream_buttons[i]);
}

void MyGUI::OnButtonClick(WPARAM wParam) {
    switch (LOWORD(wParam)) {
    case IDC_PIP:
        switch (GetPIPScale()) {
        case 0: SetPIPScale(2); break;
        case 2: SetPIPScale(4); break;
        case 4: SetPIPScale(0); break;
        }
        OnResize();
        break;
    case IDC_MIRROR:
        Streaming::SetMirror(!Streaming::GetMirror());
        break;
    case IDC_SCALE:
        PIPRender::SetScale(!PIPRender::GetScale());
        break;
    }
}

void MyGUI::UpdateStatus(pxcCHAR *line) {
    GUIBase::UpdateStatus(line);
}

void MyGUI::DisplayMainImage(PXCImage* image) {
    PIPRender::UpdatePanel(image);
}

void MyGUI::DisplayPIPImage(PXCImage* image) {
    PIPRender::UpdatePIPPanel(image);
}

void MyGUI::OnCancel() {
    Streaming::Stop();
    if (Streaming::IsRunning()) {
        PostMessage(hwndDlg, WM_COMMAND, IDCANCEL, 0);
    } else {
        DestroyWindow(hwndDlg);
        PostQuitMessage(0);
    }
}

void MyGUI::OnStart() {
    GUIBase::OnStart(ID_START, ID_STOP);
    PXCCapture::DeviceInfo dinfo = {};
    if (device) device->QueryDeviceInfo(&dinfo);
    Streaming::SetDevice(dinfo);
    Streaming::SetStreams(GetProfileSet());
    Streaming::Start();
}

void MyGUI::OnStop() {
    Streaming::Stop();
    if (IsRunning()) {
        PostMessage(hwndDlg, WM_COMMAND, ID_STOP, 0);
    }
    else {
        GUIBase::OnStop(ID_START, ID_STOP);
    }
}

void MyGUI::OnSave() {
    Streaming::Save();
}

void MyGUI::OnStreamingEnded() {
    PostMessage(hwndDlg, WM_COMMAND, ID_STOP, 0);
}
