# -*- coding: utf-8 -*

from tools1 import *
import tools2
import threading
import _thread
from datetime import datetime
import sys

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
从指定文件读取并返回每个人的信息
'''


def get_every_info(file_path, key_value_table):
    file_obj = open(file_path, "r", encoding="utf-8")
    values_arr = []
    first_line = file_obj.readline()
    if "\n" in first_line:
        first_line = first_line[:-1]
    labels = first_line.split(",")
    for line in file_obj:
        if "\n" in line:
            line = line[:-1]
        value_str_arr = line.split(",")
        if len(value_str_arr) < 9:
            continue
        values_table = {}
        values_table["info"] = []
        colum_index = 0
        for value in value_str_arr:
            label = labels[colum_index]
            key = key_value_table[label]
            if key == "info":
                values_table[key].append(value)
            else:
                values_table[key] = value
            colum_index += 1
        values_arr.append(values_table)
    return values_arr


'''
对读取到的个人信息列表进行添加列和筛选行，然后返回
'''


def alter(values_arr):
    if (not len(sys.argv) == 3) or (not len(sys.argv[1]) == 6) or (not len(sys.argv[2]) == 4):
        print("命令参数错误！")
        exit(0)
    appid = sys.argv[1]
    grade = sys.argv[2]
    new_values_arr = []
    for values in values_arr:
        if values["grade"] == grade:
            values["appid"] = appid
            new_values_arr.append(values)
    return new_values_arr


'''
展示并确认信息
'''


def checkInfos(values_arr, value_key_table):
    labels_line = ""
    for key in value_key_table:
        labels_line = labels_line + str(value_key_table[key]) + "\t"
    print(labels_line + "appid")
    for values in values_arr:
        line = ""
        for key in values:
            line = line + str(values[key]) + "\t"
        print(line)
    print("符合条件的人数：" + str(len(values_arr)))
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
    file_path = "./info.csv"
    key_value_table = {"姓名": "name", "学院": "info", "班级": "info", "性别": "info", "学号": "info", "电话": "info",
                       "账号": "account", "密码": "password", "年级": "grade","联系方式":"contact"}
    value_key_table = {"info": ["学院", "班级", "性别", "学号", "电话"], "name": "姓名",
                       "account": "账号", "password": "密码", "grade": "年级","contact":"联系方式"}
    values_arr = get_every_info(file_path, key_value_table)
    values_arr = alter(values_arr)
    checkInfos(values_arr, value_key_table)
    thread_arr = get_threads(values_arr)
    # 执行每个线程的准备方法，为抢讲座做好准备
    time_prepare_start = time.time()
    print("正在为所有人做抢讲座前的准备工作~")
    for thread in thread_arr: _thread.start_new_thread(thread.prepare, ())
    # 等待所有用户的线程做好准备
    for thread in thread_arr:
        while thread.prepare_done == 0:
            continue
    time_prepare_done = time.time()
    time_prepare_take = time_prepare_done - time_prepare_start
    print("准备工作所花时间：" + str(time_prepare_take)[:5] + "秒")
    # 用一个人的信息去获得等待时间
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
    print("讲座报名开始时间：" + values["start_time"])
    print("距离报名开始时间还剩：" + transform_time(values["interval_time"]))
    # 计算线程等待时间
    time_sleep = values["interval_time"] - 2 - values["net_delay_time"]
    # 如果时间是负的，就设为0
    if time_sleep < 0:
        time_sleep = 0
    # 线程等待
    print("倒计时中，请勿打扰~~~")
    time.sleep(time_sleep)
    # 开始抢讲座
    print("疯狂报名中~~~")
    start_time = values["start_time"]
    start_time_tmp = time.strptime(start_time, "%Y-%m-%d %H:%M")
    start_time_float = time.mktime(start_time_tmp)
    # 循环请求易班网络时间，直到网络时间超过开始抢讲座时间
    while get_time_from_url(url["yiban_signup_get"]) < start_time_float:
        continue
    # 开抢7秒后再抢
    time_wait = 7
    print("延迟" + str(time_wait) + "秒后再抢~~~")
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
    print("报名结束，已将结果写入resoult_info.txt文件！\n\n")
