from PyQt5.QtCore import QRunnable, pyqtSlot
import asyncio
import time
class Worker(QRunnable):

    def __init__(self, fn,fn2,loop: asyncio.AbstractEventLoop,*args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.fn2=fn2
        self.loop=loop
        self.args = args
        self.kwargs = kwargs
        self.stopCondition=False


    @pyqtSlot()
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.fn(self.fn2))

        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()


    def stop(self):
        try:
            self.loop.stop()
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
