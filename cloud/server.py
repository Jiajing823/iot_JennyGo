from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import json
import pickle
import os
import numpy as np
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from joblib import dump,load
import matplotlib.image as mpimg
from datetime import datetime



UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'iot'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/iot'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mongo= PyMongo(app)
##formal

@app.route('/turtle/status/<state>', methods=['POST'])
def status(state):
    record= mongo.db.userrecord
    now = datetime.now()
    current_time = now.strftime("%Y/%m/%d %H:%M:%S")
    record.insert({'time': current_time, 'status': state})
    return 'OK', 200

@app.route('/turtle/run', methods=['GET'])
def run():
    record= mongo.db.userrecord
    latest = record.find_one(sort=[("_id",-1)])
    return jsonify({'time': latest['time'], 'status': latest['status']})

@app.route('/turtle/post/sensor', methods=['POST'])
def sensor():
    sensor= mongo.db.sensor
    temp= request.json["temperature"]
    humid= request.json["humidity"]
    light = request.json['light']
    trial= request.json["trial"]
    sensor.insert({'trial': trial, 'temperature': temp, 'humidity': humid, 'light':int(light)})
    return jsonify({'result':1})

@app.route('/turtle/get/stats', methods=['GET'])
def stats():
    sensor= mongo.db.sensor
    stats = sensor.find_one(sort=[("_id",-1)])
    temp = stats['temperature']
    humid = stats['humidity']
    light = stats['light']
    return jsonify({'temperature':int(temp), 'humidity':int(humid), 'light':int(light)})

@app.route('/turtle/post/img/<label>', methods=['POST'])
def post_image_train(label):
    # Get the name of the uploaded file
    img_file = request.files['file']
    # Make the filename safe, remove unsupported chars
    filename = secure_filename(img_file.filename)

    # Move the file form the temporal folder to
    # the upload folder we setup
    save_folder = os.path.join(app.config['UPLOAD_FOLDER'], os.path.join('train/',label))
    save_path = os.path.join(save_folder, filename)
    img_file.save(save_path)
    return 'OK', 200

@app.route('/turtle/post/img/test', methods=['POST'])
def post_image_test():
    sensor = mongo.db.sensor
    response = mongo.db.response
    from test import test
    from utils import judge
    from train import rgb2gray
    # Get the name of the uploaded file
    for i in range(5):
        img_file = request.files['file%s' % str(i)]
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(img_file.filename)
        save_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'test')
        img_path = os.path.join(save_folder, filename)
        img_file.save(img_path)
        image = mpimg.imread(img_path)
        if i == 0:
            images = image
            images = rgb2gray(images)
        else:
            image = rgb2gray(image)
            images = np.concatenate((images, image),axis=2)
        os.remove(img_path)
    judge(pred)
    return 'OK', 200

@app.route('/turtle/get/img/snapshots', methods=['GET'])
def get_image_snapshots(): 
    filename = '20.jpg'
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],'snapshots'),
                               filename)

@app.route('/turtle/post/img/snapshots', methods=['POST'])
def post_image_snapshots():    
    # Get the name of the uploaded file
    img_file = request.files['file']
    # Make the filename safe, remove unsupported chars
    filename = secure_filename(img_file.filename)

#     # Move the file form the temporal folder to
#     # the upload folder we setup
    save_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'snapshots')
    save_path = os.path.join(save_folder, filename)
    img_file.save(save_path)
    return 'OK', 200

@app.route('/turtle/post/result', methods=['GET','POST'])
def result():
    from message import message
#     sensor = mongo.db.sensor
    response = mongo.db.response
    f = open('predictions.pkl', 'rb')
    predictions = pickle.load(f)
    f.close()
    pred = predictions['current']
    mood = list(predictions['mood'].keys())[np.argmax([value for value in predictions['mood'].values()])]
    personality = predictions['personality']
    msg = request.data.decode('utf-8')
    keyword = message(msg)
    if (personality == 'Mysterious'):
        res_set = response.find({"TOPIC": keyword, "LABEL2": mood})
    else:
        res_set = response.find({"TOPIC": keyword, "LABEL1": personality, "LABEL2": mood})
    num_res = res_set.count()
    idx = np.random.randint(0,num_res)
    result = res_set[idx]
    answer = {"class": pred, "answer": result['RESPONSE'], "mood": result['LABEL2'], "personality": result['LABEL1']}
    return jsonify(answer)


if __name__== '__main__':
    app.run(debug=True, host="0.0.0.0", port= 5000)