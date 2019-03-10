# -*- coding: utf-8 -*

from tools1 import *


'''
定义全局变量字典，需要用到的值都存储在该字典中
'''
values = {}



if __name__ == "__main__":
    print("\n\n------------------------易班抢讲座程序------------------------")
    print("------------------------develop by ljc------------------------\n")
    print("使用说明：\n1.在讲座开抢前几分钟用浏览器访问并登录易班网(www.yiban.cn)然后运行此程序\n2.按提示输入相关信息并确认无误\n3.输入完毕等待报名结果\n")
    # 输入信息
    input_to_values(values)
    # 登录易班
    login_yiban(values)
    # 请求讲座报名页面
    into_enroll_page(values)
    # 获取讲座报名相关信息
    get_enroll_info(values)
    print("讲座报名开始时间：" + values["start_time"])
    print("距离报名开始时间还剩：" + transform_time(values["interval_time"]))
    # 计算线程等待时间
    time_sleep = values["interval_time"] - 1 - values["net_delay_time"]
    # 如果时间是负的，就设为0
    if time_sleep < 0:
        time_sleep = 0
    # 线程等待
    print("倒计时中，请勿打扰~~~")
    time.sleep(time_sleep)
    # 开始抢讲座
    print("疯狂报名中~~~")
    grab_enroll(values)
    # 判断是否报名成功
    if values["success"] == 1:
        print("报名成功！")
        print("报名开始时刻到报名成功时刻大约花了：" + str(values["take_time"]) + "秒")
    else:
        print("报名失败~")