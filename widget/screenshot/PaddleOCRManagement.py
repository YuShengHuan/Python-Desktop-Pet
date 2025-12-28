# env/Lib/site-packages/paddlex/utils/cache.py
# 修改DEFAULT_CACHE_DIR 模型下载路径
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from paddleocr import PaddleOCR
import time


class PaddleOCRManagement(QObject):
    # 定义信号：模型初始化完成信号（可选）、识别完成信号
    model_init_finished = Signal()  # 模型加载完成后发射

    predict_init_finished = Signal()  # 识别完成后发射（你定义的信号）
    predict_finished = Signal(int,list)  # 识别完成后发射（你定义的信号）

    def __init__(self, parent=None):
        super().__init__(parent)

        self.ocr = None  # OCR模型实例
        self.time_out_wait = 5000  # 最大等待时间（ms）
        self.thread_init_model = None  # 模型初始化子线程
        self.thread_predict = None

        # 初始化时自动启动子线程加载模型（无需手动调用）
        self.start_model_init_thread()

    def start_model_init_thread(self):
        """创建子线程，并将模型初始化任务移到子线程执行（核心方法）"""
        # 1. 创建子线程实例
        self.thread_init_model = QThread()
        # 2. 将当前对象（PaddleOCRManagement）移动到子线程？不！
        self.moveToThread(self.thread_init_model)

        # 3. 信号绑定：线程启动后，自动执行 init_model 方法
        self.thread_init_model.started.connect(self.init_model)
        # 4. 信号绑定：模型初始化完成后，发射信号 + 退出线程
        self.model_init_finished.connect(self.thread_init_model.quit)
        # 5. 信号绑定：线程退出后，释放线程资源
        self.thread_init_model.finished.connect(self.thread_init_model.deleteLater)

        # 6. 启动子线程（此时会自动触发 started 信号，执行 init_model）
        self.thread_init_model.start()

    def init_model(self):
        """模型初始化方法（在子线程中执行，不阻塞主线程）"""
        print("子线程开始加载 PaddleOCR 模型...")
        # 耗时操作：加载 OCR 模型
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang='ch',
            det_limit_side_len=2000,  # 检测最大边长，适配大图片
            det_limit_type='max'  # 按最大边限制尺寸
        )
        # 发射模型初始化完成信号
        self.model_init_finished.emit()

    def wait_for_model_ready(self):
        """安全等待模型加载完成（带超时判断，不阻塞主线程？若在主线程调用，用循环+延时；若在子线程调用，可直接等待）"""
        start_time = time.time()  # 记录开始等待时间
        while not self.ocr:
            # 计算已等待时间（ms）
            elapsed_time = (time.time() - start_time) * 1000
            # 若超过最大等待时间，跳出循环
            if elapsed_time >= self.time_out_wait:
                print(f"模型加载超时（{self.time_out_wait}ms）！")
                return False
            # 短暂延时，避免死循环占用CPU
            time.sleep(0.1)
        return True

    def start_predict(self, image_):
        # 1. 创建子线程实例
        self.thread_predict = QThread()
        # 2. 将当前对象（PaddleOCRManagement）移动到子线程？不！
        self.moveToThread(self.thread_predict)

        # 3. 信号绑定：线程启动后，自动执行 init_model 方法
        self.thread_predict.started.connect(lambda image_=image_: self.predict(image_))
        # 4. 信号绑定：模型初始化完成后，发射信号 + 退出线程
        self.predict_init_finished.connect(self.thread_predict.quit)
        # 5. 信号绑定：线程退出后，释放线程资源
        self.thread_predict.finished.connect(self.thread_predict.deleteLater)

        # 6. 启动子线程（此时会自动触发 started 信号，执行 init_model）
        self.thread_predict.start()

    def predict(self, image_):
        """执行OCR识别（会等待模型加载完成，带超时处理）"""
        # 1. 等待模型加载完成（带超时）
        if not self.wait_for_model_ready():
            self.predict_finished.emit(-1, [])  # 识别失败，发射信号
        # 2. 模型已就绪，执行识别
        try:
            rec_texts = self.ocr.ocr(image_)[0]["rec_texts"]
            self.predict_finished.emit(0, rec_texts)  # 0 表示识别成功
        except Exception as e:
            print(f"OCR识别失败：{e}")
            self.predict_finished.emit(-2, [])  # -2 表示识别异常
        finally:
            self.predict_init_finished.emit()
