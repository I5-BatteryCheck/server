import cv2
import requests
#import serial
from flask import Flask, jsonify, render_template, request, url_for, send_file
from datetime import datetime
from PIL import Image
import json
import numpy as np
import base64


app = Flask(__name__)

front_server_url = ['http://192.168.253.253:5005/test']
model_server_url = ['http://172.16.212.152:5020/model']
#arduino = serial.Serial('COM3', 9600)




#사진 촬영 함수
def capture(n, width=0, height=0):
    # 웹캠 열기
    cap = cv2.VideoCapture(n)  # 0은 기본 웹캠을 의미합니다. 다른 웹캠을 사용하려면 인덱스를 조정하세요.

    if width*height !=0:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if not cap.isOpened():
        print("웹캠을 열 수 없습니다.")
        return

    # 프레임 읽기
    ret, frame = cap.read()

    if not ret:
        print("프레임을 읽을 수 없습니다.")
        return

    # 리소스 해제
    cap.release()

    return frame

# 현재 시간 구하는 함수
def get_time():
    now = datetime.now()
    now = str(now)
    now = now.split('.')[0]
    now = now.replace('-','').replace(' ','').replace(':','')
    return now


def encode_file_to_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string


# 0.5초마다 센서값 http 신호 -> 
#                             센서 값 저장
#                             사진 촬영, 센서 값>리액트
recent_sensors_value ={
    'temperature' : 0,
    'humidity' : 0,
    'Illuminance' : 0,
    'gas' : 0
    }


@app.route('/')
def show_image():
    return '<h1> welcome </h1>'

@app.route('/monitor/<index>', methods=['GET'])
def show_monitor(index):
    image_path = f'./monitor_{index}.jpg'
    return send_file(image_path, mimetype='image/jpg')

@app.route('/sensor', methods=['POST'])
def read_sensor():
    print('/sensor')
    print(1)
    data = request.get_json()
    print(data)

    print(2)
    for key in data.keys():
        recent_sensors_value[key] = data[key]
    
    print(3)
    for n in range(1,2):
        ct = capture(n, 160,140)
        array = ct.astype(np.uint8)
        image = Image.fromarray(array)
        image.save(f'./monitor_{n}.jpg')
    
    print(4)
    return jsonify(data)



@app.route('/sensor_value', methods=['GET'])
def read_monitor():
    print(recent_sensors_value)
    return jsonify(recent_sensors_value)

    
# capture http신호 ->
#                    최근 센서 값과 사진을 촬영해서 > model
@app.route('/capture', methods=['POST'])
def read_capture():
    try:
        print(1)
        data = request.get_json()
        print(11)
        res = {'status': 'success',
               'files' : data}
        print(res)

        print(2)
        if 1:
            data2model = {}
            #data2model['time'] = get_time()
            print(3)
            for key in recent_sensors_value.keys():
                data2model[key] = recent_sensors_value[key]

            with open('./data.json', 'w') as json_file:
                json.dump(data2model, json_file, indent=4) 
            

            print(4)
            files = []
            for n in range(1,2):
                ct = capture(n, 640,480)
                array = ct.astype(np.uint8)
                image = Image.fromarray(array)
                image.save(f'image_{n}.jpg')
                files.append( ('images', (f'image_{n}.jpg', open(f'./image_{n}.jpg', 'rb'), 'image/jpg' )) )
        
            print(5)
            # POST 요청 보내기
            response = requests.post(model_server_url[0], data={'data': json.dumps(data2model)}, files = files)
            print(6)
            response_data = response.json()
            print(response_data)

            return jsonify(res)
        
            
    except:
        print('capture')
 
 
    
# 후처리 결과 http ->
#                   아두이노로 시리얼로 송신 
@app.route('/post_processing', methods=['POST'])
def read_post_processing():
    try:
        data = request.get_json()
        print(data)
        print(data['isNormal'])
        print(data['isNormal'])
        print(data['isNormal'])
        if data:
            print(1)
            data2arduino=data
            print(2)
            #data2arduino=data2arduino.encode('utf-8')
            print(3)
            #arduino.write(data2arduino)
        

        tmp = {}
        return jsonify(tmp)

    except:
        print('post_processing error')
    

if __name__ == '__main__':
    app.run('0.0.0.0', port=5010, debug=True)