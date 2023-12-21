import getpass

from entry import Entry

class User(Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.value = getpass.getuser()
        except ImportError:
            pass
