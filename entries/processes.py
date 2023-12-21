from entry import Entry
from processes import Processes as ProcessesUtil


class Processes(Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = ProcessesUtil().number
