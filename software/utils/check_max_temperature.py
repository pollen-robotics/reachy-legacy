import time

from pypot.dynamixel import get_available_ports, DxlIO

max_temp = 55


if __name__ == '__main__':
    ports = get_available_ports()

    if '/dev/ttyAMA0' in ports:
        ports.remove('/dev/ttyAMA0')

    for p in ports:
        print('Looking for motors on port "{}"'.format(p))
        with DxlIO(p) as io:
            ids = io.scan(range(30))
            print('Ids found: {}'.format(ids))

            print('Setting max temperature to "{}C"...'.format(max_temp))
            io.set_highest_temperature_limit({id: max_temp for id in ids})
            print('Done.')

            time.sleep(1.0)
