import argparse      # Do obsługi argumentów wiersza poleceń
import time          # Do pomiaru czasu i opóźnień
import os            # Do operacji na plikach
from ctypes import * # Do obsługi WinAPI (funkcji systemowych Windows)
from ctypes.wintypes import * # Typy danych specyficzne dla Windows


# Stałe XMODEM
SOH = 0x01  # Początek pakietu (Start Of Header)
EOT = 0x04  # Koniec transmisji (End Of Transmission)
ACK = 0x06  # Potwierdzenie (Acknowledge)
NAK = 0x15  # Brak potwierdzenia (Negative Acknowledge)
CAN = 0x18  # Anulowanie transmisji (Cancel)
DATA_LENGTH = 128            # Dane w pakiecie XMODEM
PACKET_LENGTH = 132          # SOH + numery + dane + suma
PACKET_LENGTH_CRC = 133      # ...+ 2 bajty CRC

# Stałe WinAPI
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80
INVALID_HANDLE_VALUE = -1
PURGE_RXCLEAR = 0x0001
PURGE_TXCLEAR = 0x0002


class DCB(Structure):
    _fields_ = [
        ("DCBlength", DWORD), ("BaudRate", DWORD), ("fBinary", DWORD),
        ("fParity", DWORD), ("fOutxCtsFlow", DWORD), ("fOutxDsrFlow", DWORD),
        ("fDtrControl", DWORD), ("fDsrSensitivity", DWORD),
        ("fTXContinueOnXoff", DWORD), ("fOutX", DWORD), ("fInX", DWORD),
        ("fErrorChar", DWORD), ("fNull", DWORD), ("fRtsControl", DWORD),
        ("fAbortOnError", DWORD), ("wReserved", WORD), ("XonLim", WORD),
        ("XoffLim", WORD), ("ByteSize", BYTE), ("Parity", BYTE),
        ("StopBits", BYTE), ("XonChar", CHAR), ("XoffChar", CHAR),
        ("ErrorChar", CHAR), ("EofChar", CHAR), ("EvtChar", CHAR),
        ("wReserved1", WORD)
    ]


class COMMTIMEOUTS(Structure):
    _fields_ = [
        ("ReadIntervalTimeout", DWORD), ("ReadTotalTimeoutMultiplier", DWORD),
        ("ReadTotalTimeoutConstant", DWORD), ("WriteTotalTimeoutMultiplier", DWORD),
        ("WriteTotalTimeoutConstant", DWORD)
    ]


def CRC16(data: bytes) -> int:
    crc = 0x0000
    poly = 0x1021
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc


def calculate_checksum(data: bytes, crc_enabled: bool) -> int:
    return CRC16(data) if crc_enabled else sum(data) & 0xFF


class WinSerialPort:
    def __init__(self, port_name):
        self.h_port = windll.kernel32.CreateFileW(
            "\\\\.\\" + port_name,
            GENERIC_READ | GENERIC_WRITE,
            0, None, OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL, None
        )
        if self.h_port == INVALID_HANDLE_VALUE:
            self._raise_error("CreateFileW")
        self._configure_port()

    def _configure_port(self):
        dcb = DCB()
        dcb.DCBlength = sizeof(DCB)
        if not windll.kernel32.GetCommState(self.h_port, byref(dcb)):
            self._raise_error("GetCommState")
        dcb.BaudRate = 9600
        dcb.ByteSize = 8
        dcb.Parity = 0
        dcb.StopBits = 0
        dcb.fDtrControl = 1
        dcb.fRtsControl = 1
        if not windll.kernel32.SetCommState(self.h_port, byref(dcb)):
            self._raise_error("SetCommState")
        timeouts = COMMTIMEOUTS()
        timeouts.ReadIntervalTimeout = 50
        timeouts.ReadTotalTimeoutMultiplier = 10
        timeouts.ReadTotalTimeoutConstant = 3000
        timeouts.WriteTotalTimeoutMultiplier = 10
        timeouts.WriteTotalTimeoutConstant = 1000
        if not windll.kernel32.SetCommTimeouts(self.h_port, byref(timeouts)):
            self._raise_error("SetCommTimeouts")

    def _raise_error(self, func_name):
        code = windll.kernel32.GetLastError()
        raise WindowsError(f"{func_name} error: {code}")

    def purge(self):
        windll.kernel32.PurgeComm(self.h_port, PURGE_RXCLEAR | PURGE_TXCLEAR)

    def read(self, size):
        buf = create_string_buffer(size)
        read = DWORD()
        windll.kernel32.ReadFile(self.h_port, buf, size, byref(read), None)
        return buf.raw[:read.value]

    def read_one(self):
        data = self.read(1)
        return data if data else None

    def write(self, data: bytes) -> int:
        written = DWORD()
        buf = (c_ubyte * len(data)).from_buffer_copy(data)
        windll.kernel32.WriteFile(self.h_port, buf, len(data), byref(written), None)
        return written.value

    def close(self):
        windll.kernel32.CloseHandle(self.h_port)


class XmodemSender:
    def __init__(self, port, crc_enabled=False):
        self.port = port
        self.crc_enabled = crc_enabled
        self.packet_length = PACKET_LENGTH_CRC if crc_enabled else PACKET_LENGTH
        self.max_retries = 10

    def send_file(self, filename):
        self.port.purge()
        start = time.time()
        while True:
            if time.time() - start > 60:
                print("Timeout: brak odpowiedzi")
                return False
            init = self.port.read_one()
            if not init: continue
            if init[0] == NAK:
                self.crc_enabled = False
                print("CRC disabled")
                break
            if init[0] == ord('C'):
                self.crc_enabled = True
                print("CRC enabled")
                break
            if init[0] == CAN:
                print("Odebrano CAN, przerywam")
                return False

        filesize = os.path.getsize(filename)
        print(f"Wysyłanie pliku ({filesize} bajtów)")
        seq = 1

        with open(filename, 'rb') as f:
            while True:
                chunk = f.read(DATA_LENGTH)
                if not chunk:
                    break

                if len(chunk) < DATA_LENGTH:
                    chunk += b'\x1a' * (DATA_LENGTH - len(chunk))

                packet = bytearray([SOH, seq, 0xFF - seq]) + chunk
                csum = calculate_checksum(chunk, self.crc_enabled)

                if self.crc_enabled:
                    packet += bytes([(csum >> 8) & 0xFF, csum & 0xFF])
                else:
                    packet.append(csum)

                retries = 0
                ack_received = False

                while retries < self.max_retries and not ack_received:
                    print(f"Wysyłanie bloku {seq} (próba {retries + 1})")
                    self.port.write(packet)
                    resp = self.port.read_one()

                    if resp:
                        if resp[0] == ACK:
                            ack_received = True
                        elif resp[0] == CAN:
                            print("Odebrano CAN, przerywam")
                            return False
                    retries += 1 if not ack_received else 0

                if not ack_received:
                    self.port.write(bytes([CAN, CAN]))
                    print("Błąd: Przekroczono limit prób")
                    return False
                seq = (seq + 1) % 256

        eot_ack = False
        retries = 0
        while retries < self.max_retries and not eot_ack:
            print("Wysyłanie EOT...")
            self.port.write(bytes([EOT]))
            resp = self.port.read_one()
            if resp and resp[0] == ACK:
                eot_ack = True
            elif resp and resp[0] == CAN:
                print("Odebrano CAN, przerywam")
                return False
            else:
                retries += 1

        return eot_ack


class XmodemReceiver:
    def __init__(self, port, crc_enabled=False):
        self.port = port
        self.crc_enabled = crc_enabled
        self.packet_length = PACKET_LENGTH_CRC if crc_enabled else PACKET_LENGTH
        self.max_retries = 10

    def receive_file(self, filename):
        init_char = b'C' if self.crc_enabled else bytes([NAK])
        start_time = time.time()
        response = None

        while time.time() - start_time < 60:
            print(f"Wysyłanie inicjatora: {init_char}")
            self.port.write(init_char)
            retry_start = time.time()

            while time.time() - retry_start < 10:
                data = self.port.read_one()
                if data:
                    if data[0] in [SOH, EOT]:
                        response = data[0]
                        break
                    elif data[0] == CAN:
                        print("Odebrano CAN, przerywam")
                        return False
            if response:
                break
            print("Brak odpowiedzi, ponawiam inicjację...")
        else:
            print("Brak odpowiedzi po 60 sekundach")
            return False

        with open(filename, 'wb') as f:
            expected_seq = 1
            retries = 0

            while True:
                header = self.port.read_one()
                if not header:
                    retries += 1
                    if retries >= self.max_retries:
                        self.port.write(bytes([CAN, CAN]))
                        print("Przekroczono limit prób")
                        return False
                    continue

                if header[0] == CAN:
                    print("Transmisja przerwana przez nadawcę")
                    return False

                if header[0] == EOT:
                    print("Odebrano EOT")
                    self.port.write(bytes([ACK]))
                    break

                if header[0] != SOH:
                    continue

                packet = bytearray(header)
                while len(packet) < self.packet_length:
                    chunk = self.port.read(self.packet_length - len(packet))
                    if chunk:
                        packet.extend(chunk)
                    else:
                        retries += 1
                        if retries >= self.max_retries:
                            self.port.write(bytes([CAN, CAN]))
                            print("Przekroczono limit prób")
                            return False
                        break

                if len(packet) < self.packet_length:
                    continue

                block_num = packet[1]
                block_inv = packet[2]
                data = packet[3:131]

                if block_inv != (0xFF - block_num) or block_num != expected_seq:
                    print(f"Błędny numer bloku: {block_num}, oczekiwano: {expected_seq}")
                    self.port.write(bytes([NAK]))
                    continue

                if self.crc_enabled:
                    received_crc = (packet[131] << 8) | packet[132]
                    calculated_crc = CRC16(data)
                    valid = (received_crc == calculated_crc)
                else:
                    received_checksum = packet[131]
                    calculated_checksum = sum(data) & 0xFF
                    valid = (received_checksum == calculated_checksum)

                if valid:
                    trimmed_data = data.rstrip(b'\x1a')
                    f.write(trimmed_data)
                    self.port.write(bytes([ACK]))
                    expected_seq = (expected_seq + 1) % 256
                    retries = 0
                else:
                    print("Błędna suma kontrolna")
                    retries += 1
                    if retries >= self.max_retries:
                        self.port.write(bytes([CAN, CAN]))
                        print("Przekroczono limit prób")
                        return False
                    self.port.write(bytes([NAK]))

        return True


def main():
    parser = argparse.ArgumentParser(description='XMODEM Transfer')
    parser.add_argument('port', help='COM port (e.g. COM1)')
    parser.add_argument('mode', type=int, choices=[1, 2], help='1=Sender, 2=Receiver')
    parser.add_argument('--crc', action='store_true', help='Enable CRC16')
    args = parser.parse_args()

    try:
        port = WinSerialPort(args.port)
    except Exception as e:
        print(f"Błąd portu: {e}")
        return

    if args.mode == 1:
        sender = XmodemSender(port, args.crc)
        result = sender.send_file('message.png')
    else:
        receiver = XmodemReceiver(port, args.crc)
        result = receiver.receive_file('received.png')

    port.close()
    print("Sukces" if result else "Błąd")


if __name__ == '__main__':
    main()