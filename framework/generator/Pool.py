from typing import List, Set, Dict, Tuple, Optional

from driver import Driver

class Pool:
    pool_size: int
    pool: List[Driver]

    def __init__(self, pool_size):
        self.pool_size = pool_size
        self.pool = []

    def add_driver(self, driver: Driver):
        if len(self.pool) >= self.pool_size:
            return

        self.pool.append(driver)

    def empty(self):
        return len(self.pool) == 0

    def full(self):
        return len(self.pool) >= self.pool_size

    def __iter__(self):
        for v in self.pool:
            yield v

    def pop(self):
        return self.pool.pop()

    def __len__(self):
        return len(self.pool)
