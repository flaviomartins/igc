'''
Created on Aug 6, 2011

@author: xhaker
'''

import itertools
from heapq import heappush, heappop


class MaxPq(object):
    '''
    classdocs
    '''

    INVALID = 0     # mark an entry as deleted

    def __init__(self, *args, **kwds):
        '''
        Constructor
        '''
        self.pq = []                         # the priority queue list
        self.counter = itertools.count(1)    # unique sequence count
        self.task_finder = {}                # mapping of tasks to entries

    def push(self, priority, task, count=None):
        priority = -1 * priority
        if count is None:
            count = next(self.counter)
        entry = [priority, count, task]
        self.task_finder[task] = entry
        heappush(self.pq, entry)

    def pop(self):
        while True:
            try:
                priority, count, task = heappop(self.pq)
                try:
                    del self.task_finder[task]
                except KeyError:
                    pass
                if count is not self.INVALID:
                    return task
            except IndexError:
                return None

    def delete(self, task):
        entry = self.task_finder[task]
        entry[1] = self.INVALID

    def reprioritize(self, priority, task):
        entry = self.task_finder[task]
        self.push(priority, task, entry[1])
        entry[1] = self.INVALID

    def get_priority(self, task):
        entry = self.task_finder[task]
        return  entry[0]

    def inc_priority(self, task, increment=1):
        if task not in self.task_finder:
            self.push(increment, task)
        else:
            entry = self.task_finder[task]
            priority = -1 * entry[0] + increment
            self.push(priority, task, entry[1])
            entry[1] = self.INVALID

    def __contains__(self, task):
        return task in self.task_finder

    def __len__(self):
        return len(self.task_finder)
