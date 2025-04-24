#include <iostream>
#include <fstream>
#include <string>
#include "include/ReaderWriter.h"
#include "include/Transmitter.h"
#include "include/Receiver.h"

using namespace std;

int main() {
    // Tworzymy obiekt do komunikacji przez port COM2
    auto connection = std::make_unique<ReaderWriter>("COM2");

    int operationMode = 0;
    int controlMode = 0;

    // Wybór trybu pracy: nadawanie albo odbiór
    cout << "Wybierz tryb pracy:\n"
            "0) wysyłanie\n"
            "1) odbieranie\n";
    cin >> operationMode;

    // Wybór metody kontroli błędów
    cout << "Wybierz tryb kontroli:\n"
            "0) suma kontrolna\n"
            "1) CRC\n";
    cin >> controlMode;

    cin.get(); // usuniecie znaku nowej linii

    // Sprawdzenie poprawności opcji
    if ((operationMode != 0 && operationMode != 1) || (controlMode != 0 && controlMode != 1)) {
        cout << "Niepoprawne parametry!" << endl;
        return 1;
    }

    if (operationMode == 0) {
        // TRYB NADAWANIA
        cout << "Podaj nazwę pliku do wysłania: ";
        string inputFileName;
        getline(cin, inputFileName);

        ifstream inputFile(inputFileName, ios::binary);
        if (!inputFile.is_open()) {
            cerr << "Nie udało się otworzyć pliku!" << endl;
            return 1;
        }

        ByteVector fileData;
        // Wczytujemy bajty z pliku do wektora
        while (inputFile) {
            uint8_t byte = inputFile.get();
            if (inputFile)
                fileData.push_back(byte);
        }
        inputFile.close();

        // Tworzymy nadajnik i wysyłamy dane
        Transmitter transmitter(std::move(connection));
        transmitter.sendFile(fileData, controlMode);
    } else {
        // TRYB ODBIERANIA
        cout << "Podaj nazwę pliku do odebrania: ";
        string outputFileName;
        getline(cin, outputFileName);

        // Tworzymy odbiornik i odbieramy dane
        Receiver receiver(std::move(connection));
        ByteVector receivedData = receiver.receiveFile(controlMode);

        // Zapisujemy odebrane dane do pliku
        ofstream outputFile(outputFileName, ios::binary);
        outputFile.write(reinterpret_cast<char*>(receivedData.data()), receivedData.size());
        outputFile.close();
    }

    return 0;
}
