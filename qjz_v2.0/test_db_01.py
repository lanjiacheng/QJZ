import pymysql

'''
从指定文件读取并返回每个人的信息
'''
def get_every_info(file_path):
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
        if len(value_str_arr) < 10:
            print(value_str_arr)
            continue
        values_arr.append(value_str_arr)
    return values_arr


db = pymysql.connect("localhost","root","root","qjz")

insert_sql = "INSERT INTO `student` \
(`student_num`, `name`, `institute`, `class`, `sex`, `phone_num`, `account`, `password`, `grade`, `appid`, `contact`,`delete_time`) \
VALUES \
('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, '%s', %s)"

values_arr = get_every_info("./info.csv")
for values in values_arr:
    current_sql = insert_sql % (values[4],values[0],values[1],values[2],values[3],values[5],values[6],values[7],values[8],"NULL",values[9],"NULL")
    print(current_sql)
    cursor = db.cursor()
    cursor.execute(current_sql)
db.commit()
print("total:" + str(len(values_arr)))
# i = 0
# for values in values_arr:
#     print(str(i) + "\t:\t" + values[9])
#     i = i+1

#
# sql = "select * from student"
# cursor = db.cursor()
# cursor.execute(sql)
# resoults = cursor.fetchall()
# for row in resoults:
#     print(row)

db.close()