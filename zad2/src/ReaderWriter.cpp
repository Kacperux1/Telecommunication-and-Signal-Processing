#include <iostream>
#include "../include/ReaderWriter.h"
using namespace std;

ReaderWriter::ReaderWriter(string portName){
    //otwieranie portu
    com = CreateFile(("\\\\.\\" + portName).c_str(),
                     GENERIC_READ | GENERIC_WRITE,
                     0,
                     NULL,
                     OPEN_EXISTING,
                     0,
                     NULL);
    if(com == INVALID_HANDLE_VALUE)
        throw OpeningPortError("Can't open port: " + portName);

    //konfiguracja portu
    DCB dcbSerialParams = {0};
    GetCommState(com, &dcbSerialParams);
    dcbSerialParams.DCBlength = sizeof(dcbSerialParams);
    dcbSerialParams.BaudRate = CBR_9600;
    dcbSerialParams.ByteSize = 8;
    dcbSerialParams.StopBits = ONESTOPBIT;
    dcbSerialParams.Parity = NOPARITY;
    SetCommState(com, &dcbSerialParams);

    //konfiguracja timeouts
    COMMTIMEOUTS timeouts = {0};
    timeouts.ReadIntervalTimeout = 5000;		//in ms
    timeouts.ReadTotalTimeoutConstant = 5000;
    timeouts.ReadTotalTimeoutMultiplier = 10;
    timeouts.WriteTotalTimeoutConstant = 50;
    timeouts.WriteTotalTimeoutMultiplier = 10;
    SetCommTimeouts(com, &timeouts);
}

void ReaderWriter::write(const ByteVector& bytes){
    DWORD noOfBytesWritten = 0;
    WriteFile(com,
              bytes.data(),
              bytes.size(),
              &noOfBytesWritten,
              NULL);
    if(noOfBytesWritten != bytes.size()){
        throw ConnectionBrokenError("Blad zapisu danych");
    }
}

uint8_t  ReaderWriter::read(){
    uint8_t  tmp;
    DWORD noOfBytesRead = 0;
    ReadFile(com,
             &tmp,
             sizeof(tmp),
             &noOfBytesRead,
             NULL);
    if(noOfBytesRead == 0){
        throw ConnectionBrokenError("Blad odczytu informacji");
    }
    return tmp;
}

ReaderWriter::~ReaderWriter(){
    CloseHandle(com);
}