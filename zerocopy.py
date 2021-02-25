#!/usr/bin/env python3

''' This sample shows how some time can be saved by accessing the image buffer
    without copying its contents. Keep in mind that while a zero-copy array has a
    reference to the image buffer, this buffer cannot be released and cannot be
    reused for grabbing.
'''

import sys
import time
import neoapi

# grab image and diplay (opencv)
result = 0
try:  # for all no throw tests
    camera = neoapi.Cam()
    camera.Connect()
    if camera.f.PixelFormat.GetEnumValueList().HasFeature('BGR8'):
        camera.f.PixelFormat.SetString('BGR8')
    elif camera.f.PixelFormat.GetEnumValueList().HasFeature('Mono8'):
        camera.f.PixelFormat.SetString('Mono8')
    else:
        print('no supported pixelformat')
        sys.exit(1)
    camera.f.ExposureTime.Set(camera.f.ExposureTime.GetMin())

    print("camera model: %s" % camera.GetFeature('DeviceModelName').GetString())
    print("AOI: %d x %d" % (camera.f.Width.Get(), camera.f.Height.Get()))
    print("payload size: %d\n" % camera.f.PayloadSize.Get())

    pxl_sum = 0
    time_zc = 0
    count_zc = 0
    time_cp = 0
    count_cp = 0

    deadline = time.perf_counter() + 10
    print("Using zero copy for 10 seconds.")
    while time.perf_counter() < deadline:
        img = camera.GetImage(1000)
        if not img.IsEmpty():
            start = time.perf_counter()
            arr = img.GetNPArrayZeroCopy()
            pxl_sum += arr[0, 0]
            time_zc += time.perf_counter() - start
        count_zc += 1

    deadline = time.perf_counter() + 10
    print("Using copy for 10 seconds.")
    while time.perf_counter() < deadline:
        img = camera.GetImage(1000)
        if not img.IsEmpty():
            start = time.perf_counter()
            arr = img.GetNPArray()
            pxl_sum += arr[0, 0]
            time_cp += time.perf_counter() - start
        count_cp += 1

    print(" zc: %.3g s,  %d images, %.3g s / per image" % (time_zc, count_zc, time_zc / count_zc))
    print("cpy: %.3g s,  %d images, %.3g s / per image" % (time_cp, count_cp, time_cp / count_cp))
    if time_zc and count_cp:
        ratio = (time_cp * count_zc) / (time_zc * count_cp)
        print("zero copy is %.1f times faster" % ratio)

except (neoapi.NeoException, Exception) as exc:
    print('error: ', exc.GetDescription())
    result = 1

sys.exit(result)
