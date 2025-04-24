#include "../include/Transmitter.h"
#include <cmath>
#include <vector>
#include <cstdint>

using namespace std;
using ByteVector = std::vector<uint8_t>;

void Transmitter::sendFile(ByteVector inputData, int checksumMode) {

    // Czekamy na sygnał od odbiornika: NAK (dla sumy) lub 'C' (dla CRC)
    uint8_t syncChar = (checksumMode == ALGEBRAIC_CHECKSUM) ? NAK : C;
    while (readerWriter->read() != syncChar);

    // Dzielimy dane na bloki po 128 bajtów
    int totalBlocks = static_cast<int>(ceil(inputData.size() / 128.0));

    for (int i = 0; i < totalBlocks; ++i) {

        auto blockStart = inputData.begin() + i * 128;
        auto blockEnd = (inputData.end() - blockStart <= 128) ? inputData.end() : blockStart + 128;

        ByteVector chunk(blockStart, blockEnd);

        // Uzupełniamy blok zerami, jeśli krótszy niż 128
        if (chunk.size() < 128) {
            chunk.resize(128, 0x00);
        }

        // Nagłówek: SOH, numer bloku, jego uzupełnienie do 255
        ByteVector header = {
                SOH,
                static_cast<uint8_t>(i + 1),
                static_cast<uint8_t>(255 - (i + 1))
        };

        // Wysyłanie nagłówka, bloku i sumy kontrolnej
        readerWriter->write(header);
        readerWriter->write(chunk);

        if (checksumMode == ALGEBRAIC_CHECKSUM) {
            readerWriter->write(ByteVector{algebraicChecksum(chunk)});
        } else {
            ByteVector crc = crc16Checksum(chunk);
            readerWriter->write(crc);
        }

        // Czekamy na odpowiedź: ACK, NAK lub CAN
        uint8_t reply = readerWriter->read();

        if (reply == ACK) {
            // OK, przechodzimy dalej
            continue;
        } else if (reply == NAK) {
            // Błąd - ponawiamy ten sam blok
            --i;
        } else if (reply == CAN) {
            throw ConnectionBrokenError("Przerwane połączenie!");
        } else {
            throw ConnectionBrokenError(" Błąd protokołu.");
        }
    }

    // Po wysłaniu wszystkich bloków - koniec transmisji
    readerWriter->write(ByteVector{EOT});
}
