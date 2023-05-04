import threading


class TimerThread(threading.Thread):
    def __init__(self, interval, command):
        threading.Thread.__init__(self)
        self.interval = interval
        self.command = command
        self.stop_event = threading.Event()

    def run(self):
        while not self.stop_event.wait(self.interval):
            self.command()

    def stop(self):
        self.stop_event.set()
