import pickle
import numpy as np
from matplotlib import pyplot as plt
import csv
import xlsxwriter


# csv_file = open('data6.csv', 'w', newline='')
# writer = csv.writer(csv_file)
work_book = xlsxwriter.Workbook('data11.xlsx')
worksheet = work_book.add_worksheet()

with open("test12.result", 'rb') as f:
    flag = True
    row = 0
    while True:
        try:
            positionArray = []
            velocityArray = []
            aa = pickle.load(f)
            # if flag:
            #     writer.writerow(aa.keys())
            #     flag = False
            for j in range(6):

                worksheet.write(row, j, aa['Joints'][j])
                worksheet.write(row, j+6, aa['Joints_Velocity'][j])
                worksheet.write(row, j + 12, aa['TCP_Pose'][j])
                worksheet.write(row, j + 18, aa['TCP_Velocity'][j])
            row += 1
            # positionArray.append(aa['Joints'])
            # velocityArray.append(aa['Joints_Velocity'])
            # writer.writerow(positionArray)
            # positionArray.append(aa['Joints'])
            # velocityArray.append(aa['Joints_Velocity'])

        except EOFError:
            break


    work_book.close()

