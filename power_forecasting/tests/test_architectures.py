"""
Unittests for architectures
"""

import unittest


class LSTM(unittest.TestCase):
    import power_forecasting.architectures._lstm as lstm
    def setUp(self) -> None:
        self.model = self.lstm.LSTM(
            "watt", "/home/cooper/research/models/watt"
        )

    def test_model(self):
        print(self.model.model.summary())
        self.assertEqual(True, True)


class Architecture(unittest.TestCase):
    import power_forecasting.architectures._architecture as architecture
    def test_another(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
