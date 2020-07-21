"""
Contains the Building base class. This locates the model files.
"""

from occupancy_forecasting import buildings
from typing import Type


class Building:
    """
    Base class for all buildings, that gives the location of the saved models.
    """

    def __init__(self) -> None:
        """
        Initiate a building object storing its model location
        """
        self.name: str = "Building"
        # TODO: this will be default occupancy building, so make sure it exists
        self.occupancy_building: Type[buildings.Building] = buildings.Building
