#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  backend.py

import serial

class SerialBackend:
    def __init__(self, serial_port: str = '/dev/ttyACM2', baud_rate: int = 38400) -> None:
        self.serial_port = serial_port
        self.ser = serial.Serial(serial_port, baud_rate, timeout=1)

    def read_int(self) -> int:
        return int(self.ser.readline())

    def read_float(self) -> float:
        return float(self.ser.readline())

    def write_raw_byte(self, byte: int) -> None:
        self.ser.write(bytes([byte]))
