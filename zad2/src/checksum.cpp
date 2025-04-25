#include "../include/checksum.h"
#include <iostream>
#include <vector>
#include <cstdint>

using namespace std;
using ByteVector = std::vector<uint8_t>;

// Sta?a reprezentuj?ca wielomian dla kodu CRC-16-CCITT
const dword POLY = 0x011021;  // Wielomian dla CRC-16-CCITT
const uint8_t POLY_LENGTH = 17;  // D?ugo?? wielomianu CRC w bitach (16 + 1 bit do uwzgl?dnienia)

// Wypisuje wektor bajtów w postaci binarnej
void printBinary(const ByteVector& bytes){
    for(int bitIndex = 0; bitIndex < bytes.size() * 8; bitIndex++){
        int noOfByte = bitIndex / 8;
        int noOfBit = bitIndex % 8;
        bool bit = (bool)(bytes[noOfByte] & (1 << (7 - noOfBit)));  // Sprawdzamy czy dany bit jest 1
        if(bit){
            cout << "1";
        }else{
            cout << "0";
        }
    }
}

// Wypisuje 4-bajtowe s?owo od pierwszego bitu 1
void printBinary(dword bytes){
    bool start = false;  // Flaga, która ?ledzi, czy rozpocz?to wypisywanie bitów
    for(int bitIndex = 0; bitIndex < sizeof(bytes) * 8; bitIndex++){
        bool bit = bytes & (1 << ((sizeof(bytes) * 8) - 1 - bitIndex));  // Sprawdzamy bit
        if(bit){
            cout << "1";
            start = true;
        }else{
            if(start)
                cout << "0";
        }
    }
}

// Funkcja obliczaj?ca sum? algebraiczn? (prosta suma wszystkich bajtów modulo 256)
uint8_t algebraicChecksum(const ByteVector& bytes){
    int sum = 0;
    for(uint8_t addend : bytes){
        sum += addend;
        sum %= 256;  // Dzia?amy w modulo 256, poniewa? suma nie mo?e przekroczy? 255
    }
    return (uint8_t)sum;  // Zwracamy wynik jako 8-bitow? liczb?
}

// Funkcja obliczaj?ca CRC-16-CCITT (zastosowanie w protokole XMODEM)
ByteVector crc16Checksum(const ByteVector& bytes){
    ByteVector a(bytes);  // Tworzymy kopi? wektora z danymi
    a.push_back(0); a.push_back(0);  // Dodajemy dwa bajty wype?niaj?ce na ko?cu (s?u?? do przechowywania sumy CRC)

    // P?tla przechodz?ca przez wszystkie bity danych
    for(int bitIndex = 0; bitIndex < bytes.size() * 8; bitIndex++){
        int noOfByte = bitIndex / 8;  // Indeks bajtu
        int noOfBit = bitIndex % 8;   // Indeks bitu w obr?bie bajtu
        bool bit = (bool)(a[noOfByte] & (1 << (7 - noOfBit)));  // Sprawdzamy, czy dany bit w bajcie jest równy 1

        if(bit){
            dword toXor = POLY << (7 - noOfBit);  // Przygotowujemy wielomian do XOR-owania (przesuni?ty w zale?no?ci od bitu)

            // Wykonujemy operacj? XOR z wielomianem przesuni?tym na odpowiedni? pozycj?
            a[noOfByte] ^= (uint8_t)((toXor >> 16) & 0x0000ff);
            a[noOfByte + 1] ^= (uint8_t)((toXor >> 8) & 0x0000ff);
            a[noOfByte + 2] ^= (uint8_t)((toXor >> 0) & 0x0000ff);
        }
    }

    // Zwracamy dwa ostatnie bajty, które zawieraj? wynik CRC
    return ByteVector(a.end() - 2, a.end());
}

