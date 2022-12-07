#! /usr/bin/bash

g++ -rdynamic  janela.cpp -o janela -std=c++17 `pkg-config gtk+-3.0 --cflags --libs gstreamer-1.0`
