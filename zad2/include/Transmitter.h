#ifndef TRANSMITTER_H
#define TRANSMITTER_H

#include <vector>
#include <cstdint>
#include <memory>
#include "ReaderWriter.h"
#include "../include/checksum.h"

// Alias na typ bajtowego wektora
using ByteVector = std::vector<uint8_t>;

// Stałe Xmodem
constexpr uint8_t SOH = 0x01;
constexpr uint8_t EOT = 0x04;
constexpr uint8_t ACK = 0x06;
constexpr uint8_t NAK = 0x15;
constexpr uint8_t CAN = 0x18;
constexpr uint8_t C   = 0x43;

// Tryby nadawania
constexpr int ALGEBRAIC_CHECKSUM = 0;
constexpr int CRC_CHECKSUM = 1;

class Transmitter {
private:
    std::unique_ptr<ReaderWriter> readerWriter;

public:
    Transmitter(std::unique_ptr<ReaderWriter> rw) : readerWriter(std::move(rw)) {}

    // Główna metoda nadawania pliku
    void sendFile(ByteVector data, int mode);
};

#endif // TRANSMITTER_H

