"""
ASC Building file
"""

from power_forecasting.buildings._building import Building


class ASC(Building):
    """
    ASC Building class
    """

    def __init__(self) -> None:
        """
        Provide ASC subdirectory within the model directory
        """
        super().__init__()
        self.name: str = "ASC"
        self.path += self.name
