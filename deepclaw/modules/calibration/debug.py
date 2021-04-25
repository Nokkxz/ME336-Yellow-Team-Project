import numpy as np
from deepclaw.driver.sensors.camera.Realsense_L515 import Realsense
from scipy.spatial.transform import Rotation as R
import cv2, time

camera = Realsense('./configs/basic_config/camera_rs_d435.yaml')
time.sleep(1)
temp = camera.get_intrinsics()
mtx = np.array( [ [temp[0].fx, 0,  temp[0].ppx],
                                    [0, temp[0].fy, temp[0].ppy], 
                                    [0,0,1]] 
                                )
H_base_camera = np.load("./configs/E_T_B.npy")

def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (0,0,255), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (255,0,0), 5)
    return img

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((8*11,3), np.float32)
objp[:,:2] = (np.mgrid[0:11,0:8]*0.02).T.reshape(-1,2)
axis = np.float32([[0.1,0,0], [0,0.1,0], [0,0,0.1]]).reshape(-1,3)

frame = camera.get_frame()
color = frame.color_image[0]
gray = cv2.cvtColor(color,cv2.COLOR_BGR2GRAY)
ret, corners = cv2.findChessboardCorners(gray, (11,8),None)

corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
# Find the rotation and translation vectors.
ret,rvecs, tvecs = cv2.solvePnP(objp, corners2, mtx, np.array([0.0, 0.0, 0.0, 0.0, 0.0]))

imgpts, jac = cv2.projectPoints(axis, rvecs, tvecs, mtx, np.array([0.0, 0.0, 0.0, 0.0, 0.0]))
img = cv2.drawChessboardCorners(color, (11,8), corners2,ret)
img = draw(color,corners2,imgpts)
cv2.imwrite("board.png",img)

r = R.from_rotvec(rvecs[:,0])
r.as_euler('xyz', degrees=True)  # array([  13.24822816,    0.8891145 , -178.25399893])

rotation = r.as_matrix()

H_camera_board = np.concatenate([np.concatenate([rotation, tvecs[:,0].reshape([3,1])],axis=1),np.array([0, 0, 0, 1]).reshape(1,4)])

H_base_board = np.dot(H_base_camera, H_camera_board)
print("The pose of the chessboard with reference to the robot base")
print(H_base_board)

print("The rpy of the chessboard with reference to the robot base")
rpy = R.from_matrix(H_base_board[:3,:3]).as_euler('xyz', degrees=True)  
print(rpy)
print(mtx)
