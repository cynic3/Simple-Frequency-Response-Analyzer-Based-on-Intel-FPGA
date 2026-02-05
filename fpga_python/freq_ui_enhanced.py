"""
增强版频率测试仪GUI - 保持原有功能，添加美化和新功能
"""
import numpy as np
from collections import deque
from PyQt5.QtWidgets import (QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
                             QHBoxLayout, QGridLayout, QSpinBox, QDoubleSpinBox,
                             QFrame, QComboBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor
import pyqtgraph as pg
from scipy.signal import hilbert

from udp_receiver import UDPReceiver


class FreqMeterEnhanced(QMainWindow):
    """增强版频率测试仪"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("频率特性测试仪 - 网络特性模拟")
        self.resize(1400, 900)
        self.setStyleSheet(self.get_stylesheet())
        
        # 初始化状态
        self.is_paused = False
        self.is_started = False
        self.frozen_sin_data = None
        self.frozen_ad_data = None
        self.zoom_level = 1.0
        
        self.init_ui()
        self.setup_udp()
        self.setup_timer()
    
    def init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # 顶部控制栏
        self.setup_top_controls(main_layout)
        
        # 参数显示栏
        self.setup_info_display(main_layout)
        
        # 图表区域
        self.setup_plots_area(main_layout)
        
        # 数据缓存初始化
        self.BUFFER_SIZE = 2048
        self.sin_buffer = deque([0] * self.BUFFER_SIZE, maxlen=self.BUFFER_SIZE)
        self.ad_buffer = deque([0] * self.BUFFER_SIZE, maxlen=self.BUFFER_SIZE)
        self.processed_ad_buffer = deque([0] * self.BUFFER_SIZE, maxlen=self.BUFFER_SIZE)
        self.x_data = np.arange(-self.BUFFER_SIZE, 0)
        self.network_points = deque(maxlen=500)
        
        # 网络参数
        self.amplitude_factor = 0.5
        self.phase_shift = 0.0
    
    def setup_top_controls(self, parent_layout):
        """设置顶部控制栏"""
        top_frame = QFrame()
        top_frame.setObjectName("controlFrame")
        top_frame.setFixedHeight(60)
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(15, 8, 15, 8)
        top_layout.setSpacing(12)
        
        # 启动/停止按钮
        self.start_button = QPushButton("▶ 开始")
        self.start_button.setFixedSize(100, 40)
        self.start_button.setObjectName("startButton")
        self.start_button.clicked.connect(self.toggle_start)
        top_layout.addWidget(self.start_button)
        
        # 暂停/继续按钮
        self.pause_button = QPushButton("⏸ 暂停")
        self.pause_button.setFixedSize(100, 40)
        self.pause_button.setObjectName("pauseButton")
        self.pause_button.setEnabled(False)
        self.pause_button.clicked.connect(self.toggle_pause)
        top_layout.addWidget(self.pause_button)
        
        # 分隔符
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet("color: #bdc3c7;")
        top_layout.addWidget(sep1)
        
        # 缩放控制
        zoom_label = QLabel("缩放:")
        top_layout.addWidget(zoom_label)
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["50%", "100%", "150%", "200%", "500%"])
        self.zoom_combo.setCurrentIndex(1)
        self.zoom_combo.currentTextChanged.connect(self.on_zoom_changed)
        self.zoom_combo.setFixedWidth(80)
        top_layout.addWidget(self.zoom_combo)
        
        # 分隔符
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("color: #bdc3c7;")
        top_layout.addWidget(sep2)
        
        # 更新网络参数按钮
        self.update_network_button = QPushButton("🔄 更新网络参数")
        self.update_network_button.setFixedSize(150, 40)
        self.update_network_button.setObjectName("updateButton")
        self.update_network_button.setEnabled(False)
        self.update_network_button.clicked.connect(self.update_network_parameters)
        top_layout.addWidget(self.update_network_button)
        
        top_layout.addStretch()
        
        # 状态指示灯
        self.status_indicator = QLabel("● 待命")
        self.status_indicator.setStyleSheet("color: #95a5a6; font-weight: bold; font-size: 11px;")
        top_layout.addWidget(self.status_indicator)
        
        parent_layout.addWidget(top_frame)
    
    def setup_info_display(self, parent_layout):
        """设置信息显示栏"""
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_frame.setFixedHeight(70)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 10, 15, 10)
        info_layout.setSpacing(25)

        # 幅值显示
        amp_container = QVBoxLayout()
        amp_label = QLabel("峰值幅度")
        amp_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-weight: bold;")
        self.amp_value = QLabel("0")
        self.amp_value.setStyleSheet("color: #3498db; font-size: 16px; font-weight: bold;")
        amp_container.setSpacing(2)
        amp_container.addWidget(amp_label)
        amp_container.addWidget(self.amp_value)
        info_layout.addLayout(amp_container)

        # 幅值因子显示
        af_container = QVBoxLayout()
        af_label = QLabel("幅值因子")
        af_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-weight: bold;")
        self.af_value = QLabel("0.50")
        self.af_value.setStyleSheet("color: #27ae60; font-size: 16px; font-weight: bold;")
        af_container.setSpacing(2)
        af_container.addWidget(af_label)
        af_container.addWidget(self.af_value)
        info_layout.addLayout(af_container)

        # 相位偏移显示
        ps_container = QVBoxLayout()
        ps_label = QLabel("相位偏移 (rad)")
        ps_label.setStyleSheet("color: #7f8c8d; font-size: 11px; font-weight: bold;")
        self.ps_value = QLabel("0.00")
        self.ps_value.setStyleSheet("color: #f39c12; font-size: 16px; font-weight: bold;")
        ps_container.setSpacing(2)
        ps_container.addWidget(ps_label)
        ps_container.addWidget(self.ps_value)
        info_layout.addLayout(ps_container)

        # 状态显示
        status_container = QVBoxLayout()
        status_l = QLabel("状态")
        status_l.setStyleSheet("color: #7f8c8d; font-size: 11px; font-weight: bold;")
        self.status_value = QLabel("停止")
        self.status_value.setStyleSheet("color: #95a5a6; font-size: 16px; font-weight: bold;")
        status_container.setSpacing(2)
        status_container.addWidget(status_l)
        status_container.addWidget(self.status_value)
        info_layout.addLayout(status_container)

        info_layout.addStretch()
        parent_layout.addWidget(info_frame)

    def setup_plots_area(self, parent_layout):
        """设置图表区域"""
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        # 原始信号图
        sin_widget = self.create_plot_widget("sin2_do 波形 (原信号)", "red")
        self.sin_plot_widget = sin_widget['plot']
        self.sin_curve = sin_widget['curve']
        grid_layout.addWidget(sin_widget['container'], 0, 0)

        # 网络输出信号图
        ad_widget = self.create_plot_widget("ad_in 波形 (网络输出)", "blue")
        self.ad_plot_widget = ad_widget['plot']
        self.ad_curve = ad_widget['curve']
        grid_layout.addWidget(ad_widget['container'], 0, 1)

        # 网络特性分析图
        network_container = QWidget()
        network_layout = QVBoxLayout(network_container)

        network_label = QLabel("📊 网络特性分析")
        network_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
        network_layout.addWidget(network_label)

        self.network_plot_widget = pg.PlotWidget(title="输入-输出特性")
        self.network_plot_widget.setLabel('left', '输出幅值')
        self.network_plot_widget.setLabel('bottom', '输入幅值')
        self.network_plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.network_plot_widget.setMouseEnabled(x=True, y=True)
        self.network_plot_widget.setStyleSheet("background-color: #ffffff;")

        self.network_scatter = self.network_plot_widget.plot(pen=None, symbol='o',
                                                              symbolSize=4, symbolBrush='g')
        network_layout.addWidget(self.network_plot_widget)

        grid_layout.addWidget(network_container, 1, 0, 1, 2)
        parent_layout.addLayout(grid_layout, 1)

    def create_plot_widget(self, title, color):
        """创建图表控件"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(5, 5, 5, 5)

        label = QLabel(f"📈 {title}")
        label.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 12px;")
        layout.addWidget(label)

        plot_widget = pg.PlotWidget()
        plot_widget.setYRange(-2048, 2047)
        plot_widget.setLabel('left', '幅值')
        plot_widget.setLabel('bottom', '采样点')
        plot_widget.showGrid(x=True, y=True, alpha=0.2)
        plot_widget.setMouseEnabled(x=True, y=False)
        plot_widget.setStyleSheet("background-color: #ffffff;")

        curve = plot_widget.plot(pen=pg.mkPen(color, width=1.5))
        layout.addWidget(plot_widget)

        return {'container': container, 'plot': plot_widget, 'curve': curve}

    def setup_udp(self):
        """设置UDP接收"""
        self.udp_thread = UDPReceiver()
        self.udp_thread.data_received.connect(self.update_buffer)
        self.udp_thread.start()

    def setup_timer(self):
        """设置更新定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)

    def toggle_start(self):
        """切换开始/停止"""
        if not self.is_started:
            self.udp_thread.start_receiving()
            self.start_button.setText("⏹ 停止")
            self.start_button.setObjectName("stopButton")
            self.pause_button.setEnabled(True)
            self.update_network_button.setEnabled(True)
            self.is_started = True
            self.status_indicator.setText("● 运行中")
            self.status_indicator.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px;")
            self.status_value.setText("运行")
            self.status_value.setStyleSheet("color: #27ae60; font-size: 16px; font-weight: bold;")

            self.sin_buffer.clear()
            self.ad_buffer.clear()
            self.processed_ad_buffer.clear()
            self.network_points.clear()
        else:
            self.udp_thread.stop_receiving()
            self.start_button.setText("▶ 开始")
            self.start_button.setObjectName("startButton")
            self.pause_button.setEnabled(False)
            self.update_network_button.setEnabled(False)
            self.pause_button.setText("⏸ 暂停")
            self.is_paused = False
            self.is_started = False
            self.status_indicator.setText("● 待命")
            self.status_indicator.setStyleSheet("color: #95a5a6; font-weight: bold; font-size: 11px;")
            self.status_value.setText("停止")
            self.status_value.setStyleSheet("color: #95a5a6; font-size: 16px; font-weight: bold;")

    def toggle_pause(self):
        """切换暂停/继续"""
        if not self.is_started:
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            self.pause_button.setText("▶ 继续")
            self.frozen_sin_data = np.array(self.sin_buffer)
            self.frozen_ad_data = np.array(self.processed_ad_buffer)
            self.status_indicator.setText("⏸ 暂停")
            self.status_indicator.setStyleSheet("color: #f39c12; font-weight: bold; font-size: 11px;")
            self.status_value.setText("暂停")
            self.status_value.setStyleSheet("color: #f39c12; font-size: 16px; font-weight: bold;")
        else:
            self.pause_button.setText("⏸ 暂停")
            self.frozen_sin_data = None
            self.frozen_ad_data = None
            self.status_indicator.setText("● 运行中")
            self.status_indicator.setStyleSheet("color: #27ae60; font-weight: bold; font-size: 11px;")
            self.status_value.setText("运行")
            self.status_value.setStyleSheet("color: #27ae60; font-size: 16px; font-weight: bold;")

    def on_zoom_changed(self, text):
        """缩放级别改变"""
        self.zoom_level = float(text.rstrip('%')) / 100.0

    def update_network_parameters(self):
        """更新网络参数"""
        self.amplitude_factor = np.random.uniform(0.1, 2.0)
        self.phase_shift = np.random.uniform(-np.pi / 4, np.pi / 4)
        self.af_value.setText(f"{self.amplitude_factor:.2f}")
        self.ps_value.setText(f"{self.phase_shift:.2f}")
        self.network_points.clear()

    def apply_network_effects(self, ad_array):
        """应用网络效果"""
        processed_array = ad_array * self.amplitude_factor

        if len(processed_array) > 10:
            try:
                analytic_signal = hilbert(processed_array)
                rotated_signal = analytic_signal * np.exp(1j * self.phase_shift)
                processed_array = np.real(rotated_signal)
            except Exception as e:
                print(f"相位变化应用错误: {e}")

        return processed_array

    def update_buffer(self, sin_val, ad_val):
        """更新缓冲区"""
        self.sin_buffer.append(sin_val)
        self.ad_buffer.append(ad_val)

    def update_plot(self):
        """更新图表"""
        if self.is_paused and self.frozen_sin_data is not None:
            # 显示冻结的数据
            sin_array = self.frozen_sin_data
            processed_array = self.frozen_ad_data
        elif self.is_paused or not self.is_started:
            return
        else:
            sin_array = np.array(self.sin_buffer)
            ad_array = np.array(self.ad_buffer)
            processed_ad = self.apply_network_effects(ad_array)
            self.processed_ad_buffer.extend(processed_ad[-len(ad_array):])
            processed_array = np.array(self.processed_ad_buffer)

        # 应用缩放
        display_size = int(len(self.x_data) * self.zoom_level)
        if display_size > len(self.x_data):
            display_size = len(self.x_data)

        x_display = self.x_data[-display_size:]
        sin_display = sin_array[-display_size:]
        ad_display = processed_array[-display_size:]

        self.sin_curve.setData(x_display, sin_display)
        self.ad_curve.setData(x_display, ad_display)

        # 更新网络特性
        if len(self.network_points) < 500 or np.random.random() < 0.1:
            if len(sin_array) > 0 and len(processed_array) > 0:
                idx = np.random.randint(0, min(len(sin_array), len(processed_array)))
                self.network_points.append((sin_array[idx], processed_array[idx]))

        if len(self.network_points) > 10:
            input_vals, output_vals = zip(*self.network_points)
            self.network_scatter.setData(input_vals, output_vals)

            if len(input_vals) > 0:
                x_min, x_max = min(input_vals), max(input_vals)
                x_range = np.linspace(x_min, x_max, 10)
                y_theory = x_range * self.amplitude_factor

                if not hasattr(self, 'theory_line'):
                    self.theory_line = self.network_plot_widget.plot(x_range, y_theory,
                                                                     pen=pg.mkPen('r', width=2))
                else:
                    self.theory_line.setData(x_range, y_theory)

        # 只显示峰值幅度
        if len(sin_array) > 10:
            peak_amp = np.max(np.abs(sin_array))
            self.amp_value.setText(f"{peak_amp:.0f}")
    
    def closeEvent(self, event):
        """关闭事件"""
        self.udp_thread.stop()
        event.accept()
    
    @staticmethod
    def get_stylesheet():
        """获取样式表"""
        return """
        QMainWindow {
            background-color: #f8f9fa;
        }
        
        #controlFrame {
            background-color: #ffffff;
            border-bottom: 1px solid #ecf0f1;
            border-radius: 4px;
        }
        
        #infoFrame {
            background-color: #ffffff;
            border: 1px solid #ecf0f1;
            border-radius: 4px;
        }
        
        QPushButton {
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            font-size: 11px;
            padding: 6px 12px;
        }
        
        QPushButton:hover {
            background-color: #2980b9;
        }
        
        QPushButton:pressed {
            background-color: #1f618d;
        }
        
        #startButton {
            background-color: #27ae60;
        }
        
        #startButton:hover {
            background-color: #229954;
        }
        
        #stopButton {
            background-color: #e74c3c;
        }
        
        #stopButton:hover {
            background-color: #c0392b;
        }
        
        #pauseButton {
            background-color: #f39c12;
        }
        
        #pauseButton:hover {
            background-color: #d68910;
        }
        
        #pauseButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        #updateButton {
            background-color: #9b59b6;
        }
        
        #updateButton:hover {
            background-color: #8e44ad;
        }
        
        #updateButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        QComboBox {
            background-color: white;
            color: #2c3e50;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox QAbstractItemView {
            background-color: white;
            color: #2c3e50;
            selection-background-color: #3498db;
        }
        
        QLabel {
            color: #2c3e50;
        }
        """
