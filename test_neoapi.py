import neoapi
import pytest


# connect a camera and stop any running acquisition
@pytest.fixture
def cam():
    cam = neoapi.Cam()
    cam.Connect()
    assert cam.IsConnected()
    # reset to default factory settings: continuous acquisition
    cam.f.UserSetSelector.value = neoapi.UserSetSelector_Default
    cam.f.UserSetLoad.Execute()
    cam.f.AcquisitionStop.Execute()
    return cam


def test_connect_and_stop_camera(cam):
    assert cam.IsConnected()


def test_get_device_info(cam):
    assert cam.f.DeviceModelName.GetString() == 'VLXT-28M.I'
    assert cam.f.DeviceVendorName.GetString() == 'Baumer'
    assert cam.f.DeviceType.GetString() == 'Transmitter'
    assert cam.f.DeviceFirmwareVersion.GetString() == 'CID:012010/PID:11700832'
    assert cam.f.DeviceSerialNumber.GetString() == '700005720605'


def test_feature_transport_layer_type(cam):
    f = cam.f.DeviceTLType
    assert f.GetString() == 'GigEVision'
    assert f.GetName() == 'DeviceTLType'
    assert f.GetDescription()
    assert f.GetDisplayName()


def test_set_device_user_id(cam):
    cam.f.DeviceUserID.SetString('Leica Camera')
    assert cam.f.DeviceUserID.value == "Leica Camera"


def test_feature_auto_exposure(cam):
    f = cam.f.ExposureAuto
    assert f.IsImplemented()
    assert f.IsAvailable()
    assert f.IsWritable()


def test_feature_exposure_time(cam):
    f = cam.f.ExposureTime
    assert f.GetName() == 'ExposureTime'
    assert f.GetDescription()
    assert f.GetDisplayName()
    assert f.GetMin() == 8  # 8 µs
    assert f.GetMax() == 60_000_000  # 60 sec


def test_set_exposure_time_min(cam):
    cam.f.ExposureAuto.value = neoapi.ExposureAuto_Off
    min_time = cam.f.ExposureTime.GetMin()
    cam.f.ExposureTime.value = min_time
    assert cam.f.ExposureTime.value == min_time


def test_serial_number_not_writable(cam):
    assert cam.f.DeviceSerialNumber.IsAvailable()
    assert cam.f.DeviceSerialNumber.IsReadable()
    assert not cam.f.DeviceSerialNumber.IsWritable()


# image capture tests
def test_continuous_frame_acquisition_of_100_frames(cam):
    cam.f.AcquisitionMode.value = neoapi.AcquisitionMode_Continuous
    cam.f.ExposureAuto.value = neoapi.ExposureAuto_Off
    cam.f.ExposureTime.value = 100.0  # 100 µs
    cam.f.AcquisitionStart.Execute()
    for frame_count in range(0, 100):
        cam.f.TriggerSoftware.Execute()
        image = cam.GetImage()
        assert not image.IsEmpty()
        assert image.GetWidth() == cam.f.Width.value
        assert image.GetHeight() == cam.f.Height.value
    cam.f.AcquisitionStop.Execute()


def test_single_frame_acquisition_with_software_trigger(cam):
    cam.f.AcquisitionMode.value = neoapi.AcquisitionMode_SingleFrame
    # a trigger is required for each frame
    cam.f.TriggerSelector.value = neoapi.TriggerSelector_FrameStart
    cam.f.TriggerMode.value = neoapi.TriggerMode_On
    cam.f.TriggerSource.value = neoapi.TriggerSource_Software
    cam.f.ExposureMode.value = neoapi.ExposureMode_Timed
    cam.f.ExposureTime.value = 100_000.0  # 100 ms exposure per frame
    cam.f.AcquisitionStart.Execute()  # prepare for acquisition and wait for trigger
    cam.f.TriggerSoftware.Execute()
    image = cam.GetImage()
    assert not image.IsEmpty()
    assert image.GetWidth() == cam.f.Width.value
    assert image.GetHeight() == cam.f.Height.value
    # no more frames available
    cam.f.TriggerSoftware.Execute()
    image = cam.GetImage()
    assert image.IsEmpty()
    cam.f.AcquisitionStop.Execute()


def test_multi_frame_acquisition_with_software_trigger(cam):
    cam.f.AcquisitionMode.value = neoapi.AcquisitionMode_MultiFrame
    multi_frame_count = 20
    cam.f.AcquisitionFrameCount.value = multi_frame_count
    # a trigger is required for each frame
    cam.f.TriggerSelector.value = neoapi.TriggerSelector_FrameStart
    cam.f.TriggerMode.value = neoapi.TriggerMode_On
    cam.f.TriggerSource.value = neoapi.TriggerSource_Software
    cam.f.ExposureMode.value = neoapi.ExposureMode_Timed
    cam.f.ExposureTime.value = 100_000.0  # 100 ms exposure per frame
    cam.f.AcquisitionStart.Execute()  # prepare for acquisition and wait for trigger
    frame_count = 0
    while frame_count < multi_frame_count:
        cam.f.TriggerSoftware.Execute()
        image = cam.GetImage()
        assert not image.IsEmpty()
        assert image.GetWidth() == cam.f.Width.value
        assert image.GetHeight() == cam.f.Height.value
        frame_count += 1
    assert frame_count == multi_frame_count
    # no more frames available
    cam.f.TriggerSoftware.Execute()
    image = cam.GetImage()
    assert image.IsEmpty()
    cam.f.AcquisitionStop.Execute()


# streaming mode with 10 fps
def test_get_image_stream_with_10_fps(cam):
    cam.f.TriggerMode.value = neoapi.TriggerMode_Off
    # set optional frame rate to 10 fps
    cam.f.AcquisitionFrameRateEnable.value = True
    cam.f.AcquisitionFrameRate.value = 10
    img = cam.GetImage()
    assert not img.IsEmpty()


# GetImage() retrieves only the most recent image from the buffer queue
# default mode
def test_streaming_buffer_mode(cam):
    cam.SetImageBufferCycleCount(1)
    cam.SetImageBufferCount(10)
    assert cam.GetImageBufferCount() == 10


# GetImage() retrieves only the most recent image from the buffer queue
def test_cycling_buffer_mode(cam):
    cam.SetImageBufferCycleCount(9)
    cam.SetImageBufferCount(10)
    assert cam.GetImageBufferCount() == 10


# cycle count == buffer count
def test_queued_buffer_mode(cam):
    cam.SetImageBufferCycleCount(10)
    cam.SetImageBufferCount(10)
    assert cam.GetImageBufferCount() == 10


def test_image_buffers(cam):
    cam.SetImageBufferCount(8)  # set amount of buffers to 8
    img = []  # create array to store images
    for i in range(9):
        if cam.IsConnected():
            try:
                img.append(cam.GetImage())  # exception expected after all buffers are used
                img[i].Save("MyImage")
            except neoapi.NoImageBufferException as ex:
                # print(sys.exc_info()[0])
                print("NoImageBufferException: ", ex)
