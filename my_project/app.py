from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbsparta


# HTML 화면 보여주기
@app.route('/')
def home():
    return render_template('index.html')


# API 역할을 하는 부분
# 1. 일정 생성(Create) - /makesche (POST)
@app.route('/makesche', methods=['POST'])
def make_sche():
    todo = request.form['todo']
    start_date = request.form['start_date']
    start_time = request.form['start_time']
    end_date = request.form['end_date']
    end_time = request.form['end_time']
    startend = request.form['startend']
    alert1_day = request.form['alert1_day']
    alert1_time = request.form['alert1_time']
    alert2_day = request.form['alert2_day']
    alert2_time = request.form['alert2_time']
    memo = request.form['memo']
    doc = {
        'todo': todo,
        'start_date': start_date,
        'start_time': start_time,
        'end_date': end_date,
        'end_time': end_time,
        'startend': startend,
        'alert1_day': alert1_day,
        'alert1_time': alert1_time,
        'alert2_day': alert2_day,
        'alert2_time': alert2_time,
        'memo': memo
    }
    print(doc)
    db.todo.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '작성하신 대로 스케줄을 저장했습니다. 멍!'})

# 2. 일정 조회(Read) - /readsche (GET)
@app.route('/readsche', methods=['GET'])
def read_sche():
    todolist = list(db.todo.find({},{'_id' : 0}))
    return jsonify({'result': 'success', 'todolist': todolist,'msg': '일정을 불러왔습니다. 멍!'})

# 3. 일정 검색(Read?) - /findsche (POST)
@app.route('/findsche', methods=['POST'])
def find_sche():
    keyword = request.form['keyword']
    serched = list(db.todo.find({'todo':keyword},{'_id':0}))
    return jsonify({'result': 'success', 'serched' : serched,'msg': '검색 완료!'})

# 4. 일정 변경(Update) - /fixsche (POST)

# 5. 일정 삭제(Delete) - /delsche(POST)
@app.route('/delsche', methods=['POST'])
def del_sche():
    del_todo = request.form['todo']
    db.todo.delete_one({'todo':del_todo})
    return jsonify({'result': 'success', 'msg': '선택하신 일정을 삭제했어요!'})
# 6. 알림 보내기?
###위의 것들 다 했다면###
# 7. 날씨 조회 /wether (GET)
# 8. 회원시스템 개발시작!


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
