import unittest

from tools import acceleration_torque


# TODO: Need to figure out new tests for dvdt
class TestAccellerationTorqueFunc(unittest.TestCase):
    def test_accelleration_torqueAt20(self):
        input_rpm = 20
        expected_break_power = 108.213152
        dvdt = 10
        break_power = acceleration_torque(input_rpm, dvdt)
        break_power = round(break_power, 6)
        self.assertEqual(break_power, expected_break_power)

    def test_accelleration_torqueAt10(self):
        input_rpm = 10
        expected_break_power = 34.403288
        break_power = acceleration_torque(input_rpm)
        break_power = round(break_power, 6)
        self.assertEqual(break_power, expected_break_power)

    def test_accelleration_torqueAt1(self):
        input_rpm = 1
        expected_break_power = 10.046032
        break_power = acceleration_torque(input_rpm)
        break_power = round(break_power, 6)
        self.assertEqual(break_power, expected_break_power)

    def test_accelleration_torqueAtNeg1(self):
        input_rpm = -1
        expected_break_power = 10.046032
        break_power = acceleration_torque(input_rpm)
        break_power = round(break_power, 6)
        self.assertEqual(break_power, expected_break_power)

    def test_accelleration_torqueAtNeg10(self):
        input_rpm = -10
        expected_break_power = 34.403288
        break_power = acceleration_torque(input_rpm)
        break_power = round(break_power, 6)
        self.assertEqual(break_power, expected_break_power)

    def test_accelleration_torqueAtNeg20(self):
        input_rpm = -20
        expected_break_power = 108.213152
        break_power = acceleration_torque(input_rpm)
        break_power = round(break_power, 6)
        self.assertEqual(break_power, expected_break_power)

    def test_accelleration_torqueWONumClass(self):
        input_rpm = 20
        expected_break_power = 108.213152
        break_power = acceleration_torque(input_rpm)
        break_power = round(break_power, 6)
        self.assertEqual(break_power, expected_break_power)


def run():
    unittest.main()


if __name__ == "__main__":
    run()
