from attr import dataclass

from YNABClient import YNABClient


@dataclass
class AppContext:
    ynab: YNABClient
