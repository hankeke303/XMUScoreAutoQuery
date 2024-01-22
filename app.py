# -*- coding: utf-8 -*-
import argparse
import json, yaml
import requests
import time
import traceback

from login import login
from notify import notify
from urllib import parse

http_header = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh-Hans;q=0.9",
    "Connection": "keep-alive",
    # "Host": "jw.xmu.edu.cn",
    "Referer": "https://jw.xmu.edu.cn/new/index.html",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
}

query_template = {
    "querySetting": [
        {
            "name": "SFYX",
            "caption": "是否有效",
            "linkOpt": "AND",
            "builderList": "cbl_m_List",
            "builder": "m_value_equal",
            "value": "1",
            "value_display": "是"
        },
        {
            "name": "SHOWMAXCJ",
            "caption": "显示最高成绩",
            "linkOpt": "AND",
            "builderList": "cbl_m_List",
            "builder": "m_value_equal",
            "value": "0",
            "value_display": "否"
        },
        {
            "name": "XNXQDM",
            "linkOpt": "AND",
            "builder": "equal",
            "value": "2022-2023-3"
        }
    ],
    "*order": "-XNXQDM,-KCH,-KXH"
}

parser = argparse.ArgumentParser()

parser.add_argument('--username',
                    metavar='username',
                    help="统一身份认证用户名")
parser.add_argument('--password',
                    metavar='password',
                    help="统一身份认证密码")
parser.add_argument('--webvpn',
                    choices=["true", "false"],
                    help="是否通过 WebVPN 发送请求")
parser.add_argument('--vpn-username',
                    metavar='vpn_username',
                    help="WebVPN 用户名")
parser.add_argument('--vpn-password',
                    metavar='vpn_password',
                    help="WebVPN 密码")
parser.add_argument('--interval',
                    metavar='interval',
                    help="查询间隔，单位为分钟")

args = parser.parse_args()

try:
    with open("config.yaml", "r") as f:
        conf: dict = yaml.load(f, Loader=yaml.FullLoader)
        username = args.username if args.username else str(conf['info']['username'])
        password = args.password if args.password else str(conf['info']['password'])
        assert username != None and password != None
        interval = int(args.interval) if args.interval else conf['interval']
        query_terms = conf['terms']
        query_courses = conf['courses']
except:
    print("Plese fill the parameters in config.yaml or use command line arguments.")
    exit(1)

try:
    with open("scores.yaml", "r", encoding='utf-8') as f:
        save_scores: dict = yaml.load(f, Loader=yaml.FullLoader)
        if save_scores == None:
            save_scores = {}
except FileNotFoundError:
    save_scores = {}
except:
    print("scores.yaml is not a valid yaml file.")
    exit(1)

# print("username: " + username)
# print("password: " + password)
# print("use_webvpn: " + str(use_webvpn))
# print("webvpn_username: " + webvpn_username)
# print("webvpn_password: " + webvpn_password)
# print("interval: " + str(interval))
# exit()

session = requests.Session()
session.headers = http_header

def loginAndGetToken():
    login(session, username, password)
    print("login")
    res = session.get("https://jw.xmu.edu.cn/appShow?appId=4768574631264620", allow_redirects=True)
    with open('Cookie.txt', 'w') as f:
        f.write(str(session.cookies.get_dict()))

try:
    with open('Cookie.txt', 'r') as f:
        cookie = eval(f.read())
        session.cookies.update(cookie)
except:
    loginAndGetToken()

res = session.get("https://jw.xmu.edu.cn/appShow?appId=4768574631264620", allow_redirects=True)
# print(res.status_code, res.url, res.headers)
# print(session.cookies.get_dict())

while True:
    try:
        noti = ""
        res = session.post("https://jw.xmu.edu.cn/jwapp/sys/cjcx/modules/cjcx/cxycjdxnxq.do",
                            data={"XH": username})
        # print(res.status_code) # 401 代表未登录
        # print(res.text)
        if res.status_code == 401:
            loginAndGetToken()
            continue
        elif res.status_code != 200:
            raise Exception("Failed to get scores.")
        terms = json.loads(res.text)['datas']['cxycjdxnxq']['rows']
        for term in terms:
            if not query_terms or term['XNXQDM_DISPLAY'] in query_terms or term['XNXQDM'] in query_terms:
                query_template['querySetting'][2]['value'] = term['XNXQDM']
                # print(query_template)
                res = session.post("https://jw.xmu.edu.cn/jwapp/sys/cjcx/modules/cjcx/xscjcx.do",
                                    data=parse.urlencode(query_template))
                if res.status_code == 401:
                    loginAndGetToken()
                    continue
                # print(res.status_code)
                # print(res.text)
                # exit()
                if res.status_code != 200:
                    raise Exception("Failed to get scores.")
                scores = json.loads(res.text)['datas']['xscjcx']['rows']
                for score in scores:
                    if score['DJCJLXDM_DISPLAY'] == '百分制' and (not query_courses or score['KCM'] in query_courses \
                        or score['XSKCM'] in query_courses or score['KCH'] in query_courses):
                            if score['KCH'] not in save_scores or save_scores[score['KCH']]['score'] != score['ZCJ']:
                                save_scores[score['KCH']] = {"score": score['ZCJ'], "name": score['KCM'], "term": term['XNXQDM_DISPLAY'], "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
                                noti += f"{score['KCM']}：{score['ZCJ']} 分，绩点 {score['XFJD']}。\n"
                # print(noti)
                # print(save_scores)
                # time.sleep(600)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        if noti:
            noti = "以下课程有新成绩：\n" + noti
            print(noti)
            notify('新成绩', noti)
            with open("scores.yaml", "w", encoding='utf-8') as f:
                yaml.dump(save_scores, f, encoding='utf-8', allow_unicode=True)
        else:
            print("没有新成绩")
    except Exception as e:
        traceback.print_exc()
    time.sleep(interval * 60)