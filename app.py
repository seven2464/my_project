from flask import Flask, render_template, jsonify
import mysql.connector
import webbrowser

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

# 模块1
@app.route("/data")
def get_data():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='plank_innovate',
        port=3306
    )
    #创建游标
    cur = conn.cursor()
    #执行SQL语句
    cur.execute("SELECT defect_count, defect_name FROM detection_result")
    #获取结果
    rows = cur.fetchall()
    #关闭游标
    cur.close()
    #关闭连接
    conn.close()
    #返回JSON数据
    data = {
        "defect_count_num_chipping": 0,
        "defect_count_num_glueOverflow": 0,
        "defect_count_num_greasyDirt": 0,
        "defect_count_num_potholes": 0,
        "defect_count_num_scratches": 0
    }
    # 累加缺陷数量
    for row in rows:
        if row[1] == "chipping":
            data["defect_count_num_chipping"] += row[0]
        elif row[1] == "glueOverflow":
            data["defect_count_num_glueOverflow"] += row[0]
        elif row[1] == "greasyDirt":
            data["defect_count_num_greasyDirt"] += row[0]
        elif row[1] == "potholes":
            data["defect_count_num_potholes"] += row[0]
        elif row[1] == "scratches":
            data["defect_count_num_scratches"] += row[0]
    #返回JSON数据
    return jsonify(data)

@app.route("/accuracy_data")
def accuracy_data():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='plank_innovate',
        port=3306,
        buffered=True
    )
    # 创建游标
    cur = conn.cursor()

    # 初始化数据字典
    data = {
        "chipping_accuracy": [],
        "glue_accuracy": [],
        "greasy_accuracy": [],
        "pothole_accuracy": [],
        "scratch_accuracy": []
    }

    # 执行 SQL 语句并将结果存入数据字典
    defect_names = [
        "chipping",
        "glueOverflow",
        "greasyDirt",
        "potholes",
        "scratches"
    ]
    for defect_name in defect_names:
        cur.execute("SELECT accuracy FROM detection_result WHERE defect_name=%s", (defect_name,))
        accuracy_data = [row[0] for row in cur.fetchall()]  # 将元组转换为简单列表
        data[defect_name] = accuracy_data

    # 关闭游标
    cur.close()
    # 关闭连接
    conn.close()

    print(data)

    # 返回 JSON 数据
    return jsonify(data)
# 模块3
@app.route("/detection_time")
def detection_time():
    conn = mysql.connector.connect(
        host='localhost', user='root', password='123456',
        database='plank_innovate', port=3306
    )
    cur = conn.cursor()
    cur.execute("SELECT detection_time FROM detection_result")
    times = cur.fetchall()
    cur.close()
    conn.close()

    # 将浮点数转换为字符串形式
    # detection_times = [str(time[0]) for time in times]      #需要优化
    return jsonify({"detection_time_all": times})

# 模块4
@app.route("/abc_judgment")
def abc_judgment():
    conn = mysql.connector.connect(
        host='localhost', user='root', password='123456',
        database='plank_innovate', port=3306
    )
    cur = conn.cursor()
    cur.execute("SELECT plank_level FROM detection_result")

    #获取结果
    lever_judgments = cur.fetchall()
    #关闭游标，连接
    cur.close()
    conn.close()

    # 返回JSON数据
    data = {
        "A_level_count": 0,
        "B_level_count": 0,
        "C_level_count": 0
    }

    # 累加板材等级
    for row in lever_judgments:
        plank_lever = row[0]  # 获取 plank_lever 字段的值
        if plank_lever == "A级板材":
            data["A_level_count"] += 1
        elif plank_lever == "B级板材":
            data["B_level_count"] += 1
        elif plank_lever == "C级板材":
            data["C_level_count"] += 1

    return jsonify(data)

#模块5
@app.route("/defects_area")
def defect_area():
    conn = mysql.connector.connect(
        host='localhost', user='root', password='123456',
        database='plank_innovate', port=3306
    )
    cur = conn.cursor()
    cur.execute("SELECT defects_area FROM detection_result")
    defects_areas = cur.fetchall()
    # 确保数据是一维数组
    data = [area[0] for area in defects_areas]  # 提取每个元组中的面积值
    cur.close()
    conn.close()
    return jsonify({"defects_area_all": data})


# 模块6
@app.route("/damage_level")
def damage_level():
    conn = mysql.connector.connect(
        host='localhost', user='root', password='123456',
        database='plank_innovate', port=3306
    )
    cur = conn.cursor()
    cur.execute("SELECT damage_level FROM detection_result")

    defect_areas = cur.fetchall()
    cur.close()
    conn.close()

    # 返回JSON数据
    area_data = {
        "slight_count": 0,  #轻微
        "perfect_count": 0,  #完好
        "severe_count": 0,  #严重
        "medium_count": 0    #中度
    }

    # 累加缺陷损伤程度
    for row in defect_areas:
        defect_area = row[0]  # 获取 plank_lever 字段的值
        if defect_area == "轻微":
            area_data["slight_count"] += 1
        elif defect_area == "完好":
            area_data["perfect_count"] += 1
        elif defect_area == "严重":
            area_data["severe_count"] += 1
        elif defect_area == "中度":
            area_data["medium_count"] += 1

    return jsonify(area_data)


# 模块7--中间
@app.route("/title_data")
def title_data():
    conn = mysql.connector.connect(
        host='localhost', user='root', password='123456',
        database='plank_innovate', port=3306
    )
    cur = conn.cursor()
    # 查询总数
    cur.execute("SELECT COUNT(*) FROM detection_result")
    total_count = cur.fetchone()[0]  # 获取第一行第一列的数据

    # 查询 A 级板材的数量
    cur.execute("SELECT COUNT(*) FROM detection_result WHERE plank_level='A级板材'")
    level_A_count = cur.fetchone()[0]  # 获取第一行第一列的数据

    cur.close()
    conn.close()

    # 构造返回的 JSON 数据
    data = {
        "total_count": total_count,
        "level_A_count": level_A_count
    }

    return jsonify(data)



webbrowser.open_new_tab('http://127.0.0.1:5000')

if __name__ == '__main__':
    app.run(debug=True)

