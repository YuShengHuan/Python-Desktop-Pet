from PySide6.QtCore import Signal, QObject
from pynput import keyboard


class HotkeyWorker(QObject):
    # 定义信号：用于通知主线程执行UI操作（解决线程安全问题）
    trigger_screenshot = Signal()  # 对应 Ctrl+Shift+A 的UI操作
    trigger_quit = Signal()        # 对应 Ctrl+Shift+Q 的退出操作

    def register_system_global_shortcuts(self):
        # 回调函数：仅发射信号，不直接操作UI
        def on_ctrl_shift_a():
            print("系统级全局快捷键 Ctrl+Shift+A 触发！（应用后台也生效）")
            self.trigger_screenshot.emit()  # 发射信号，让主线程执行UI逻辑

        def on_ctrl_shift_Q():
            print("系统级全局快捷键 Ctrl+Shift+Q 触发：退出应用！")
            self.trigger_quit.emit()  # 发射信号，让主线程执行退出逻辑

        # 创建全局快捷键监听器
        hotkey_listener = keyboard.GlobalHotKeys({
            '<ctrl>+<shift>+a': on_ctrl_shift_a,
            '<ctrl>+<shift>+q': on_ctrl_shift_Q
        })
        hotkey_listener.run()  # 阻塞运行监听器（正常需求，快捷键持续监听）
        print("全局注册初始化成功......")