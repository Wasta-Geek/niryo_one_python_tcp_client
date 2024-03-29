#!/usr/bin/env python

# tcp_client.py
# Copyright (C) 2017 Niryo
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import socket
from .packet_builder import PacketBuilder
from .command import Command


class NiryoOneClient:
    class HostNotReachableException(Exception):
        def __init__(self):
            super(Exception, self).__init__("Unable to communicate with robot server, please verify your network.")

    class ClientNotConnectedException(Exception):
        def __init__(self):
            super(Exception, self).__init__("You're not connected to  the robot.")

    def __init__(self, timeout=5):
        self.__port = 40001
        self.__is_running = True
        self.__is_connected = False
        self.__timeout = timeout
        self.__client_socket = None
        self.__packet_builder = PacketBuilder()

    def __del__(self):
        self.quit()

    def connect(self, ip_address):
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client_socket.settimeout(self.__timeout)
        try:
            self.__client_socket.connect((ip_address, self.__port))
        except socket.timeout:
            print("Unable to connect to the robot.")
            self.__shutdown_connection()
            self.__client_socket = None
        except socket.error as e:
            print("An error occurred while attempting to connect: {}".format(e))
            self.__shutdown_connection()
            self.__client_socket = None
        else:
            print("Connected to server ({}) on port: {}".format(ip_address, self.__port))
            self.__is_connected = True
            self.__client_socket.settimeout(None)

        return self.__is_connected

    def calibrate(self, calibrate_mode):
        self.send_command(Command.CALIBRATE, [calibrate_mode])
        return self.receive_answer()

    def set_learning_mode(self, enabled):
        self.send_command(Command.SET_LEARNING_MODE, [enabled])
        return self.receive_answer()

    def move_joints(self, j1, j2, j3, j4, j5, j6):
        self.send_command(Command.MOVE_JOINTS, [j1, j2, j3, j4, j5, j6])
        return self.receive_answer()

    def move_pose(self, x_pos, y_pos, z_pos, roll_rot, pitch_rot, yaw_rot):
        self.send_command(Command.MOVE_POSE, [x_pos, y_pos, z_pos, roll_rot, pitch_rot, yaw_rot])
        return self.receive_answer()

    def shift_pose(self, axis, shift_value):
        self.send_command(Command.SHIFT_POSE, [axis, shift_value])
        return self.receive_answer()

    def set_arm_max_velocity(self, percentage_speed):
        self.send_command(Command.SET_ARM_MAX_VELOCITY, [percentage_speed])
        return self.receive_answer()

    def set_joystick_mode(self, enabled):
        self.send_command(Command.SET_JOYSTICK_MODE, [enabled])
        return self.receive_answer()

    def set_pin_mode(self, pin, pin_mode):
        self.send_command(Command.SET_PIN_MODE, [pin, pin_mode])
        return self.receive_answer()

    def digital_write(self, pin, digital_state):
        self.send_command(Command.DIGITAL_WRITE, [pin, digital_state])
        return self.receive_answer()

    def digital_read(self, pin):
        self.send_command(Command.DIGITAL_READ, [pin])
        return self.receive_answer()

    def change_tool(self, tool):
        self.send_command(Command.CHANGE_TOOL, [tool])
        return self.receive_answer()

    def open_gripper(self, gripper, speed):
        self.send_command(Command.OPEN_GRIPPER, [gripper, speed])
        return self.receive_answer()

    def close_gripper(self, gripper, speed):
        self.send_command(Command.CLOSE_GRIPPER, [gripper, speed])
        return self.receive_answer()

    def pull_air_vacuum_pump(self, vacuum_pump):
        self.send_command(Command.PULL_AIR_VACUUM_PUMP, [vacuum_pump])
        return self.receive_answer()

    def push_air_vacuum_pump(self, vacuum_pump):
        self.send_command(Command.PUSH_AIR_VACUUM_PUMP, [vacuum_pump])
        return self.receive_answer()

    def setup_electromagnet(self, electromagnet, pin):
        self.send_command(Command.SETUP_ELECTROMAGNET, [electromagnet, pin])
        return self.receive_answer()

    def activate_electromagnet(self, electromagnet, pin):
        self.send_command(Command.ACTIVATE_ELECTROMAGNET, [electromagnet, pin])
        return self.receive_answer()

    def deactivate_electromagnet(self, electromagnet, pin):
        self.send_command(Command.DEACTIVATE_ELECTROMAGNET, [electromagnet, pin])
        return self.receive_answer()

    def get_saved_position_list(self):
        self.send_command(Command.GET_SAVED_POSITION_LIST)
        return self.receive_answer()

    def wait(self, duration):
        self.send_command(Command.WAIT, [duration])
        return self.receive_answer()

    def get_joints(self):
        self.send_command(Command.GET_JOINTS)
        return self.receive_answer()

    def get_pose(self):
        self.send_command(Command.GET_POSE)
        return self.receive_answer()

    def get_hardware_status(self):
        self.send_command(Command.GET_HARDWARE_STATUS)
        return self.receive_answer()

    def get_learning_mode(self):
        self.send_command(Command.GET_LEARNING_MODE)
        return self.receive_answer()

    def get_digital_io_state(self):
        self.send_command(Command.GET_DIGITAL_IO_STATE)
        return self.receive_answer()

    def send_command(self, command_type, parameter_list=None):
        if self.__is_connected is False:
            raise self.ClientNotConnectedException()
        send_success = False
        if self.__client_socket is not None:
            try:
                packet = self.__packet_builder.build_command_packet(command_type, parameter_list)
                self.__client_socket.send(packet)
            except socket.error as e:
                print(e)
                raise self.HostNotReachableException()
        return send_success

    def quit(self):
        self.__is_running = False
        self.__shutdown_connection()
        self.__client_socket = None

    def __shutdown_connection(self):
        if self.__client_socket is not None and self.__is_connected is True:
            self.__client_socket.shutdown(socket.SHUT_RDWR)
            self.__client_socket.close()
            self.__is_connected = False

    def receive_answer(self):
        READ_SIZE = 512
        try:
            received = self.__client_socket.recv(READ_SIZE)
        except socket.error as e:
            print(e)
            raise self.HostNotReachableException()
        # Means client is disconnected
        if not received:
            raise self.HostNotReachableException()
        return received
