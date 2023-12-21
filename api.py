import json
from datetime import datetime
from typing import Sequence

from _version import __version__
from distributions import Distributions
from entry import Entry
from utility import Utility

class API:

    def __init__(self, entries: Sequence[Entry]):
        self.entries = entries

    def json_serialization(self, indent: int = 0) -> str:
        document = {
            "data": {entry.name: entry.value for entry in self.entries},
            "meta": {
                "version": Utility.version_to_semver_segments(__version__),
                "date": datetime.now().isoformat(),
                "count": len(self.entries),
                "distro": Distributions.get_local().value,
            },
        }

        return json.dumps(document, indent=((indent * 2) or None))
