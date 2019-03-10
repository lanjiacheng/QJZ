import pymysql

db = pymysql.connect("47.107.255.240","ljc","ljc","qjz")

cursor = db.cursor()
sql = "select * from student"
cursor.execute(sql)
all_rows = cursor.fetchall()
for row in all_rows:
    print(row)
db.close()