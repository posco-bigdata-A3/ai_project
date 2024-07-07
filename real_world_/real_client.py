import socket
import pickle
import struct
import time
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image

WS_PC = [0, 180, 0, 300]

def get_workspace_crop(img):
    retval = img[WS_PC[0]:WS_PC[1], WS_PC[2]:WS_PC[3], ...]
    return retval

class RealSenseClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.buffer = b""
        self.remainingBytes = 0
        self.frame_length = None
        self.timestamp = None

    def get_camera_data(self):
        if self.remainingBytes == 0:
            try:
                self.frame_length = struct.unpack('<I', self.socket.recv(4))[0]
                self.timestamp = struct.unpack('<d', self.socket.recv(8))[0]
                self.remainingBytes = self.frame_length
                print(f"Receiving frame of length {self.frame_length}")
            except Exception as e:
                print(f"Error receiving frame length: {e}")
                return None, None
        
        try:
            data = self.socket.recv(self.remainingBytes)
            self.buffer += data
            self.remainingBytes -= len(data)
            
            if len(self.buffer) == self.frame_length:
                depth_img, color_img = pickle.loads(self.buffer)
                self.buffer = b""
                self.remainingBytes = 0
                return depth_img, color_img
            else:
                return None, None
        except Exception as e:
            print(f"Error receiving frame data: {e}")
            return None, None

if __name__ == '__main__':
    ip = "192.168.0.6"
    port = 1024
    realsense = RealSenseClient(ip, port)
    
    counter = 0
    limit = 10
    sleep = 0.05

    while counter < limit:
        depth_img, color_img = realsense.get_camera_data()
        if depth_img is None or color_img is None:
            print("Failed to get frames. Retrying...")
            time.sleep(sleep)
            continue
        
        print("depth img shape: ", depth_img.shape)
        print("color img shape: ", color_img.shape)
        counter += 1
        time.sleep(sleep)
        print('Step counter at {}'.format(counter))

        fig, ax = plt.subplots(2, 2, figsize=(10, 5))
        ax[0][0].imshow(color_img)
        ax[0][1].imshow(depth_img, cmap='gray')
        ax[1][0].imshow(get_workspace_crop(color_img))
        ax[1][1].imshow(get_workspace_crop(depth_img), cmap='gray')
        plt.show()