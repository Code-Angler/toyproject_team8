import flask
import crawler

from pymongo import MongoClient
from datetime import datetime
from bs4 import BeautifulSoup

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta


# HTML 화면 보여주기
@app.route('/')
def home():
    # 김선용 파트!

    # db.visitorCounter.insert_one({'Counts': 0})
    # db.visitorsToday.insert_one({'today date': 0})
    # db.todayCounter.insert_one({'todayCounts': 0})
    # db.visitorIP.insert_one({'IP': flask.request.remote_addr})
    # db.final_result.insert_one({"type": "판다형", "counts": 1})
    # db.final_result.insert_one({"type": "2형", "counts": 1})
    # db.final_result.insert_one({"type": "3형", "counts": 1})
    # db.final_result.insert_one({"type": "4형", "counts": 1})
    # db.final_result.insert_one({"type": "5형", "counts": 1})
    # db.final_result.insert_one({"type": "6형", "counts": 1})
    # db.final_result.insert_one({"type": "7형", "counts": 1})
    # db.final_result.insert_one({"type": "8형", "counts": 1})
    # db.final_result.insert_one({"type": "9형", "counts": 1})
    # db.final_result.insert_one({"type": "10형", "counts": 1})
    # db.final_result.insert_one({"type": "11형", "counts": 1})
    # db.final_result.insert_one({"type": "12형", "counts": 1})
    # db.final_result.insert_one({"type": "13형", "counts": 1})
    # 처음 파일 연 사람 이 4줄 실행할것, 오류 날 시 MongoDB 열어서 visitorIP 수동으로 추가해줄 것!

    # db.visitorCounter.update_one({"Counts" : 0})  # 초기 방문자수 0으로 세팅하기
    # db.todayCounter.update_one({"todayCounts": 0})  # 일일 방문자수 0으로 세팅하기

    visitor_counts = db.visitorCounter.find_one({})['Counts']  # 총 방문자수
    today_visitor_counts = db.todayCounter.find_one({})['todayCounts']  # 일일 방문자수

    ip_address = flask.request.remote_addr  # 방문자 IP 주소

    today = str(datetime.now())
    today_date = today.split(' ')[0]

    # 일일 방문자수 로직
    if db.visitorsToday.find({'today date': today_date}).count() > 0:  # 날짜가 그대로라면
        if db.visitorIP.find({'IP': ip_address}).count() > 0:  # 방문했던 IP 라면 카운트 변동 없음
            pass
        else:  # 날짜가 그대로고, 방문했던 IP가 아니라면
            updated_today_visitor_counts = today_visitor_counts + 1
            db.todayCounter.update_one({'todayCounts': today_visitor_counts},
                                       {'$set': {'todayCounts': updated_today_visitor_counts}})
    else:  # 날짜가 바뀌었다면
        db.visitorsToday.insert_one({'today date': today_date})  # DB 날짜를 업데이트
        db.todayCounter.update_one({'todayCounts': today_visitor_counts},
                                   {'$set': {'todayCounts': 0}})  # 일일 방문자수를 0으로 세팅
        if db.visitorIP.find({'IP': ip_address}).count() > 0:  # 방문했던 IP 라면 카운트 변동 없음
            pass
        else:  # 날짜가 그대로고, 방문했던 IP가 아니라면
            db.todayCounter.update_one({'todayCounts': 0},
                                       {'$set': {'todayCounts': 1}})

    # 총 방문자수 로직
    if db.visitorIP.find({'IP': ip_address}).count() > 0:  # 방문했던 IP 라면 카운트 변동 없음
        pass
    else:  # 방문하지 않았던 IP 라면 해당 IP를 DB에 추가하고, 카운트 +1
        db.visitorIP.create_index("date", expireAfterSeconds=5)  # 숫자는 '초' 단위. IP를 얼마나 저장할 것인가
        db.visitorIP.insert_one({'IP': ip_address, "date": datetime.utcnow()})
        updated_visitor_counts = visitor_counts + 1
        db.visitorCounter.update_one({'Counts': visitor_counts}, {'$set': {'Counts': updated_visitor_counts}})

    return render_template('home.html')


# API 역할을 하는 부분
@app.route('/visitor', methods=['POST'])
def save_name():
    name_receive = request.form['name_give']

    doc = {
        'name': name_receive
    }

    db.visitorsName.insert_one(doc)

    return jsonify({'msg': '저장 완료'})

@app.route('/api/todayCounts', methods=['GET'])
def show_todayCounts():
    db_today_counts = list(db.todayCounter.find({}, {'_id': False}))
    return jsonify({'today_counts': db_today_counts})


@app.route('/api/totalCounts', methods=['GET'])
def show_totalCounts():
    db_total_counts = list(db.visitorCounter.find({}, {'_id': False}))
    return jsonify({'total_counts': db_total_counts})

@app.route('/api/monitor', methods=['GET'])
def show_monitor():
    crawler.bs("모니터")
    crawling_list = list(db.crawling.find({}, {'_id': False}))
    return jsonify({'monitor': crawling_list})

@app.route('/api/<english_name>', methods=['GET'])
def show_item(search_name, english_name):  # 동적 url 테스트 함수
    crawler.bs(search_name)
    crawling_list = list(db.crawling.find({'name':search_name}, {'_id': False}))
    return jsonify({english_name: crawling_list})

@app.route('/result', methods=['POST'])
def count_result():
    result_receive = request.form['result_give']
    count_receive = 0

    doc = {
        'type': result_receive,
        'counts': count_receive
    }
    db.final_result.insert_one(doc)

    if (db.final_result.find_one({'counts': 0})['type']) == "판다형":
        counts = db.final_result.find_one({'type': '판다형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '판다형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '2형':
        counts = db.final_result.find_one({'type': '2형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '2형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '3형':
        counts = db.final_result.find_one({'type': '3형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '3형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '4형':
        counts = db.final_result.find_one({'type': '4형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '4형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '5형':
        counts = db.final_result.find_one({'type': '5형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '5형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '6형':
        counts = db.final_result.find_one({'type': '6형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '6형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '7형':
        counts = db.final_result.find_one({'type': '7형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '7형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '8형':
        counts = db.final_result.find_one({'type': '8형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '8형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '9형':
        counts = db.final_result.find_one({'type': '9형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '9형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '10형':
        counts = db.final_result.find_one({'type': '10형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '10형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '11형':
        counts = db.final_result.find_one({'type': '11형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '11형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '12형':
        counts = db.final_result.find_one({'type': '12형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '12형'}, {'$set': {'counts': updated_counts}})
    elif (db.final_result.find_one({'counts': 0})['type']) == '13형':
        counts = db.final_result.find_one({'type': '13형'})['counts']
        updated_counts = counts + 1
        db.final_result.update_one({'type': '13형'}, {'$set': {'counts': updated_counts}})

    db.final_result.delete_many({'counts': 0})

    return jsonify({'result': 'success'})

@app.route('/result/statistic', methods=['GET'])
def make_statistic():
    result_list = list(db.final_result.find({}, {'_id': False}))
    return jsonify({'statistic': result_list})

# @app.route('/api/like', methods=['POST'])
# def like_star():
#     visitor_today_receive = request.form['sample_give']
#     print(sample_receive)
#     return jsonify({'msg': 'like 연결되었습니다!'})
#
#
# @app.route('/api/delete', methods=['POST'])
# def delete_star():
#     sample_receive = request.form['sample_give']
#     print(sample_receive)
#     return jsonify({'msg': 'delete 연결되었습니다!'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
