import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QTextEdit, QPushButton
from PyQt5 import QtGui


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.title = 'My App'
        self.top = 100
        self.left = 100
        self.width = 400
        self.height = 300
        self.iconName = 'home.png'
        
        #self.setWindowIcon(QtGui.QIcon(self.iconName)) #TODO: find icon
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
               
        self.createEditor()
               
        self.show()


    def createEditor(self):
        self.textEdit = QTextEdit(self)
        self.setCentralWidget(self.textEdit)
        
        
if __name__ == '__main__':
        
    App = QApplication(sys.argv)
    window = Window()
    sys.exit(App.exec())
        
    
        