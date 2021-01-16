import execjs
import requests
import re
import json
from email.mime.text import MIMEText
from email.header import Header
from smtplib import SMTP_SSL
import traceback
import os

if os.path.exists('./.env'):
    from dotenv import load_dotenv

    load_dotenv()

SNO = os.getenv('SNO')
PASSWD = os.getenv('PASSWD')
QQ = os.getenv('QQ')
SMTP_CODE = os.getenv('SMTP_CODE')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'
}

url = {
    'login': 'https://sso.scut.edu.cn/cas/login?service=https%3A%2F%2Fiamok.scut.edu.cn%2Fcas%2Flogin',
    'get_data': 'https://iamok.scut.edu.cn/mobile/recordPerDay/getRecordPerDay',
    'send_data': 'https://iamok.scut.edu.cn/mobile/recordPerDay/submitRecordPerDay'
}

session = requests.session()
session.trust_env = False


def login():
    resp = session.get(url.get('login'), headers=headers)
    with open('./des.js', encoding='utf-8') as f:
        js_ctx = execjs.compile(f.read())

    lt = re.findall('name="lt" value="(.*?)"', resp.text)[0]
    data = dict(
        rsa=js_ctx.call('strEnc', SNO + PASSWD + lt, '1', '2', '3'),
        ul=len(SNO),
        pl=len(PASSWD),
        lt=lt,
        execution=re.findall('name="execution" value="(.*?)"', resp.text)[0],
        _eventId='submit'
    )
    session.post(
        url.get('login'),
        headers={
            **headers,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://sso.scut.edu.cn',
            'Referer': 'https://sso.scut.edu.cn/cas/login?service=https%3A%2F%2Fiamok.scut.edu.cn%2Fcas%2Flogin'
        },
        data=data)


def get_data():
    resp = session.get(
        url.get('get_data'),
        headers={
            **headers,
            'Accept': 'application/json,text/plain,*/*',
            'Referer': 'https://iamok.scut.edu.cn/iamok/web/mobile/index.html',

        })
    data = resp.json().get('data')
    return json.dumps(data)


def send_data(data):
    resp = session.post(
        url.get('send_data'),
        headers={
            **headers,
            'Accept': 'application/json,text/plain,*/*',
            'Referer': 'https://iamok.scut.edu.cn/iamok/web/mobile/index.html',
            'Origin': 'https://iamok.scut.edu.cn',
            'Content-Type': 'application/json;charset=UTF-8'
        },
        data=data)
    data = resp.json()
    return data.get('msg'), data.get('code') == 200


def iamok():
    login()
    data = get_data()
    return send_data(data)


def send_mail(msg, success):
    print(msg)
    smtp = SMTP_SSL('smtp.qq.com')
    smtp.login(QQ, SMTP_CODE)
    mail_msg = MIMEText(msg, "plain", 'utf-8')
    mail_msg["Subject"] = Header(f'iamok打卡{"成功" if success else "失败"}', 'utf-8')
    MAIL_URL = QQ + '@qq.com'
    mail_msg["From"] = MAIL_URL
    mail_msg["To"] = MAIL_URL
    smtp.sendmail(MAIL_URL, MAIL_URL, mail_msg.as_string())
    smtp.quit()


if __name__ == '__main__':
    try:
        send_mail(*iamok())
    except Exception as e:
        send_mail(traceback.format_exc(), False)
