import pyttsx3
import threading

# 定义语音播报函数
def speak_text(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 270)  # 设置语速
    engine.setProperty('volume', 2)  # 设置音量

    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # 设置第一个语音合成器

    engine.say(text)
    engine.runAndWait()
    engine.stop()


# 调用语音播报的函数
def voice_report(self):
    #判断第一个中括号的文本是什么，如果是特定的字符，则转换成别的

    if self.lineEdit_12.text() == "chipping":
        self.lineEdit_12.setText("崩边")

    elif self.lineEdit_12.text() == "glueOverflow":
        self.lineEdit_12.setText("溢胶")

    elif self.lineEdit_12.text() == "greasyDirt":
        self.lineEdit_12.setText("油污")

    elif self.lineEdit_12.text() == "potholes":
        self.lineEdit_12.setText("坑洞")

    elif self.lineEdit_12.text() == "scratches":
        self.lineEdit_12.setText("划痕")

    else:
        self.lineEdit_12.setText("空")

    # 定义播报内容
    text = "检测完成，缺陷类别为{}，板材级别为{}。".format(self.lineEdit_12.text(),self.lineEdit_22.text(),)

    # 创建线程进行语音播报
    thread = threading.Thread(target=speak_text, args=(text,))
    thread.start()
#创建用于图像识别的播报函数
def voice_report_image(self):

    if self.ui.lineEdit_11.text() == "chipping":
        self.ui.lineEdit_11.setText("崩边")

    elif self.ui.lineEdit_11.text() == "glueOverflow":
        self.ui.lineEdit_11.setText("溢胶")

    elif self.ui.lineEdit_11.text() == "greasyDirt":
        self.ui.lineEdit_11.setText("油污")

    elif self.ui.lineEdit_11.text() == "potholes":
        self.ui.lineEdit_11.setText("坑洞")

    elif self.ui.lineEdit_11.text() == "scratches":
        self.ui.lineEdit_11.setText("划痕")

    else:
        self.ui.lineEdit_11.setText("空")

    # 定义播报内容
    text = "检测完成，缺陷类别为{}，板材级别为{}。".format(self.ui.lineEdit_11.text(), self.ui.lineEdit_18.text(), )

    # 创建线程进行语音播报
    thread = threading.Thread(target=speak_text, args=(text,))
    thread.start()
