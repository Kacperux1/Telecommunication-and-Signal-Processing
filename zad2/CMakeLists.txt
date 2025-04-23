cmake_minimum_required(VERSION 3.25)
project(untitled1)

set(CMAKE_CXX_STANDARD 17)

add_executable(untitled1 main.cpp
        src/checksum.cpp
        src/ReaderWriter.cpp
        src/Receiver.cpp
        src/Transmitter.cpp
        include/ReaderWriter.h
        include/Receiver.h
        include/Transmitter.h
        include/checksum.h)
