from enum import Enum, auto
import neoapi


class Camera:
    # create and connect a camera
    def __init__(self, **kwargs):
        self._id = kwargs['id'] if 'id' in kwargs else ''
        self._camera = neoapi.Cam()
        self._camera.Connect(self._id)
        if self._camera.IsConnected():
            self.reset_to_default()

    class AutoExposureMode(Enum):
        ONCE = auto()
        CONT = auto()

    def is_connected(self):
        return self._camera.IsConnected()

    def transport_layer_version(self):
        return f'{self.value("DeviceTLVersionMajor")}.' \
               f'{self.value("DeviceTLVersionMinor")}.' \
               f'{self.value("DeviceTLVersionSubMinor")}'

    def device_info(self):
        self.print(f'DeviceTLType')
        self.print(f'DeviceUserID')
        self.print(f'DeviceVendorName')
        self.print(f'DeviceVersion')
        print(f'TL Version: {self.transport_layer_version()}')

    def reset_to_default(self):
        self.set("UserSetSelector", neoapi.UserSetSelector_Default)
        self.execute("UserSetLoad")

    def execute(self, feature_name):
        # if command exists, execute it
        getattr(self._camera.f, f'{feature_name}').Execute()

    def print(self, feature_name):
        print(f'{feature_name} = {self.value(feature_name)}')

    # enable PTP
    def enable_ptp(self):
        # disable energy efficiency for higher PTP accuracy
        self.unlock_transport_layer()
        self.set('EnergyEfficientEthernetEnable', False)
        self.set('PtpEnable', True)
        # todo: restore tl lock value

    def ptp_mode(self, **kwargs):
        if 'mode' in kwargs:
            if kwargs['mode'] == 'auto':
                mode = neoapi.PtpMode_Auto
            elif kwargs['mode'] == 'slave':
                mode = neoapi.PtpMode_Slave
            else:
                raise   # invalid mode
        else:
            raise   # invalid argument
        self.set('PtpMode', mode)

    # lock/unlock transport layer
    # should be locked during acquisition
    # 0: unlock
    # 1: lock
    def lock_transport_layer(self):
        self.set('TLParamsLocked', 1)

    def unlock_transport_layer(self):
        self.set('TLParamsLocked', 0)

    # lock transport layer and start acquisition
    def start_acquisition(self):
        self.lock_transport_layer()
        self.execute('AcquisitionStart')

    # stop acquisition unlock transport layer
    def stop_acquisition(self):
        self.execute('AcquisitionStop')
        self.unlock_transport_layer()

    # get info about feature
    def info(self, feature_name):
        implemented = self.implemented(feature_name)
        available = self.available(feature_name)
        readable = self.readable(feature_name)
        writable = self.writable(feature_name)
        print(f'Feature "{feature_name}" is: '
              f'{"not " if not implemented else ""}implemented, '
              f'{"not " if not available else ""}available, '
              f'{"not " if not writable else ""}writable, '
              f'{"not " if not readable else ""}readable: '
              f'interface={self.interface(feature_name)}, '
              f'visible={self.visible(feature_name)}, '
              f'value={self.string(feature_name) if readable else None}'
              )

    def has_feature(self, feature_name):
        return self._camera.HasFeature(feature_name)

    def implemented(self, feature_name) -> object:
        f = getattr(self._camera.f, f'{feature_name}')
        return f.IsImplemented()

    def available(self, feature_name) -> object:
        f = getattr(self._camera.f, f'{feature_name}')
        return f.IsAvailable()

    def readable(self, feature_name) -> object:
        f = getattr(self._camera.f, f'{feature_name}')
        return f.IsReadable()

    def writable(self, feature_name) -> object:
        f = getattr(self._camera.f, f'{feature_name}')
        return f.IsWritable()

    def interface(self, feature_name):
        f = getattr(self._camera.f, f'{feature_name}')
        return f.GetInterface()

    def visible(self, feature_name):
        f = getattr(self._camera.f, f'{feature_name}')
        return f.GetVisibility()

    # get the Name of the feature (CamelCase)
    def name(self, feature_name):
        f = getattr(self._camera.f, f'{feature_name}')
        return f.GetName()

    # get the name as it should be displayed (with spaces)
    def display_name(self, feature_name):
        f = getattr(self._camera.f, f'{feature_name}')
        return f.GetDisplayName()

    def description(self, feature_name):
        f = getattr(self._camera.f, f'{feature_name}')
        return f.GetDescription()

    # get additional vendor specific description
    def extension(self, feature_name):
        f = getattr(self._camera.f, f'{feature_name}')
        return f.GetExtension()

    # get a short description of the feature
    def tool_tip(self, feature_name):
        f = getattr(self._camera.f, f'{feature_name}')
        return f.GetToolTip()

    # get the value back as a String
    def string(self, feature_name):
        f = getattr(self._camera.f, f'{feature_name}')
        return f.GetString()

    def value(self, feature_name) -> object:
        f = getattr(self._camera.f, f'{feature_name}')
        if f.IsImplemented() and f.IsAvailable() and f.IsReadable():
            return f.value
        else:
            raise

    def set(self, feature_name, new_value):
        # todo: check if implemented, available and writable
        f = getattr(self._camera.f, f'{feature_name}')
        if f.IsImplemented() and f.IsAvailable() and f.IsReadable():
            f.value = new_value
        else:
            raise

    def get_image(self):
        return self._camera.GetImage()

    def set_exposure_time(self, time_us):
        self.set('ExposureAuto', 'Off')
        self.set('ExposureMode', 'Timed')
        self.set('ExposureTime', time_us)

    def set_auto_exposure(self, auto_mode):
        if auto_mode == self.AutoExposureMode['ONCE']:
            self.set('ExposureAuto', 'Once')
        else:
            if auto_mode == self.AutoExposureMode['CONT']:
                self.set('ExposureAuto', 'Continuous')
