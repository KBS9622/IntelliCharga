import pandas as pd
import numpy as np
from src.grab_tou_data import GrabTOUData
import os
from pandas.tseries.offsets import DateOffset
import matplotlib.pyplot as plt

file_name = 'full_data.csv'


def load_csv_data(file_name, subdir='', header_exists=False):
    """
    Loads data from .csv file in to DataFrame

    :param file_name: .csv file name in string
    :param subdir: optional parameter to specify the subdirectory of the file
    :return: extracted data in DataFrame
    """

    file_dir = os.path.realpath('../')
    for root, dirs, files in os.walk(file_dir):
        if root.endswith(subdir):
            for name in files:
                if name == file_name:
                    file_path = os.path.join(root, name)

    # cols = ['date', 'from', 'code', 'region_name', 'unit_rate_incl_vat']
    if not header_exists:
        df = pd.read_csv(file_path, header=None)
    else:
        df = pd.read_csv(file_path)

    return df


data = load_csv_data(file_name=file_name, subdir="TOU_Data")

print(data.head())
cols = ['date', 'from', 'code', 'region_name', 'unit_rate_incl_vat']
data.columns = cols

print(data.head())

date_list = data['date'].str.split('T', n=1, expand=True)
date_list[1] = date_list[1].str.replace('Z', '')

data['date'] = date_list[0]
data['from'] = date_list[1]
data['date'] = pd.to_datetime(data['date'])
data['from'] = pd.to_timedelta(data['from'])

data['timestamp'] = data['date'] + data['from']
data['timestamp'] += DateOffset(minutes=60)
cols_to_drop = ['date', 'from', 'code', 'region_name']
data.drop(cols_to_drop, axis=1, inplace=True)
data = data.set_index('timestamp')

print(data.tail())

start = pd.to_datetime('2020-09-30 00:00:00')
end = pd.to_datetime('2020-09-30 23:30:00')

# from bs4 import BeautifulSoup
# # from selenium import webdriver
# # from selenium.webdriver.support.ui import WebDriverWait
# # from selenium.webdriver.support import expected_conditions as ec
# # from selenium.webdriver.common.by import By
# import pandas as pd
# import requests
# import csv
#
# # driver = webdriver.Chrome('../utils/chromedriver.exe')
#
#
# start_time = pd.to_datetime('2019-01-31 01:23:00')
# end_time = pd.to_datetime('2019-01-31 23:13:00')
#
# if start_time:
#     print(start_time.date())
#
#
# def convert_acc(x):
#     x = int(x, 16)
#     if x > 127:
#         x = x - 256
#     return np.float64(x * 0.01536)
#
# def convert_mag(x):
#     x = int(x,16)
#     if x>32767:
#         x = x-65536
#     return np.float64(x*0.0366)
#
#
# def convert_acc_mag_row(row):
#     # Initially the data was gathered without magnetometer, so check length for identification #
#     data_dict = {'x': [], 'y': [], 'z': []}
#     if len(row) == 162:
#         data_dict['mx'] = convert_mag(row[:4])
#         data_dict['my'] = convert_mag(row[4:8])
#         data_dict['mz'] = convert_mag(row[8:12])
#         row = row[12:]
#         for i in range(0, len(row), 6):
#             data_dict['x'].append(convert_acc(row[i:i+2]))
#             data_dict['y'].append(convert_acc(row[i+2:i+4]))
#             data_dict['z'].append(convert_acc(row[i+4:i+6]))
#     return data_dict
#
#
# def convert_to_units1():
#     global df
#     df['accData'] = df['accData'].apply(convert_acc_mag_row)
#     df = df.reset_index(drop=True)
#     df = df.drop(0).reset_index(drop=True)
#     data = df['accData'][df['speed'] <= 1]
#     [x, y, z] = data
#     [mx, my, mz] = df[['mx', 'my', 'mz']][df['speed'] <= 1].mean().tolist()
#     [x, y, z] = df['accData'][df['speed'] <= 1].iloc[0].mean().tolist()
#     phi = math.atan(y / z)
#     theta = math.atan(-x / (y * math.sin(phi) + z * math.cos(phi)))
#     Rx = np.array([[1, 0, 0], [0, math.cos(phi), math.sin(phi)], [0, -math.sin(phi), math.cos(phi)]])
#     Ry = np.array([[math.cos(theta), 0, -math.sin(theta)], [0, 1, 0], [math.sin(theta), 0, math.cos(theta)]])
#     Rz = np.array([[math.cos(phi), math.sin(phi), 0], [-math.sin(phi), math.cos(phi), 0], [0, 0, 1]])
#
#     R = Rx.dot(Ry).dot(Rz)
#     R = np.linalg.inv(R)
#
#     def rotate_acc(row):
#         A = np.array([[row['ax']], [row['ay']], [row['az']]])
#         B = np.dot(R, A)
#         return B[:, 0]
#
#     acc_sample = df['accData'].iloc[0]
#     acc_sample.apply(rotate_acc, axis=1)
#
# def convert_to_units(all_data):
#     acc_data = all_data["accData"]
#     j = 0
#     for acc_sample in acc_data:
#         if len(acc_sample) == 162:
#             acc_sample = acc_sample[12:]
#             for i in range(0, len(acc_sample), 6):
#                 x = convert_acc(acc_sample[i:i + 2])
#                 y = convert_acc(acc_sample[i + 2:i + 4])
#                 z = convert_acc(acc_sample[i + 4:i + 6])
#
#                 # Apply rotation matrix and store the values
#                 A = np.array([[x], [y], [z]])
#                 try:
#                     phi = math.atan(y / z)
#                     theta = math.atan(-x / (y * math.sin(phi) + z * math.cos(phi)))
#                 except Exception:
#                     print(y, z)
#                 Rx = np.array([[1, 0, 0], [0, math.cos(phi), math.sin(phi)], [0, -math.sin(phi), math.cos(phi)]])
#                 Ry = np.array(
#                     [[math.cos(theta), 0, -math.sin(theta)], [0, 1, 0], [math.sin(theta), 0, math.cos(theta)]])
#                 Rz = np.array([[math.cos(phi), math.sin(phi), 0], [-math.sin(phi), math.cos(phi), 0], [0, 0, 1]])
#
#                 R = Rx.dot(Ry).dot(Rz)
#                 R = np.linalg.inv(R)
#
#                 B = np.dot(R, A)
#                 x, y, z = B[:, 0]
#                 df_acc = pd.DataFrame({'x': x, 'y': y, 'z': z}, index=[i / 6 + j])
#                 all_data = all_data.append(df_acc)
#             j += 25
#     return df
#
#
#
#
#
#
#
#
#
#
