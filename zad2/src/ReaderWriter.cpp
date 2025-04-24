#include <iostream>
#include "../include/ReaderWriter.h"
using namespace std;

// Konstruktor klasy ReaderWriter – tutaj otwieramy port COM i konfigurujemy go
ReaderWriter::ReaderWriter(string portName) {
    // Tworzymy nazwę portu zgodną z wymaganiami Windows API, np. "\\\\.\\COM2"
    com = CreateFile(
            ("\\\\.\\" + portName).c_str(),  // pełna ścieżka portu
            GENERIC_READ | GENERIC_WRITE,   // chcemy mieć możliwość odczytu i zapisu
            0,                              // port nie może być współdzielony
            NULL,                           // brak zabezpieczeń
            OPEN_EXISTING,                  // otwieramy istniejący port
            0,                              // brak specjalnych flag
            NULL                            // brak szablonu
    );

    // Błąd otwarcia portu
    if (com == INVALID_HANDLE_VALUE)
        throw OpeningPortError("Nie można otworzyć portu: " + portName);

    // Konfiguracja parametrów połączenia
    DCB dcbSerialParams = { 0 };
    GetCommState(com, &dcbSerialParams);
    dcbSerialParams.DCBlength = sizeof(dcbSerialParams);
    dcbSerialParams.BaudRate = CBR_9600;      // 9600 bps
    dcbSerialParams.ByteSize = 8;             // 8 bitów danych
    dcbSerialParams.StopBits = ONESTOPBIT;    // 1 bit stopu
    dcbSerialParams.Parity = NOPARITY;        // brak parzystości
    SetCommState(com, &dcbSerialParams);

    // Ustawienie timeoutów – maksymalny czas oczekiwania na operacje
    COMMTIMEOUTS timeouts = { 0 };
    timeouts.ReadIntervalTimeout = 5000;         // max odstęp między bajtami
    timeouts.ReadTotalTimeoutConstant = 5000;    // max całkowity czas oczekiwania
    timeouts.ReadTotalTimeoutMultiplier = 10;    // czas zależny od ilości bajtów
    timeouts.WriteTotalTimeoutConstant = 50;     // stały czas zapisu
    timeouts.WriteTotalTimeoutMultiplier = 10;   // mnożnik dla zapisu
    SetCommTimeouts(com, &timeouts);
}

// Funkcja do wysyłania danych przez port – zapisuje cały wektor bajtów
void ReaderWriter::write(const ByteVector& bytes) {
    DWORD noOfBytesWritten = 0;
    WriteFile(
            com,
            bytes.data(),             // dane do wysłania
            bytes.size(),             // ilość bajtów
            &noOfBytesWritten,        // ile rzeczywiście wysłano
            NULL
    );

    // Jeśli nie udało się wysłać wszystkiego – sygnalizujemy błąd
    if (noOfBytesWritten != bytes.size()) {
        throw ConnectionBrokenError("Błąd zapisu danych");
    }
}

// Odczyt pojedynczego bajtu z portu
uint8_t ReaderWriter::read() {
    uint8_t tmp;
    DWORD noOfBytesRead = 0;
    // odczytujemy 1 bajt
    ReadFile(
            com,
            &tmp,
            sizeof(tmp),
            &noOfBytesRead,
            NULL
    );

    // Jeśli nie odczytano nic – uznajemy to za zerwanie połączenia
    if (noOfBytesRead == 0) {
        throw ConnectionBrokenError("Wystąpił błąd podczas odczytu danych");
    }

    return tmp;
}

// Destruktor – zamyka port COM
ReaderWriter::~ReaderWriter() {
    CloseHandle(com);
}
