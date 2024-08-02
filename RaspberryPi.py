
import cv2
import requests
import serial
from flask import Flask, jsonify, render_template, request, url_for, send_file
from datetime import datetime
from PIL import Image
import json
import numpy as np
import base64
import time
import signal
import sys
app = Flask(__name__)
front_server_url = ['http://192.168.253.253:5005/test']
model_server_url = ['http://172.16.212.152:5020/model']
#arduino = serial.Serial('/dev/ttyACM0', 9600)
# 라즈베리에서 인식한 웹캠의 인덱스 ls /dev/video*로 확인 후 수정
first_camera_index = 0
camera_array = [0,2]
# 웹캠 객체를 전역 변수로 선언
webcams = {}
def initialize_webcams():
    for index in camera_array:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            webcams[index] = cap
        else:
            print(f"웹캠 {index}을(를) 열 수 없습니다. 다시 시도합니다.")
            cap.release()
            time.sleep(2)  # 잠시 대기 후 다시 시도
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                webcams[index] = cap
                print(f"웹캠 {index}을(를) 성공적으로 열었습니다.")
            else:
                print(f"웹캠 {index}을(를) 여는 데 실패했습니다.")

def release_webcams():
    for cap in webcams.values():
        cap.release()
    print("모든 웹캠을 해제했습니다.")

def capture(n, width=0, height=0):
    cap = webcams.get(n)
    if cap is None or not cap.isOpened():
        print(f"웹캠 {n}이(가) 열려 있지 않습니다.")
        return
    if width * height != 0:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        return
    return frame

def get_time():
    now = datetime.now()
    now = str(now).split('.')[0].replace('-', '').replace(' ', '').replace(':', '')
    return now

def encode_file_to_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string
recent_sensors_value = {
    'temperature': 0,
    'humidity': 0,
    'Illuminance': 0,
    'gas': 0
}

@app.route('/camera_on', methods=['GET'])
def camera_on():
    try:
        initialize_webcams()
        return jsonify({'status': 'success', 'message': 'Cameras initialized.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/camera_off', methods=['GET'])
def camera_off():
    try:
        release_webcams()
        return jsonify({'status': 'success', 'message': 'Cameras released.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/')
def show_image():
    return '<h1> welcome </h1>'

@app.route('/monitor/<index>', methods=['GET'])
def show_monitor(index):
    image_path = f'./monitor_{index}.jpg'
    return send_file(image_path, mimetype='image/jpg')

@app.route('/sensor', methods=['POST'])
def read_sensor():
    data = request.get_json()
    image_index = 0  # 이미지 저장시 이미지간 식별을 위한 인덱스 first_camera_index -> 0 , second_camera_index -> 1 ...
    for key in data.keys():
        recent_sensors_value[key] = data[key]
    for n in camera_array:
        ct = capture(n, 160, 140)
        if ct is not None:
            array = ct.astype(np.uint8)
            image = Image.fromarray(array)
            image.save(f'./monitor_{n}.jpg')
        image_index += 1
    return jsonify(data)

@app.route('/sensor_value', methods=['GET'])
def read_monitor():
    return jsonify(recent_sensors_value)

@app.route('/capture', methods=['POST'])
def read_capture():
    try:
        data = request.get_json()
        res = {'status': 'success', 'files': data}
        data2model = {}
        for key in recent_sensors_value.keys():
            data2model[key] = recent_sensors_value[key]
        with open('./data.json', 'w') as json_file:
            json.dump(data2model, json_file, indent=4)
        image_index = 0
        files = []
        for n in camera_array:
            ct = capture(n, 640, 480)
            if ct is not None:
                array = ct.astype(np.uint8)
                image = Image.fromarray(array)
                image.save(f'image_{image_index}.jpg')
                files.append(('images', (f'image_{image_index}.jpg', open(f'./image_{n}.jpg', 'rb'), 'image/jpg')))
            image_index += 1
        response = requests.post(model_server_url[0], data={'data': json.dumps(data2model)}, files=files)
        response_data = response.json()
        return jsonify(res)
    except Exception as e:
        print(f'capture error: {e}')

@app.route('/post_processing', methods=['POST'])
def read_post_processing():
    try:
        data = request.get_json()
        if data:
            data2arduino = json.dumps(data).encode('utf-8')
            #arduino.write(data2arduino)
        return jsonify({})
    except Exception as e:
        print(f'post_processing error: {e}')
        
def signal_handler(sig, frame):
    print('프로그램을 종료합니다.')
    release_webcams()
    sys.exit(0)
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)  # SIGINT 신호(Ctrl+C)를 처리하는 핸들러 설정
    #initialize_webcams()
    try:
        app.run('0.0.0.0', port=5010, debug=True)
    finally:
        release_webcams()
