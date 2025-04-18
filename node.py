from threading import Thread,Event
import random
maxlen = 30
class Naver(Thread):
    def __init__(self,dir, listname):
        Thread.__init__(self)
        self.stop = Event()
        self.i = 0
        self.j = 1
        self.path_list = list(range(maxlen))
        self.log = []

    def run(self):
        while not self.stop.is_set():
            if self.j >= len(self.path_list):
                # print("Path executed !")
                self.log.append("Path executed !")
                break
            # print(f"Moving from {self.path_list[self.i]} to {self.path_list[self.j]}")
            self.log.append(f"Moving from {self.path_list[self.i]} to {self.path_list[self.j]}")
            
            self.i += 1
            self.j += 1
            self.stop.wait(1)
        # print("Stop signal detected !!")
        self.log.append("Stop signal detected !!")