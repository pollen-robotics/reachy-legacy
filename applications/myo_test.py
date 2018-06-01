import time
import numpy

import myo

class Listener(myo.DeviceListener):
    def on_connect(self, device, timestamp, version):
        print('Connected!')

        device.set_stream_emg(myo.StreamEmg.enabled)

        for _ in range(3):
            device.vibrate('short')
            time.sleep(0.5)

    def on_emg_data(self, device, timestamp, emg):
        self.emg = numpy.array(emg)

if __name__ == '__main__':
    myo.init('../../myo-sdk-win-0.9.0/bin')

    listener = Listener()
    listener.emg = numpy.array([numpy.nan])

    hub = myo.Hub()
    hub.run(100, listener)

    data = []

    try:
        while True:
            if not numpy.isnan(listener.emg).any():
                data.append(listener.emg)
            time.sleep(0.01)
    except KeyboardInterrupt:
        hub.shutdown()

    print(len(data))
    data = numpy.array(data)
    numpy.save('emg.npy', data)
