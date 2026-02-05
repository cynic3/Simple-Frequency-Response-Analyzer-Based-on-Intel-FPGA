"""
频率特性测试仪主程序 - 含欢迎界面
"""
import sys
from PyQt5.QtWidgets import QApplication
from welcome_ui import WelcomeWindow
from freq_ui_enhanced import FreqMeterEnhanced


class ApplicationManager:
    """应用管理器 - 处理欢迎界面和主窗口的切换"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.welcome_window = None
        self.main_window = None
    
    def show_welcome(self):
        """显示欢迎界面"""
        self.welcome_window = WelcomeWindow()
        self.welcome_window.start_system.connect(self.on_start_system)
        self.welcome_window.show()
    
    def on_start_system(self):
        """启动主系统"""
        self.welcome_window.close()
        self.main_window = FreqMeterEnhanced()
        self.main_window.show()
    
    def run(self):
        """运行应用"""
        self.show_welcome()
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    manager = ApplicationManager()
    manager.run()
