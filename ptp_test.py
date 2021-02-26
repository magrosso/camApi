''' This example describes the FIRST STEPS of handling NeoAPI Python SDK.
    The given source code applies to handle one camera and image acquisition
'''

import sys
import neoapi
import Camera

camera = Camera.Camera(id='gev')
camera.device_info()

# unlock TL
camera.info('PtpMode')
camera.ptp_mode(mode='slave')
camera.info('PtpMode')

camera.info('PtpEnable')
camera.enable_ptp()
camera.info('PtpEnable')

camera.info('PtpStatus')

camera.info('PtpServoStatus')

#camera.info('PtpClockAccuracy')
#camera.info('PtpMode')
#camera.info('PtpClockID')
#camera.info('PtpClockOffset')
#camera.info('PtpClockOffsetMode')
#camera.info('PtpClockOffsetSet')
#camera.info('PtpControl')
#camera.info('PtpDataSetLatch')
#camera.info('PtpDriftOffset')
#camera.info('PtpDriftOffsetMode')
#camera.info('PtpDriftOffsetSet')
#camera.info('PtpGrandmasterClockID')
#camera.info('PtpKi')
#camera.info('PtpKp')
#camera.info('PtpOffsetFromMaster')
#camera.info('PtpParentClockID')
#camera.info('PtpTestControl')
#camera.info('PtpTimestampOffset')
#camera.info('PtpTimestampOffsetMode')
#camera.info('PtpTimestampOffsetSet')
#camera.info('PtpUseControllerTestSettings')

