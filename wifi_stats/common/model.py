
"""Data model for connected stations"""

class Station:
    """Station model"""

    mac_address: str
    band: str
    index: int
    data: dict

    def __init__(
        self,
        mac_address: str,
        band: str,
        index: int,
        data: dict,
    ):
        self.mac_address = mac_address
        self.band = band
        self.index = index
        self.data = data
