FROM youdaoyzbx/ymir-executor:ymir2.1.0-yolov5-v7.0-cu111-tmi

COPY . /app/
RUN pip install flask

CMD python server.py

