#!/usr/bin/env python3

''' A simple Program for grabbing video from baumer camera and converting it to opencv img.
'''

import sys
import cv2
import neoapi
import Camera

def main():
    result = 0
    try:
        camera = Camera.Camera(id='gev')

        # reset to default factory settings: continuous acquisition
        camera.f.UserSetSelector.value = neoapi.UserSetSelector_Default
        camera.f.UserSetLoad.Execute()
        camera.f.AcquisitionStop.Execute()
        print(f'Trigger mode: {camera.f.TriggerMode.value}')

        # exposure time settings
        camera.f.ExposureAuto.value = neoapi.ExposureAuto_Off
        camera.f.ExposureMode.value = neoapi.ExposureMode_Timed
        camera.f.ExposureTime.value = 200_000
        print(f'Exposure auto set: {camera.f.ExposureAuto.value}')
        print(f'Exposure mode: {camera.f.ExposureMode.value}')
        print(f'Exposure time: {camera.f.ExposureTime.value} µs')

        # set frame rate
        camera.f.AcquisitionFrameRateEnable.value = True
        camera.f.AcquisitionFrameRate.value = 24
        print(f'Frame Rate set: {camera.f.AcquisitionFrameRate.value} fps')

        # enable test pattern
        camera.f.TestPatternGeneratorSelector.value = neoapi.TestPatternGeneratorSelector_SensorProcessor
        camera.f.TestPattern.value = neoapi.TestPattern_GreyHorizontalRamp

        empty_image_count = 0
        total_frame_count = 0
        while True:
            img = camera.GetImage().GetNPArray()
            total_frame_count += 1
            if img.size == 0:  # empty image (rows = 0?)
                empty_image_count += 1
                continue

            title = 'Press [ESC] to exit ..'
            cv2.namedWindow(title, cv2.WINDOW_NORMAL)
            cv2.imshow(title, img)

            if cv2.waitKey(1) == 27:
                break

        print(f'total frames: {total_frame_count}')
        print(f'empty frames: {empty_image_count}')

    except (neoapi.NeoException, Exception) as exc:
        print('error: ', exc.GetDescription())
        result = -1

    cv2.destroyAllWindows()
    sys.exit(result)


# get image and display (opencv)
main()
