from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve, QObject, pyqtSignal

class WindowAnimator(QObject):
    # 定义动画完成信号
    windowAnimationFinished = pyqtSignal()
    resultLabelAnimationFinished = pyqtSignal()
    
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        
        # 窗口几何动画
        self.window_animation = QPropertyAnimation(widget, b"geometry")
        self.window_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.window_animation.setDuration(280)
        self.window_animation.finished.connect(self._emit_window_animation_finished)
        
        # 结果标签高度动画
        self.result_label_animation = None  # 将在 setup_result_label_animation 中初始化
        
        # 动画状态追踪
        self.animation_in_progress = False
    
    def setup_result_label_animation(self, result_label):
        """设置结果标签的高度动画"""
        self.result_label = result_label
        self.result_label_animation = QPropertyAnimation(result_label, b"minimumHeight")
        self.result_label_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.result_label_animation.setDuration(280)
        self.result_label_animation.finished.connect(self._emit_result_label_animation_finished)
    
    def is_animating(self):
        """返回当前是否有动画正在进行"""
        return self.animation_in_progress
    
    def animate_window_resize(self, target_width, target_height):
        """调整窗口大小的动画"""
        current_geo = self.widget.geometry()
        target_geo = QRect(current_geo.x(), current_geo.y(), 
                           target_width, target_height)
        
        return self.animate_window_to_geometry(target_geo)
    
    def animate_window_to_geometry(self, target_rect):
        """窗口动画到指定的目标几何位置和大小"""
        if self.animation_in_progress:
            return False  # 如果动画正在进行，不开始新动画
        
        self.animation_in_progress = True
        current_geo = self.widget.geometry()
        
        self.window_animation.setStartValue(current_geo)
        self.window_animation.setEndValue(target_rect)
        self.window_animation.start()
        
        return True  # 成功开始动画
    
    def animate_result_label_height(self, target_height):
        """结果标签高度动画"""
        if self.result_label_animation is None:
            return False  # 如果动画还未设置，返回失败
        
        # 设置动画的起始值和结束值
        self.result_label_animation.setStartValue(self.result_label.height())
        self.result_label_animation.setEndValue(target_height)
        
        # 开始动画
        self.result_label_animation.start()
        return True
    
    def _emit_window_animation_finished(self):
        """窗口动画完成时发出信号"""
        self.animation_in_progress = False
        self.windowAnimationFinished.emit()
    
    def _emit_result_label_animation_finished(self):
        """结果标签动画完成时发出信号"""
        self.resultLabelAnimationFinished.emit()
