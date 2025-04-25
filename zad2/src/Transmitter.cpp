#include "../include/Transmitter.h"
#include <cmath>
#include <vector>
#include <cstdint>

using namespace std;
using ByteVector = std::vector<uint8_t>;

// Metoda odpowiadająca za wysyłanie pliku przez port szeregowy
void Transmitter::sendFile(ByteVector data, int checksumMode) {
    // Oczekiwanie na sygnał od odbiornika, zależnie od wybranego trybu sumy kontrolnej
    cout << "Oczekiwanie na gotowosc odbiornika..." << endl;
    if (checksumMode == ALGEBRAIC_CHECKSUM)
        while (readerWriter->read() != NAK);
    else
        while (readerWriter->read() != C);

    // Obliczenie liczby bloków danych (po 128 bajtów)
    int totalBlocks = (int)ceil(data.size() / 128.0);
    cout << "Rozpoczynanie transmisji pliku, liczba bloków: " << totalBlocks << endl;

    for (int blockIdx = 0; blockIdx < totalBlocks; blockIdx++) {
        // Wyodrębnienie aktualnego bloku danych
        ByteVector::iterator blockStart = data.begin() + blockIdx * 128;
        ByteVector::iterator blockEnd = (data.end() - blockStart <= 128)
                                        ? data.end()
                                        : blockStart + 128;

        ByteVector block(blockStart, blockEnd);

        // Uzupełnienie bloku zerami, jeśli jest krótszy niż 128 bajtów
        if (block.size() < 128)
            block.insert(block.end(), 128 - block.size(), 0);

        // Budowanie nagłówka (SOH + numer bloku + jego negacja)
        ByteVector header = {
                SOH,
                (uint8_t)(blockIdx + 1),
                (uint8_t)(255 - (blockIdx + 1))
        };

        // Wysyłanie nagłówka i danych bloku
        cout << "Wysylanie bloku " << blockIdx + 1 << " z " << totalBlocks << "..." << endl;
        readerWriter->write(header);
        readerWriter->write(block);

        // Dodanie sumy kontrolnej zależnie od trybu
        if (checksumMode == ALGEBRAIC_CHECKSUM)
            readerWriter->write(ByteVector({algebraicChecksum(block)}));
        else
            readerWriter->write(crc16Checksum(block));

        // Oczekiwanie na odpowiedź odbiornika
        uint8_t response = readerWriter->read();

        if (response == NAK) {
            // Jeśli suma się nie zgadza – ponów wysyłkę tego bloku
            cout << "Błąd w bloku " << blockIdx + 1 << " – ponawiam wysyłkę..." << endl;
            blockIdx--;
        } else if (response == CAN) {
            throw ConnectionBrokenError("Połączenie anulowane przez odbiornik!");
        } else if (response != ACK) {
            //throw ConnectionBrokenError("Błąd protokołu przy potwierdzeniu bloku!");
        } else {
            cout << "Blok " << blockIdx + 1 << " wyslany pomyslnie!" << endl;
        }
    }

    // Po zakończeniu wysyłania – sygnał EOT
    readerWriter->write(ByteVector({EOT}));
    cout << "Transmisja zakonczona pomyslnie." << endl;
}
