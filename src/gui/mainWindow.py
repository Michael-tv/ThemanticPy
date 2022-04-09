import sys

from PyQt5.QtWidgets import (QMainWindow, QApplication, QTextEdit, QPushButton, 
                             QTreeView, QMenu, QToolBar, QHBoxLayout, QVBoxLayout,
                             QMenuBar, QWidget, QGroupBox)
from PyQt5.QtGui import QFont, QColor, QStandardItem, QStandardItemModel


class StandardItem(QStandardItem):
    def __init__(self, txt='', fontSize=13, setBold=False, color=QColor(0,0,0)):
        super().__init__()
        
        fnt = QFont('Open Sans', fontSize)
        fnt.setBold(setBold)
        self.setEditable(False)
        self.setForeground(color)
        self.setFont(fnt)
        self.setText(txt)

class mainWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle('Main Widget')
        
        # Try grid layout

        self.layout = QHBoxLayout()
        
        self.editor = self.createEditor()
        self.layout.addWidget(self.editor, stretch=1)
        
        self.tree = self.createTreeView()
        self.layout.addWidget(self.tree, stretch=1)       
    
    def createEditor(self):
        return QTextEdit(self)
    
        
    def createTreeView(self):
        treeView = QTreeView(self)
        treeModel = QStandardItemModel()
        rootNode = treeModel.invisibleRootItem()
        
        treeView.setHeaderHidden(True)
        
        # Define data model
        # -----------------
        #TODO: Must be done in function
        america = StandardItem(txt='America', fontSize=16, setBold=True)
        
        california = StandardItem('California', 14)
        america.appendRow(california)
        
        oakland = StandardItem('Oakland', 12, color=QColor(155,0,0))
        sanFran = StandardItem('San Francisco', 12, color=QColor(155,0,0))
        sanJose = StandardItem('San Jose', 12, color=QColor(155,0,0))
        
        california.appendRow(oakland)
        california.appendRow(sanFran)
        california.appendRow(sanJose)
        # or use california.appendrows([oakland, .., ..])
        
        rootNode.appendRow(america)
        
        
        treeView.setModel(treeModel)
        treeView.expandAll()
        treeView.doubleClicked.connect(self.getValue)
        
        
        return treeView
    
    def getValue(self, val):
        print(val.data())
        print(val.row())
        print(val.column())    
        
        
    def readModel(self):
        
        # Create a function that reads the data model from a yaml file
        
        return
    
    def saveModel(self):
        # Create a function that saves a model to a yaml file
        return 


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

        self.createMenuBar()
        
        self.layout
        
        self.centralWidget = mainWidget()  
        self.setCentralWidget(self.centralWidget)     
        
    def createMenuBar(self):
        menuBar = self.menuBar()
        #self.setMenuBar(menuBar)
        
        # Create menus
        menuBar.addMenu(QMenu('&File', self))
        menuBar.addMenu(QMenu('&Edit', self))
        menuBar.addMenu(QMenu('&Help', self))  

        self.show()
        


            
    
if __name__ == '__main__':
        
    App = QApplication(sys.argv)
    window = Window()
    sys.exit(App.exec())
        
    
        