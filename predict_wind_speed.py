# -*- coding: utf-8 -*-
"""Predict_Wind_Speed.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1hlIO3zAPJcdEVfjyG-wcdT01CbIYGaGU
"""

!pip install wget

# PREDICT FUNCTION
import wget
from tensorflow import keras
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import date

def get_X_and_y(filename):
  # Read the file called 'filename'.txt and then generate 2 numpy arrays X and y

  # file_wo_ext is file without extension (without '.txt')
  file_wo_ext = str(Path(filename).with_suffix(''))
  print("file_wo_ext=", file_wo_ext)

  # DELETE THE 2ND LINE FROM THE TEXT FILE AND SAVE
  # IT AS A NEW .TXT FILE
  ff = open(file_wo_ext+'_NEW'+'.txt','w')
  with open(file_wo_ext+'.txt') as f:
    lines = f.readlines()
    lines.pop(1)
    ff.writelines(lines)

  df = pd.read_table(file_wo_ext+'_NEW'+'.txt',sep="\s+")
  print("df orig=")
  print(df)

  # Replace all 9 values from all columns except for 'MM' and 'DD' columns
  # df2 = df[df.columns[~df.columns.isin(['MM','DD'])]].replace(9.0, np.NaN)
  # df2 = df2.assign(MM = lambda x: df['MM'])
  # df = df.assign(DD = lambda x: df['DD'])

  # df = df.replace(99.0, np.NaN)
  # df = df.replace(999.0, np.NaN)
  # df = df.replace(9999.0, np.NaN)

  #df = df.replace('MM', np.NaN)

  # For speed model should I not drop rows with 'WDIR' that is null?]
  df = df[df['WDIR'].notna()]
  df = df[df['WSPD'].notna()]
  #df = df[df['WVHT'].notna()]
  #df = df[df['DPD'].notna()]

  df = df.reset_index()

  df = df.drop(['GST', 'APD', 'MWD', 'PRES', 'ATMP', 'WTMP', 'DEWP', 'VIS', 'TIDE'], axis=1)

  # CREATE A NEW COLUMN CALLED DAYS_SINCE_START_OF_YEAR WHICH RECORDS THE NUMBER OF DAYS
  # SINCE THE START OF THE YEAR.
  for index, row in df.iterrows():
      ##print(row['WDIR'], row['WSPD'])
      #print("Cur Date")
      #print(row['#YY'], row['MM'], row['DD'])
      since_date = date(int(row['#YY']), 1, 1)
      cur_date = date(int(row['#YY']), int(row['MM']), int(row['DD']))
      diff_date = cur_date - since_date
      num_days = diff_date.days
      num_hours = int(row['hh']) + int(row['mm'])/60
      #if (index < 100):
      #  print(row['hh'], row['mm'], num_hours)
      num_days += num_hours/24
      #print(num_days)

      df.at[index, 'Days_Since_Start_of_Year'] = num_days

  DF_BY_INDEX = 70/10
  df_new = df[df.index % DF_BY_INDEX == 0]
  df_new = df_new.reset_index()
  print("df_new=")
  print(df_new)

  def create_dataset_without_flatten(X, y, look_back=1):
      dataX, dataY = [], []
      for i in range(X.shape[0]-look_back):
          # MAKE SURE THIS VAR A ONLY CONTAINS THE DAYS_SINCE_START_OF_YEAR COLUMN
          a = X.iloc[i:(i+look_back), :].values
          #print("a=", a)
          dataX.append(a)
          dataY.append(y.iloc[i])

      return np.array(dataX), np.array(dataY)

  rows_shift = 45*10
  #rows_shift = 3
  #X = df_new[['Days_Since_Start_of_Year', 'WVHT', 'DPD']]
  X = df_new[['Days_Since_Start_of_Year']]
  y = df_new['WSPD'].shift(-rows_shift)
  
  
  
  X_np, y_np = create_dataset_without_flatten(X, y, look_back=rows_shift)
  cols_per_row = 1
  #col_index = 0
  X_shape = X_np.shape
  print("X_shape=", X_shape)
  print("y_shape=", y_np.shape)


  return X_np, y_np

def predict_wind(station_name):
  realtime_url = 'https://www.ndbc.noaa.gov/data/realtime2/'+station_name+'.txt'
  filename = wget.download(realtime_url)
  print("filename=", filename)
  # Get the X and y data
  X, y = get_X_and_y(filename)

  # Load the speed model from local directory (on Github) called 'model_speed'
  model_speed = keras.models.load_model('./content/model_speed')

  # numpy array's shape is [number of rows] by 1
  y_pred = model_speed.predict(X)

  print("X SHAPE IN PREDICT=", X.shape)
  return X, y, y_pred

X, y, y_pred = predict_wind('KIKT')
print(X[0,449,0])
X_new = [row[449][0] for row in X]
print(X_new)
out_df = pd.DataFrame({'Date': X_new, 'WSPD_pred': y})
print(out_df)
# 7.7

!unzip "model1 (1).zip"

