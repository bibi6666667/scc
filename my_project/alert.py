from pymongo import MongoClient
client = MongoClient('localhost',27017)
db = client.dbsparta

# 6. 알림 보내기 - schedule
import schedule, time, datetime
from pprint import pprint
from datetime import datetime

###알람체크함수 - 현재시간과 비교해 이메일, 카톡 알림시간 체크###
def alert_send():
    # 현재시간
    year = datetime.today().year
    month = datetime.today().month
    day = datetime.today().day
    hour = datetime.today().hour
    minute = datetime.today().minute
    today_datetime = datetime(year, month, day, hour, minute)
    print(today_datetime)
    # 이메일 알림시간 가져오기
    alert_e_list = list(db.todo.find({'alert_e': 'true'}))
    for alert_e in alert_e_list:
        alert_e_date = alert_e['alert_e_date']
        alert_e_time = alert_e['alert_e_time']
        todo = alert_e['todo']
        userID = alert_e['userID']
        alert_e_year = int(alert_e_date.split('-')[0])
        alert_e_month = int(alert_e_date.split('-')[1])
        alert_e_day = int(alert_e_date.split('-')[2])
        alert_e_hour = int(alert_e_time.split(':')[0])
        alert_e_minute = int(alert_e_time.split(':')[1])
        alert_e_datetime = datetime(alert_e_year, alert_e_month, alert_e_day, alert_e_hour, alert_e_minute)
        # 이메일알림시간 = 현재시간이면 메일 보냄
        if (alert_e_datetime == today_datetime):
            print('📧이메일 알림시간이다!')
            send_email(todo, userID)

# 6-1. 이메일전송함수
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

# 6-2. 카톡 메시지전송 함수
#def send_katalk():

# 6-3. schedule로 1분마다 반복실행하며 사용자가 설정한 시간에 알림(메일/카톡) 보내기
def job():
    alert_send()
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