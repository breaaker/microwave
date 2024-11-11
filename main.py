import numpy as np
import matplotlib.pyplot as plt
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QHBoxLayout, QScrollArea, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QPixmap, QIcon
from PIL import Image
from PyQt6.QtCore import QTimer
import sys
import qdarktheme

##定义元件类,包括传输线，电阻，电容，电感
class trans_line():
    def __init__(self, Z, length):
        self.Z = Z
        self.length = length

    def get_Z(self):
        return self.Z
    
    def set_Z(self, Z):
        self.Z = Z

    def get_length(self):
        return self.length
    
    def set_length(self, length):
        self.length = length

class resistor():
    #sp = 0:串联元件，sp = 1:并联元件
    def __init__(self, R, sp):
        self.R = R
        self.sp = sp

    def get_R(self):
        return self.R
    
    def set_R(self, R):
        self.R = R

    def get_sp(self):
        return self.sp
    
    def set_sp(self, sp):
        self.sp = sp

class capacitor():
    def __init__(self, R, sp):
        self.R = R
        self.sp = sp
    
    def get_R(self):
        return self.R
    
    def set_R(self, R):
        self.R = R
    
    def get_sp(self):
        return self.sp
    
    def set_sp(self, sp):
        self.sp = sp

class inductor():
    def __init__(self, R, sp):
        self.R = R
        self.sp = sp
    
    def get_R(self):
        return self.R
    
    def set_R(self, R):
        self.R = R
    
    def get_sp(self):
        return self.sp
    
    def set_sp(self, sp):
        self.sp = sp
##定义电路类
class circuit():
    def __init__(self):
        self.elements = []
    
    def add_element(self, element):
        self.elements.append(element)
    
    def set_element(self, index, element):
        if index >= len(self.elements):
            return 0
        self.elements[index] = element
        return 1

    def del_element(self, index):
        if index >= len(self.elements):
            return 0
        self.elements.pop(index)
        return 1
##定义z和gamma之间的转换函数
def z2gamma(z):
    return (z-1)/(z+1)

def gamma2z(gamma):
    return (1+gamma)/(1-gamma)
##定义复数到字符串的转换函数
def z2string(z):
    if z.real == 0:
        return f"{z.imag}j"
    elif z.imag == 0:
        return f"{z.real}"
    elif z.imag > 0:
        return f"{z.real}\n+{z.imag}j"
    elif z.imag < 0:
        return f"{z.real}\n{z.imag}j"
##定义画图函数,将电路画成一张图片
def paint(circuit):
    pics = []
    indexs = []
    for i in range(len(circuit.elements)):
        element = circuit.elements[i]

        if isinstance(element,trans_line):
            pic = "pics/trans_line.png"
            Z = element.get_Z()
            Z_str = z2string(Z)
            length = element.get_length()
            index = f"{i}\nZ={Z_str}$\Omega$\nL={length}$\lambda$"

        elif isinstance(element, resistor):
            sp = element.get_sp()
            pic = f"pics/resistor_{sp}.png"
            R = element.get_R()
            R_str = z2string(R)
            index = f"{i}\nR={R_str}$\Omega$"
            
        elif isinstance(element, capacitor):
            sp = element.get_sp()
            pic = f"pics/capacitor_{sp}.png"
            R = element.get_R()
            R_str = z2string(R)
            index = f"{i}\nR={R_str}$\Omega$"

        elif isinstance(element, inductor):
            sp = element.get_sp()
            pic = f"pics/inductor_{sp}.png"
            R = element.get_R()
            R_str = z2string(R)
            index = f"{i}\nR={R_str}$\Omega$"

        pic = Image.open(pic)
        pics.append(pic)
        indexs.append(index)

    pics.reverse()
    indexs.reverse()
    width = 0
    index_height = 60

    height = pics[0].height + index_height
    for i in range(len(pics)):
        width += pics[i].width
    ##拼接图片
    new_pic = Image.new("RGB", (width, height), (255, 255, 255))
    x_offset = 0
    for i in range(len(pics)):
        new_pic.paste(pics[i], (x_offset, 0))
        paint_index(pics[i].width/200, index_height/200, indexs[i])
        index = Image.open("pics/index.png")

        new_pic.paste(index, (x_offset, pics[i].height))
        x_offset += pics[i].width

    new_pic.save("pics/circuit.png")
##定义画序号的函数
def paint_index(width, height, x):
    plt.figure(figsize=(width, height))
    plt.text(0,0,x, fontsize=3)
    plt.axis('off')
    plt.savefig("pics/index.png", dpi=200)
    plt.close()
##定义计算电路的函数
def calculate(circuit, Z):
    results = []
    Z0 = 50
    for element in circuit.elements:
        if isinstance(element, trans_line):
            Z0 = element.get_Z()
            z = Z/Z0
            gamma = z2gamma(z)
            length = element.get_length()
            gamma = gamma*np.exp(-4j*np.pi*length)
            z = gamma2z(gamma)
            Z = Z0*z
                    
        else:
            if element.get_sp() == 0:
                Z = Z + element.get_R()
            else:
                Z = 1/(1/Z + 1/element.get_R())
            z = Z/Z0
            gamma = z2gamma(z)
        
        results.append([z, gamma])
    
    return results

class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 900)
        self.initUI()
    
    def initUI(self):
        Icon = QIcon("pics/icon.png")
        self.setWindowIcon(Icon)
        self.setWindowTitle("微波电路计算器")
        self.layout_1 = QVBoxLayout()
        self.setLayout(self.layout_1)

        ##主题部分
        self.firstline = QHBoxLayout()
        self.welcome = QLabel("欢迎使用微波电路计算器")
        self.light = QPushButton("亮色主题")
        self.light.clicked.connect(self.light_theme)
        ##默认为亮色主题
        self.light_theme()
        self.dark = QPushButton("暗色主题")
        self.dark.clicked.connect(self.dark_theme)
        self.firstline.addWidget(self.welcome)
        self.firstline.addWidget(self.light)
        self.firstline.addWidget(self.dark)
        self.layout_1.addLayout(self.firstline)

        ##新建电路部分
        self.label = QLabel("在此新建电路")
        self.layout_1.addWidget(self.label)
        self.newbutton = QPushButton("新建")
        self.layout_1.addWidget(self.newbutton)
        self.newbutton.clicked.connect(self.new_circuit)

        ##定时器，用于刷新输入部分
        self.timer = QTimer()
        self.timer.start(100)
        self.timer.timeout.connect(self.refresh)

        ##添加组件部分
        self.label2 = QLabel("管理电路元件,可以添加,修改,删除")
        self.layout_1.addWidget(self.label2)

        self.temp = QComboBox()
        self.temp.addItem("添加")
        self.temp.addItem("修改")
        self.temp.addItem("删除")
        self.layout_1.addWidget(self.temp)

        self.index = QLineEdit()
        self.index.setPlaceholderText("输入元件序号")
        self.layout_1.addWidget(self.index)

        self.addselect = QComboBox()
        self.addselect.addItem("传输线")
        self.addselect.addItem("电阻")
        self.addselect.addItem("电容")
        self.addselect.addItem("电感")
        self.layout_1.addWidget(self.addselect)

        self.tl_layout = QHBoxLayout()
        self.tl_Z0 = QLineEdit()
        self.tl_Z0.setPlaceholderText("输入特性阻抗,单位Omega")
        self.tl_length = QLineEdit()
        self.tl_length.setPlaceholderText("长度,以波长为单位")
        self.tl_layout.addWidget(self.tl_Z0)
        self.tl_layout.addWidget(self.tl_length)
        self.layout_1.addLayout(self.tl_layout)
        
        self.r_layout = QHBoxLayout()
        self.R = QLineEdit()
        self.R.setPlaceholderText("输入阻值,单位Omega,复数用j表示虚部")
        self.sp = QComboBox()
        self.sp.addItem("串联")
        self.sp.addItem("并联")
        self.r_layout.addWidget(self.R)
        self.r_layout.addWidget(self.sp)
        self.layout_1.addLayout(self.r_layout)

        self.addbutton = QPushButton("添加")
        self.layout_1.addWidget(self.addbutton)

        self.addbutton.clicked.connect(self.add_element)

        self.changebutton = QPushButton("修改")
        self.layout_1.addWidget(self.changebutton)
        self.changebutton.clicked.connect(self.change_element)

        self.deletebutton = QPushButton("删除")
        self.layout_1.addWidget(self.deletebutton)
        self.deletebutton.clicked.connect(self.delete_element)

        ##展示电路部分
        self.label3 = QLabel("展示电路")
        self.layout_1.addWidget(self.label3)
        self.pic = QScrollArea()
        self.layout_1.addWidget(self.pic)

        ##计算部分
        self.label4 = QLabel("开始计算,表格展示经过每个元件后的结果")
        self.layout_1.addWidget(self.label4)
        self.Z = QLineEdit()
        self.Z.setPlaceholderText("输入负载阻抗,单位Omega")
        self.layout_1.addWidget(self.Z)
        self.calculate = QPushButton("计算")
        self.layout_1.addWidget(self.calculate)

        self.calculate.clicked.connect(self.calculate_circuit)

        self.results = QTableWidget()
        self.layout_1.addWidget(self.results)
    
    ##切换主题
    def light_theme(self):
        qdarktheme.setup_theme("light")
    def dark_theme(self):
        qdarktheme.setup_theme("dark")

    ##刷新输入部分
    def refresh(self):

        if self.addselect.currentText() == "传输线":
            self.tl_Z0.show()
            self.tl_length.show()
            self.R.hide()
            self.sp.hide()
        else:
            self.tl_Z0.hide()
            self.tl_length.hide()
            self.R.show()
            self.sp.show()

        if self.temp.currentText() == "添加":
            self.index.hide()
            self.addselect.show()
            self.addbutton.show()
            self.changebutton.hide()
            self.deletebutton.hide()
        elif self.temp.currentText() == "修改":
            self.index.show()
            self.addselect.show()
            self.addbutton.hide()
            self.changebutton.show()
            self.deletebutton.hide()
        else:
            self.index.show()
            self.addselect.hide()
            self.tl_Z0.hide()
            self.tl_length.hide()
            self.R.hide()
            self.sp.hide()
            self.addbutton.hide()
            self.changebutton.hide()
            self.deletebutton.show()
    ##新建电路
    def new_circuit(self):
        self.circuit = circuit()
        pic = QPixmap("pics/new.png")
        circuit_pic = QLabel(self)
        circuit_pic.setPixmap(pic)
        self.pic.setWidget(circuit_pic)
    ##画电路
    def painter(self):
        if hasattr(self, "circuit"):
            paint(self.circuit)
            pic = QPixmap("pics/circuit.png")
            circuit_pic = QLabel(self)
            circuit_pic.setPixmap(pic)
            self.pic.setWidget(circuit_pic)
    ##添加元件
    def add_element(self):
        if not hasattr(self, "circuit"):
            return
        
        if self.addselect.currentText() == "传输线":
            if self.tl_Z0.text() == "" or self.tl_length.text() == "":
                return
            Z = complex(self.tl_Z0.text())
            length = float(self.tl_length.text())
            self.circuit.add_element(trans_line(Z, length))

        else:
            if self.R.text() == "":
                return
            R = complex(self.R.text())
            if self.sp.currentText() == "串联":
                sp = 0
            else:
                sp = 1
            if self.addselect.currentText() == "电阻":
                self.circuit.add_element(resistor(R, sp))
            elif self.addselect.currentText() == "电容":
                self.circuit.add_element(capacitor(R, sp))
            else:
                self.circuit.add_element(inductor(R, sp))

        self.painter()
    ##修改元件
    def change_element(self):
        if not hasattr(self, "circuit"):
            return
        if self.index.text() == "":
            return
        index = int(self.index.text())
        if self.addselect.currentText() == "传输线":
            if self.tl_Z0.text() == "" or self.tl_length.text() == "":
                return
            Z = float(self.tl_Z0.text())
            length = float(self.tl_length.text())
            element = trans_line(Z, length)
            re = self.circuit.set_element(index, element)
        else:
            if self.R.text() == "":
                return
            R = complex(self.R.text())
            if self.sp.currentText() == "串联":
                sp = 0
            else:
                sp = 1
            if self.addselect.currentText() == "电阻":
                element = resistor(R, sp)
            elif self.addselect.currentText() == "电容":
                element = capacitor(R, sp)
            else:
                element = inductor(R, sp)
            re = self.circuit.set_element(index, element)
        if re == 0:
            return
        self.painter()

    ##删除元件
    def delete_element(self):
        if not hasattr(self, "circuit"):
            return
        if self.index.text() == "":
            return
        index = int(self.index.text())
        re = self.circuit.del_element(index)
        if re == 0:
            return
        self.painter()
    ##计算电路
    def calculate_circuit(self):
        if not hasattr(self, "circuit"):
            return
        if self.Z.text() == "":
            return
        Z = complex(self.Z.text())
        results = calculate(self.circuit, Z)
        self.results.setRowCount(len(results))
        self.results.setColumnCount(2)
        self.results.setHorizontalHeaderLabels(["z", "gamma"])
        vheaders = [f"item{i}" for i in range(len(results))]
        self.results.setVerticalHeaderLabels(vheaders)
        self.results.setColumnWidth(0, 300)
        self.results.setColumnWidth(1, 300)

        for i in range(len(results)):
            z = QTableWidgetItem("{:.4f}".format(results[i][0]))
            gamma = QTableWidgetItem("{:.4f}".format(results[i][1]))
            self.results.setItem(i, 0, z)
            self.results.setItem(i, 1, gamma)

app = QtWidgets.QApplication(sys.argv)
window = MainWidget()
window.show()

app.exec()