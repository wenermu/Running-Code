import requests, time, re, rsa, json, base64
from urllib import parse

s = requests.Session()

username = ""
password = ""
# Server酱报错推送提醒，需要填下下面的key，官网：https://sc.ftqq.com/3.version
SCKEY = ""

if (username == "" or password == ""):
    username = input("账号：\n")
    password = input("密码：\n")
    SCKEY = input("SCKEY：\n")

# 推送url
scurl = f"https://sc.ftqq.com/{SCKEY}.send"


def main():
    msg = login(username, password)
    if (msg == "error"):
        return None
    else:
        pass
    rand = str(round(time.time() * 1000))
    surl = f'https://api.cloud.189.cn/mkt/userSign.action?rand={rand}&clientType=TELEANDROID&version=8.6.3&model=SM-G930K'
    url = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN&activityId=ACT_SIGNIN'
    url2 = f'https://m.cloud.189.cn/v2/drawPrizeMarketDetails.action?taskId=TASK_SIGNIN_PHOTOS&activityId=ACT_SIGNIN'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
        "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
        "Host": "m.cloud.189.cn",
        "Accept-Encoding": "gzip, deflate",
    }
    # 签到
    response = s.get(surl, headers=headers)
    netdiskBonus = response.json()['netdiskBonus']
    if (response.json()['isSign'] == "false"):
        print(f"未签到，签到获得{netdiskBonus}M空间")
    else:
        print(f"已签到，签到获得{netdiskBonus}M空间")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; SM-G930K Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.136 Mobile Safari/537.36 Ecloud/8.6.3 Android/22 clientId/355325117317828 clientModel/SM-G930K imsi/460071114317824 clientChannelId/qq proVersion/1.0.6',
        "Referer": "https://m.cloud.189.cn/zhuanti/2016/sign/index.jsp?albumBackupOpened=1",
        "Host": "m.cloud.189.cn",
        "Accept-Encoding": "gzip, deflate",
    }
    # 第一次抽奖
    response = s.get(url, headers=headers)
    if ("errorCode" in response.text):
        if (response.json()['errorCode'] == "User_Not_Chance"):
            print("开始第一次抽奖,抽奖次数不足")
        else:
            print(response.text)
            if (SCKEY != ""):
                data = {
                    "text": "第一次抽奖出错",
                    "desp": response.text
                }
                sc = requests.post(scurl, data=data)
    else:
        res_json = response.json()
        description = res_json.get('prizeName')
        print(f"抽奖获得{description}")
#         description = response.text
#         print("第一次抽奖信息:", description)
    # 第二次抽奖
    response = s.get(url2, headers=headers)
    if ("errorCode" in response.text):
        if (response.json()['errorCode'] == "User_Not_Chance"):
            print("开始第二次抽奖,抽奖次数不足")
        else:
            print(response.text)
            if (SCKEY != ""):
                data = {
                    "text": "第二次抽奖出错",
                    "desp": response.text
                }
                sc = requests.post(scurl, data=data)
    else:
        res_json = response.json()
        description = res_json.get('prizeName')
        print(f"抽奖获得{description}")
#         description = response.text
#         print("第二次抽奖信息:", description)


def int2char(a):
    BI_RM = list("0123456789abcdefghijklmnopqrstuvwxyz")
    return BI_RM[a]


def b64tohex(a):
    d = ""
    e = 0
    c = 0
    b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    for i in range(len(a)):
        if list(a)[i] != "=":
            v = b64map.index(list(a)[i])
            if 0 == e:
                e = 1
                d += int2char(v >> 2)
                c = 3 & v
            elif 1 == e:
                e = 2
                d += int2char(c << 2 | v >> 4)
                c = 15 & v
            elif 2 == e:
                e = 3
                d += int2char(c)
                d += int2char(v >> 2)
                c = 3 & v
            else:
                e = 0
                d += int2char(c << 2 | v >> 4)
                d += int2char(15 & v)
    if e == 1:
        d += int2char(c << 2)
    return d


def rsa_encode(j_rsakey, string):
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{j_rsakey}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    result = b64tohex((base64.b64encode(rsa.encrypt(f'{string}'.encode(), pubkey))).decode())
    return result


def calculate_md5_sign(params):
    return hashlib.md5('&'.join(sorted(params.split('&'))).encode('utf-8')).hexdigest()


def login(username, password):
    url = "https://cloud.189.cn/udb/udb_login.jsp?pageId=1&redirectURL=/main.action"
    r = s.get(url)
    captchaToken = re.findall(r"captchaToken' value='(.+?)'", r.text)[0]
    lt = re.findall(r'lt = "(.+?)"', r.text)[0]
    returnUrl = re.findall(r"returnUrl = '(.+?)'", r.text)[0]
    paramId = re.findall(r'paramId = "(.+?)"', r.text)[0]
    j_rsakey = re.findall(r'j_rsaKey" value="(\S+)"', r.text, re.M)[0]
    s.headers.update({"lt": lt})

    username = rsa_encode(j_rsakey, username)
    password = rsa_encode(j_rsakey, password)
    url = "https://open.e.189.cn/api/logbox/oauth2/loginSubmit.do"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/76.0',
        'Referer': 'https://open.e.189.cn/',
    }
    data = {
        "appKey": "cloud",
        "accountType": '01',
        "userName": f"{{RSA}}{username}",
        "password": f"{{RSA}}{password}",
        "validateCode": "",
        "captchaToken": captchaToken,
        "returnUrl": returnUrl,
        "mailSuffix": "@189.cn",
        "paramId": paramId
    }
    r = s.post(url, data=data, headers=headers, timeout=5)

    # 测试用
    # if (SCKEY != ""):
    #     msgs = r.json()['msg']
    #     datas = {
    #         "text": "天翼云提示",
    #      "desp": f"登录提示：{msgs}"
    #     }
    #     requests.post(scurl, data=datas)

    if (r.json()['result'] == 0):
        print(r.json()['msg'])
    else:
        if (SCKEY == ""):
            print(r.json()['msg'])
        else:
            msg = r.json()['msg']
            print(msg)
            data = {
                "text": "登录出错",
                "desp": f"错误提示：{msg}"
            }
            sc = requests.post(scurl, data=data)
        return "error"
    redirect_url = r.json()['toUrl']
    r = s.get(redirect_url)
    return s


if __name__ == "__main__":
    main()