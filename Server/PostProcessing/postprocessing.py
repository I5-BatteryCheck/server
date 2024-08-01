import os
import cv2
import requests
from PIL import Image
import numpy as np
from flask import Flask, jsonify,render_template, request



#라즈베리 서버 설정
raspberrypi_url = ['http://172.16.212.152:5010/post_processing']

app = Flask(__name__)

# 라즈베리로부터 데이터를 받음 -> 
#                              이미지 모델로 
#                             
@app.route('/postprocessing', methods=['POST'])
def postprocessing():
    print('welcome postprocessing')
    try:
        print(1)
        data = request.get_json()
        print('--')
        damaged = []
        pollution = []
        
        for i in range(1):
            print(2)
            data_part = data[f'{i}']
            num = data_part['len']
            cls = data_part['cls']
            conf = data_part['conf']
            xywh = data_part['xywh']
            
            print(3)
            if num:
                battery_area = xywh[0][2]*xywh[0][3]
                print(4)
                for n in range(1,num):
                    area = xywh[n][2]*xywh[n][3] / battery_area
                    if cls[n] == 1:
                        damaged.append(area)
                    else:
                        pollution.append(area)

        print(5)
        if (sum(damaged)> 0.01 or sum(pollution)> 0.05 or bool(1-num)):
            data['isNormal'] = False
        else:
            data['isNormal'] = True
        
        print(6)
        # response = requests.post(raspberrypi_url[0], json = data)
        # response_data = response.json()

        data2Ras = {'isNormal' : data['isNormal']}
        response = requests.post(raspberrypi_url[0], json = data2Ras)

        tmp = {}
        return jsonify(tmp)
    
    except:
        print('postprocessing_error')



if __name__ == '__main__':
    app.run('0.0.0.0', port=5030, debug=True)