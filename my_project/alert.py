from pymongo import MongoClient
client = MongoClient('localhost',27017)
db = client.dbsparta

# 6. 알림 보내기 - schedule
import schedule, time, datetime
from pprint import pprint
from datetime import datetime

# 6-1. 📧alert1 체크함수 - 현재시간과 비교해 이메일 알림시간 체크###
def alert1_send():
    # 현재시간
    year = datetime.today().year
    month = datetime.today().month
    day = datetime.today().day
    hour = datetime.today().hour
    minute = datetime.today().minute
    today_datetime = datetime(year, month, day, hour, minute)
    print(today_datetime)
    # 이메일 알림 (1) - 날짜,시간 가져오기
    alert1list = list(db.todo.find({'alert1': 'true'}))
    for alert1 in alert1list:
        alert1date = alert1['alert1date']
        alert1time = alert1['alert1time']
        todo = alert1['todo']
        userID = alert1['userID']
        alert1year = int(alert1date.split('-')[0])
        alert1month = int(alert1date.split('-')[1])
        alert1day = int(alert1date.split('-')[2])
        alert1hour = int(alert1time.split(':')[0])
        alert1minute = int(alert1time.split(':')[1])
        alert1datetime = datetime(alert1year, alert1month, alert1day, alert1hour, alert1minute)
        # 이메일알림시간 = 현재시간이면 메일 보냄
        if (alert1datetime == today_datetime):
            print('📧이메일 알림(1) 보낼 시간!')
            send_email(todo, userID)

# 6-2. 📧📧alert2 체크함수 - 현재시간과 비교해 이메일 알림시간 체크###
def alert2_send():
    # 현재시간
    year = datetime.today().year
    month = datetime.today().month
    day = datetime.today().day
    hour = datetime.today().hour
    minute = datetime.today().minute
    today_datetime = datetime(year, month, day, hour, minute)
    print(today_datetime)
    # 이메일 알림 (2) - 날짜,시간 가져오기
    alert2list = list(db.todo.find({'alert2': 'true'}))
    for alert2 in alert2list:
        alert2date = alert2['alert2date']
        alert2time = alert2['alert2time']
        todo = alert2['todo']
        userID = alert2['userID']
        alert2year = int(alert2date.split('-')[0])
        alert2month = int(alert2date.split('-')[1])
        alert2day = int(alert2date.split('-')[2])
        alert2hour = int(alert2time.split(':')[0])
        alert2minute = int(alert2time.split(':')[1])
        alert2datetime = datetime(alert2year, alert2month, alert2day, alert2hour, alert2minute)
        # 이메일알림시간 = 현재시간이면 메일 보냄
        if (alert2datetime == today_datetime):
            print('📧📧이메일 알림(2) 보낼 시간!')
            send_email(todo, userID)

# 6-3. 이메일전송함수
def send_email(todo, userID):
    import smtplib
    from email import encoders  # 파일전송을 할 때 이미지나 문서 동영상 등의 파일을 문자열로 변환할 때 사용할 패키지
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.image import MIMEImage

    me = "doggo.and.mee@gmail.com"
    my_password = ""
    you = userID

    ## 여기서부터 코드를 작성하세요.
    # 이메일 작성 form을 받아옵니다.
    msg = MIMEMultipart('alternative')
    # 제목을 입력합니다.
    msg['Subject'] = '🐶 멍! "'+todo+'" 알림이 왔어요!'
    # 송신자를 입력합니다.
    msg['From'] = me
    # 수신자를 입력합니다.
    msg['To'] = you

    # 이메일 내용을 작성합니다
    html = """
        <html><body>
        <h1>📧 '멍이와 나' 알림 메일 </h1>
        <p>안녕하세요!</p><br>
        <p>'멍이와 나(Doggo&Me)'에서 보낸 """\
           + userID +"님의 일정,</p><br><p><span style='border:dotted 2px; margin:5px; padding:5px;'>'"\
           + todo +"""'</span>에 대한 알림 메일입니다.</p><br>
        <p>오늘의 일정 잊지 말아요!</p> 
        <p>그럼 오늘도 행복한 하루 되세요. 멍멍🐕!</p><br>
        -멍이 드림🐶-             
        </body></html>
        """

    # 이메일 내용의 타입을 지정합니다.
    text = MIMEText(html, 'html')
    # 이메일 form에 작성 내용을 입력합니다
    msg.attach(text)
    ## 여기에서 코드 작성이 끝납니다.

    # Gmail 을 통해 전달할 것임을 표시합니다.
    s = smtplib.SMTP_SSL('smtp.gmail.com',465)
    # Gmail에 로그인합니다.
    s.login(me, my_password)
    # 메일을 전송합니다.
    s.sendmail(me, you, msg.as_string())
    # 메일보내기 프로그램을 종료합니다.
    s.quit()

# 6-4. schedule로 1분마다 반복실행하며 사용자가 설정한 시간에 알림(메일/카톡) 보내기
def job():
    alert1_send()
    alert2_send()
    print("🐕일하고 있음!🐕")

def run():
    schedule.every(50).seconds.do(job)
    while True:
        schedule.run_pending()





#job확인
#pprint(schedule.jobs)
#job실행-예약일정에 상관없이 모든 job이 1회 실행
#schedule.run_all()

if __name__ == "__main__":
   run()