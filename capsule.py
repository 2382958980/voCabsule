import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QVBoxLayout)
from PyQt5.QtCore import Qt, QRect, QTimer,QThread
from PyQt5.QtGui import QPainter, QFont

from translation import TranslationService, TranslationWorker
from UIstyle import UIStyleManager
from dragHandler import WindowDragHandler
from animator import WindowAnimator

class CapsuleWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.translation_service = TranslationService()
        self.ui_style = UIStyleManager()
        self.drag_handler = WindowDragHandler(self)
        
        self.expanded = False
        
        self.collapsed_width = 240
        self.expanded_width = 240
        self.collapsed_height = 50
        self.expanded_height = 120
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(self.collapsed_width, self.collapsed_height)        
        self.animator = WindowAnimator(self)        
        self.setup_ui()        
        self.setup_translation_thread()        
        self.setStyleSheet(self.ui_style.get_window_style())
        
        QTimer.singleShot(300, self.translation_worker.warm_up_service)
    
    def setup_translation_thread(self):
        """设置翻译线程"""
        # 创建线程
        self.translation_thread = QThread()
        
        # 创建工作对象
        self.translation_worker = TranslationWorker(self.translation_service)
        
        # 将工作对象移动到线程
        self.translation_worker.moveToThread(self.translation_thread)
        
        # 连接信号和槽
        self.translation_worker.translationFinished.connect(self.on_translation_finished)
        
        # 启动线程
        self.translation_thread.start()
    
    def setup_ui(self):
        """设置UI组件"""
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 10, 15, 10)
        self.main_layout.setSpacing(0)
        
        # 创建上半部分布局（输入框和按钮）
        self.top_layout = QHBoxLayout()
        self.top_layout.setSpacing(10)
        
        # 添加输入框
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("输入要翻译的文本...")
        self.input_text.setStyleSheet(self.ui_style.get_input_style())
        self.top_layout.addWidget(self.input_text)
        
        # 添加圆形翻译按钮
        self.translate_button = QPushButton()
        self.translate_button.setFixedSize(30, 30)
        self.translate_button.setStyleSheet(self.ui_style.get_button_style())
        # 设置翻译图标
        self.translate_button.setText("▲")
        self.translate_button.setFont(QFont("Arial", 10, QFont.Bold))
        self.translate_button.clicked.connect(self.toggle_expand)
        self.top_layout.addWidget(self.translate_button)
        
        # 将上半部分布局添加到主布局
        self.main_layout.addLayout(self.top_layout)
        
        # 添加结果标签（初始隐藏）
        self.result_label = QLabel()
        self.result_label.setStyleSheet(self.ui_style.get_result_label_style())
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setFixedHeight(0)  # 初始高度为0
        self.result_label.hide()  # 初始隐藏
        
        # 设置结果标签动画
        self.animator.setup_result_label_animation(self.result_label)
        
        # 连接动画完成信号
        self.animator.windowAnimationFinished.connect(self._on_window_animation_finished)
        self.animator.resultLabelAnimationFinished.connect(self._on_result_animation_finished)
        
        self.main_layout.addWidget(self.result_label)
        self.main_layout.addStretch(1)
    
    def toggle_expand(self):
        """切换窗口展开和收起状态"""
        # 如果动画正在进行中，忽略点击
        if self.animator.is_animating():
            return
            
        # 获取窗口当前几何信息
        main_window_current_geo = self.geometry()
        
        if not self.expanded:
            # 准备展开窗口
            self.expanded = True
            self.translate_button.setText("▼")
            
            self.result_label.setText("...")
            self.result_label.show()
            
            # 设置主窗口的目标几何
            main_window_target_geo = QRect(
                main_window_current_geo.x(), 
                main_window_current_geo.y(),
                self.expanded_width, 
                self.expanded_height
            )
            
            # 开始主窗口动画
            self.animator.animate_window_to_geometry(main_window_target_geo)
            
            # 结果标签高度动画
            self.animator.animate_result_label_height(50)  # 展开状态下的目标高度
            
            # 翻译将在窗口动画完成后触发
            
        else:
            # 准备收起窗口
            self.expanded = False
            self.translate_button.setText("▲")
            
            # 设置主窗口的目标几何
            main_window_target_geo = QRect(
                main_window_current_geo.x(), 
                main_window_current_geo.y(),
                self.collapsed_width, 
                self.collapsed_height
            )
            
            # 开始主窗口动画
            self.animator.animate_window_to_geometry(main_window_target_geo)
            
            # 结果标签高度动画（收起至高度为0）
            self.animator.animate_result_label_height(0)
    
    def _on_window_animation_finished(self):
        """主窗口动画完成时触发的函数"""
        if self.expanded:
            self.perform_translation()
    
    def _on_result_animation_finished(self):
        """结果标签动画完成时触发的函数"""
        if not self.expanded and self.result_label.height() == 0:
            self.result_label.hide()
    
    def perform_translation(self):
        """开始异步翻译过程"""
        if not self.expanded:
            return
            
        query_text = self.input_text.text().strip()
        
        # 如果输入为空，显示提示
        if not query_text:
            self.result_label.setText("未输入翻译文本")
            return
        
        self.result_label.setText("...")
        
        # 使用QTimer.singleShot确保在UI更新后再执行翻译
        QTimer.singleShot(2, lambda: self.translation_worker.translate(query_text))
    
    def on_translation_finished(self, result):
        """翻译完成后的回调函数"""
        self.result_label.setText(result)
    
    def paintEvent(self, event):
        """自定义绘制事件，创建胶囊形状和增强视觉效果"""
        painter = QPainter(self)
        self.ui_style.paint_capsule_background(self, painter)
    
    def mousePressEvent(self, event):
        """记录鼠标按下的位置"""
        self.drag_handler.on_mouse_press(event)
    
    def mouseMoveEvent(self, event):
        """实现窗口拖动"""
        self.drag_handler.on_mouse_move(event)
    
    def mouseReleaseEvent(self, event):
        """重置鼠标位置记录"""
        self.drag_handler.on_mouse_release(event)
    
    def closeEvent(self, event):
        """窗口关闭事件，确保线程正确结束"""
        # 停止翻译线程
        self.translation_thread.quit()
        self.translation_thread.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CapsuleWindow()
    window.show()
    sys.exit(app.exec_())
