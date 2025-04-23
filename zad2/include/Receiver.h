#ifndef RECEIVER_H
#define RECEIVER_H

#include <vector>
#include <memory>
#include <cstdint>
#include "ReaderWriter.h"
#include "../include/checksum.h"

// Alias typu
using ByteVector = std::vector<uint8_t>;

class Receiver {
private:
    std::unique_ptr<ReaderWriter> readerWriter;

public:
    // Konstruktor z przekazaniem readera
    Receiver(std::unique_ptr<ReaderWriter> rw) : readerWriter(std::move(rw)) {}

    // Główna funkcja odbioru pliku
    ByteVector receiveFile(int mode);
};

#endif // RECEIVER_H

