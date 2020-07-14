"""
Cooper Library Building file
"""

from power_forecasting.buildings._building import Building


class Cooper(Building):
    """
    Cooper Building class
    """

    def __init__(self) -> None:
        """
        Provide Cooper subdirectory within the model directory
        """
        super().__init__()
        self.name: str = "Cooper"
        self.path += self.name
