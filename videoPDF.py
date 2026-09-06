import threading
from tkinter import Tk, messagebox

from docx import Document
from docx2pdf import convert
from docx.shared import Pt
from docx.oxml.ns import qn
from datetime import datetime
import os

import ai
from global_store import shared_data

#已经传送到pdf生成器里面了，下面如何设置生成pdf的速率呢？
#1.默认写好，比较简单
#2.新加一个设置的界面，一个参数，点击齿轮按钮，跳出新的界面来设置这个参数，比如：每检测50次生成一个检测报告，可供用户选择生成pdf的速率。
#现在先使用第一个方案，默认每检测10次生成一个检测报告。参数在后台写好，后续可以添加更多的设置选项。
#拟定添加大模型进入这个中，然后通过大模型对所获得的信息进行分析来给出附注解决办法

# 定义一个全局变量来存储累计的缺陷数量
total_name = []
total_defect_count = 0
total_time = 0
total_area = 0

def video_pdf(data):
    #打印出接受到的参数
    # print("这个是pdf_report函数里打印的数据：",data)
    print("==========================================================================")
    print("缺陷类别:",data[0],"缺陷数量:",data[1],"检测时间:",data[2],"准确率：",data[3],"缺陷位置：",data[4],"损伤程度：",data[5],"板坯级别：",data[6],
          "板坯数量：",data[7],"a级数量：",data[8],"b级数量：",data[9],"c级数量：",data[10],"缺陷面积：",data[11],"面积占比：",data[12],"a级占比：",data[13],
          "日期：",data[14],"批次：",data[15],"板坯规格：",data[16],"板坯型号：",data[17],"检测类别：",data[20],"传输速率：",data[19],"检测类别",data[20],"样品名称：",data[21])
    print("==========================================================================")
    #对缺陷数量进行一个累加，并储存在新的变量中，因为这是每检测一个就会生成新的数据，所以要把之前的数据也加进来
    global total_name   # 声明使用全局变量
    global total_defect_count
    global total_time
    global total_area
    #将检测到的缺陷类别加入列表，如果结果为“空”，则不加入列表
    # 如果缺陷类别不为空且尚未在列表中，则添加
    if data[0] != "空" and data[0] not in total_name:
        total_name.append(data[0])
    total_defect_count += int(data[1])   # 累加缺陷数量
    total_time += float(data[2])   # 累加检测时间
    total_area += float(data[11])   # 累加缺陷面积
    print("累计缺陷类别:",total_name)
    print("累计检测时间:",total_time)
    print("累计缺陷数量:",total_defect_count)
    print("累计缺陷面积:",total_area)

    #使用全局变量中的检测数量来替换生成pdf的速率数值，默认值为50
    detectNum = shared_data.get('detectNum', 50)
    detectType = shared_data.get('detectType', '委托检验')
    entrustUnit = shared_data.get('entrustUnit', '玻影智鉴团队')
    produceUnit = shared_data.get('produceUnit', '玻影智鉴团队')
    detectPlace = shared_data.get('detectPlace', '人工智能实验室')
    detectBasis = shared_data.get('detectBasis', '技术条件')

    #运行该py就生成pdf
    # 使用参数组合成一段话，作为对大模型提问的话
    aiquestion = f"请问，该批板材的缺陷类别为{total_name}，缺陷共出现{total_defect_count}处，检测准确率为{data[3]}%，检测共消耗时间为{total_time}秒，a级板占比为{data[13]}%，c级板数量为{data[10]}个，b级板数量为{data[9]}个，a级数量为{data[8]}个，总数量为{data[7]}个，损伤程度为{data[5]}，缺陷位置为{data[4]}，缺陷总面积为{total_area}平方毫米，这个是我的检测数据，我该如何优化我的生产线，200字,以“根据检测数据”开头，以“通过以上措施，有望提高生产线的效率和产品质量。”结尾"
    # 将这句话传入ai.py中
    print("AI模型提问：",aiquestion)
    response = ai.ask_ai(aiquestion)
    # 将返回的结果打印出来，或进行进一步处理
    print(response)

    results = {
        '样品名称': data[21],
        '检验类别': detectType, # 假设的检验类别，可以根据需要进行更改，比如：委托检验、自检检验等。准备在界面上加入一个设置按钮，用户可以选择生成pdf的速率和下面的一些信息
        '检测日期': data[14],
        '检测批次': data[15],
        '板坯规格': data[16],
        '板坯型号': data[17],
        '委托单位': entrustUnit,  # 假设的委托单位，可以根据需要进行更改
        '生产单位': produceUnit,  # 假设的生产单位，可以根据需要进行更改
        '检测数量': str(data[7]),
        '检测地点': detectPlace,  # 假设的检测地点，可以根据需要进行更改
        '检测依据': detectBasis,  # 假设的检测依据，可以根据需要进行更改
        '检测结论': f'经检验，该检验样品为{data[21]}，板坯规格为{data[16]}，板坯型号为{data[17]}，共检测数量为{data[7]}个，其中A级板材占比{data[4]}%，A级板数量为{data[8]}个,B级板数量为{data[9]}个,C级板数量为{data[10]}个。',
        '附注': f'{response}'
    }

    input_file_path = 'file/板探智眸检测报告模板.docx'
    output_file_path, pdf_file_path = fill_report_template(input_file_path, results)
    print(f'Saved DOCX file: {output_file_path}')
    print(f'Saved PDF file: {pdf_file_path}')

def set_cell_text(cell, text, font_name='宋体', font_size=14):
    cell.text = text
    run = cell.paragraphs[0].runs[0]
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
    run.font.size = Pt(font_size)

# 这里是你之前注释掉的代码，可以根据需求进行调整
def fill_report_template(file_path, results):
    doc = Document(file_path)
    current_time = datetime.now().strftime('%Y%m%d%H%M')

    table = doc.tables[0]  # 假设表格在文档中的第一个表格
    set_cell_text(table.cell(0, 1), results.get('样品名称', ''))
    set_cell_text(table.cell(0, 3), results.get('检验类别', ''))
    set_cell_text(table.cell(1, 1), results.get('检测日期', ''))
    set_cell_text(table.cell(1, 3), results.get('检测批次', ''))
    set_cell_text(table.cell(2, 1), results.get('板坯规格', ''))
    set_cell_text(table.cell(2, 3), results.get('板坯型号', ''))
    set_cell_text(table.cell(3, 1), results.get('委托单位', ''))
    set_cell_text(table.cell(3, 3), results.get('生产单位', ''))
    set_cell_text(table.cell(4, 1), results.get('检测数量', ''))
    set_cell_text(table.cell(4, 3), results.get('检测地点', ''))
    set_cell_text(table.cell(5, 1), results.get('检测依据', ''))
    set_cell_text(table.cell(6, 1), results.get('检测结论', ''))
    set_cell_text(table.cell(7, 1), results.get('附注', ''))

    for para in doc.paragraphs:
        full_text = ''.join([run.text for run in para.runs])
        if '{key}' in full_text:
            full_text = full_text.replace('{key}', current_time)
            for i in range(len(para.runs)):
                para.runs[i].text = ''
            para.runs[0].text = full_text
            para.runs[0].font.name = '宋体'
            para.runs[0]._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            para.runs[0].font.size = Pt(12)

    base_dir = 'file/检测报告'
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    output_file_path = os.path.join(base_dir, f'板探智眸视频检测报告(视频检测)_{current_time}.docx')
    pdf_file_path = os.path.join(base_dir, f'板探智眸视频检测报告(视频检测)_{current_time}.pdf')

    doc.save(output_file_path)
    convert(output_file_path, pdf_file_path)

    # # 在后台线程中显示弹窗，避免主线程阻塞
    threading.Thread(target=show_messagebox).start()

    return output_file_path, pdf_file_path


# 弹窗提示报告生成成功
def show_messagebox():
    # messagebox.showinfo('提示', '检测报告生成成功！')
    # 创建根窗口并隐藏它
    root = Tk()
    root.withdraw()  # 隐藏主窗口

    # 显示消息弹窗
    messagebox.showinfo('提示', '检测报告生成成功！')

    # 退出主窗口
    root.quit()
    root.destroy()