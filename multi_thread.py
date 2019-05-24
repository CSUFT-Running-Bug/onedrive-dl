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

    for thread in threads:
        thread.join()


def process(data):
    print(data)
