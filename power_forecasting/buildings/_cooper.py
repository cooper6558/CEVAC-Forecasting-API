"""
Cooper Library Building file
"""

from power_forecasting.buildings._building import Building


class Cooper(Building):
    """
    Cooper Building class
    """
    def __init__(self):
        """
        Provide Cooper subdirectory within the model directory
        """
        self.building_name: str = "Cooper"
        super().__init__()
