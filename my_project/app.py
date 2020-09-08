from bson.json_util import dumps
from bson.objectid import ObjectId
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
from flask import g

app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('localhost',27017)
db = client.dbsparta

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'apple'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib

###################
# HTML 화면 보여주기#
###################
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register')
def register():
    return render_template('register.html')


###################
# 로그인을 위한 API #
###################
# 이메일 중복체크 API
@app.route('/api/dplct_check', methods=['POST'])
def dplct_check():
    userID = request.form['userID']
    dplct_val = list(db.user.find({'id': userID}))
    if len(dplct_val) == 1:
        return jsonify({'result': 'fail', 'msg_fail': '이미 가입된 이메일 주소입니다. 다른 이메일을 사용해 주세요!'})
    elif len(dplct_val) == 0:
        return jsonify({'result': 'success', 'msg_success': '사용 가능한 이메일 주소입니다!'})

# [회원가입 API]
# id, pw, nickname을 받아서, mongoDB에 저장합니다.
# 저장하기 전에, pw를 sha256 방법(=단방향 암호화. 풀어볼 수 없음)으로 암호화해서 저장합니다.
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

    return jsonify({'result': 'success', 'msg': '회원가입이 완료되었습니다. 이제 로그인을 해 주세요!'})


# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 찾으면 JWT 토큰을 만들어 발급합니다.
    if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않거나, 존재하지 않는 회원입니다. 확인해 주세요🤔'})


# [유저 정보 확인 API]
# 로그인된 유저만 call 할 수 있는 API입니다.
# 유효한 토큰을 줘야 올바른 결과를 얻어갈 수 있습니다.
# (그렇지 않으면 남의 장바구니라든가, 정보를 누구나 볼 수 있겠죠?)
@app.route('/api/nick', methods=['GET'])
def api_valid():
    # 토큰을 주고 받을 때는, 주로 header에 저장해서 넘겨주는 경우가 많습니다.
    # header로 넘겨주는 경우, 아래와 같이 받을 수 있습니다.
    token_receive = request.headers['token_give']

    # try / catch 문?
    # try 아래를 실행했다가, 에러가 있으면 except 구분으로 가란 얘기입니다.

    try:
        # token을 시크릿키로 디코딩합니다.
        # 보실 수 있도록 payload를 print 해두었습니다. 우리가 로그인 시 넣은 그 payload와 같은 것이 나옵니다.
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # print(payload)

        # payload 안에 id가 들어있습니다. 이 id로 유저정보를 찾습니다.
        # 여기에선 그 예로 닉네임을 보내주겠습니다.
        userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})
        return jsonify({'result': 'success', 'id': userinfo['id'], 'nickname': userinfo['nick']})
    except jwt.ExpiredSignatureError:
        # 위를 실행했는데 만료시간이 지났으면 에러가 납니다.
        return jsonify({'result': 'fail', 'msg': '🐕로그인 유지시간(30분)이 만료되었어요. 다시 로그인 해 주세요!'})

################
#로그인 데코레이터#
################
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 아래 코드는 header에서 token_give 값을 가져오는 이전 코드입니다.
        # token_receive = request.headers.get("token_give")

        # client에 저장된 쿠키는 해당 클라이언트에서 서버로 보낼 때 항상 함께 보내도록 구현되어있어서
        # 모든 요청마다 클라이언트에서 쿠키값을 넣어주지 않아도 자동으로 동봉되어 서버로 전달됩니다.
        # 쿠키값을 꺼내는 방법은 아래와 같습니다.
        token_receive = request.cookies.get('token_give')
        #print(token_receive)
        if token_receive is not None:
            try:
                payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            except jwt.InvalidTokenError:
                payload = None
            if payload is None:
                return jsonify({'result': 'fail', 'msg':'아이디/비밀번호가 일치하지 않거나, 존재하지 않는 회원입니다. 확인해 주세요🤔'})
            user_id = payload["id"]
            g.user_id = user_id
            g.user = db.user.find_one({'id': user_id}, {'_id': 0}) if user_id else None
        else:
            return jsonify({'result': 'fail', 'msg':'아이디/비밀번호가 일치하지 않거나, 존재하지 않는 회원입니다. 확인해 주세요🤔'})
        return f(*args, **kwargs)
    return decorated_function


#####################
# API 역할을 하는 부분#
#####################
# 1. 일정 생성(Create) - /makesche (POST)
@app.route('/makesche', methods=['POST'])
@login_required #데코레이터
def make_sche():
    userID = g.user_id
    todo = request.form['todo']
    start_date = request.form['start_date']
    start_time = request.form['start_time']
    end_date = request.form['end_date']
    end_time = request.form['end_time']
    alert_k = request.form['alert_k']
    alert_k_date = request.form['alert_k_date']
    alert_k_time = request.form['alert_k_time']
    alert_e = request.form['alert_e']
    alert_e_date = request.form['alert_e_date']
    alert_e_time = request.form['alert_e_time']
    memo = request.form['memo']
    doc = {
        'userID': userID,
        'todo': todo,
        'start_date': start_date,
        'start_time': start_time,
        'end_date': end_date,
        'end_time': end_time,
        'alert_k': alert_k,
        'alert_k_date' : alert_k_date,
        'alert_k_time': alert_k_time,
        'alert_e': alert_e,
        'alert_e_date' : alert_e_date,
        'alert_e_time': alert_e_time,
        'memo': memo
    }
    db.todo.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '🐕작성하신 대로 스케줄을 저장했습니다. 멍!'})


# 2. 일정 조회(Read) - /readsche (GET)
@app.route('/readsche', methods=['GET'])
@login_required #데코레이터
def read_sche():
    userID = g.user_id
    sche_list = list(db.todo.find({'userID': userID}))
    return dumps({'result': 'success', 'sche_list': sche_list, 'msg': '🐕일정을 불러왔습니다. 멍!'})


# 3. 일정 검색(Read?) - /findsche (POST)
@app.route('/findsche', methods=['POST'])
@login_required #데코레이터
def find_sche():
    userID = g.user_id
    keyword = request.form['keyword']
    searched = list(db.todo.find({'todo': {'$regex':keyword}, 'userID': userID}))
    return dumps({'result': 'success', 'searched': searched, 'msg': '검색 완료!'})


# 4-1. 일정 변경을 위한 조회(find-one) - /readasche (GET)
@app.route('/readasche', methods=['GET'])
@login_required #데코레이터
def read_a_sche():
    userID = g.user_id
    fix_id = request.args.get('id')
    fix_todo = db.todo.find_one({"_id": ObjectId(fix_id), 'userID': userID})
    return dumps({'result': 'success', 'fix_todo': fix_todo})


# 4-2. 일정 변경(Update) - /fixsche (POST)
@app.route('/fixsche', methods=['POST'])
@login_required #데코레이터
def fix_sche():
    userID = g.user_id
    id = request.form['id']
    todo = request.form['todo']
    start_date = request.form['start_date']
    start_time = request.form['start_time']
    end_date = request.form['end_date']
    end_time = request.form['end_time']
    alert_k = request.form['alert_k']
    alert_k_date = request.form['alert_k_date']
    alert_k_time = request.form['alert_k_time']
    alert_e = request.form['alert_e']
    alert_e_date = request.form['alert_e_date']
    alert_e_time = request.form['alert_e_time']
    memo = request.form['memo']
    db.todo.update_one({'_id': ObjectId(id), 'userID': userID}, {'$set': {
        'todo': todo,
        'start_date': start_date,
        'start_time': start_time,
        'end_date': end_date,
        'end_time': end_time,
        'alert_k': alert_k,
        'alert_k_date': alert_k_date,
        'alert_k_time': alert_k_time,
        'alert_e': alert_e,
        'alert_e_date': alert_e_date,
        'alert_e_time': alert_e_time,
        'memo': memo
    }})
    return jsonify({'result': 'success', 'msg': '🐕수정된 스케줄을 저장했습니다. 멍!'})

# 5. 일정 삭제(Delete) - /delsche(POST)
@app.route('/delsche', methods=['POST'])
def del_sche():
    del_id = request.form['id']
    db.todo.delete_one({"_id": ObjectId(del_id)})
    return dumps({'result': 'success', 'msg': '🐕선택하신 일정이 삭제되었습니다. 멍!'})

# 6. 알림 보내기 - schedule -> alert.py에!
###알람체크함수 - 현재시간과 비교해 이메일, 카톡 알림시간 체크###
# 6-1. 이메일전송함수
# 6-2. 카톡 메시지전송 함수
# 6-3. schedule로 1분마다 반복실행하며 설정한 시간에 알림 보내기


# 7. 날씨 조회 /weather (GET)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
