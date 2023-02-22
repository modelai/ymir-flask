import base64
import io
import json
import os
import shutil
import subprocess
import time

import requests
from flask import Flask, jsonify, render_template, request
from PIL import Image

# 初始化Flask应用
app = Flask(__name__)
IMG_FOLDER = os.path.join('static', 'IMG')
app.config['UPLOAD_FOLDER'] = IMG_FOLDER


@app.route('/')
def index():
    return render_template('server.html')


# 定义API接口
@app.route('/predict', methods=['POST'])
def predict():
    # 获取上传的图片数据
    # image_data = request.json['image']

    # 将base64编码的图片数据转换为PIL.Image对象
    # image_bytes = base64.b64decode(image_data)
    # image = Image.open(io.BytesIO(image_bytes))

    image_file = request.files['image']
    print(image_file)
    image = Image.open(image_file)
    width, height = image.size
    time_stamp = str(round(time.time()))
    image.save(f'{time_stamp}.jpg')

    # 进行预测
    class_names = ['dog']
    cmd = f'python3 detect.py --source {time_stamp}.jpg --weights dog.pt --save-txt --save-conf --exist-ok'
    subprocess.run(cmd.split(), check=True)

    # 返回预测结果
    output_image = f'runs/detect/exp/{time_stamp}.jpg'
    static_image = os.path.join(IMG_FOLDER, os.path.basename(output_image))
    os.makedirs(IMG_FOLDER, exist_ok=True)
    shutil.move(output_image, static_image)
    with open(f'runs/detect/exp/labels/{time_stamp}.txt', 'r') as fp:
        lines = fp.readlines()

    results = []
    for line in lines:
        class_id, cx, cy, w, h, conf = [float(i) for i in line.split()]
        x1 = round((cx - w / 2) * width)
        x2 = round((cx + w / 2) * width)
        y1 = round((cy - h / 2) * height)
        y2 = round((cy + h / 2) * height)
        results.append(
            dict(class_name=class_names[int(class_id)], x1=x1, y1=y1, x2=x2, y2=y2, confidence=round(conf, 2)))
    return render_template('result.yaml',
                           user_image=static_image,
                           height=height,
                           width=width,
                           result=json.dumps(results))


# 启动API服务器
if __name__ == '__main__':
    app.run(debug=True, port=15500, host='0.0.0.0')
