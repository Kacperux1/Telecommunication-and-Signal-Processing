#include <iostream>
#include <fstream>
#include <string>
#include "include/ReaderWriter.h"
#include "include/Transmitter.h"
#include "include/Receiver.h"
using namespace std;

const int SENDING_MODE = 0;
const int RECEIVING_MODE = 1;

int main(){
    auto rw = std::make_unique<ReaderWriter>("COM2");

	int workingMode;
	int checksumMode;
	cout << "Wybierz tryb pracy:\n"
		"0) wysylanie\n"
		"1) odbieranie\n";
	cin >> workingMode;
	checksumMode=0;
	cin.get();
	if((workingMode != 0 && workingMode != 1) || (checksumMode != 0 && checksumMode != 1)){
		cout << "Niepoprawne parametry!" << endl;
		return 0;
	}

	if(workingMode == 0){
		cout << "Podaj sciezke do pliku: " << endl;
		string filename;
		getline(cin, filename);
		ifstream is(filename, ios::binary);
		ByteVector data;
		while(is){
            uint8_t b = is.get();
			if(is)
				data.push_back(b);
		}
		is.close();
		Transmitter tr(std::move(rw));
		tr.sendFile(data, checksumMode);
	}
	if(workingMode == 1){
		cout << "Podaj nazwe pliku do odebrania: " << endl;
		string filename;
		getline(cin, filename);
		Receiver re(std::move(rw));
		ByteVector data = re.receiveFile(checksumMode);
		ofstream os(filename, ios::binary);
		os.write((char*)data.data(), data.size());
		os.close();
	}

}
