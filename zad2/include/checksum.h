#ifndef CHECKSUM_H
#define CHECKSUM_H

#include <iostream>
#include <vector>
#include <cstdint>

using namespace std;

// Typy używane w kodzie
using ByteVector = std::vector<uint8_t>;
using dword = uint32_t;

// Stała reprezentująca wielomian dla kodu CRC-16-CCITT
extern const dword POLY;
extern const uint8_t POLY_LENGTH;

// Funkcje do obliczeń i wypisywania
void printBinary(const ByteVector& bytes);
void printBinary(dword bytes);
uint8_t algebraicChecksum(const ByteVector& bytes);
ByteVector crc16Checksum(const ByteVector& bytes);

#endif // CHECKSUM_H

