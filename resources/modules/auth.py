#!/usr/bin/python
# -*- coding: utf-8 -*-
# Authors are caasiu and LiuLang <gsushzhsosgsu@gmail.com>
# Use of this source code is governed by GPLv3 license that can be found
# in http://www.gnu.org/licenses/gpl-3.0.html


import time, json, base64, re, random, urlparse, os
import requests
import rsa
from resources.modules import utils


#some base url and information needed by service
timestamp = str(int(time.time()*1000))
ppui_logintime = str(random.randint(52000, 58535))
PASSPORT_BASE = 'https://passport.baidu.com/'
PASSPORT_URL = PASSPORT_BASE + 'v2/api/'
ACCEPT_HTML = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
REFERER = PASSPORT_BASE + 'v2/?login'
PASSPORT_LOGIN = PASSPORT_BASE + 'v2/api/?login'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0'
PAN_REFERER = 'http://pan.baidu.com/disk/home'
ACCEPT_JSON = 'application/json, text/javascript, */*; q=0.8'


default_headers = {
    'User-agent': USER_AGENT,
    'Referer': PAN_REFERER,
    'Accept': ACCEPT_JSON,
    'Accept-language': 'zh-cn, zh;q=0.5',
    'Accept-encoding': 'gzip, deflate',
    'Pragma': 'no-cache',
    'Cache-control': 'no-cache',
}


def json_loads_single(s):
    return json.loads(s.replace("'",'"').replace('\t',''))


def RSA_encrypt(public_key, message):
    rsakey = rsa.PublicKey.load_pkcs1_openssl_pem(public_key)
    encrypted = rsa.encrypt(message.encode('utf-8'), rsakey)
    return base64.encodestring(encrypted).decode('utf-8').replace('\n', '')


def add_cookie(cookie,string,keys):
    str_list = re.split('[,;]\s*', string)
    for key in keys:
        for item in str_list:
            if re.match(key,item):
                s = re.search('=(.+)', item)
                cookie[key] = s.group(1)
    return cookie


def get_BAIDUID():
    url = ''.join([
                    PASSPORT_URL,
                    '?getapi&tpl=mn&apiver=v3',
                    '&tt=', timestamp,
                    '&class=login&logintype=basicLogin',
                    ])
    req = requests.get(url, headers={'Referer': ''}, timeout=50, verify=False)
    if req:
        cookie = req.cookies.get_dict()
        cookie['cflag'] = '65535%3A1'
        cookie['PANWEB'] = '1'
        return cookie
    else:
        return None


def get_token(cookie):
    url = ''.join([
                    PASSPORT_URL,
                    '?getapi&tpl=mn&apiver=v3',
                    '&tt=', timestamp,
                    '&class=login&logintype=basicLogin',
                    ])

    headers={
            'Accept': ACCEPT_HTML,
            'Cache-control': 'max-age=0',
            }

    headers_merged = default_headers.copy()
    #merge the headers
    for key in headers.keys():
        headers_merged[key] = headers[key]

    req = requests.get(url, headers=headers_merged, cookies=cookie, timeout=50, verify=False)
    if req:
        hosupport = req.headers['Set-Cookie']
        content_obj = json_loads_single(req.text)
        if content_obj:
            token = content_obj['data']['token']
            return token
    return None


def get_UBI(cookie, tokens):
    url = ''.join([

                    PASSPORT_URL,
                    '?loginhistory',
                    '&token=', tokens['token'],
                    '&tpl=pp&apiver=v3',
                    '&tt=', timestamp,
                    ])
    headers={'Referer': REFERER,}

    headers_merged = default_headers.copy()
    #merge the headers
    for key in headers.keys():
        headers_merged[key] = headers[key]

    req=requests.get(url, headers=headers_merged, cookies=cookie, timeout=50, verify=False)
    if req:
        ubi=req.headers['Set-Cookie']
        return ubi
    return None


def get_public_key(cookie, tokens):
    url = ''.join([
                    PASSPORT_BASE,
                    'v2/getpublickey',
                    '?token=', tokens['token'],
                    '&tpl=pp&apiver=v3&tt=', timestamp,

                    ])

    headers={'Referer': REFERER,}

    headers_merged = default_headers.copy()
    #merge the headers
    for key in headers.keys():
        headers_merged[key] = headers[key]

    req = requests.get(url, headers=headers_merged, cookies=cookie, timeout=50, verify=False)
    if req:
        data = json_loads_single(req.text)
        return data
    return None


def post_login(cookie, tokens, username, password_enc, rsakey='', verifycode='', codeString=''):
    url=PASSPORT_LOGIN
    headers={
            'Accept': ACCEPT_HTML,
            'Referer': REFERER,
            'Connection': 'Keep-Alive',
    }

    headers_merged = default_headers.copy()
    #merge the headers
    for key in headers.keys():
        headers_merged[key] = headers[key]

    data={
        'staticpage':'http://yun.baidu.com/res/static/thirdparty/pass_v3_jump.html',
        'charset':'UTF-8',
        'token':tokens['token'],
        'tpl':'netdisk',
        'subpro':'netdisk_web',
        'apiver':'v3',
        'tt': timestamp,
        'codestring':codeString,
        'safeflg':'0',
        'u':'http://yun.baidu.com/disk/home',
        'isPhone':'',
        'quick_user':'0',
        'logintype':'basicLogin',
        'logLoginType':'pc_loginBasic&idc=',
        'loginmerge':'true',
        'username':username,
        'password':password_enc,
        'verifycode':verifycode,
        'mem_pass':'on',
        'rsakey':rsakey,
        'crypttype':'12',
        'ppui_logintime':ppui_logintime,
        'callback':'parent.bd__pcbs__28g1kg',
        'dv': 'MDEwAAoA2wAKAk4AGwAAAF00AA0CAB3Ly25ZQRVUGl0PTgNcA1MAUA87ZDtLKlkqXTJAJAcCAATLy8vLDAIAI9OKjo6OFeWx8L75q-qn-Kf3pPSrn8Cf7479jvmW5IDwg_SQBwIABMvLy8sHAgAEy8vLywcCAATLy8vLBgIAKMvLy9DQ0NDQ0NDVkpKSkEBAQEUTExMQEBAQFUNDQ0GkpKSh9_f39RAXAgAIy8qBgYKljqkFAgAEy8vLwQECAAbLw8PNWugVAgAIy8vKkCqBv5wEAgAGycnLyfzKFgIAIuqe9cXr2eDT4tXi1uTQ59Hl0-DX4tPn3-bX7t7q3OXU4NMQAgAByxMCABnL3t7etsK2xvzT_IXwnrDSs9q-y-WG6YSrCAIACcvI9fWHh4cPCwgCAAnLz6Cg09PTWMYJAgAMy8--vs3Nzc3NQDIyCQIAJNPQCwoKCgoKCpnKyp7fkdaExYjXiNiL24Sw77DAodKh1rnLrw0CAB3Ly1gBGU0MQgVXFlsEWwtYCFdjPGMTcgFyBWoYfAwCACPTw8PDw1SO2pvVksCBzJPMnM-fwPSr9ITlluWS_Y_rm-if-wcCAATLy8vLDAIAI9Ofm5ubAsSQ0Z_YisuG2YbWhdWKvuG-zq_cr9i3xaHRotWxBwIABMvLy8sMAgAj05mdnZ0CpvKz_broqeS75LTnt-jcg9yszb7NutWnw7PAt9MMAgAj05-fn58-IXU0ej1vLmM8YzNgMG9bBFsrSjlKPVIgRDRHMFQNAgAby8tuLjhsLWMkdjd6JXoqeSl2Qh1CMUQmSyJW',

        }
    req = requests.post(url, headers=headers_merged, cookies=cookie, data=data, timeout=50, verify=False)
    content = req.text
    if content:
        match = re.search('"(err_no[^"]+)"', content)
        if not match:
            return (-1, None)
        query = dict(urlparse.parse_qsl(match.group(1)))
        query['err_no'] = int(query['err_no'])
        err_no = query['err_no']
        if err_no == 0 or err_no == 18:
            auth_cookie = req.headers['Set-Cookie']
            keys = ['STOKEN','HOSUPPORT','BDUSS','BAIDUID','USERNAMETYPE','PTOKEN','PASSID','UBI','PANWEB','HISTORY','cflag','SAVEUSERID']
            auth_cookie = add_cookie(cookie,auth_cookie,keys)
            return (0, auth_cookie)
        elif err_no == 257:
            return (err_no, query)
        elif err_no == 400031:
            return (err_no, query)
        else:
            return (err_no, query)
    else:
        return (-1, None)


def get_signin_vcode(cookie, codeString):
        url=''.join([
                        PASSPORT_BASE,
                        'cgi-bin/genimage?',
                        codeString,
                    ])
        headers={'Referer':REFERER,}

        headers_merged = default_headers.copy()
        #merge the headers
        for key in headers.keys():
            headers_merged[key] = headers[key]
        req=requests.get(url, headers=headers_merged, cookies=cookie, timeout=50, verify=False)
        #vcode_data is bytes
        vcode_data=req.content
        if vcode_data:
            vcode_path = os.path.join(utils.data_dir(), 'vcode.png')
            with open(vcode_path, 'wb') as fh:
                fh.write(vcode_data)

        return vcode_path


def get_refresh_codeString(cookie, tokens, vcodetype):
    url = ''.join([
        PASSPORT_BASE,
        'v2/?reggetcodestr',
        '&token=', tokens['token'],
        '&tpl=pp&apiver=v3',
        '&tt=', timestamp,
        '&fr=ligin',
        '&vcodetype=', vcodetype,
        ])

    headers_merged = default_headers.copy()
    headers_merged.update({'Referer': REFERER})

    req = requests.get(url, headers=headers_merged, cookies=cookie, timeout=50, verify=False)
    if req:
        req.encoding = 'gbk'
        return json.loads(req.text)

    return None


def refresh_vcode(cookie, tokens, vcodetype):
    _info = get_refresh_codeString(cookie, tokens, vcodetype)
    codeString = _info['data']['verifyStr']
    vcode_path = get_signin_vcode(cookie, codeString)
    return (codeString, vcode_path)


def parse_bdstoken(content):
    bdstoken = ''
    bds_re = re.compile('"bdstoken"\s*:\s*"([^"]+)"', re.IGNORECASE)
    bds_match = bds_re.search(content)
    if bds_match:
        bdstoken = bds_match.group(1)
        return bdstoken
    else:
        return None


#get baidu accout token
def get_bdstoken(temp_cookie):
    url = PAN_REFERER
    headers_merged = default_headers.copy()

    req = requests.get(url, headers=headers_merged, cookies=temp_cookie, timeout=50, verify=False)
    req.encoding = 'utf-8'
    if req:
        _cookie = req.headers['Set-Cookie']
        key = ['STOKEN','SCRC','PANPSC']
        auth_cookie = add_cookie(temp_cookie, _cookie, key)
        return (auth_cookie, parse_bdstoken(req.text))
    else:
        return None
