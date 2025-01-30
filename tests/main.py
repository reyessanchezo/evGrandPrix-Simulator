import unittest

from tools.drag_force import aerodynamic_drag_power


class TestDrageForce(unittest.TestCase):
    def test_drag_force(self):
        self.assertEqual(round(aerodynamic_drag_power(100), 4), 0.0075)
        self.assertEqual(round(aerodynamic_drag_power(1000), 4), 7.5416)
        self.assertEqual(round(aerodynamic_drag_power(2500), 4), 117.8376)
        self.assertEqual(round(aerodynamic_drag_power(5000), 4), 942.7008)
        self.assertEqual(round(aerodynamic_drag_power(10000), 4), 7541.6061)
        self.assertEqual(round(aerodynamic_drag_power(50000), 4), 942700.7589)
        self.assertEqual(round(aerodynamic_drag_power(100000), 4), 7541606.0715)


def run():
    unittest.main()


if __name__ == "__main__":
    run()
