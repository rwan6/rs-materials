/*******************************************************************************

INTEL CORPORATION PROPRIETARY INFORMATION
This software is supplied under the terms of a license agreement or nondisclosure
agreement with Intel Corporation and may not be copied or disclosed except in
accordance with the terms of that agreement
Copyright(c) 2012-2015 Intel Corporation. All Rights Reserved.

*******************************************************************************/
#include <Windows.h>
#include <WindowsX.h>
#include <commctrl.h>
#include "resource1.h"
#include "my_gui.h"

MyGUI g;

static INT_PTR CALLBACK DialogProc(HWND hwndDlg, UINT message, WPARAM wParam, LPARAM) { 
    switch (message) { 
    case WM_INITDIALOG:
        g.OnInitDialog(hwndDlg);
        return TRUE; 
    case WM_COMMAND: 
        /* Check if any of the device/stream menu is pressed */
        if (g.OnDeviceMenuClick(wParam)) return TRUE;
        if (g.OnStreamMenuClick(wParam)) return TRUE;

        /* Additional selections */
        switch (LOWORD(wParam)) {
        case IDCANCEL:
            g.OnCancel();
            return TRUE;
        case ID_SYNC_SYNC:
            g.OnSync(Streaming::SYNC_OPTION_SW);
            break;
        case ID_SYNC_SYNC_HW:
            g.OnSync(Streaming::SYNC_OPTION_HW);
            break;
        case ID_SYNC_NOSYNC:
            g.OnSync(Streaming::SYNC_OPTION_NONE);
            break;
        case ID_START:
            g.OnStart();
            return TRUE;
        case ID_SAVE:
            g.OnSave();
            return TRUE;
        case ID_STOP:
            g.OnStop();
            return TRUE;
        case ID_MODE_LIVE:
            g.OnLiveMode();
            return TRUE;
        case ID_MODE_ADAPT:
            g.OnAdaptMode();
            return TRUE;
        case ID_MODE_PLAYBACK:
            g.OnPlayback();
            return TRUE;
        case ID_MODE_RECORD:
            g.OnRecord();
            return TRUE;
        }

        /* If radio button is pressed, check it */
        g.OnStreamButtonClick(wParam);
        
        switch (HIWORD(wParam)) {
        case BN_CLICKED:
            g.OnButtonClick(wParam);
            break;
        }
        break;
    case WM_SIZE:
        g.OnResize();
        return TRUE;
    } 
    return FALSE; 
} 

#pragma warning(disable:4706) /* assignment within conditional */
int APIENTRY wWinMain(HINSTANCE hInstance, HINSTANCE, LPTSTR, int) {
    InitCommonControls();

    HWND hWnd=CreateDialogW(hInstance,MAKEINTRESOURCE(IDD_MAINFRAME),0,DialogProc);
    if (!hWnd)  {
        MessageBoxW(0,L"Failed to create a window",L"Raw Streams",MB_ICONEXCLAMATION|MB_OK);
        return 1;
    }

    UpdateWindow(hWnd);

    MSG msg;
    for (int sts;(sts=GetMessageW(&msg,NULL,0,0));) {
        if (sts == -1) return sts;
        TranslateMessage(&msg);
        DispatchMessage(&msg);
    }

    return (int)msg.wParam;
}
