numA = 0
numB = 0
numC = 0

def judgment(defect_count,lineEdit_13):
    #声明为全局变量
    global numA, numB, numC

    if int(defect_count) == 0:
        numA += 1
        print("numA的值为：",numA)
        lineEdit_13.setText("A级板材")
        print("此板材为A级板材")
    elif int(defect_count) < 5:
        numB += 1
        print("numB的值为：",numB)
        lineEdit_13.setText("B级板材")
    elif int(defect_count) >= 5:
        numC += 1
        print("numC的值为：", numC)
        lineEdit_13.setText("B级板材")

    return numA, numB, numC


