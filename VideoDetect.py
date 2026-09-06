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
import videoPDF

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

#视频检测类，
class VideoDetect(QMainWindow):
    def __init__(self,VideoUi,model,segmentation_unet,parent=None):
        super(VideoDetect, self).__init__(parent)
        self.VideoUi = VideoUi
        self.model = model
        self.unet_model = segmentation_unet
        self.video_path = None
        self.is_detecting = False
        self.fps = 30  # 设置目标帧率为60
        self.cap = None  # 视频捕捉对象初始化为 None
        self.timer = QTimer(self)  # 初始化QTimer
        self.timer.timeout.connect(self.process_frame)  # 定时处理每一帧
        # 初始化A级板，B级板，C级板数量
        self.numA = 0
        self.numB = 0
        self.numC = 0
        self.area = 901600

    # 上传视频功能
    def upload_video(self):
        self.video_path, _ = QFileDialog.getOpenFileName(self, "选择视频文件", "", "视频文件 (*.mp4 *.avi)")
        if self.video_path:
            self.show_video()
        else:
            QMessageBox.warning(self, "警告", "请选择有效的视频文件！")
        # 展示视频
        # 展示视频
    def show_video(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            QMessageBox.warning(self, "警告", "无法打开视频文件！")
            return

        self.timer.start(int(1000 / self.fps))  # 每帧间隔时间为1000ms除以目标帧率

    # 处理每一帧
    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            self.timer.stop()  # 停止计时器
            self.cap.release()
            return

        # 将每一帧显示在label_11上
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # 将 BGR 转换为 RGB
        height, width, bytesPerComponent = frame.shape
        bytesPerLine = bytesPerComponent * width
        qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
        self.VideoUi.label_11.setPixmap(QPixmap.fromImage(qImg).scaled(self.VideoUi.label_11.size(),
                                                                       QtCore.Qt.KeepAspectRatio))

    # 开始检测
    def start_detection(self):
        if not self.video_path:
            QMessageBox.warning(self, "错误", "请先上传视频文件！")
            return

        #运行开始检测线程，并弹出提示
        threading.Thread(target=self.show_begin_messagebox).start()

        self.is_detecting = True
        detect_thread = threading.Thread(target=self.detect_video)
        detect_thread.start()

    def detect_video(self):
        cap = cv2.VideoCapture(self.video_path)
        labels = ['chipping', 'glueOverflow', 'greasyDirt', 'potholes', 'scratches']  # 缺陷类别
        frame_skip = 25  # 每隔30帧检测一次
        frame_count = 0  # 初始化帧计数器

        while cap.isOpened() and self.is_detecting:
            start_time = time.time()  # 记录开始时间
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1  # 增加帧计数器

            # 只在达到frame_skip的帧数时执行检测逻辑
            if frame_count % frame_skip == 0:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                # 执行目标检测
                results = self.model(img)

                # 使用分割模型检测缺陷
                mask = predict_img(self.unet_model, img)

                # 获取检测结果的标签和置信度
                defect_name = ''
                confidence = 0.0
                if len(results.xyxy[0]) > 0:
                    defect_name = labels[int(results.xyxy[0][0][5])]
                    confidence = float(results.xyxy[0][0][4])

                # 计算缺陷数量
                defect_count = len(results.xyxy[0])

                # 计算检测时间
                end_time = time.time()
                detection_time = end_time - start_time

                # 打印检测信息
                print('---')
                print('Defect_name: {}'.format(defect_name))
                print('Defect Count: {}'.format(defect_count))
                print('confidence: {}'.format(confidence))
                print('Detection Time: {} seconds'.format(detection_time))

                # 标记缺陷并显示在UI上
                marked_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                for result in results.xyxy[0]:
                    x1, y1, x2, y2, _, cls = result
                    cv2.rectangle(marked_img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

                marked_img = cv2.cvtColor(np.array(marked_img), cv2.COLOR_BGR2RGB)
                q_img = QtGui.QImage(marked_img.data, marked_img.shape[1], marked_img.shape[0],
                                     QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(q_img)

                self.VideoUi.label_42.setPixmap(pixmap.scaled(self.VideoUi.label_42.size(), QtCore.Qt.KeepAspectRatio))

                # 找出离中心最远的框
                max_distance = 0
                farthest_box = None

                img_center = (pixmap.width() // 2, pixmap.height() // 2)

                for result in results.xyxy[0]:
                    x1, y1, x2, y2, _, cls = result
                    box_center = ((x1 + x2) / 2, (y1 + y2) / 2)
                    distance = ((img_center[0] - box_center[0]) ** 2 + (img_center[1] - box_center[1]) ** 2) ** 0.5
                    if distance > max_distance:
                        max_distance = distance
                        farthest_box = (x1, y1, x2, y2)

                # 如果有检测框，对离中心最远的框进行位置比较
                if farthest_box is None:
                    print('No defects')
                    self.VideoUi.lineEdit_30.setText("No defects")
                    self.VideoUi.lineEdit_33.setText("100%")
                    self.VideoUi.lineEdit_34.setText("No defects")
                    self.VideoUi.lineEdit_35.setText("No defects")
                    self.VideoUi.lineEdit_31.setText("0")
                    self.VideoUi.lineEdit_42.setText("0")
                else:
                    x1, y1, x2, y2x = farthest_box

                    result = self.compare_coordinates(int(x1), int(y1), int(x2), int(y2))
                    print('Result: {}'.format(result))
                    self.VideoUi.lineEdit_34.setText(result)

                    defect_area = self.calculate_defect_area(int(x1), int(y1), int(x2), int(y2))
                    one_area = defect_area / 768
                    real_area = defect_count * one_area
                    # self.lineEdit_32.setText(str(real_area))
                    self.VideoUi.lineEdit_41.setText(str(round(real_area * 10, 3)))

                    areaRatio = real_area / self.area * 10000
                    print("面积占比为：", areaRatio)
                    # self.lineEdit_18.setText(str(areaRatio)+"%")
                    # print(str(round(areaRatio, 3))+"%")
                    self.VideoUi.lineEdit_42.setText(str(round(areaRatio * 10, 2)))

                # 更新UI信息
                self.VideoUi.lineEdit_30.setText(defect_name)  # 更新缺陷名称
                self.VideoUi.lineEdit_31.setText(str(defect_count))  # 更新缺陷数量
                self.VideoUi.lineEdit_33.setText("100%")  # 更新置信度（固定值为100%，根据需要修改）
                self.VideoUi.lineEdit_32.setText(str(round(detection_time, 3)))  # 更新检测时间

                # 判定板材等级并显示在界面上
                self.judgment(defect_count)
                #损伤程度判定
                self.damageJudgment(defect_count)
                #将检测结果写入数据库
                self.save_to_database()



            # 控制帧率
            elapsed_time = time.time() - start_time
            delay = max(0.001 / self.fps - elapsed_time, 0)
            time.sleep(delay)

        cap.release()
        self.is_detecting = False

        # 生成报告
        self.run_video_report_thread()

    # 停止检测
    def stop_detection(self):
        self.is_detecting = False
        threading.Thread(target=self.show_stop_messagebox).start()


    # A,B,C级板材判定，并显示在界面上
    def judgment(self, defect_count):
        if int(defect_count) == 0:
            self.numA += 1
            print("numA的值为：", self.numA)
            self.VideoUi.lineEdit_36.setText("A级板材")
            print("此板材为A级板材")
        elif int(defect_count) < 5:
            self.numB += 1
            print("numB的值为：", self.numB)
            self.VideoUi.lineEdit_36.setText("B级板材")
        elif int(defect_count) >= 5:
            self.numC += 1
            print("numC的值为：", self.numC)
            self.VideoUi.lineEdit_36.setText("C级板材")

        # A级数量显示
        self.VideoUi.lineEdit_38.setText(str(self.numA))
        # B级数量显示
        self.VideoUi.lineEdit_39.setText(str(self.numB))
        # C级数量显示
        self.VideoUi.lineEdit_40.setText(str(self.numC))

        self.plankNum(self.numA, self.numB, self.numC)

    # 坐标比较，设置阈值，调用进行比较
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

    # 板坯数量，A级板占比
    def plankNum(self, numA, numB, numC):
        plankNums = numA + numB + numC

        # 板坯数量显示
        self.VideoUi.lineEdit_37.setText(str(plankNums))
        # A级板占比显示
        self.VideoUi.lineEdit_43.setText(str(round(self.numA / plankNums * 100, 2)))

    # 损伤程度判定
    def damageJudgment(self, defect_count):
        if int(defect_count) == 0:
            self.VideoUi.lineEdit_35.setText("完好")
        elif int(defect_count) <= 3:
            self.VideoUi.lineEdit_35.setText("轻微")
        elif int(defect_count) <= 5:
            self.VideoUi.lineEdit_35.setText("中等")
        elif int(defect_count) >= 6:
            self.VideoUi.lineEdit_35.setText("严重")

    def creat_ai_report(self):
        # 从全局存储中获取数据
        detectBatch = shared_data.get('detectBatch', '1')
        boardSpec = shared_data.get('boardSpec', '')
        boardModel = shared_data.get('boardModel', '')
        detectNum = shared_data.get('detectNum', '')
        transferRate = shared_data.get('transferRate', '')
        detectType = shared_data.get('detectType', '')
        sampleName = shared_data.get('sampleName', '')

        additional_data = [self.VideoUi.lineEdit_30.text(), self.VideoUi.lineEdit_31.text(),self.VideoUi.lineEdit_32.text(),
                           self.VideoUi.lineEdit_33.text(), self.VideoUi.lineEdit_34.text(), self.VideoUi.lineEdit_35.text(),
                           self.VideoUi.lineEdit_36.text(), self.VideoUi.lineEdit_37.text(), self.VideoUi.lineEdit_38.text(),
                           self.VideoUi.lineEdit_39.text(), self.VideoUi.lineEdit_40.text(), self.VideoUi.lineEdit_41.text(),
                           self.VideoUi.lineEdit_42.text(),self.VideoUi.lineEdit_43.text(),self.VideoUi.dateTimeEdit.text()]
        # 添加从 on_save 函数中传递过来的数据
        incoming_data = [
            detectBatch, boardSpec, boardModel, detectNum, transferRate, detectType, sampleName
        ]

        # 将两个数据集合合并
        data = additional_data + incoming_data

        videoPDF.video_pdf(data)

    #创建新的线程来生成报告
    def run_video_report_thread(self):
        # 创建一个新的线程来生成报告
        thread = threading.Thread(target=self.creat_ai_report)
        thread.start()

    # 弹窗提示报告生成成功
    def show_begin_messagebox(self):
        # messagebox.showinfo('提示', '检测报告生成成功！')
        # 创建根窗口并隐藏它
        root = Tk()
        root.withdraw()  # 隐藏主窗口

        # 显示消息弹窗
        messagebox.showinfo('提示', '开始检测！')

        # 退出主窗口
        root.quit()
        root.destroy()

    # 弹窗提示报告生成成功
    def show_stop_messagebox(self):
        # messagebox.showinfo('提示', '检测报告生成成功！')
        # 创建根窗口并隐藏它
        root = Tk()
        root.withdraw()  # 隐藏主窗口

        # 显示消息弹窗
        messagebox.showinfo('提示', '停止检测！')

        # 退出主窗口
        root.quit()
        root.destroy()

    def save_to_database(self):
        #获取检测数据，并保存到数据库

        #连接数据库mysql
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='plank_innovate',
            port=3306
        )

        cursor = conn.cursor()
        #创建表格，如果不存在
        create_table_query = '''
                CREATE TABLE IF NOT EXISTS video_detection_results (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    defect_name VARCHAR(255),
                    defect_count INT,
                    accuracy FLOAT,
                    detection_time FLOAT,
                    defects_area DOUBLE,
                    area_ratio VARCHAR(255),
                    defect_location VARCHAR(255),
                    damage_level VARCHAR(255),
                    plank_level VARCHAR(255)
                )
                '''
        cursor.execute(create_table_query)
        #插入数据
        #将检测数据保存到数据库
        # 定义要写入数据库的数据
        defect_name = self.VideoUi.lineEdit_30.text()
        defect_count = self.VideoUi.lineEdit_31.text()
        accuracy = '100'
        detection_time = self.VideoUi.lineEdit_32.text()
        defects_area = self.VideoUi.lineEdit_41.text()
        area_ratio = self.VideoUi.lineEdit_42.text()
        defect_location = self.VideoUi.lineEdit_34.text()
        damage_level = self.VideoUi.lineEdit_35.text()
        plank_level = self.VideoUi.lineEdit_36.text()

        # 构造SQL语句
        insert_query = '''
            INSERT INTO video_detection_results (defect_name, defect_count, accuracy, detection_time, defects_area, area_ratio, defect_location, damage_level, plank_level)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        # 构造数据
        data = (defect_name, defect_count, accuracy, detection_time, defects_area, area_ratio, defect_location, damage_level, plank_level)

        # 执行SQL语句
        cursor.execute(insert_query, data)

        # 提交事务
        conn.commit()

        # 关闭数据库连接
        conn.close()
        # 弹窗提示保存成功
        print("保存成功")