import time

import RPi.GPIO as GPIO
import esptool
import serial.tools.list_ports

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # BUTTON
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)  # RED LIGHT
GPIO.setup(7, GPIO.OUT, initial=GPIO.LOW)  # GREEN LIGHT

FIRMWARE_DIR = '/home/pi/programmator'
FIRMWARE_FILENAME = 'firmware.factory.bin'
BLEOTA_FILENAME = 'bleota.bin'
LITTLEFS_FILENAME = 'littlefs.bin'
ESP_32_DESC = 'CP2102 USB to UART Bridge Controller'


def red_light(enable: bool):
    if enable:
        GPIO.output(8, GPIO.HIGH)
    else:
        GPIO.output(8, GPIO.LOW)


def green_light(enable: bool):
    if enable:
        GPIO.output(7, GPIO.HIGH)
    else:
        GPIO.output(7, GPIO.LOW)


def get_com_port() -> str | None:
    for p in [tuple(p) for p in serial.tools.list_ports.comports()]:
        if ESP_32_DESC in p[1]:
            return p[0]
    return None


def main():
    red_light(True)
    # if button pressed
    if GPIO.input(10) == GPIO.HIGH:

        # get com_port
        com_port = get_com_port()
        if not com_port:
            print('Device is not connected')

            # show LEDS for device is not connected
            red_light(False)
            time.sleep(0.1)
            red_light(True)
            time.sleep(0.1)
            red_light(False)
            time.sleep(0.1)
            red_light(True)

            return False

        # show LEDS for firmware upload
        red_light(True)
        green_light(True)

        # clear flash
        esptool.main(['-p', com_port, 'erase_flash'])

        # upload firmware 
        esptool.main(['-p', com_port, 'write_flash', '0x00', f'{FIRMWARE_DIR}/{FIRMWARE_FILENAME}'])

        # upload bleota
        if "s3" in FIRMWARE_FILENAME or "-v3" in FIRMWARE_FILENAME or "t-deck" in FIRMWARE_FILENAME or "wireless-paper" in FIRMWARE_FILENAME or "wireless-tracker" in FIRMWARE_FILENAME:
            BLEOTA_FILENAME = "bleota-s3.bin"
        esptool.main(['-p', com_port, 'write_flash', '0x260000', f'{FIRMWARE_DIR}/{BLEOTA_FILENAME}'])

        # upload littlefs
        esptool.main(['-p', com_port, 'write_flash', '0x300000', f'{FIRMWARE_DIR}/{LITTLEFS_FILENAME}'])


        # show LEDS for successfully
        red_light(False)
        time.sleep(5)
        green_light(False)


if __name__ == '__main__':
    while True:
        main()
