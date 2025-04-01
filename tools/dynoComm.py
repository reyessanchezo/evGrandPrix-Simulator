import can
import usb

dev = usb.core.find(idVendor=0x1D50, idProduct=0x606F)


class Listen(can.Listener):
    def on_message_received(self, msg) -> None:
        # print(f"Received: {msg}")
        pass


def send_one():
    with can.Bus(interface="gs_usb", channel=0, bitrate=250000) as bus:
        listener = Listen()
        notifier = can.Notifier(bus, [listener])

        try:
            while True:
                num = int(input("Number: "))
                data = bytearray([num])
                msg = can.Message(
                    arbitration_id=100,
                    data=data,
                    is_extended_id=False,
                    check=True,
                )
                bus.send(msg)
                print(f"{bus.channel_info}: {msg}")
        except can.CanError:
            print("Message NOT sent")
        except KeyboardInterrupt:
            notifier.stop()

def dynoSwitch(commQ):
    with can.Bus(interface="gs_usb", channel=0, bitrate=250000) as bus:
        listener = Listen()
        notifier = can.Notifier(bus, [listener])

        try:
            while True:
                num = int(commQ.get(block=True, timeout=None))
                data = bytearray([num])
                msg = can.Message(
                    arbitration_id=100,
                    data=data,
                    is_extended_id=False,
                    check=True,
                )
                bus.send(msg)
                #print(f"{bus.channel_info}: {msg}")
        except can.CanError:
            print("Message NOT sent")
        except KeyboardInterrupt:
            notifier.stop()

def dynoMode(mode, commQ):
    commQ.put(mode)

if __name__ == "__main__":
    send_one()