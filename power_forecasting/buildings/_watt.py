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
        self.building_name: str = "Watt"
        super().__init__()
