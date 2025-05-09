from PyQt5.QtCore import QPoint, Qt

class WindowDragHandler:
    def __init__(self, window):
        self.window = window
        self.old_pos = None
    
    def on_mouse_press(self, event):
        """记录鼠标按下的位置"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
    
    def on_mouse_move(self, event):
        """实现窗口拖动"""
        if event.buttons() & Qt.LeftButton and self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.window.move(self.window.x() + delta.x(), self.window.y() + delta.y())
            self.old_pos = event.globalPos()
    
    def on_mouse_release(self, event):
        """重置鼠标位置记录"""
        if event.button() == Qt.LeftButton:
            self.old_pos = None
