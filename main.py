import pyvesc


def simple_example():
    # pyvesc.SetDutyCycle
    my_msg = pyvesc.SetDutyCycle(0)

    packet = pyvesc.encode(my_msg)

    buffer = b"\x23\x82\x02" + packet + b"\x38\x23\x12\x01"

    msg, consumed = pyvesc.decode(buffer)

    buffer = buffer[consumed:]

    assert my_msg.duty_cycle == msg.duty_cycle
    print("Success!")


if __name__ == "__main__":
    simple_example()
    print(dir(pyvesc.SetDutyCycle))
