# MIT License.
# Copyright (c) 2020 by BioicDL. All rights reserved.
# Created by LiuXb on 2020/11/24
# -*- coding:utf-8 -*-

"""
@Modified: 
@Description:
"""
import threading
import time
import queue

from deepclaw.driver.arms import URController_rtde as URctl
from deepclaw.driver.arms.ArmController import ArmController
import pickle


# receive
class GetRobotData(object):
    def __init__(self):
        self.flag = True

    def stop(self):
        self.flag = False

    # push data to buffer
    def run(self, robot: ArmController, data_buffer: queue.Queue):
        while self.flag:
            status = robot.get_state()
            time.sleep(0.01)
            time_stamp = time.time()
            status.update({'time': time_stamp})
            data_buffer.put(status)
            # print(data_buffer.get())


# write
class SaveRobotData(object):
    def __init__(self):
        self.flag = True

    def stop(self):
        self.flag = False

    def run(self, data_buffer: queue.Queue, filename: str):
        while self.flag:
            time.sleep(0.01)
            if data_buffer.empty():
                continue
            else:
                dd = data_buffer.get()
                with open(filename, "ab") as f:
                    pickle.dump(dd, f)


class MoveRobot(object):
    def __init__(self):
        self.flag = True
        self.action = None
        self.joint = None

    def stop(self):
        self.flag = False

    def set_joints(self, joint):
        self.joint = joint

    def run(self, robot: ArmController, data_buffer: queue.Queue = queue.Queue(maxsize=5000)):
        # get data
        gd = GetRobotData()
        read_thread = threading.Thread(target=gd.run, args=(robot, data_buffer,), daemon=True)
        read_thread.start()
        srd = SaveRobotData()
        write_thread = threading.Thread(target=srd.run, args=(data_buffer, 'test12.result'), daemon=True)
        write_thread.start()
        # robot move
        # start_joints = [-1.57, -1.57, -1.57, -1.9, 1.57, -1.57]
        # target_joints = [-1.57, -1.57, -0.9, -0.8, 1.57, -1.57]
        # robot.move_j(start_joints, 3, 6)
        # robot.move_j(target_joints, 3, 6)

        # start_point = [-0.18246, -0.68835, 0.45416, 1.6984, -1.8888, 0.6290]
        # end_point = [-0.0, -0.4, 0.3, 1.6984, -1.8888, 0.6290]

        start_point = [-0.3892851151079589, -0.3682649768115375, 0.04614461354888244, 2.2542664595069044, -2.1577230405724532, 0.0400075423311235]
        end_point = [0.15187793252132198, -0.3682209644731936, 0.04613768841089927, 2.254392008739246, -2.157709829869653, 0.03999406389204092]
        end_point = [0.15187289148918068, -0.36824285448867394, 0.19094064392090843, 2.2543793879010128, -2.157687910000569, 0.040065884281925035]

        start_point = [-0.11335, -0.30967, 0.12822 + 0.0, 2.2166, -2.2166, 0]
        target_point = [-0.11497, -0.70276, 0.40416+0.05, 1.7987, -1.8151, 0.6662]
        # robot.move_L(start_point)
        # robot.move_L(target_point, 2, 8)

        # robot.move_p(start_point)
        # robot.move_p(target_point, 2, 8)

        start_joint2 = [-1.63, -1.57, -1.57, -1.9, 1.57, -1.57]
        target_joint2 = [-1.63, -1.833, -1.15, -0.8, 1.57, -1.57]

        robot.move_j(start_joint2, 3, 15)
        robot.move_j(target_joint2, 3, 15)

        # robot.move_j(self.joint, 2.8, 2.2)
        gd.stop()
        srd.stop()

        robot.move_L(start_point)



if __name__ == '__main__':
    rb = URctl.URController('../../configs/basic_config/robot_ur5.yaml')
    print('Start move!')
    joints_pos = [-1.41319307, -1.51162964, -1.66329875, -1.50447379,  1.53746051, 0.14490873]
    db = queue.Queue(maxsize=0)
    x = MoveRobot()
    x.set_joints(joints_pos)
    x.run(rb, db)
    # state = robot.get_state()
    # print(state)
    # rb.go_home()
    # home_joints = [-1.57, -1.57, -1.57, -1.9, 1.57, -1.57]
    # # rb.move_j(home_joints, 2, 4)
    # print('reach home pose')

    # for i in range(10):
    #     status = robot.get_state()
    #     time_stamp = time.time()
    #     status.update({'time': time_stamp})
    #     print(status)
    #     time.sleep(0.5)
    #     with open("dict", "ab") as f:
    #         pickle.dump(status, f)
    #
    print('============================================')
    with open("test8.txt", 'rb') as f:
        while True:
            try:
                aa = pickle.load(f)
                print(aa)
            except EOFError:
                break














