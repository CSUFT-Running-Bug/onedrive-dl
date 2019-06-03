# coding=utf-8
import threading

exit_flag = 0
lock = threading.Lock()


class MyThread(threading.Thread):
    def __init__(self, name, q, target):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.target = target

    def run(self):
        # print("开启线程：" + self.name)
        while not exit_flag:
            # 加锁，防止get()阻塞线程
            lock.acquire()
            data = None
            if not self.q.empty():
                data = self.q.get()
            lock.release()
            if data is not None:
                self.target(data)
        # print("退出线程：" + self.name)


def start(thread_num, work_queue, target):
    threads = []
    for i in range(thread_num):
        name = 'thread-' + str(i)
        thread = MyThread(name, work_queue, target)
        thread.setDaemon(True)
        thread.start()
        threads.append(thread)

    while not work_queue.empty():
        pass

    global exit_flag
    exit_flag = 1
    # 当生产队列为空后（剩余几个消费线程没完全运行完），再join主线程，无法用CTRL-C中断，只能等待子线程执行完
    # 下载98%-99%的时候无法使用CTRL-C中断程序
    for thread in threads:
        thread.join()


def process(data):
    print(data)
