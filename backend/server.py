from flask import Flask, render_template, request, Response, redirect
import sys
import time
from datetime import datetime as dt
import os
import requests
import json
from flask_cors import CORS
import pymongo
from redis import Redis


with open('../metadata/config.json', 'r') as f:
    config = json.loads(f.read())

app = Flask(__name__)
CORS(app)

conn = pymongo.MongoClient('mongodb://{}:{}@{}'.format(config['MONGODB']['USERNAME'], config['MONGODB']['PASSWORD'], config['MONGODB']['IP']), int(config['MONGODB']['PORT']))
mongo_db = conn.get_database('2019_appjam_spring') # 데이터베이스 선택
beacon_collection = mongo_db.get_collection('beacon')
env_collection = mongo_db.get_collection('environment')


redis_db = Redis(config['REDIS']['IP'], config['REDIS']['PORT'])


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/')
def index(name=None):
    return 'test'

@app.route('/upload_json', methods = ['POST'])
def upload_json():
    result = request.data
    result = result.decode()
    result = json.loads(result)
    print(result, file=sys.stderr)
    return json.dumps(result)

@app.route('/get_json')
def get_json():
    test_dict = {
        'ch':'abc',
        'numb': 123,
        'numb_2': 1.234,
        'list': [1,2,3,4],
    }
    ret = json.dumps(test_dict)
    return ret

@app.route('/environment', methods = ['GET', 'POST'])
def get_environment():
    if request.method == 'GET' :
        env_data = get_recent_env_data()
        return json.dumps(env_data)
    elif request.method == 'POST' :
        data = request.data
        data = json.loads(data)
        # data = {"time": str(dt.now()), "temperature": 37.5, "humidity": 29.8}
        env_collection.insert(data)
        print(data, file=sys.stderr)
        return 'success'


def init():
    collection = mongo_db.get_collection('environment') # 테이블 선택
    result = collection.find().sort([("time", -1)]).limit(1)
    result = list(result)[0]
    del(result['_id'])
    result = json.dumps(result)
    redis_db.set('recent_environment', result)

def get_recent_env_data():
    result = redis_db.get('recent_environment')
    result = json.loads(result)
    return result

# @app.route('/main')
# def main(name=None):
#     return render_template('main.html', name=name)

# @app.route('/describe_image', methods = ['POST'])
# def describe_image():
#     binary_image = request.data
#     try:
#         # start_time = time.time()
#         result = use_describe_api(binary_image)
#         result = json.loads(result)
#         result = translate_text(result)
#         result = json.dumps(result)
#         # print(time.time() - start_time, file=sys.stderr)
#         # print(result, file=sys.stderr)
#         return result
#     except Exception as e:
#         print(str(e), file=sys.stderr)
#         return 'error'
    
# @app.route('/find_celebrity', methods = ['POST'])
# def find_celebrity():
#     binary_image = request.data
#     try:
#         # start_time = time.time()
#         result = use_analyze_api(binary_image)
#         result = json.loads(result)
#         result = json.dumps(result)
#         # print(time.time() - start_time, file=sys.stderr)
#         # print(result, file=sys.stderr)
#         return result
#     except Exception as e:
#         print(str(e), file=sys.stderr)
#         return 'Celebrity Not Found'


# def use_describe_api(image):
#     api_url = "https://eastasia.api.cognitive.microsoft.com/vision/v2.0/describe"
#     headers = {
#         'Content-Type': 'application/octet-stream',
#         'Ocp-Apim-Subscription-Key': config['vision_key']
#     }
#     params = {'maxCandidates': '1'}
#     data = image

#     resp = requests.post(api_url, params=params, headers=headers, data=data)
#     resp.raise_for_status()
#     return resp.text

# def use_analyze_api(image):
#     api_url = "https://eastasia.api.cognitive.microsoft.com/vision/v2.0/analyze"
#     headers = {
#         'Content-Type': 'application/octet-stream',
#         'Ocp-Apim-Subscription-Key': config['vision_key']
#     }
#     params = {
#         'visualFeatures':'Categories',
#         'details': 'Celebrities',
#         'language': 'en'
#     }
#     data = image

#     resp = requests.post(api_url, params=params, headers=headers, data=data)
#     resp.raise_for_status()
#     return resp.text

# def translate_text(image_data):
#     result = image_data
#     for i, caption in enumerate(image_data["description"]["captions"]):
#         tranlated_text = use_translate_api(caption['text'])
#         result["description"]["captions"][i]['text'] = tranlated_text

#     return result

# def use_translate_api(text):
#     api_url = "https://openapi.naver.com/v1/papago/n2mt"
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
#         'X-Naver-Client-Id': config['papago_id'],
#         'X-Naver-Client-Secret': config['papago_secret']
#     }
#     data= {
#         'source':'en',
#         'target':'ko',
#         'text':text
#     }
#     data = urlencode(data)

#     try:
#         resp = requests.post(api_url, headers=headers, data=data)
#         resp.raise_for_status()
#         res = json.loads(resp.text)
#         return res['message']['result']['translatedText']
#     except Exception as e:
#         print(str(e))
#         return '번역 에러'


def make_current_time_stamp():
    return time.strftime('%y%m%d_%H%M%S')

def make_filepath(dirpath, filename):
    basename = os.path.basename(filename)
    name = os.path.splitext(basename)[0]
    output_file_path = dirpath + '/'
    return (output_file_path, name)


if __name__ == '__main__':
    init()

    app.run(debug=True, host='0.0.0.0', port=8080)