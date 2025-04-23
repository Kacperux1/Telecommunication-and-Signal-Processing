#include "../include/Receiver.h"
#include <chrono>
#include <windows.h>
#include "../include/Transmitter.h"
using namespace std;
using namespace std::chrono;

ByteVector Receiver::receiveFile(int mode){
	ByteVector data;
	system_clock::time_point start = system_clock::now();
	bool letsStart = false;
	while(system_clock::now() - start < seconds(60)){
		if(mode == ALGEBRAIC_CHECKSUM)
			readerWriter->write(ByteVector({NAK}));
		else
			readerWriter->write(ByteVector({C}));
		try{
			if(readerWriter->read() == SOH){
				letsStart = true;
				break;
			}
		}catch(ConnectionBrokenError e){}
		Sleep(5);
	}
	if(letsStart){
        uint8_t  action = SOH;
		do{
            uint8_t  blockNumber1 = readerWriter->read();
            uint8_t  blockNumber2 = readerWriter->read();
			ByteVector block;
			for(int i = 0; i < 128; i++){
				block.push_back(readerWriter->read());
			}
			if(mode == ALGEBRAIC_CHECKSUM){
                uint8_t  checksum = readerWriter->read();
				if(algebraicChecksum(block) == checksum){
					readerWriter->write(ByteVector({ACK}));
					data.insert(data.end(), block.begin(), block.end());
				}else{
					readerWriter->write(ByteVector({NAK}));
				}
			}else{
				ByteVector receivedChecksum({readerWriter->read(), readerWriter->read()});
				ByteVector calculatedChecksum = crc16Checksum(block);
				if(receivedChecksum[0] == calculatedChecksum[0] &&
						receivedChecksum[1] == calculatedChecksum[1]){
					readerWriter->write(ByteVector({ACK}));
					data.insert(data.end(), block.begin(), block.end());
				}else{
					readerWriter->write(ByteVector({NAK}));
				}
			}
			action = readerWriter->read();
		}while(action == SOH);
		if(action == EOT){
			readerWriter->write(ByteVector({ACK}));
		}else{
			throw ConnectionBrokenError("Protocol error!");
		}
	}
	return data;
}
