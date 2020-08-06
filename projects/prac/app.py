from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

## html을 주는 부분
@app.route('/')
def home():
    return render_template('index.html')

## API역할을 하는 부분
@app.route('/test', methods=['get'])
def test_get() :
    title_receive = request.args.get('title_give')
    print(title_receive)
    return jsonify({'result':'success', 'msg':'이 요청은 get!'})

@app.route('/test', methods=['POST'])
def test_post():
    title_receive = request.form['title_give']
    print(title_receive)
    return jsonify({'result': 'success', 'msg': '이 요청은 POST!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)