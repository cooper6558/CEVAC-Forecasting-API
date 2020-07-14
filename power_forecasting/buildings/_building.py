"""
Contains the Building base class. This locates the model files.
"""

# TODO: find a way to input this path string
PATH: str = "/home/cooper/research/models/"

class Building:
    """
    Base class for all buildings, that gives the location of the saved models.
    """
    def __init__(self) -> None:
        """
        Initiate a building object storing its model location
        """
        self.building_name: str
        self.name: str = self.building_name
        self.path: str = PATH + self.building_name.lower()