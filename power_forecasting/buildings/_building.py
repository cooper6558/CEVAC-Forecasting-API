"""
Contains the Building base class. This locates the model files.
"""

# TODO: find a way to input this path string
PATH: str = "/home/cooper/research/models"

class Building:
    """
    Base class for all buildings, that gives the location of the saved models.
    """
    def __init__(self, building_name: str):
        """
        Initiate a building object storing its model location
        :param building_name: specific building name;
            capitalization insensitive
        """
        self.name: str = building_name
        self.path: str = PATH + building_name.lower()
