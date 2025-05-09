import os
import random
import hashlib
import requests
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from dotenv import load_dotenv

class TranslationService:
    def __init__(self):
        # 百度翻译API参数
        load_dotenv()
        self.app_id = os.getenv("BAIDU_APP_ID")
        self.app_key = os.getenv("BAIDU_APP_KEY")
        self.base_url = "https://fanyi-api.baidu.com/api/trans/vip/translate"

        if not self.app_id or not self.app_key:
            raise ValueError("百度翻译 API 密钥未配置")
        
    def translate(self, text):
        """调用百度翻译API进行翻译"""
        if not text.strip():
            return "请输入要翻译的文本"
        
        # 自动检测源语言
        to_lang = "zh" if self.is_english(text) else "en"
        from_lang = "en" if to_lang == "zh" else "zh"
        
        # 生成随机数和签名
        salt = str(random.randint(32768, 65536))
        sign = self.app_id + text + salt + self.app_key
        sign = hashlib.md5(sign.encode()).hexdigest()
        
        # 构建请求参数
        payload = {
            'appid': self.app_id,
            'q': text,
            'from': from_lang,
            'to': to_lang,
            'salt': salt,
            'sign': sign
        }
        
        try:
            # 发送请求
            response = requests.get(self.base_url, params=payload)
            result = response.json()
            
            # 解析结果
            if 'trans_result' in result:
                return result['trans_result'][0]['dst']
            else:
                error_code = result.get('error_code', '未知错误')
                error_msg = result.get('error_msg', '翻译失败')
                return f"错误 ({error_code}): {error_msg}"
                
        except Exception as e:
            return f"翻译错误: {str(e)}"
    
    def is_english(self, text):
        """简单判断文本是否为英文"""
        # 中文字符范围大致为：\u4e00-\u9fff
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                return False
        return True

    def warm_up(self):
        """
        预热翻译服务，尝试建立一个到翻译API服务器的连接。
        这有助于减少第一次实际翻译时的延迟。
        """
        try:
            # 尝试对基础URL或一个已知的、轻量级的端点进行一次简单的GET请求
            # 我们不需要一个完整的翻译，只是为了初始化网络栈
            # 注意：有些API可能对无效请求返回错误，但连接本身会被建立
            requests.get(self.base_url.split('/api/')[0], timeout=2) # 例如，只请求 https://fanyi-api.baidu.com
            print("Translation service warmed up.") # 调试信息
        except requests.exceptions.RequestException as e:
            # 预热失败是可接受的，例如没有网络连接时
            print(f"Translation service warm-up failed (this is okay if offline): {e}") # 调试信息
        except Exception as e:
            print(f"An unexpected error occurred during warm-up: {e}")


class TranslationWorker(QObject):
    # 定义信号
    translationFinished = pyqtSignal(str)
    # translationWarmedUp = pyqtSignal() # 如果需要，可以添加一个预热完成的信号

    def __init__(self, translation_service):
        super().__init__()
        self.translation_service = translation_service
        self.text_to_translate = ""
        
    @pyqtSlot(str)
    def translate(self, text):
        """在独立线程中执行翻译"""
        self.text_to_translate = text
        if not text.strip():
            self.translationFinished.emit("请输入要翻译的文本")
            return
            
        # 执行翻译
        result = self.translation_service.translate(text)
        
        # 发送信号，传递翻译结果
        self.translationFinished.emit(result)

    @pyqtSlot()
    def warm_up_service(self):
        """在工作线程中执行预热操作"""
        self.translation_service.warm_up()
        # self.translationWarmedUp.emit() # 如果需要，可以发出信号
