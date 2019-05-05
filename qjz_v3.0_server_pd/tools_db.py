# -*- coding: utf-8 -*

import pymysql

def get_infos_from_db(appid):
    db = pymysql.connect("47.107.255.240","ljc","ljc","qjz")
    cursor = db.cursor()
    sql = "select * from student where appid = '%s' and delete_time is null order by student_num asc" % str(appid)
    cursor.execute(sql)
    all_rows = cursor.fetchall()
    infos = []
    for row in all_rows:
        values = {'info':['','','','','']}
        col_index = 0
        for col in row:
            if col_index == 0:
                values['info'][3] = col
            elif col_index == 1:
                values['name'] = col
            elif col_index == 2:
                values['info'][0] = col
            elif col_index == 3:
                values['info'][1] = col
            elif col_index == 4:
                values['info'][2] = col
            elif col_index == 5:
                values['info'][4] = col
            elif col_index == 6:
                values['account'] = col
            elif col_index == 7:
                values['password'] = col
            elif col_index == 8:
                values['grade'] = col
            elif col_index == 9:
                values['appid'] = col
            elif col_index == 10:
                values['contact'] = col
            col_index = col_index + 1
        infos.append(values)
    db.close()
    return infos