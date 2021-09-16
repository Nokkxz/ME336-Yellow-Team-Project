import sys
import os

# append the DeepClawDev directory to python path and set it as working directory

_root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(_root_path)
os.chdir(_root_path)
# print('work_dir: ', _root_path)

import time
import yaml
import numpy as np
import matplotlib.pyplot as plt
import cv2
from scipy.spatial.transform import Rotation as R

from deepclaw.driver.arms.ArmController import ArmController
from deepclaw.modules.end2end.yolov5.YOLO5 import Yolo5
from deepclaw.driver.sensors.camera.Realsense_L515 import Realsense
from deepclaw.driver.arms.franka.FrankaController import FrankaController
from deepclaw.modules.grasp_planning.GeoGrasp import GeoGrasp
from deepclaw.driver.arms import URController_rtde as URctl


import _thread
import time


def move_test(robot_server: ArmController, t_joint1, t_joint2, vel=0.4, acc=0.6):
    # while 1:
        robot_server.move_j(t_joint1, vel, acc)
        robot_server.move_j(t_joint2, vel, acc)
        robot_server.gripperGrasp()

def state_test(robot_server: ArmController):
    while 1:
        time.sleep(0.01)
        state = robot_server.get_state()
        if state['Joints_Velocity'][2] > 0.5:
            robot_server.gripperOpen()

        print(state['Joints_Velocity'][2])

if __name__ == '__main__':
    """ Initialization """
    # camera and robot driver
    # print('work_dir: ', _root_path)
    robot = URctl.URController("./configs/basic_config/robot_ur5.yaml")
    # camera = Realsense('./configs/basic_config/camera_rs_d435.yaml')
    # object_detector = Yolo5('./configs/basic_config/yolov5_cfg.yaml')
    # home_joints = [-0.03, -1.3, 0.05, -2.2, 0.08, 1.15, 0.7]
    # robot.move_j(home_joints, 1.5, 1.5)
    home_joints = [-1.57, -1.57, -1.57, -1.57, 1.57, -1.57]

    # robot.move_j(home_joints)

    target_joints = [-1.57, -1.57, -1.0529406706439417, -1.04719, 1.57, -1.57]
#[-1.5700047651873987, -1.526870075856344, -1.0529406706439417, -1.0471933523761194, 1.570023775100708, -1.5700915495501917]
    # print(robot.get_state())


    try:
        _thread.start_new_thread(state_test, (robot,))
        # _thread.start_new_thread(move_test, (robot, home_joints, target_joints, 1,1,))
    except:
        print('Error')

    time.sleep(1)
    move_test(robot, home_joints, target_joints, 1, 1)

    # while 1:
    #     pass