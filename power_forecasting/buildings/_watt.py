"""
WFIC Building file
"""

from power_forecasting.buildings._building import Building
from occupancy_forecasting import buildings


class Watt(Building):
    """
    Watt Building class
    """

    def __init__(self) -> None:
        """
        Provide Watt subdirectory within the model directory
        """
        super().__init__()
        self.name = "Watt"
        self.occupancy_building = buildings.Watt
