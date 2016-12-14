/*******************************************************************************

INTEL CORPORATION PROPRIETARY INFORMATION
This software is supplied under the terms of a license agreement or nondisclosure
agreement with Intel Corporation and may not be copied or disclosed except in
accordance with the terms of that agreement
Copyright(c) 2013-2015 Intel Corporation. All Rights Reserved.

*******************************************************************************/
#pragma once
#include "gui_base.h"
#include "pip_render.h"
#include "streaming.h"
#include <vector>
#include <map>

class MyGUI : public GUIBase, public PIPRender, public Streaming {
public:

    MyGUI();
    virtual ~MyGUI();

    void OnInitDialog(HWND hwndDlg);
    void OnResize();
    void OnRecord();
    void OnPlayback();
    void OnAdaptMode();
    void OnLiveMode();
    void OnSync(Streaming::SYNC_OPTION sync);
    void OnButtonClick(WPARAM wParam);
    void OnCancel();
    void OnStart();
    void OnStop();
    void OnSave();

    bool OnDeviceMenuClick(WPARAM wParam);
    bool OnStreamMenuClick(WPARAM wParam);
    void OnStreamButtonClick(WPARAM wParam);

protected:

    PXCSession *session;
    PXCCapture *capture;
    PXCCapture::Device *device;
    PXCCaptureManager *captureManager;
    std::map<int /*ctrl*/, pxcUID /*iuid*/> devices;
    std::map<int /*ctrl*/, HMENU> streams;

    HMENU mode_menu;
    HMENU sync_menu;

    void PopulateDevices();
    bool PopulateDeviceFromFile(WCHAR *file);
    void SetDevice(int ctrl);
    void ReleaseDeviceAndCaptureManager();
    void MyGUI::ReleaseDevice();
    std::wstring Profile2String(PXCCapture::Device::StreamProfile *pinfo);
    void PopulateStreams();
    void CheckSelection();
    PXCCapture::Device::StreamProfileSet GetProfileSet();
    void StreamCheck(int ctrl);
    void OnStreamClick();

    virtual void UpdateStatus(pxcCHAR *line);
    virtual void DisplayMainImage(PXCImage* image);
    virtual void DisplayPIPImage(PXCImage* image);
    virtual void OnStreamingEnded();
};