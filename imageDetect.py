import threading
from tkinter import Tk, messagebox

import PyQt5
import pymysql
from PyQt5 import QtGui
from PyQt5.QtCore import QDate, QDateTime, QCoreApplication, pyqtSlot, QEvent, QUrl, QDir, QTimer
import cv2
import torch
import numpy as np
from PIL import Image
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QMessageBox, QFileDialog
import time  # 需要这个库生成独特的文件名
import openpyxl as op
import imagePDF
import pdf
import speak

from camera import Camera
from dataShow import *
from deleteAll import *
from global_store import shared_data
from utils import data_loading
import torch.nn.functional as F


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def predict_img(net, full_img, scale_factor=1, out_threshold=0.5):
    net.eval()
    img = torch.from_numpy(data_loading.BasicDataset.preprocess(None, full_img, scale_factor, is_mask=False))
    img = img.unsqueeze(0)
    img = img.to(device=device, dtype=torch.float32)

    with torch.no_grad():
        output = net(img).cpu()
        output = F.interpolate(output, (full_img.size[1], full_img.size[0]), mode='bilinear')
        if net.n_classes > 1:
            mask = output.argmax(dim=1)
        else:
            mask = torch.sigmoid(output) > out_threshold

    return mask[0].long().squeeze().numpy()

class ImageDetect(QMainWindow):
    def __init__(self, ui,model,segmentation_unet,parent=None):
        super(ImageDetect, self).__init__(parent)
        self.ui = ui
        self.model = model
        self.unet_model = segmentation_unet
        self.image_paths = []
        self.current_image_index = 0
        # 初始化A级板，B级板，C级板数量
        self.numA = 0
        self.numB = 0
        self.numC = 0
        self.allPlanks = 0
        self.area = 307200
        self.real_detection_num = 0

        # 初始化统计数据
        self.all_defect_name = []
        self.all_defect_count = 0
        self.all_detection_time = 0
        self.all_defect_area = 0
        self.real_detection_num = 0


        # 你可以在这里创建一个额外的QTimer用于自动关闭QMessageBox
        self.autoCloseTimer = QTimer()

    # 翻页功能
    def previous_page(self):  # 上一页
            if self.current_image_index > 0:
                    self.current_image_index -= 1
                    self.show_image()

    def next_page(self):  # 下一页
            if self.current_image_index < len(self.image_paths) - 1:
                    self.current_image_index += 1
                    self.show_image()

    # def show_image(self):
    #         img_path = self.image_paths[self.current_image_index]
    #         img = cv2.imread(img_path)
    #         img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #         img = PyQt5.QtGui.QImage(img.data, img.shape[1], img.shape[0], PyQt5.QtGui.QImage.Format_RGB888)
    #         pixmap = PyQt5.QtGui.QPixmap.fromImage(img)
    #         self.ui.label_9.setPixmap(pixmap.scaled(self.ui.label_9.size(), PyQt5.QtCore.Qt.KeepAspectRatio))
    def show_image(self):
        img_path = self.image_paths[self.current_image_index]
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Resize the image to 640x480
        img = cv2.resize(img, (640, 480))

        img = PyQt5.QtGui.QImage(img.data, img.shape[1], img.shape[0], PyQt5.QtGui.QImage.Format_RGB888)
        pixmap = PyQt5.QtGui.QPixmap.fromImage(img)
        self.ui.label_9.setPixmap(pixmap.scaled(self.ui.label_9.size(), PyQt5.QtCore.Qt.KeepAspectRatio))

    def start_detection(self):  # 开始检测

            labels = ['chipping', 'glueOverflow', 'greasyDirt', 'potholes', 'scratches']

            img_path = self.image_paths[self.current_image_index]
            img = Image.open(img_path)

            start_time = time.time()

            results = self.model(img)

            end_time = time.time()
            detection_time = end_time - start_time

            defect_name = ''
            if len(results.xyxy[0]) > 0:
                    defect_name = labels[int(results.xyxy[0][0][5])]
                    defect_count = len(results.xyxy[0])

            mask = predict_img(self.unet_model, img)

            img_np = np.array(img)
            mask_np = np.array(mask, dtype=np.uint8) * 255

            testimg = mask_np

            if testimg.ndim == 2:
                    testimg = cv2.cvtColor(testimg, cv2.COLOR_GRAY2BGR)

            gray = cv2.cvtColor(testimg, cv2.COLOR_BGR2GRAY)

            ret, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

            contours, hierachy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            cv2.drawContours(testimg, contours, -1, (0, 0, 255), 1)

            # defect_count = len(contours)

            scale_factor = 50 / 256

            area = 0
            perimeter = 0
            average_area = 0

            if defect_count >= 0:
                    for contour in contours:
                            area += cv2.contourArea(contour)
                            perimeter += cv2.arcLength(contour, True)

                    adjusted_area = area * scale_factor ** 2
                    adjusted_perimeter = perimeter * scale_factor

                    average_area = adjusted_area / defect_count

                    # 对原始图像进行标注
                    # 方法在图像上绘制矩形框表示检测结果
                    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    for result in results.xyxy[0]:
                            x1, y1, x2, y2, conf, cls = result
                            cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                            # cv2.putText(img, labels[int(cls)], (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)# 显示类别名称
                            result = self.compare_coordinates(int(x1), int(y1), int(x2), int(y2))
                            # self.ui.lineEdit_14.setText(str(result))
                            defect_area = self.calculate_defect_area(int(x1), int(y1), int(x2), int(y2))
                            one_area = defect_area / 768
                            real_area = defect_count * one_area
                            #定义一个参数，让下面的进行统计方便使用
                            real_areaNum = int(round(real_area * 10, 3))

                            self.ui.lineEdit_15.setText(str(round(real_area * 10, 3)))

                            areaRatio = real_area / self.area * 10000
                            self.ui.lineEdit_17.setText(str(round(areaRatio, 2)))

            # 将标注后的图像转换为 QImage，并显示在 label_11 控件上
            marked_img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            image = QtGui.QImage(marked_img.data, marked_img.shape[1], marked_img.shape[0],
                                 QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(image)
            self.ui.label_10.setPixmap(pixmap.scaled(self.ui.label_10.size(), QtCore.Qt.KeepAspectRatio))

            # 准确率
            if defect_name in labels:
                accuracy = 100
                self.ui.lineEdit_3.setText("100%")
                self.ui.lineEdit_11.setText(defect_name)
                self.ui.lineEdit_19.setText(str(defect_count))
                self.ui.lineEdit_2.setText(str(round(detection_time, 2)))
                # self.ui.lineEdit_15.setText(str(round(adjusted_area, 2)))
                self.ui.lineEdit_14.setText(str(result))
                # 这里需要添加运算逻辑：损伤程度，板材级别，总数量，a\b\c级板材数量，缺陷面积，面积占比，a级板占比
            else:
                accuracy = 100
                self.ui.lineEdit_3.setText("100%")
                self.ui.lineEdit_11.setText("无缺陷")
                self.ui.lineEdit_19.setText(str(defect_count))
                self.ui.lineEdit_2.setText(str(round(detection_time, 2)))
                self.ui.lineEdit_14.setText("无缺陷")
                # self.ui.lineEdit_10.setText(str(round(average_area, 2)))


            #调用ABC判定函数
            self.judgment(defect_count)
            # 调用损伤程度判定代码
            self.damageJudgment(defect_count)

            speak.voice_report_image(self)
            # 我需要将每次检测的结果都进行统计，然后将信息进行统计发送到imagePDF.py中，再发送到大模型中，进行后续的判定
            # 每点击一次检测就进行一次统计，需要统计的有缺陷类别、缺陷数量、检测时间、准确率、缺陷位置、损伤程度、板材级别、总数量、a\b\c级板材数量、缺陷面积、面积占比、a级板占比
            #初始化参数
            all_defect_name = []
            all_defect_count = 0
            all_detection_time = 0
            all_defect_area = 0

            # 如果检测到缺陷，更新统计数据
            for i in range(defect_count):
                # 如果这个缺陷类别还没有被统计，加入到 all_defect_name
                if labels[int(results.xyxy[0][i][5])] not in self.all_defect_name:
                    self.all_defect_name.append(labels[int(results.xyxy[0][i][5])])

            # 累加缺陷数量
            self.all_defect_count += defect_count

            # 累加检测时间
            self.all_detection_time += detection_time

            # 累加缺陷面积
            self.all_defect_area += real_areaNum

            # 累加检测次数
            self.real_detection_num += 1

            return defect_name, defect_count, accuracy, detection_time, average_area,all_defect_name,all_defect_count,all_detection_time,all_defect_area,self.real_detection_num

    def save_image(self):  # 保存图片
            img_path = self.image_paths[self.current_image_index]
            filename = os.path.basename(img_path)  # 获取原始图片文件名

            # 构建保存文件名，使用原始图片文件名作为前缀
            save_dir = 'photo/save'
            save_filename = f'{os.path.splitext(filename)[0]}_marked.jpg'

            # 将标记后的图像保存到指定位置
            marked_img_path = os.path.join(save_dir, save_filename)
            self.ui.label_10.pixmap().save(marked_img_path)

            PyQt5.QtWidgets.QMessageBox.information(self, '保存成功', f'图片已保存为 {save_filename}',PyQt5.QtWidgets.QMessageBox.Ok)

    def upload_image(self):  # 上传图片
            options = PyQt5.QtWidgets.QFileDialog.Options()
            options |= PyQt5.QtWidgets.QFileDialog.ReadOnly

            file_name, _ = PyQt5.QtWidgets.QFileDialog.getOpenFileName(self, "选择图片", "",
                                                                       "Image Files (*.jpg *.png *.jpeg * JPG);;All Files (*)",
                                                                       options=options)

            if file_name:
                self.image_paths.append(file_name)
                self.current_image_index = len(self.image_paths) - 1
                self.show_image()


    def upload_folder(self):  # 上传文件夹
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly
            options |= QFileDialog.ShowDirsOnly

            folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", options=options)

            if folder_path:
                    image_files = QDir(folder_path).entryList(['*.jpg', '*.png', '*.jpeg', '*.JPG'], QDir.Files)
                    self.image_paths.extend([os.path.join(folder_path, file) for file in image_files])
                    self.current_image_index = 0
                    self.show_image()

                    msg_box = QMessageBox()
                    msg_box.setWindowTitle("开始检测")
                    msg_box.setText("是否需要直接开始检测？")
                    msg_box.addButton(QMessageBox.Yes)
                    msg_box.addButton(QMessageBox.No)

                    reply = msg_box.exec_()
                    if reply == QMessageBox.Yes:
                            self.start_detection_and_save_to_database(folder_path)
                    else:
                            msg_box.close()

    def start_detection_and_save_to_database(self, folder_path):
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='plank_innovate',
            port=3306
        )

        cursor = conn.cursor()

        # 创建表格（如果不存在）
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS images_detection_results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            defect_category VARCHAR(255),
            defect_count INT,
            accuracy FLOAT,
            detection_time FLOAT,
            average_area FLOAT,
            total_area FLOAT
        )
        '''
        cursor.execute(create_table_query)

        labels = ['chipping', 'glueOverflow', 'greasyDirt', 'potholes', 'scratches']
        detections_results = []

        # 批量检测结果统计变量
        batch_defect_name = []  # 缺陷名称列表
        batch_defect_count = 0  # 缺陷总数
        batch_detection_time = 0  # 检测总时间
        batch_defect_area = 0  # 缺陷总面积
        image_count = len(self.image_paths)  # 检测图片总数

        # 初始化全局变量
        self.all_defect_name = []  # 所有缺陷类别
        self.all_defect_count = 0  # 所有缺陷数量
        self.all_detection_time = 0  # 所有检测时间
        self.all_defect_area = 0  # 所有缺陷面积
        self.real_detection_num = 0  # 真实检测次数

        for image_path in self.image_paths:
            img = Image.open(image_path)
            start_time = time.time()

            # 模型检测
            results = self.model(img)

            end_time = time.time()
            detection_time = end_time - start_time

            defect_name = ''
            if len(results.xyxy[0]) > 0:
                defect_name = labels[int(results.xyxy[0][0][5])]

            mask = predict_img(self.unet_model, img)

            img_np = np.array(img)
            mask_np = np.array(mask, dtype=np.uint8) * 255
            testimg = mask_np

            if testimg.ndim == 2:
                testimg = cv2.cvtColor(testimg, cv2.COLOR_GRAY2BGR)

            gray = cv2.cvtColor(testimg, cv2.COLOR_BGR2GRAY)
            ret, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            contours, hierachy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(testimg, contours, -1, (0, 0, 255), 1)

            defect_count = len(contours)

            # 计算缺陷面积和平均面积
            scale_factor = 50 / 256
            area = 0
            average_area = 0

            if defect_count > 0:
                for contour in contours:
                    area += cv2.contourArea(contour)

                adjusted_area = area * scale_factor ** 2
                average_area = adjusted_area / defect_count

            # 累加批量检测结果
            # batch_defect_name.append(defect_name)  # 记录缺陷名称
            #记录缺陷名称，如果里面有相同的了，就不再添加
            if defect_name not in batch_defect_name:
                batch_defect_name.append(defect_name)
            batch_defect_count += defect_count  # 累加缺陷数量
            batch_detection_time += detection_time  # 累加检测时间
            batch_defect_area += adjusted_area  # 累加缺陷总面积

            # 累加全局变量数据
            self.all_defect_name.append(defect_name)  # 记录所有缺陷名称
            self.all_defect_count += defect_count  # 统计所有缺陷数量
            self.all_detection_time += detection_time  # 累加所有检测时间
            self.all_defect_area += adjusted_area  # 累加所有缺陷面积
            self.real_detection_num += 1  # 增加检测次数

            # 处理检测结果
            result_dict = {
                '病害类别': defect_name,
                '病害数量': defect_count,
                '准确率': "100" if defect_name in labels else "",
                '检测耗时（s）': round(detection_time, 2),
                '平均面积': round(average_area, 2),
                '总面积': round(adjusted_area, 2)
            }

            detections_results.append(result_dict)

        # 批量写入数据库
        insert_query = '''
        INSERT INTO images_detection_results (defect_category, defect_count, accuracy, detection_time, average_area, total_area)
        VALUES (%s, %s, %s, %s, %s, %s)
        '''
        values = [(result_dict['病害类别'],
                   result_dict['病害数量'],
                   result_dict['准确率'],
                   result_dict['检测耗时（s）'],
                   result_dict['平均面积'],
                   result_dict['总面积']) for result_dict in detections_results]

        cursor.executemany(insert_query, values)

        print('数据已成功插入到MySQL数据库中！')
        conn.commit()
        cursor.close()
        conn.close()

        # 先显示检测完成的提示框
        tip_box = QMessageBox()
        tip_box.setWindowTitle("检测完成")
        tip_box.setText(
            f"共检测图片数量: {image_count}\n出现缺陷类别: {self.all_defect_name}\n总缺陷数量: {self.all_defect_count}\n总检测时间: {round(self.all_detection_time, 2)}秒\n总缺陷面积: {round(self.all_defect_area, 2)}")
        tip_box.addButton(QMessageBox.Yes)

        reply = tip_box.exec_()  # 等待用户点击后继续执行
        if reply == QMessageBox.Yes:
            # 检测结果确认后，询问是否生成AI报告
            msg_box = QMessageBox()
            msg_box.setWindowTitle("生成AI报告")
            msg_box.setText("是否要生成AI报告？")
            msg_box.addButton(QMessageBox.Yes)
            msg_box.addButton(QMessageBox.No)

            reply = msg_box.exec_()  # 等待用户点击
            if reply == QMessageBox.Yes:
                # 生成报告
                self.run_report_thread()
                report_box = QMessageBox()
                report_box.setWindowTitle("报告生成成功")
                report_box.setText("报告生成成功！请等待...")
                report_box.addButton(QMessageBox.Yes)
                report_box.exec_()
            else:
                msg_box.close()

    def deposit_the_form(self):
            # 检查文件是否已存在
            if os.path.exists("图片检测结果.xlsx"):
                    workbook = op.load_workbook("图片检测结果.xlsx")
                    worksheet = workbook.active
            else:
                    # 创建workbook
                    workbook = op.Workbook()  # 创建worksheet
                    worksheet = workbook.create_sheet(index=0)
            # 创建头文件
            header = ['病害类别', '病害数量(个)', '准确率(%)', '检测耗时（s）', '平均周长(mm)',
                      '平均面积(mm^2)', '总面积(mm^2)']
            worksheet.append(header)

            defect_name, defect_count, accuracy, detection_time, adjusted_area, average_area,all_defect_name, all_defect_count, all_detection_time, all_defect_area, self.real_detection_num = self.start_detection()

            count = worksheet.max_row + 1  # 从第二行开始
            worksheet.cell(row=count, column=1, value=defect_name)
            worksheet.cell(row=count, column=2, value=defect_count)
            worksheet.cell(row=count, column=3, value=accuracy)
            worksheet.cell(row=count, column=4, value=detection_time)
            worksheet.cell(row=count, column=6, value=average_area)
            worksheet.cell(row=count, column=7, value=adjusted_area)
            # 保存
            workbook.save("图片检测结果.xlsx")
            PyQt5.QtWidgets.QMessageBox.information(self, '写入成功', "写入表格成功",
                                                    PyQt5.QtWidgets.QMessageBox.Ok)

    def generate_report(self):

        # # 在后台线程中显示弹窗，避免主线程阻塞
        threading.Thread(target=self.show_messagebox).start()

        # 从累积统计中获取数据
        defect_name, defect_count, accuracy, detection_time, average_area, all_defect_name, all_defect_count, all_detection_time, all_defect_area, real_detection_num = \
            self.all_defect_name, self.all_defect_count, "100", self.all_detection_time, 0, self.all_defect_name, self.all_defect_count, self.all_detection_time, self.all_defect_area, self.real_detection_num

        # 其他数据从共享存储中获取
        detectBatch = shared_data.get('detectBatch', '1')
        boardSpec = shared_data.get('boardSpec', '')
        boardModel = shared_data.get('boardModel', '')
        transferRate = shared_data.get('transferRate', '')
        detectType = shared_data.get('detectType', '')
        sampleName = shared_data.get('sampleName', '')

        # 合并数据
        additional_image_data = [all_defect_name, all_defect_count, all_detection_time, self.ui.lineEdit_3.text(),
                                 self.ui.lineEdit_14.text(), self.ui.lineEdit_8.text(), self.ui.lineEdit_18.text(),
                                 self.ui.lineEdit_4.text(),
                                 self.ui.lineEdit_16.text(), self.ui.lineEdit_5.text(), self.ui.lineEdit_6.text(),
                                 all_defect_area,
                                 self.ui.lineEdit_17.text(), self.ui.lineEdit_13.text(), self.ui.dateTimeEdit.text(),
                                 self.real_detection_num]

        incoming_data = [detectBatch, boardSpec, boardModel, transferRate, detectType, sampleName]

        # 合并所有数据生成报告
        data = additional_image_data + incoming_data
        # 传入数据生成报告
        imagePDF.image_pdf_report(data)

        # A,B,C级板材判定，并显示在界面上
    def judgment(self, defect_count):
            if int(defect_count) == 0:
                    self.numA += 1
                    print("numA的值为：", self.numA)
                    self.ui.lineEdit_18.setText("A级板材")
                    print("此板材为A级板材")
            elif int(defect_count) < 5:
                    self.numB += 1
                    print("numB的值为：", self.numB)
                    self.ui.lineEdit_18.setText("B级板材")
            elif int(defect_count) >= 5:
                    self.numC += 1
                    print("numC的值为：", self.numC)
                    self.ui.lineEdit_18.setText("C级板材")
            # 计算总数量
            self.allPlanks = self.numA + self.numB + self.numC
            #计算A级板材占比
            self.aPlanks = self.numA / self.allPlanks * 100
            self.ui.lineEdit_13.setText(str(round(self.aPlanks, 2)))
            # print(self.ui.lineEdit_13.text())

            # 总数量显示
            self.ui.lineEdit_4.setText(str(self.allPlanks))
            # A级数量显示
            self.ui.lineEdit_16.setText(str(self.numA))
            # B级数量显示
            self.ui.lineEdit_5.setText(str(self.numB))
            # C级数量显示
            self.ui.lineEdit_6.setText(str(self.numC))

            # 损伤程度判定
    def damageJudgment(self, defect_count):
            if int(defect_count) == 0:
                    self.ui.lineEdit_8.setText("完好")
            elif int(defect_count) <= 3:
                    self.ui.lineEdit_8.setText("轻微")
            elif int(defect_count) <= 5:
                    self.ui.lineEdit_8.setText("中等")
            elif int(defect_count) >= 6:
                    self.ui.lineEdit_8.setText("严重")


    def compare_coordinates(self, xmin, ymin, xmax, ymax):
        threshold_box = [(150, 100), (500, 420)]  # 阈值坐标范围
        threshold_x_min, threshold_y_min = threshold_box[0]
        threshold_x_max, threshold_y_max = threshold_box[1]

        # 判断目标框的左上和右下角点坐标是否都在规划的坐标范围内
        if threshold_x_min <= xmin <= threshold_x_max and threshold_y_min <= ymin <= threshold_y_max and threshold_x_min <= xmax <= threshold_x_max and threshold_y_min <= ymax <= threshold_y_max:
            return "中心"
        else:
            return "边缘"

    # 计算缺陷区域的面积大小
    def calculate_defect_area(self, xmin, ymin, xmax, ymax):
        width = xmax - xmin
        height = ymax - ymin
        area = width * height
        return area

    def run_report_thread(self):
        # 创建一个新的线程来生成报告
        thread = threading.Thread(target=self.generate_report)
        thread.start()

    # 弹窗提示报告生成成功
    def show_messagebox(self):
        # messagebox.showinfo('提示', '检测报告生成成功！')
        # 创建根窗口并隐藏它
        root = Tk()
        root.withdraw()  # 隐藏主窗口

        # 显示消息弹窗
        messagebox.showinfo('提示', '检测报告生成中！')

        # 退出主窗口
        root.quit()
        root.destroy()