"""
WFIC Building file
"""

from power_forecasting.buildings._building import Building


class Watt(Building):
    """
    Watt Building class
    """

    def __init__(self):
        """
        Provide Watt subdirectory within the model directory
        """
        super().__init__()
        self.name: str = "Watt"
        self.path += self.name
