from PyQt5.QtGui import QPainter, QColor, QPainterPath, QFont, QPen
from PyQt5.QtCore import Qt

class UIStyleManager:
    @staticmethod
    def get_input_style():
        return """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0); 
                border-radius: 15px; 
                padding: 5px 10px;
                border: none;
                color: rgba(255, 255, 255, 100);
                font-size: 14px;
            }
        """
    
    @staticmethod
    def get_button_style():
        return """
            QPushButton {
                background-color: rgba(100, 180, 255, 180); 
                color: white; 
                border-radius: 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(120, 200, 255, 200);
            }
            QPushButton:pressed {
                background-color: rgba(80, 160, 235, 180);
            }
        """
    
    @staticmethod
    def get_result_label_style():
        return """
            color: white; 
            background-color: rgba(80, 80, 80, 0); 
            padding: 8px 12px; 
            border: none;
            font-size: 14px;
        """
    
    @staticmethod
    def get_window_style():
        return """
            QWidget {
                border: 1px solid rgba(255, 255, 255, 30);
            }
        """
    
    @staticmethod
    def paint_capsule_background(widget, painter):
        """绘制胶囊形状的背景"""
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 创建圆角矩形路径（胶囊形状）
        path = QPainterPath()
        radius = min(widget.height() / 2, 25)  # 圆角半径，最大25
        path.addRoundedRect(0, 0, widget.width(), widget.height(), radius, radius)
        
        # 设置半透明灰色背景
        painter.setClipPath(path)
        
        # 创建渐变背景效果
        gradient = QColor(40, 40, 40, 200)
        painter.fillPath(path, gradient)
        
        # 添加光泽边框效果
        pen = QPen(QColor(20, 100, 255, 30), 2)  # 轻微的白色边框
        painter.setPen(pen)
        painter.drawPath(path)
        
        # 添加内部阴影效果
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(3, 3, widget.width()-6, widget.height()-6, radius-3, radius-3)
        shadow_color = QColor(0, 0, 0, 40)
        painter.fillPath(shadow_path, shadow_color)
