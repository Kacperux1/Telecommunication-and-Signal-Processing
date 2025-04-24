#include "../include/Receiver.h"
#include <chrono>
#include <windows.h>
#include "../include/Transmitter.h"

using namespace std;
using namespace std::chrono;

ByteVector Receiver::receiveFile(int mode) {
    ByteVector receivedData;
    auto startTime = system_clock::now();
    bool hasStarted = false;

    // Czekamy maksymalnie 60 sekund na rozpoczęcie transmisji
    while (system_clock::now() - startTime < seconds(60)) {
        // Wysyłamy odpowiedni znak w zależności od trybu sumy kontrolnej
        if (mode == ALGEBRAIC_CHECKSUM)
            readerWriter->write(ByteVector{NAK});
        else
            readerWriter->write(ByteVector{C});

        try {
            // Jeśli odbieramy SOH, to znaczy że możemy zaczynać
            if (readerWriter->read() == SOH) {
                hasStarted = true;
                break;
            }
        } catch (const ConnectionBrokenError&) {
            // Błąd połączenia – po prostu kontynuujemy
        }

        Sleep(5);
    }

    if (hasStarted) {
        uint8_t controlByte;

        do {
            ByteVector blockData;

            // Odczytujemy 128 bajtów danych bloku
            for (int i = 0; i < 128; ++i) {
                blockData.push_back(readerWriter->read());
            }

            if (mode == ALGEBRAIC_CHECKSUM) {
                uint8_t receivedChecksum = readerWriter->read();

                // Sprawdzamy, czy suma kontrolna się zgadza
                if (algebraicChecksum(blockData) == receivedChecksum) {
                    readerWriter->write(ByteVector{ACK});
                    receivedData.insert(receivedData.end(), blockData.begin(), blockData.end());
                } else {
                    readerWriter->write(ByteVector{NAK});
                }
            } else {
                // W trybie CRC odczytujemy 2 bajty sumy
                ByteVector receivedCrc{readerWriter->read(), readerWriter->read()};
                ByteVector calculatedCrc = crc16Checksum(blockData);

                // Sprawdzamy, czy CRC się zgadza
                if (receivedCrc == calculatedCrc) {
                    readerWriter->write(ByteVector{ACK});
                    receivedData.insert(receivedData.end(), blockData.begin(), blockData.end());
                } else {
                    readerWriter->write(ByteVector{NAK});
                }
            }

            // Odczyt kolejnego bajtu kontrolnego (SOH lub EOT)
            controlByte = readerWriter->read();

        } while (controlByte == SOH);

        // Jeśli koniec transmisji (EOT), potwierdzamy odbiór
        if (controlByte == EOT) {
            readerWriter->write(ByteVector{ACK});
        } else {
            throw ConnectionBrokenError("Błąd protokołu!");
        }
    }

    return receivedData;
}
