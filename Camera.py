from enum import Enum, auto
import neoapi


class Camera:
    # create and connect a camera
    def __init__(self, **kwargs):
        self._id = kwargs['id'] if 'id' in kwargs else ''
        self._camera = neoapi.Cam()
        self._camera.Connect(self._id)
        self._is_connected = self._camera.IsConnected()
        if self._is_connected:
            self.reset_to_default()

    class AutoExposureMode(Enum):
        ONCE = auto()
        CONT = auto()

    def is_connected(self):
        return self._is_connected

    def reset_to_default(self):
        self.set("UserSetSelector", neoapi.UserSetSelector_Default)
        self.execute("UserSetLoad")

    def execute(self, feature_name):
        # if command exists, execute it
        getattr(self._camera.f, f'{feature_name}').Execute()

    def print(self, feature_name):
        print(f'{feature_name} = {self.get(feature_name)}')

    def get(self, feature_name) -> object:
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
