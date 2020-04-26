from secret import username, password, qyapi_key
import datetime
import time
import json
import requests


class LoginError(Exception):
    pass


class PostFailed(Exception):
    pass


class DailyReport(object):
    def __init__(self, username, password, qyapi_key, sleeptime=10):
        self.secret = {
            "username": username,
            "password": password
        }
        self.qyapi_key = qyapi_key
        self.url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={qyapi_key}"
        self.sleeptime = sleeptime
        self.headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10;  AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045136 Mobile Safari/537.36 wxwork/3.0.16 MicroMessenger/7.0.1 NetType/WIFI Language/zh"}
        self.info = ""
        self.error_msg = ""

    def _init_session(self):
        self.s = requests.Session()
        r = self.s.post("https://app.ucas.ac.cn/uc/wap/login/check", data=self.secret, headers=self.headers)
        if r.json().get('m') != "操作成功":
            self.error_msg += f'>LoginError:<font color="warning">{r.text}</font>\n'
            raise LoginError

        yday = self.s.get("https://app.ucas.ac.cn/ncov/api/default/daily?xgh=0&app_id=ucas").json()
        if yday.get('d', None):
            self.old = yday['d']
        else:
            self.error_msg += f'>get_daliy_error:<font color="warning">获取昨日信息失败</font>\n'
            raise LoginError

        self.new = {
            'realname': self.old['realname'],
            'number': self.old['number'],
            'szgj_api_info': self.old['szgj_api_info'],
            'sfzx': self.old['sfzx'],
            'szdd': self.old['szdd'],
            'ismoved': self.old['ismoved'],
            'tw': self.old['tw'],
            'sftjwh': self.old['sfsfbh'],
            'sftjhb': self.old['sftjhb'],
            'sfcxtz': self.old['sfcxtz'],
            'sfjcwhry': self.old['sfjcwhry'],
            'sfjchbry': self.old['sfjchbry'],
            'sfjcbh': self.old['sfjcbh'],
            'sfcyglq': self.old['sfcyglq'],
            'sfcxzysx': self.old['sfcxzysx'],
            'old_szdd': self.old['szdd'],
            'geo_api_info': self.old['old_city'],
            'old_city': self.old['old_city'],
            'geo_api_infot': self.old['geo_api_infot'],
            'jcjgqk': self.old['jcjgqk'],
            'date': (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d"),
            'app_id': 'ucas'
        }

    def post(self):
        r = self.s.post("https://app.ucas.ac.cn/ncov/api/default/save", data=self.new)
        res = r.json().get('m')
        if res == "操作成功" or res == "今天已经填报了":
            self.info = f"Done! {res}"
        else:
            self.info = f'<font color="warning">{res}</font>'
            raise PostFailed

    def notice(self):
        notice_data = {"msgtype": "markdown", "markdown": {"content": ""}}
        if not self.error_msg:
            notice_data["markdown"]["content"] = self.info
        else:
            notice_data["markdown"]["content"] = self.info + "\n" + self.error_msg
        requests.post(self.url, data=json.dumps(notice_data), headers={'content-type': 'application/json'})

    def sleep(self):
        time.sleep(self.sleeptime)

    def start(self):
        while True:
            try:
                self._init_session()
                self.post()
                if "Done!" in self.info:
                    print(self.info)
                    exit(0)
            except LoginError:
                if "错误" in self.error_msg:
                    print("帐号或密码错误")
                    exit(1)
                else:
                    self.sleep()
            except PostFailed:
                self.sleep()
            finally:
                if self.qyapi_key:
                    self.notice()


if __name__ == '__main__':
    DailyReport(username, password, qyapi_key).start()
