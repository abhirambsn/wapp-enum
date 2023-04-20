from rich.progress import Progress
from .print import print_error
from .logger import error_log

import threading

class LoaderQueue:
    def __init__(self):
        self.tasks = []
        self.executed = False
    
    def add_task(self, label, fn, args=None, kwargs=None):
        self.tasks.append({
            'label': label,
            'fn': fn,
            'args': args,
            'kwargs': kwargs,
            'retval': None,
            'task_id': None
        })
    
    def threaded(self, progress, task, batch_size, start=0):
        completed = 0
        for i in range(len(self.tasks[start: start + batch_size])):
            progress.update(task, description=self.tasks[start+i]['label'])
            retval = None
            if (self.tasks[i]['args'] is None and self.tasks[start+i]['kwargs'] is not None):
                retval = self.tasks[i]['fn'](**self.tasks[start+i]['kwargs'])
            elif (self.tasks[i]['args'] is not None and self.tasks[start+i]['kwargs'] is None):
                retval = self.tasks[i]['fn'](*self.tasks[start+i]['args'])
            elif (self.tasks[i]['args'] is None and self.tasks[start+i]['kwargs'] is None):
                retval = self.tasks[start+i]['fn']()
            else:
                retval = self.tasks[start+i]['fn'](*self.tasks[i]['args'], **self.tasks[i]['kwargs'])
            self.tasks[i]['retval'] = retval
            completed += 1
            progress.update(task, advance=((start+completed)/len(self.tasks))*100, total=100)

    def execute_threaded(self, initial_label="", n_threads=1):
        try:
            threads = []
            with Progress(transient=True) as progress:
                if len(self.tasks) < n_threads:
                    n_threads = len(self.tasks)
                batch_size = len(self.tasks) // n_threads
                for i in range(n_threads):
                    task = progress.add_task(initial_label + f" Thread: {i+1}", total=None)
                    t = threading.Thread(target=self.threaded, args=(progress, task, batch_size, batch_size*i))
                    threads.append(t)
                
                for t in threads:
                    t.start()
                    t.join()
            self.executed = True
        except Exception as e:
            print_error(f"ERROR: {e}")
            error_log(__name__, str(e))


    def execute(self, initial_label="Starting..."):
        try:
            with Progress(transient=True) as progress:
                task = progress.add_task(initial_label, total=None)
                completed = 0
                for i in range(len(self.tasks)):
                    progress.update(task, description=self.tasks[i]['label'])
                    retval = None
                    if completed > 0:
                        self.tasks[i]['kwargs'].update(self.tasks[i-1]['retval'])
                    if (self.tasks[i]['args'] is None and self.tasks[i]['kwargs'] is not None):
                        retval = self.tasks[i]['fn'](**self.tasks[i]['kwargs'])
                    elif (self.tasks[i]['args'] is not None and self.tasks[i]['kwargs'] is None):
                        retval = self.tasks[i]['fn'](*self.tasks[i]['args'])
                    elif (self.tasks[i]['args'] is None and self.tasks[i]['kwargs'] is None):
                        retval = self.tasks[i]['fn']()
                    else:
                        retval = self.tasks[i]['fn'](*self.tasks[i]['args'], **self.tasks[i]['kwargs'])
                    self.tasks[i]['retval'] = retval
                    completed += 1
                    if completed == len(self.tasks):
                        progress.update(task, completed=True, advance=100)
                    else:
                        progress.update(task, advance=(completed/len(self.tasks))*100)
            self.executed = True
        except Exception as e:
            print_error(f"ERROR: {e}")
            error_log(__name__, str(e))
    
    def get_return_values(self):
        if not self.executed:
            print_error("Not Executed Yet")
            return None
        return [t['retval'] for t in self.tasks]