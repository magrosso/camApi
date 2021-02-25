''' This example describes the FIRST STEPS of handling NeoAPI Python SDK.
    The given source code applies to handle one camera and image acquisition
'''

import sys
import neoapi
import Camera

result = 0
try:
    camera = Camera.Camera(id='gev')
    camera.print('ExposureTime')
    camera.print('ShortExposureTimeEnable')
    camera.print('ExposureAuto')
    camera.print('TriggerMode')

    camera.set('AcquisitionMode', neoapi.AcquisitionMode_SingleFrame)
    # a trigger is required for each frame
    camera.set('TriggerSelector', neoapi.TriggerSelector_FrameStart)
    camera.set("TriggerMode", neoapi.TriggerMode_On)
    camera.set('TriggerSource', neoapi.TriggerSource_Software)
    camera.set('ExposureMode', neoapi.ExposureMode_Timed)
    camera.set('ExposureTime', 100_000)
    camera.execute('AcquisitionStart')  # prepare for acquisition and wait for trigger
    camera.execute('TriggerSoftware')   # execute the software trigger
    image = camera.get_image()

    image_name = "getting_started.bmp"
    image.Save(image_name)
    print(f'Saved image to file: "{image_name}"')


except (neoapi.NeoException, Exception) as exc:
    print('error: ', exc.GetDescription())
    result = 1

sys.exit(result)
