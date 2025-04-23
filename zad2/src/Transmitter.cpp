#include "../include/Transmitter.h"
#include <cmath>
#include <vector>
#include <cstdint>

using namespace std;
using ByteVector = std::vector<uint8_t>;

void Transmitter::sendFile(ByteVector data, int mode){
	//oczekiwanie na odbiornik
	if(mode == ALGEBRAIC_CHECKSUM)
		while(readerWriter->read() != NAK);
	else
		while(readerWriter->read() != C);
	//rozpoczynanie nadawania
	int noOfBlocks = (int)ceil(data.size() / 128.0);
	for(int blockIndex = 0; blockIndex < noOfBlocks; blockIndex++){
		//wyodrebnianie bloku
		ByteVector::iterator blockBegin = data.begin() + blockIndex * 128;
		ByteVector::iterator blockEnd;
		if(data.end() - blockBegin <= 128)
			blockEnd = data.end();
		else
			blockEnd = data.begin() + (blockIndex + 1) * 128;
		ByteVector block(blockBegin, blockEnd);
		//dopelnianie zerami
		if(block.size() < 128)
			block.insert(block.end(), 128 - block.size(), 0);
		//tworzenie naglowka
		ByteVector header = {
			SOH,
			(uint8_t)(blockIndex + 1),
			(uint8_t)(255 - (blockIndex + 1))};
		//wysylanie
		readerWriter->write(header);
		readerWriter->write(block);
		if(mode == ALGEBRAIC_CHECKSUM)
			readerWriter->write(ByteVector({algebraicChecksum(block)}));
		else
			readerWriter->write(crc16Checksum(block));
		//odbieranie potwierdzenia
        uint8_t response = readerWriter->read();
		if(response == NAK){
			blockIndex--;
		}else if(response == CAN){
			throw ConnectionBrokenError("Connection canceled!");
		}else if(response != ACK){
			throw ConnectionBrokenError("Protocol error!");
		}
	}
	readerWriter->write(ByteVector({EOT}));
}
