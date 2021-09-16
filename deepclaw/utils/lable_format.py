# MIT License.
# Copyright (c) 2021 by BioicDL. All rights reserved.
# Created by LiuXb on 2021/2/8
# -*- coding:utf-8 -*-

"""
@Modified: 
@Description: transfer mask format to other label format(yolo, coco .ect)
"""
import getpass
import glob
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import sys
import json
import time


def del_file(path_data):
    for i in os.listdir(path_data):
        file_data = path_data + "/" + i
        if os.path.isfile(file_data):
            os.remove(file_data)
        else:
            del_file(file_data)

def get_folder_list(target_path='./GraspingData/metal/'):
    folder_list = glob.glob(os.path.join(target_path, '*'))
    folder_list.sort()
    return folder_list


def get_mask_list(target_path='./20210125211711', camera_id='camera0', label_folder='labels_rembg'):
    label_path = os.path.join(target_path, camera_id, label_folder)
    mask_list = glob.glob(os.path.join(label_path, '*.pgm'))
    mask_list.sort()
    return mask_list


#obj_c = {'glass': 0, 'paper': 1, 'metal': 2, 'plastic': 4}
obj_c = {'bottle': 0, 'can': 1, 'glass': 2, 'box': 3}
is_debug = False
label_dict = {"version": [], "shapes": [], 'imagePath': [], "imageHeight": [], "imageWidth": []}
shape_dict = {"label": [], "mask_index": [], "mask_path": [], "position": [], "angle": []}


class LabelGenerator(object):
    """ transfer mask format to other label format(yolo, coco .ect)"""
    def __init__(self, input_path='./GraspingData/metal/', camera_id='camera0', src_label_folder='labels_rembg'):
        self.folder_list = [input_path] #glob.glob(os.path.join(input_path, '*'))
        #self.folder_list.sort()
        self.cameraID = camera_id
        self.src_label = src_label_folder
        self.category = None

    def set_object_class(self, obj_class='paper'):
        self.category = obj_class

    def transfer2yolo(self):
        """ yolo label file is a txt file,
        each label information in it is 'class norm_center_x norm_centenorm_width norm_height' """
        """ """
        yolo_label_path = 'labels_yolo'
        for i in self.folder_list:
            temp_mask_list = get_mask_list(i, camera_id=self.cameraID, label_folder=self.src_label)
            # create label folder
            output_label_path = os.path.join(i, self.cameraID, yolo_label_path)

            if not os.path.isdir(output_label_path):
                os.makedirs(output_label_path)
            else:
                del_file(output_label_path) # delete existed file

            with open(os.path.join(output_label_path, 'classes.txt'), 'a') as f:
                for sub_key in obj_c.keys():
                    f.write("%s\n" % sub_key)

            for temp_mask_img in temp_mask_list:
                mask = cv2.imread(temp_mask_img, cv2.IMREAD_ANYDEPTH)
                label_path = temp_mask_img.split('.')[0] + '.json'
                labels_file = temp_mask_img.split('/')[-1].split('.')[0] + '.txt'
                temp_mask = np.zeros(mask.shape, dtype='uint8')
                width = mask.shape[1]
                height = mask.shape[0]
                if not os.path.isfile(label_path):
                    if self.category is None:
                        print('Set object class!!')
                    temp_mask[np.where(mask != 0)] = 1

                    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                    # temp_mask = cv2.erode(temp_mask, kernel)
                    # temp_mask = cv2.dilate(temp_mask, kernel)

                    # stats: [col_left,row_top, width, height]
                    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(temp_mask, connectivity=4, ltype=cv2.CV_32S)
                    # plt.imshow(labels)
                    # plt.show()
                    print(num_labels)
                    if num_labels == 1:
                        # no object
                        continue
                    if is_debug:
                        for k in range(num_labels):
                            cv2.rectangle(temp_mask, (stats[k][0], stats[k][1]), (stats[k][0]+stats[k][2], stats[k][1]+stats[k][3]), (1,1,1), 2)
                            cv2.circle(temp_mask, (int(centroids[k][0]), int(centroids[k][1])), 2, (1, 1, 1), 2)
                        cv2.imshow('rect', temp_mask*255)
                        cv2.waitKey()
                    # object rectangle
                    for k in range(1, num_labels):
                        center_x = (stats[k][0] + stats[k][2]/2)/width
                        center_y = (stats[k][1] + stats[k][3]/2)/height
                        rect_width = stats[k][2]/width
                        rect_height = stats[k][3]/height
                        with open(os.path.join(output_label_path, labels_file), 'a') as f:
                            f.write("%d %.6f %.6f %.6f %.6f\n" % (obj_c[self.category], center_x, center_y, rect_width, rect_height))
                else:
                    with open(label_path) as f:
                        data = json.load(f)

                    for k in data['shapes']:
                        obj_mask = temp_mask.copy()
                        obj_mask[np.where(mask == k['mask_index'])] = 1
                        # plt.imshow(obj_mask)
                        # plt.show()
                        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(obj_mask, connectivity=4, ltype=cv2.CV_32S)
                        if num_labels == 1:
                            # no object
                            continue
                        if is_debug:
                            for m in range(1, num_labels):
                                cv2.rectangle(obj_mask, (stats[m][0], stats[m][1]), (stats[m][0]+stats[m][2], stats[m][1]+stats[m][3]), (1,1,1), 2)
                                cv2.circle(obj_mask, (int(centroids[m][0]), int(centroids[m][1])), 2, (1, 1, 1), 2)
                            cv2.imshow('rect', obj_mask*255)
                            cv2.waitKey()

                        # object rectangle
                        for m in range(1, num_labels):
                            center_x = (stats[m][0] + stats[m][2]/2)/width
                            center_y = (stats[m][1] + stats[m][3]/2)/height
                            rect_width = stats[m][2]/width
                            rect_height = stats[m][3]/height
                            rect_area = rect_width*rect_height

                            # if rect_width > rect_height:
                            #     rect_longer = rect_width
                            #     rect_shorter = rect_height
                            # else:
                            #     rect_longer = rect_height
                            #     rect_shorter = rect_width

                            # print(rect_width)
                            # print(rect_height)
                            # plt.imshow(obj_mask)
                            # plt.show()
                            #
                            # if rect_area < 0.001 or rect_area > 0.02\
                            #         or rect_longer > 0.3 or rect_longer < 0.1\
                            #         or rect_shorter < 0.04 or rect_shorter > 0.1:
                            #     continue



                            with open(os.path.join(output_label_path, labels_file), 'a') as f:
                                f.write("%d %.6f %.6f %.6f %.6f\n" % (obj_c[k['label']], center_x, center_y, rect_width, rect_height))

    def transfer2coco(self):
        pass


if __name__ == "__main__":
    print('Label Format Test! \n')
    # object category

    user_name = getpass.getuser()
    # folder_name = time.strftime("%Y%m%d", time.localtime())
    # folder_path = os.path.join('/media', user_name, 'BARD/Yellow_team/20210417/GraspingData/', folder_name)

    # folder_name = time.strftime("%Y%m%d", time.localtime())
    ##### change the folder name here
    folder_name = "20210514_box"
    folder_path = os.path.join('/home/doyle/Documents/Yellow_team/20210417/GraspingData', folder_name)

    #folder_path = '/home/bionicdl-saber/Documents/GitHub/DeepClawDev/projects/ICRA2020/GraspingData/metal'

    ss = LabelGenerator(input_path=folder_path)
    ss.set_object_class('box')
    ss.transfer2yolo()


