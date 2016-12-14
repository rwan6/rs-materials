/*******************************************************************************

INTEL CORPORATION PROPRIETARY INFORMATION
This software is supplied under the terms of a license agreement or nondisclosure
agreement with Intel Corporation and may not be copied or disclosed except in
accordance with the terms of that agreement
Copyright(c) 2013-2015 Intel Corporation. All Rights Reserved.

*******************************************************************************/
#include <tchar.h>
#include "timer.h"

Timer::Timer():fps(0) {
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&last);
}

Timer::~Timer() {
}

void Timer::Tick(PXCImage::ImageInfo *info) {
    LARGE_INTEGER now;
    QueryPerformanceCounter(&now);
    fps++;

    if (now.QuadPart-last.QuadPart>freq.QuadPart) { // update every second
        last = now;

        pxcCHAR line[256];
        swprintf_s<sizeof(line)/sizeof(line[0])>(line,L"%s %dx%d FPS=%d", PXCImage::PixelFormatToString(info->format), info->width, info->height, fps);
        UpdateStatus(line);
        fps=0;
    }
}
