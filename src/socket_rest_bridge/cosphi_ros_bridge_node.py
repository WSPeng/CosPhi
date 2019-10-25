#!/usr/bin/env python3
import requests
import socket
import sys
import math
import copy


class SocketRestBridge:
    def __init__(self):
        self.dict_data = {0: {'x': 0.0, 'y': 0.0, 'yaw_theta': 0.0}}
        # self.json_data_item = {'type': 0, 'r': 0.0, 'rad': 0.0, 'l': 0, 'h': 0, 'yaw_rad': 0.0}
        self.corner_id_start_counting = 13
        self.json_data = {}
        self.origin = [0.0, 0.0]
        self.origin_2 = [0.0, 1,0]
        self.vec_origin2 = [0.0, 0.0]

    def compute_rest_message(self):
        json_data_item = {'type': 0, 'r': 0.0, 'rad': 0.0, 'l': 0, 'h': 0, 'yaw_rad': 0.0}
        for key, value in self.dict_data.items():
            # print(value)
            print(key)
            if float(key) > 13:
                json_data_item['type'] = 4
            elif float(key) < 6:
                json_data_item['type'] = 0
            elif 11 < float(key) < 14:
                json_data_item['type'] = 3
                if float(key) < 13:
                    self.origin = [value['x'], value['y']]
                else:
                    self.origin_2 = [value['x'], value['y']]
                self.vec_origin2 = [self.origin_2[0] - self.origin[0], self.origin_2[1] - self.origin[1]]
            point = [value['x'], value['y']]
            vec1 = [point[0] - self.origin[0], point[1] - self.origin[1]]
            r = math.sqrt((vec1[0])**2 + (vec1[1])**2)
            m1 = (vec1[1] - self.vec_origin2[1])/1
            m2 = (vec1[1] - self.vec_origin2[1])/(vec1[0] - self.vec_origin2[0] + 0.01)
            tn_angle = (m1 - m2)/(1 + m1*m2)
            rad = math.atan(tn_angle)
            json_data_item['r'] = r
            json_data_item['rad'] = rad
            json_data_item['yaw_rad'] = value['yaw_theta']
            # print(json_data_item)
            self.json_data[str(key+1)] = copy.deepcopy(json_data_item)
            # for j in self.json_data:
            #     print(self.json_data[j])

    def run(self):
        # init TCP Socket
        TCP_IP = 'localhost'
        TCP_PORT = 6666
        BUFFER_SIZE = 1024
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))

        # init restful
        rest_ip = "http://127.0.0.1:5000/update"
        json_data = {}

        print("connected to the CosPhi- Topics are Publishing....")
        while True:
            try:
                data = s.recv(BUFFER_SIZE)
                # parse to extract data of each robot
                data = data.decode("utf-8")
                array_robots = data.split('\n')
                # print(array_robots)
                # parse to extract the coordinates of each robot,
                # add them to the standard form then publish them on a topic defined by the robot ID
                for index in range(len(array_robots)-1):
                    Array_All = array_robots[index].split()
                    if Array_All[0] == "Detected":
                        frame_time = Array_All[5]
                    elif Array_All[0] == "Robot":
                        ID = Array_All[1]
                        # publish only fresh positions
                        if Array_All[5] == frame_time:
                            # Topic_Name = '/cosphi_ros_bridge/robot'+ID
                            if float(ID) < 0:
                                self.corner_id_start_counting = self.corner_id_start_counting + 1
                                ID = self.corner_id_start_counting
                            elif float(ID) < 6:
                                ID = int(ID)
                            elif float(ID) < 8:
                                ID = int(ID) + 6

                            x = float(Array_All[2])
                            y = float(Array_All[3])
                            yaw_theta = float(Array_All[4])
                            self.dict_data[ID] = {'x': x, 'y': y, 'yaw_theta': yaw_theta}

                self.compute_rest_message()

                if self.corner_id_start_counting >= 16:
                    self.corner_id_start_counting = 13
                # print(self.json_data)
                r = requests.post(rest_ip, json=self.json_data)
                # print(r.text)
            except KeyboardInterrupt:
                print('close')
                sys.exit(0)


if __name__ == '__main__':
    bridge = SocketRestBridge()
    bridge.run()