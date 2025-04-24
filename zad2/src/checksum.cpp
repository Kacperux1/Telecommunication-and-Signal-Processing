#include "../include/checksum.h"
#include <iostream>
#include <vector>
#include <cstdint>

using namespace std;
typedef std::vector<uint8_t> ByteVector;

//stala reprezentujaca wielomian dla kodu CRC-16-CCITT
const dword POLY = 0x011021;
const uint8_t POLY_LENGTH = 17;

//oblicza sume algebraiczna ("podstawowa sume kontrolna")
uint8_t algebraicChecksum(const ByteVector& bytes){
	int sum = 0;
	for(uint8_t addend : bytes){
		sum += addend;
		sum %= 256;
	}
	return (uint8_t)sum;
}

//oblicza CRC-16-CCITT (wykorzystywane w XMODEM)
ByteVector crc16Checksum(const ByteVector& bytes){
    ByteVector a(bytes);
    a.push_back(0); a.push_back(0);

    for(int bitIndex = 0; bitIndex < bytes.size() * 8 - POLY_LENGTH; bitIndex++){
        int noOfByte = bitIndex / 8;
        int noOfBit = bitIndex % 8;
        bool bit = (bool)(a[noOfByte] & (1 << (7 - noOfBit)));
        if(bit){
            dword toXor = POLY << (7 - noOfBit);
            a[noOfByte] ^= (uint8_t)((toXor >> 16) & 0x0000ff);
            a[noOfByte + 1] ^= (uint8_t)((toXor >> 8) & 0x0000ff);
            a[noOfByte + 2] ^= (uint8_t)((toXor >> 0) & 0x0000ff);
        }
    }
    return ByteVector(a.end() - 2, a.end());
}
