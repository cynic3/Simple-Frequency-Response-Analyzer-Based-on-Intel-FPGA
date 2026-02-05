"""
欢迎界面模块 - 频率特性测试仪系统
提供专业的启动界面和系统介绍
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPixmap
from PyQt5.QtCore import QSize


class WelcomeWindow(QMainWindow):
    """欢迎界面类"""
    start_system = pyqtSignal()  # 信号：用户点击进入系统
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("频率特性测试仪系统")
        self.setFixedSize(900, 700)
        self.setStyleSheet(self.get_welcome_stylesheet())
        self.init_ui()
        self.center_window()
    
    def center_window(self):
        """居中显示窗口"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 顶部渐变背景区域
        top_widget = QFrame()
        top_widget.setObjectName("topFrame")
        top_widget.setFixedHeight(280)
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(40, 60, 40, 40)
        
        # 系统标题
        title_label = QLabel("频率特性测试仪系统")
        title_font = QFont("微软雅黑", 48, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("Network Characteristic Frequency Testing System")
        subtitle_font = QFont("Arial", 14)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setStyleSheet("color: rgba(255,255,255,0.8);")
        subtitle_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(subtitle_label)
        
        top_layout.addStretch()
        main_layout.addWidget(top_widget)
        
        # 中间内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(60, 60, 60, 40)
        content_layout.setSpacing(20)
        
        # 系统简介
        intro_title = QLabel("系统简介")
        intro_title_font = QFont("微软雅黑", 16, QFont.Bold)
        intro_title.setFont(intro_title_font)
        intro_title.setStyleSheet("color: #2c3e50;")
        content_layout.addWidget(intro_title)
        
        intro_text = QLabel(
            "本系统用于实时测试和分析网络信号特性，通过UDP接收FPGA采集的数据，\n"
            "实现信号幅值、频率、相位等参数的实时监测和网络特性分析。\n\n"
            "主要功能：\n"
            "• 实时频率估计与幅值检测\n"
            "• 网络特性参数模拟与分析\n"
            "• 动态波形显示与交互缩放\n"
            "• 暂停/继续实时显示"
        )
        intro_font = QFont("微软雅黑", 11)
        intro_text.setFont(intro_font)
        intro_text.setStyleSheet("color: #555555; line-height: 1.6;")
        intro_text.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        content_layout.addWidget(intro_text)
        
        content_layout.addStretch()
        main_layout.addWidget(content_widget)
        
        # 底部信息区域
        bottom_widget = QFrame()
        bottom_widget.setObjectName("bottomFrame")
        bottom_widget.setFixedHeight(120)
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(40, 20, 40, 20)
        
        # 作者信息
        authors_label = QLabel("项目成员")
        authors_font = QFont("微软雅黑", 11, QFont.Bold)
        authors_label.setFont(authors_font)
        authors_label.setStyleSheet("color: #2c3e50;")
        bottom_layout.addWidget(authors_label)
        
        authors_info = QLabel(
            "何宜霖 (22121973)  |  高宇涛 (22121154)  |  "
            "霍晟宇 (22121249)  |  沈文博 (22121156)"
        )
        authors_info_font = QFont("微软雅黑", 10)
        authors_info.setFont(authors_info_font)
        authors_info.setStyleSheet("color: #7f8c8d;")
        authors_info.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(authors_info)
        
        # 版本信息
        version_label = QLabel("v1.0 Enhanced Edition")
        version_font = QFont("Arial", 9)
        version_label.setFont(version_font)
        version_label.setStyleSheet("color: #bdc3c7;")
        version_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(version_label)
        
        main_layout.addWidget(bottom_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(40, 20, 40, 30)
        button_layout.setSpacing(20)
        
        button_layout.addStretch()
        
        # 进入系统按钮
        enter_button = QPushButton("进入系统")
        enter_button.setFixedSize(180, 50)
        enter_font = QFont("微软雅黑", 12, QFont.Bold)
        enter_button.setFont(enter_font)
        enter_button.setObjectName("enterButton")
        enter_button.setCursor(Qt.PointingHandCursor)
        enter_button.clicked.connect(self.on_enter_clicked)
        button_layout.addWidget(enter_button)
        
        # 退出按钮
        exit_button = QPushButton("退出")
        exit_button.setFixedSize(100, 50)
        exit_button.setFont(enter_font)
        exit_button.setObjectName("exitButton")
        exit_button.setCursor(Qt.PointingHandCursor)
        exit_button.clicked.connect(self.close)
        button_layout.addWidget(exit_button)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
    
    def on_enter_clicked(self):
        """进入系统"""
        self.start_system.emit()
    
    @staticmethod
    def get_welcome_stylesheet():
        """获取欢迎界面样式表"""
        return """
        QMainWindow {
            background-color: #f8f9fa;
        }
        
        #topFrame {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                       stop:0 #3498db, stop:1 #2980b9);
            border-bottom: 3px solid #2c3e50;
        }
        
        #bottomFrame {
            background-color: #ecf0f1;
            border-top: 1px solid #bdc3c7;
        }
        
        #enterButton {
            background-color: #27ae60;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            padding: 10px 20px;
        }
        
        #enterButton:hover {
            background-color: #229954;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        #enterButton:pressed {
            background-color: #1e8449;
        }
        
        #exitButton {
            background-color: #95a5a6;
            color: white;
            border: none;
            border-radius: 8px;
            font-weight: bold;
        }
        
        #exitButton:hover {
            background-color: #7f8c8d;
        }
        
        #exitButton:pressed {
            background-color: #566573;
        }
        
        QLabel {
            background-color: transparent;
        }
        """
