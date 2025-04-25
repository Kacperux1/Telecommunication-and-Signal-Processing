#include "../include/Receiver.h"
#include <chrono>
#include <windows.h>
#include "../include/Transmitter.h"
using namespace std;
using namespace std::chrono;

ByteVector Receiver::receiveFile(int mode){
    ByteVector data;
    system_clock::time_point start = system_clock::now(); // Zaczynamy odmierzać czas
    bool letsStart = false;

    // Czekamy maksymalnie 60 sekund na rozpoczęcie transmisji
    cout << "Oczekiwanie na rozpoczecie transmisji..." << endl;
    while(system_clock::now() - start < seconds(60)){
        if(mode == ALGEBRAIC_CHECKSUM)
            readerWriter->write(ByteVector({NAK}));  // Wysyłamy NAK dla sumy algebraicznej
        else
            readerWriter->write(ByteVector({C}));  // Wysyłamy C dla CRC16
        try{
            // Czekamy na znak SOH (początek transmisji)
            if(readerWriter->read() == SOH){
                letsStart = true;  // Rozpoczynamy transmisję
                cout << "Rozpoczecie transmisji." << endl;
                break;
            }
        }catch(ConnectionBrokenError e){
            // Ignorujemy błąd połączenia, jeśli wystąpi
        }
        Sleep(5);  // Krótkie opóźnienie przed kolejną próbą
    }

    // Jeśli udało się rozpocząć transmisję
    if(letsStart){
        uint8_t action = SOH;  // Zmienna do kontrolowania przebiegu transmisji
        do{
            uint8_t blockNumber1 = readerWriter->read(); // Numer bloku (pierwszy bajt)
            uint8_t blockNumber2 = readerWriter->read(); // Numer bloku (drugi bajt)

            // Odczytujemy 128 bajtów z bloku
            ByteVector block;
            for(int i = 0; i < 128; i++){
                block.push_back(readerWriter->read());
            }

            cout << "Odebrano blok " << (int)blockNumber1 << "..." << endl;

            // Sprawdzanie sumy kontrolnej w zależności od trybu
            if(mode == ALGEBRAIC_CHECKSUM){
                uint8_t checksum = readerWriter->read(); // Odczytujemy sumę kontrolną
                cout << "Sprawdzanie sumy kontrolnej dla bloku " << (int)blockNumber1 << "..." << endl;

                // Jeśli suma kontrolna jest poprawna, potwierdzamy odebranie bloku
                if(algebraicChecksum(block) == checksum){
                    readerWriter->write(ByteVector({ACK}));  // Wysyłamy ACK
                    data.insert(data.end(), block.begin(), block.end());  // Dodajemy blok do danych
                    cout << "Blok " << (int)blockNumber1 << " odebrany poprawnie." << endl;
                }else{
                    readerWriter->write(ByteVector({NAK}));  // Wysyłamy NAK, jeśli suma nie pasuje
                    cout << "Błąd sumy kontrolnej dla bloku " << (int)blockNumber1 << ". Wysyłam NAK." << endl;
                }
            }else{
                // Obsługa CRC16
                ByteVector receivedChecksum({readerWriter->read(), readerWriter->read()});  // Odczytujemy otrzymaną sumę CRC
                ByteVector calculatedChecksum = crc16Checksum(block);  // Obliczamy sumę CRC dla odebranego bloku
                cout << "Sprawdzanie CRC dla bloku " << (int)blockNumber1 << "..." << endl;

                // Jeśli suma CRC się zgadza, potwierdzamy odbiór
                if(receivedChecksum[0] == calculatedChecksum[0] && receivedChecksum[1] == calculatedChecksum[1]){
                    readerWriter->write(ByteVector({ACK}));  // Wysyłamy ACK
                    data.insert(data.end(), block.begin(), block.end());  // Dodajemy blok do danych
                    cout << "CRC bloku " << (int)blockNumber1 << " jest poprawne. Blok odebrany." << endl;
                }else{
                    readerWriter->write(ByteVector({NAK}));  // Wysyłamy NAK, jeśli CRC się nie zgadza
                    cout << "Błąd CRC dla bloku " << (int)blockNumber1 << ". Wysyłam NAK." << endl;
                }
            }
            action = readerWriter->read();  // Odczytujemy kolejny bajt kontrolny
        }while(action == SOH);  // Jeśli mamy kolejny blok, powtarzamy

        // Jeśli otrzymaliśmy znak EOT, kończymy transmisję
        if(action == EOT){
            readerWriter->write(ByteVector({ACK}));  // Wysyłamy ACK na zakończenie
            cout << "Transmisja zakonczona. Otrzymano EOT." << endl;
        }else{
            throw ConnectionBrokenError("Blad protokołu!");  // Błąd protokołu, oczekiwano EOT
        }
    }

    return data;  // Zwracamy odebrane dane
}

