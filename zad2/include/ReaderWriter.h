#ifndef READERWRITER_H
#define READERWRITER_H

#include <windows.h>
#include <string>
#include <vector>
#include <stdexcept>
#include <cstdint>

using ByteVector = std::vector<uint8_t>;

class OpeningPortError : public std::runtime_error {
public:
    explicit OpeningPortError(const std::string& msg) : std::runtime_error(msg) {}
};

class ConnectionBrokenError : public std::runtime_error {
public:
    explicit ConnectionBrokenError(const std::string& msg) : std::runtime_error(msg) {}
};

class ReaderWriter {
public:
    explicit ReaderWriter(std::string portName);
    void write(const ByteVector& bytes);
    uint8_t read();
    ~ReaderWriter();

private:
    HANDLE com;
};

#endif // READERWRITER_H

