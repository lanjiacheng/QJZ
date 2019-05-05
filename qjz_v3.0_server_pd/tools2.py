# -*- coding: utf-8 -*

import requests
import re
import time
# from rk import RClient
from datetime import datetime
from fateadm_api import *

'''
定义需要用到的URL
'''
url = {
    'yiban_login': 'https://www.yiban.cn/login/',  # get,登录页面
    'yiban_do_login': 'https://www.yiban.cn/login/doLoginAjax/',  # post,请求登录
    'yiban_index': 'https://www.yiban.cn/',  # get,易班首页
    'yiban_app_base': 'https://q.yiban.cn/app/index/appid/',  # get,易班app页面，后面需加应用id
    'yiban_signup_get': 'https://q.yiban.cn/signup/getSignupAjax/',  # post,查询讲座状态
    # 'yiban_signup_get': 'http://localhost:8080/Demo1_1/server01',  # post,查询讲座状态
    'yiban_signup_insert': 'https://q.yiban.cn/signup/insertBoxAjax/',  # post,抢讲座入口
    # 'yiban_signup_insert': 'http://localhost:8080/Demo1_1/server02',  # post,抢讲座入口
    'yiban_captcha_get': 'https://www.yiban.cn/captcha/index/'  # get,获取登录的验证码
}

# 创建用于识别验证码的客户端对象
# rc = RClient('ljc1998', 'ljc19980217.', '117226', 'abf23a6f920644d9b8db7908b773f16a')

'''
记录日志方法，传入需要记录的字符串，就会将该字符串打印到日志文件log.txt中
'''


def log(info):
    now_time = datetime.now()
    now_time_str = now_time.strftime('%Y-%m-%d %H:%M:%S')
    line = "[" + now_time_str + "]" + " : " + info + "\n"
    log_file = open("./log.txt", "a", encoding="utf-8")
    log_file.write(line)
    log_file.close()
    return 0


'''
工具函数，用于将网络请求返回的cookies与全局cookies合并，返回全局cookies
'''


def merge_cookies(resp, obj):
    all_cookies = obj.all_cookies
    cookies = requests.utils.dict_from_cookiejar(resp.cookies)
    all_cookies.update(cookies)
    return all_cookies


'''
工具函数，用于按正则表达式从网络请求返回的内容查找匹配字符串，返回匹配到的第一个字符串
'''


def find_str(resp, pattern):
    p = re.compile(pattern)
    try:
        resoult = p.findall(resp.text)[0]
    except:
        return ""
    return resoult


'''
工具函数，用于获取访问指定url返回的时间
'''


def get_time_from_url(u):
    r = requests.post(u)
    date = r.headers['Date']
    time_tmp = time.strptime(date[5:25], "%d %b %Y %H:%M:%S")
    time_float = time.mktime(time_tmp) + 8 * 60 * 60
    return time_float


'''
工具函数，用于获取指定response的时间戳
'''


def get_time_from_response(r):
    date = r.headers['Date']
    time_tmp = time.strptime(date[5:25], "%d %b %Y %H:%M:%S")
    time_float = time.mktime(time_tmp) + 8 * 60 * 60
    return time_float


'''
工具函数，将单位为秒的时间转换成xx天xx时xx分xx秒格式
'''


def transform_time(old_time):
    flag = ""
    if (old_time < 0):
        old_time = abs(old_time)
        flag = "-"
    days = int(old_time / (60 * 60 * 24))
    hours = int(old_time % (60 * 60 * 24) / (60 * 60))
    minutes = int(old_time % (60 * 60) / 60)
    seconds = int(old_time % 60)
    new_time = flag + str(days) + "天" + str(hours) + "时" + str(minutes) + "分" + str(seconds) + "秒"
    return new_time


'''
工具函数，获取验证码图片，返回验证码图片字节流
'''


def get_captcha_img(obj):
    all_cookies = obj.all_cookies
    r = requests.get(
        url=url["yiban_captcha_get"],
        cookies=all_cookies
    )
    return r.content


'''
工具函数，识别验证码
'''


def read_captcha_img(img, obj):
    # values = obj.values
    # r = rc.rk_create(img, 4010)
    # p1 = re.compile(r'"Result":"(.{1})","Id"')
    # p2 = re.compile(r'"Id":"(.*)"}')
    # try:
    #     code = p1.findall(r)[0]
    #     img_id = p2.findall(r)[0]
    # except:
    #     code = "0"
    #     img_id = "0"
    # values["img_id"] = img_id
    # return code
    result = api.PredictExtend(pred_type, img)
    if result != '':
        return result
    else:
        return '铖'


'''
登录易班
'''


def login_yiban(obj):
    values = obj.values
    all_cookies = obj.all_cookies
    r1 = requests.get(url=url["yiban_login"])
    merge_cookies(r1, obj)
    data_keys_time = find_str(r1, r"data-keys-time='([\d]+.*)'")
    headers_do = {"X-Requested-With": "XMLHttpRequest"}
    r2 = requests.post(
        url=url["yiban_do_login"],
        data={"account": values["account"], "password": values["password"], "keysTime": data_keys_time},
        cookies=all_cookies,
        headers=headers_do
    )
    merge_cookies(r2, obj)

    if all_cookies.__contains__("YB_SSID") and all_cookies.__contains__("yiban_user_token"):
        obj.resoult_info += "登陆易班成功->"
    else:
        # 密码错误
        if find_str(r2, r'"code":"(\d+)","message"') == "415" or find_str(r2, r'"code":(\d+),"message"') == "415":
            obj.resoult_info += "账号或密码错误->"
            return 1
        elif find_str(r2, r'"code":"(\d+)","message"') == "422" or find_str(r2, r'"code":(\d+),"message"') == "422":
            obj.resoult_info += "该账户不存在->"
            return 1
        # 需要验证码
        elif find_str(r2, r'"code":"(\d+)","message"') == "711" or find_str(r2, r'"code":(\d+),"message"') == "711":
            obj.resoult_info += "输入验证码->"
            captcha_img = get_captcha_img(obj)
            captcha_code = read_captcha_img(captcha_img, obj)
            r2 = requests.post(
                url=url["yiban_do_login"],
                data={"account": values["account"], "password": values["password"], "captcha": captcha_code,
                      "keysTime": data_keys_time},
                cookies=all_cookies,
                headers=headers_do
            )
            merge_cookies(r2, obj)
            # 密码错误
            if find_str(r2, r'"code":"(\d+)","message"') == "415" or find_str(r2, r'"code":(\d+),"message"') == "415":
                obj.resoult_info += "账号或密码错误->"
                return 1
            elif find_str(r2, r'"code":"(\d+)","message"') == "422" or find_str(r2, r'"code":(\d+),"message"') == "422":
                obj.resoult_info += "该账户不存在->"
                return 1
            # 图片验证码错误
            if find_str(r2, r'"code":"(\d+)","message"') == "201" or find_str(r2, r'"code":(\d+),"message"') == "201":
                obj.resoult_info += "验证码错误->重新输入验证码->"
                # 接下来重新获取页面，重新获识别验证证码，重新登录，循环3次，除非登陆成功
                for i in range(3):
                    r1 = requests.get(
                        url=url["yiban_login"],
                        cookies=all_cookies
                    )
                    merge_cookies(r1, obj)
                    data_keys_time = find_str(r1, r"data-keys-time='([\d]+.*)'")
                    headers_do = {"X-Requested-With": "XMLHttpRequest"}
                    captcha_img = get_captcha_img(obj)
                    captcha_code = read_captcha_img(captcha_img, obj)
                    r2 = requests.post(
                        url=url["yiban_do_login"],
                        data={"account": values["account"], "password": values["password"], "captcha": captcha_code,
                              "keysTime": data_keys_time},
                        cookies=all_cookies,
                        headers=headers_do
                    )
                    merge_cookies(r2, obj)
                    # 密码错误
                    if find_str(r2, r'"code":"(\d+)","message"') == "415" or find_str(r2,
                                                                                      r'"code":(\d+),"message"') == "415":
                        obj.resoult_info += "账号或密码错误->"
                        return 1
                    elif find_str(r2, r'"code":"(\d+)","message"') == "422" or find_str(r2,
                                                                                        r'"code":(\d+),"message"') == "422":
                        obj.resoult_info += "该账户不存在->"
                        return 1
                    if all_cookies.__contains__("YB_SSID") and all_cookies.__contains__("yiban_user_token"):
                        obj.resoult_info += "登录成功->"
                        break
            elif all_cookies.__contains__("yiban_user_token"):
                obj.resoult_info += "登录成功->"
    if not all_cookies.__contains__("yiban_user_token"):
        obj.resoult_info += "登录失败->"
        return 1
    r3 = requests.get(url=url["yiban_index"], cookies=all_cookies)
    merge_cookies(r3, obj)
    return 0


'''
请求讲座页面
'''


def into_enroll_page(obj):
    values = obj.values
    all_cookies = obj.all_cookies
    r = requests.get(url=url["yiban_app_base"] + values["appid"], cookies=all_cookies)
    merge_cookies(r, obj)
    title = find_str(r, r"<title>(.*)</title>")
    if ("警告" in title) or ("呵呵" in title):
        obj.resoult_info += "appid错误->"
        return 1
    else:
        obj.resoult_info += "请求讲座页面成功->"
    enroll_code = find_str(r, r'"code":"(enroll-[\d]+)"')
    values["enroll_code"] = enroll_code
    return 0


'''
请求讲座信息
'''


def get_enroll_info(obj):
    values = obj.values
    all_cookies = obj.all_cookies
    t1 = time.time()
    r = requests.post(
        url=url["yiban_signup_get"],
        data={"App_id": values["appid"], "code": values["enroll_code"]},
        cookies=all_cookies
    )
    merge_cookies(r, obj)

    # 记录flag
    flag = find_str(r, r'"flag":"(.*)","questionList"')
    values["enroll_flag"] = flag
    start_time = find_str(r, r'"startTime":"(.*)","endTime"')
    values["start_time"] = start_time
    # 计算距离讲座开始报名时间
    start_time_tmp = time.strptime(start_time, "%Y-%m-%d %H:%M")
    start_time_float = time.mktime(start_time_tmp)
    values["start_time_float"] = start_time_float
    yiban_time = r.headers["Date"]
    yiban_time_tmp = time.strptime(yiban_time[5:25], "%d %b %Y %H:%M:%S")
    yiban_time_float = time.mktime(yiban_time_tmp) + 8 * 60 * 60
    interval_time = start_time_float - yiban_time_float
    values["interval_time"] = interval_time
    enroll_id = find_str(r, r'"id":"(\d+)"')
    values["enroll_id"] = enroll_id
    t2 = time.time()
    # 计算网络延迟时间
    values["net_delay_time"] = t2 - t1
    obj.resoult_info += "请求讲座信息成功->"
    return 0


'''
抢讲座
'''


def grab_enroll(obj):
    values = obj.values
    all_cookies = obj.all_cookies
    values["success"] = 0

    r = requests.post(
        url=url["yiban_signup_insert"],
        data={"App_id": values["appid"], "id": values["enroll_id"], "flag": values["enroll_flag"],
              "answers[]": values["info"]},
        cookies=all_cookies
    )
    merge_cookies(r, obj)

    # 获取本次报名请求返回的网络时间
    t_done = get_time_from_response(r)
    # 获取讲座考试报名时间
    t_start = values["start_time_float"]
    # 计算报名开始到报名完成的时间
    values["take_time"] = t_done - t_start
    if find_str(r, r'"code":"(\d+)","message"') == "200" or find_str(r, r'"code":(\d+),"message"') == "200":
        values["success"] = 1
        obj.resoult_info += "报名成功！"
        return 0
    else:
        obj.resoult_info += "报名失败！"
        return 1
