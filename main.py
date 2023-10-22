import time

import RPi.GPIO as GPIO
import esptool
import serial.tools.list_ports

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # BUTTON
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)  # RED LIGHT
GPIO.setup(7, GPIO.OUT, initial=GPIO.LOW)  # GREEN LIGHT

ESP_32_DESC = 'CP2102 USB to UART Bridge Controller'
ESP_32_COM = None


def is_com_set() -> bool:
    global ESP_32_COM

    for p in [tuple(p) for p in serial.tools.list_ports.comports()]:
        if ESP_32_DESC in p[1]:
            ESP_32_COM = p[0]

    if not ESP_32_COM:
        return False
    return True


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


def main():
    while True:
        red_light(True)
        # if button pressed
        if GPIO.input(3) == GPIO.HIGH:
            if not is_com_set():
                print('Device is not connected')
                return False
            red_light(True)
            green_light(True)
            esptool.main(['-p', ESP_32_COM, 'flash_id'])
            red_light(False)
            time.sleep(5)
            green_light(False)
        time.sleep(0.2)
        red_light(False)


if __name__ == '__main__':
    while True:
        main()
