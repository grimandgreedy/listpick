#!/bin/python
# -*- coding: utf-8 -*-
"""
generate_data_utils.py

Author: GrimAndGreedy
License: MIT
"""

def sort_priority_first(element):
    return element[0]

class ProcessSafePriorityQueue:
    def __init__(self, manager):
        self.data = manager.list()
        self.lock = manager.Lock()

    def put(self, item):
        with self.lock:
            self.data.append(item)
            self.data.sort(key=sort_priority_first)

    def get(self, timeout=None):
        start = time.time()
        while True:
            with self.lock:
                if self.data:
                    return self.data.pop(0)
            if timeout is not None and (time.time() - start) > timeout:
                raise IndexError("get timeout")
            time.sleep(0.01)

    def qsize(self):
        with self.lock:
            return len(self.data)

    def empty(self):
        with self.lock:
            return len(self.data) == 0

    def clear(self):
        with self.lock:
            self.data[:] = []
