from ultralytics import YOLO
import os
import cv2
import requests
from PIL import Image
import numpy as np
from flask import Flask, jsonify,render_template, request
import json


# 후처리 서버 설정
post_processing_url = ['http://172.16.212.152:5030/postprocessing']

# 모델 경로 확인
print('load model')
model_path = './best.pt'
if os.path.exists(model_path):
    model = YOLO(model_path)
else:
    print(f"모델 파일을 찾을 수 없습니다: {model_path}")


app = Flask(__name__)

# 라즈베리로부터 데이터를 받음 -> 
#                              이미지 모델로 
#                             
@app.route('/model', methods=['POST'])
def read_sensor():
    try:
        print("welcome")

        uploaded_files = request.files
        print(0)

        json_data = request.form.get('data')
        print(1)
        data = json.loads(json_data)
        
        print(uploaded_files)
        saved_files = []
        for file_key in uploaded_files:
            print(2)
            print(file_key)
            file = uploaded_files[file_key]
            print(3)
            print(file)
            file_path = os.path.join('./', file.filename)
            file.save(file_path)
            saved_files.append(file.filename)

        print(4)
        results = model(['./image_1.jpg'])
        print(5)
        for i, result in enumerate([results]):
            data[f'{i}'] = {}
            print('-1')
            data[f'{i}']['len'] = len(results[i].boxes.cls.tolist())
            print('-2')
            data[f'{i}']['cls'] = results[i].boxes.cls.tolist()
            print('-3')
            data[f'{i}']['conf'] = results[i].boxes.conf.tolist()
            print('-4')
            data[f'{i}']['xywh'] = results[i].boxes.xywh.tolist()
            print('-5')
            results[i].save(filename=f"./result_{i}.jpg")
            print('-6')

        print(data)
        response = requests.post(post_processing_url[0], json = data)
        response_data = response.json()



        return jsonify(data)
            
        
    except:
        

        print('model_error')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5020, debug=True)