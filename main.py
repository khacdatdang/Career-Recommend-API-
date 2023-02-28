# -*- coding: utf-8 -*-
"""Deployment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JXCe4ppwErikRCQP-sl1crhDktiksR29
"""

# !pip install fastapi
# !pip install pickle5
# !pip install uvicorn
# !pip install pydantic
# !pip install scikit-learn
# !pip install requests
# !pip install pypi-json
# !pip install pyngrok
# !pip install nest-asyncio
# !pip install numpy 
# !pip install pandas
# !pip install matplotlib

from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import json

# from pyngrok import ngrok
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from ast import literal_eval
import numpy as np
from numpy.linalg import norm


from routers import ToolsRoutes
industry_field = pd.read_csv('industry_field.csv')

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class model_input(BaseModel):
  Gender : str
  Age: int 
  Experience: int
  Education: str
  Major: str
  Grade: str
  Skill :list


#loading saved model
group_prediction = pickle.load(open('random_forest_model.sav','rb'))

def normalize_experience(data):
  if data == 0:
    return 0
  elif data > 0 & data <= 2:
    return 1
  elif data > 2 & data < 5:
    return 2
  else:
    return 3  
def normalize_age(data):
  if data < 20:
    return 0
  elif data <= 25:
    return 1
  elif data <= 30:
    return 2
  elif data <= 35:
    return 3
  elif data <= 40:
    return 4
  elif data <=45:
    return 5
  else:
    return 6  
def normalize_education(data):
  if (data == 'U'):
    return 0
  elif data == 'C':
    return 1
  else:
    return 2
def normalize_field(data):
  field_no = industry_field.index[industry_field['Name'] == data][0]
  return field_no

def normalize_gender(data):
  if data == 'Nam':
    return 0
  else : return 1
def normalize_grade(data):
  if data == 'Giỏi':
    return 0
  elif data == 'Khá':
    return 1
  elif data == 'Trung bình':
    return 2

major = pd.read_csv('major.csv')

import math
import re
from collections import Counter

WORD = re.compile(r"\w+")


def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)

def major_search(data):
    max_cosine = 0
    field = ''
    candidate_major = ''
    for index, row in major.iterrows():
        vector1 = text_to_vector(row['Major'])
        vector2 = text_to_vector(data)
        cosine = get_cosine(vector1, vector2)
        if cosine > max_cosine:
            max_cosine = cosine 
            field = row['Field']
            candidate_major = row['Major']
    return field

def normalization_data(data):
  # print(data)
  model_data = {}
  model_data['Gender'] = normalize_gender(data['Gender'])
  model_data['Age'] = normalize_gender(data['Age'])
  model_data['Experience'] = normalize_experience(data['Experience'])
  model_data['Education'] = normalize_education(data['Education'])
  model_data['Grade'] = normalize_grade(data['Grade'])
  # model_data['Major_Field_Text'] = major_search(data['Major'])
  model_data['Major_Field'] = normalize_field(major_search(data['Major']))
  model_data['Skill'] = data['Skill']

  return model_data

@app.get('/')
def read_root():
  return 'Hello world'

@app.post('/career_recommender')
def career_recommender(input_parameters : model_input):
    career_info = pd.read_csv('2802_recommend_career.csv', index_col = 0)
    input_data = input_parameters.json()
    input_dictionary = json.loads(input_data)
    skills = ['Học hiệu quả', 'Lắng nghe tích cực', 'Giải quyết vấn đề phức tạp', 'Làm việc nhóm', 'Tư duy phản biện', 'Bảo trì thiết bị', 'Lựa chọn thiết bị', 'Cài đặt', 'Hướng dẫn', 'Phán đoán và ra quyết định', 'Chiến lược học tập', 'Quản lý tài chính', 'Quản lý tài nguyên vật chất', 'Quản lý tài nguyên nhân sự', 'Toán học', 'Giám sát', 'Đàm phán', 'Điều hành và kiểm soát', 'Phân tích hoạt động', ' Giám sát hoạt động', 'Thuyết phục', 'Lập trình', 'Phân tích kiểm soát chất lượng', 'Đọc hiểu', 'Sửa chữa', 'Khoa học', 'Định hướng dịch vụ', 'Nhận thức xã hội', 'Nói', 'Phân tích hệ thống', 'Đánh giá hệ thống', 'Thiết kế công nghệ', 'Quản lý thời gian', 'Khắc phục sự cố', 'Viết']

    model_data = normalization_data(input_dictionary)
    temp = []
    for i in range(0, len(skills)):
      if (skills[i] in set(model_data['Skill'])):
        temp.append(1)
      else:
        temp.append(0)
      
    
    model_data['Skill']  = temp
    arr = model_data['Gender'], model_data['Experience'] , model_data['Age'] , model_data['Grade'], model_data['Major_Field'], model_data['Education'], model_data['Skill'] 
    # print(arr)
    temp_df = pd.DataFrame([arr],columns = ['Gender','Number of Experience','Age','Grade','Major_Field','Education','Skill_array'])
    # print(temp_df)

    # recommend_career = career_info[career_info['Ngành tiếng việt'] == model_data['Field_Text']]
    recommend_career  = career_info
    group = group_prediction.predict(temp_df.iloc[:,0:-1])[0]
    recommend_career_1 = recommend_career[recommend_career['Group'] == group]
    # print(recommend_career_1)
    recommend_career_2 = recommend_career[recommend_career['Group'] != group]

    recommend_career_1['Weight'] = recommend_career_1['Skill'].apply(lambda x: np.dot(np.array(literal_eval(x)),np.array(temp_df.iloc[0,-1]))  ) 
    recommend_career_2['Weight'] = recommend_career_2['Skill'].apply(lambda x: np.dot(np.array(literal_eval(x)),np.array(temp_df.iloc[0,-1])))
    recommend_career_1.sort_values(by=['Weight']) 
    recommend_career_2.sort_values(by=['Weight'])
    recommend_career = pd.concat([recommend_career_1,recommend_career_2])
    print(recommend_career)
    
    return recommend_career.iloc[0:5,[0,1,3,4]]


app.include_router(ToolsRoutes.router)