#include <iostream>
#include <fstream>
#include <string>
#include "include/ReaderWriter.h"
#include "include/Transmitter.h"
#include "include/Receiver.h"
using namespace std;



int main(){
    // Tworzymy obiekt , który będzie odpowiedzialny za komunikację przez port szeregowy
    auto rw = std::make_unique<ReaderWriter>("COM2");

    int workingMode;  // Zmienna do przechowywania wybranego trybu pracy
    int checksumMode;  // Zmienna do wyboru trybu sumy kontrolnej (algorytm lub CRC)

    // Zapytanie użytkownika o wybór trybu pracy
    cout << "Wybierz tryb pracy:\n"
         << "0) wysylanie\n"
         << "1) odbieranie\n";
    cin >> workingMode;
    cin.get(); //czyszczenie bufora std::in
    cout << "Wybierz typ sumy kontrolnej:\n"
         << "0) algebraiczna\n"
         << "1) CRC\n";
    cin >> checksumMode;
    cin.get();  // Odczytujemy enter po wyborze trybu

    // Sprawdzamy poprawność wpisanych parametrów
    if((workingMode != 0 && workingMode != 1) || (checksumMode != 0 && checksumMode != 1)){
        cout << "Niepoprawne parametry!" << endl;  // W przypadku niepoprawnych parametrów wyświetlamy komunikat o błędzie
        return 0;
    }

    // Obsługa trybu wysyłania
    if(workingMode == 0){
        // Zapytanie o ścieżkę do pliku, który chcemy wysłać
        cout << "Podaj sciezke do pliku: " << endl;
        string filename;
        getline(cin, filename);  // Odczytujemy nazwę pliku
        ifstream is(filename, ios::binary);  // Otwieramy plik w trybie binarnym
        ByteVector data;  // Tworzymy wektor, który będzie przechowywał dane z pliku
        while(is){
            uint8_t b = is.get();  // Odczytujemy bajt z pliku
            if(is)  // Jeśli odczyt się udał, dodajemy bajt do wektora
                data.push_back(b);
        }
        is.close();  // Zamykamy plik po odczycie

        // Tworzymy obiekt klasy Transmitter i wysyłamy plik
        Transmitter tr(std::move(rw));
        tr.sendFile(data, checksumMode);
    }

    // Obsługa trybu odbierania
    if(workingMode == 1){
        // Zapytanie o nazwę pliku, do którego mają zostać zapisane odebrane dane
        cout << "Podaj nazwe pliku do odebrania: " << endl;
        string filename;
        getline(cin, filename);  // Odczytujemy nazwę pliku
        Receiver re(std::move(rw));  // Tworzymy obiekt klasy Receiver
        ByteVector data = re.receiveFile(checksumMode);  // Odbieramy dane

        // Zapisujemy otrzymane dane do pliku
        ofstream os(filename, ios::binary);
        os.write((char*)data.data(), data.size());  // Zapisujemy dane binarne do pliku
        os.close();  // Zamykamy plik po zapisaniu
    }

}
