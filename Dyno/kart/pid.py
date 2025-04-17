from .tools import scale


class PIDController:
    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        min_output: float,
        max_output: float,
        max_rpm: float,
        dt: float = 0.1,
    ):
        """
        Initialize PID controller.

        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            min_output: Minimum output value (lower bound)
            max_output: Maximum output value (upper bound)
            dt: Time step for integral and derivative calculations (seconds)
        """
        self.kp: float = kp
        self.ki: float = ki
        self.kd: float = kd
        self.min_output: float = min_output
        self.max_output: float = max_output
        self.dt: float = dt
        self.max_rpm: float = max_rpm

        # PID terms
        self.error_sum: float = 0.0
        self.last_error: float = 0.0

    def reset(self):
        """Reset the controller state."""
        self.error_sum = 0.0
        self.last_error = 0.0

    def compute(self, setpoint: float, current_value: float):
        """
        Compute control output based on setpoint and current value.

        Args:
            setpoint: Target RPM
            current_value: Current actual RPM

        Returns:
            Control output (voltage) within the specified range
        """
        # Compute error
        error = setpoint - current_value

        # Proportional term
        p_term = self.kp * error

        # Integral term
        self.error_sum += error * self.dt
        i_term = self.ki * self.error_sum

        # Derivative term
        d_term = self.kd * (error - self.last_error) / self.dt
        self.last_error = error

        # Calculate total output
        output = p_term + i_term + d_term

        # TODO: map out result to voltage from 0 to 5
        output = scale(output, self.min_output, self.max_output, 0, 1000.0)

        return output


# Example usage
def demo_rpm_to_voltage_control(target_rpm: float, simulation_steps: int = 100):
    """
    Demonstrate PID control for RPM to voltage conversion.

    Args:
        target_rpm: Target RPM value
        simulation_steps: Number of simulation steps
    """
    kp = 0.01  # Proportional gain
    ki = 0.005  # Integral gain
    kd = 0.002  # Derivative gain
    min_voltage = 0.0  # Minimum voltage output
    max_voltage = 24.0  # Maximum voltage output

    pid = PIDController(kp, ki, kd, min_voltage, max_voltage, 10000)

    # Simulate a simple motor model (for demonstration)
    # In a real application, you would get this from actual sensor readings
    current_rpm = 0.0
    voltage = 0.0

    # Simple motor model parameters
    motor_constant = 10.0  # RPM per volt
    motor_friction = 0.1  # RPM loss per time step

    print("Step\tRPM Setpoint\tCurrent RPM\tVoltage")
    print("-" * 60)

    for step in range(simulation_steps):
        voltage = pid.compute(target_rpm, current_rpm)

        current_rpm = (
            current_rpm * (1 - motor_friction) + voltage * motor_constant * pid.dt
        )

        if step % 10 == 0 or step == simulation_steps - 1:
            print(f"{step}\t{target_rpm:.1f}\t\t{current_rpm:.1f}\t\t{voltage:.2f}")

    return voltage, current_rpm


if __name__ == "__main__":
    target_rpm = 1500.0
    final_voltage, final_rpm = demo_rpm_to_voltage_control(target_rpm)
    print(f"\nFinal results:")
    print(f"Target RPM: {target_rpm}")
    print(f"Achieved RPM: {final_rpm:.1f}")
    print(f"Applied voltage: {final_voltage:.2f} V")
