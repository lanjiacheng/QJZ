# -*- coding: utf-8 -*

from tools1 import *
import tools1
import tools2
import threading
import _thread
from datetime import datetime
import sys
from tools_db import get_infos_from_db

'''
抢讲座线程，一个线程能抢一个讲座
'''
class GrabChairThread(threading.Thread):
    def __init__(self, values, all_cookies):
        threading.Thread.__init__(self)
        self.values = values
        self.all_cookies = all_cookies
        self.resoult_info = ""
        self.prepare_done = 0

    def prepare(self):
        try:
            r = tools2.login_yiban(self)
            if r:
                return 1
            r = tools2.into_enroll_page(self)
            if r:
                return 1
            r = tools2.get_enroll_info(self)
            if r:
                return 1
        except:
            return 1
        finally:
            self.prepare_done = 1
        return 0

    def run(self):
        try:
            tools2.grab_enroll(self)
        except:
            return 1

'''
记录日志方法，传入需要记录的字符串，就会将该字符串打印到日志文件log.txt中
'''
def log(info):
    now_time = datetime.now()
    now_time_str = now_time.strftime('%Y-%m-%d %H:%M:%S')
    line = "[" + now_time_str + "]" + " : " + info + "\n"
    log_file = open("./log.txt","a",encoding="utf-8")
    log_file.write(line)
    log_file.close()
    return 0


'''
展示信息
'''
def logInfos(values_arr):
    log("从数据库student表获取的所有appid字段为" + sys.argv[1] +"的信息如下：")
    labels_line = "学院\t班级\t性别\t学号\t电话号码\t姓名\t账号\t密码\t年级\tappid\t联系方式"
    log(labels_line)
    for values in values_arr:
        line = ""
        for key in values:
            line = line + str(values[key]) + "\t"
        log(line)
    log("数目：" + str(len(values_arr)))
    return 0


'''
根据多条信息记录创建多个抢讲座线程，并返回
'''
def get_threads(values_arr):
    thread_arr = []
    for values in values_arr:
        thread = GrabChairThread(values, {})
        thread_arr.append(thread)
    return thread_arr


if __name__ == "__main__":
    if (not len(sys.argv) == 2) or (not len(sys.argv[1]) == 6):
        log("命令参数错误！\n\n")
        exit(0)
    appid = sys.argv[1]
    # 获取当前到讲座开抢的等待时间，并等到开抢前十分钟开始执行抢讲座的准备
    # 用一个人的信息去获得等待时间
    log("用某人信息去获取并计算休眠时间~~~")
    values = {'info': ['xxx', 'xxx', 'xxx', 'xxx', 'xxx'],
              'name': 'xxx',
              'account': '15723811766',
              'password': 'ljc19980217.',
              'grade': 'xxx',
              'appid': sys.argv[1]}
    # 登录易班
    login_yiban(values)
    # 请求讲座报名页面
    into_enroll_page(values)
    # 获取讲座报名相关信息
    get_enroll_info(values)
    log("讲座报名开始时间：" + values["start_time"])
    log("距离报名开始时间还剩：" + transform_time(values["interval_time"]))
    # 计算线程等待时间，提前10分钟准备
    time_sleep = values["interval_time"] - 60 * 10 - values["net_delay_time"]
    # 如果时间是负的，就设为0
    if time_sleep < 0:
        time_sleep = 0
    # 线程等待
    log(transform_time(time_sleep)+"后开始准备（默认提前10分钟）~~~")
    time_sleep = 0
    time.sleep(time_sleep)
    # 准备阶段
    log("正在为所有人做抢讲座前的准备工作~~~~")
    # 提前10分钟准备，从数据库中取出指定appid的数据
    log("正在从数据库取出数据~~~")
    values_arr = get_infos_from_db(appid)
    # 记录取到的所有信息
    logInfos(values_arr)
    # 根据多条信息创建多个线程
    thread_arr = get_threads(values_arr)
    # 执行每个线程的准备方法，为抢讲座做好准备
    time_prepare_start = time.time()
    for thread in thread_arr: _thread.start_new_thread(thread.prepare, ())
    # 等待所有用户的线程做好准备
    for thread in thread_arr:
        while thread.prepare_done == 0:
            continue
    time_prepare_done = time.time()
    time_prepare_take = time_prepare_done - time_prepare_start
    log("准备工作所花时间：" + str(time_prepare_take)[:5] + "秒")
    # 再次用一个人的信息去获得等待时间
    log("再次用某人信息去获取并计算休睡眠时间~~~")
    values = {'info': ['xxx', 'xxx', 'xxx', 'xxx', 'xxx'],
              'name': 'xxx',
              'account': '15723811766',
              'password': 'ljc19980217.',
              'grade': 'xxx',
              'appid': sys.argv[1]}
    # 清除之前的cookie
    tools1.all_cookies = {}
    # 登录易班
    login_yiban(values)
    # 请求讲座报名页面
    into_enroll_page(values)
    # 获取讲座报名相关信息
    get_enroll_info(values)
    log("讲座报名开始时间：" + values["start_time"])
    log("距离报名开始时间还剩：" + transform_time(values["interval_time"]))
    # 计算线程等待时间
    time_sleep = values["interval_time"] - 3 - values["net_delay_time"]
    # 如果时间是负的，就设为0
    if time_sleep < 0:
        time_sleep = 0
    # 线程等待
    log(transform_time(time_sleep)+"后开抢~~~")
    time.sleep(time_sleep)
    # 开始抢讲座
    log("疯狂报名中~~~")
    start_time = values["start_time"]
    start_time_tmp = time.strptime(start_time, "%Y-%m-%d %H:%M")
    start_time_float = time.mktime(start_time_tmp)
    # 循环请求易班网络时间，直到网络时间超过开始抢讲座时间
    while get_time_from_url(url["yiban_signup_get"]) < start_time_float:
        continue
    # 开抢7秒后再抢
    time_wait = 7
    log("延迟" + str(time_wait) + "秒后再抢~~~")
    time.sleep(time_wait)
    for thread in thread_arr: thread.start()
    for thread in thread_arr: thread.join()
    # 将报名结果汇总写入文件
    file_obj = open("./resoult_info.txt", "a", encoding="utf-8")
    file_obj.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
    for thread in thread_arr:
        take_time_str = "[unknow]"
        if "take_time" in thread.values:
            take_time_str = "[" + str(thread.values["take_time"]) + "]"
        line = thread.values["name"] + "：" + thread.resoult_info + take_time_str + "\n"
        file_obj.write(line)
    file_obj.write("\n")
    file_obj.close()
    log("报名结束，已将结果写入resoult_info.txt文件！\n\n")