#!/bin/bash

dpkg -s mona
if [ $? == 0 ]; then
  if [$1 == "--uninstall"]; then
    make uninstall
    rm -rf mona-1.4
  else
    echo "Mona is already installed. Run with --uninstall to uninstall"
  fi
fi

which flex
if [ $? != 0 ]; then
  echo "Flex is required to build. Please install flex before continuing (sudo apt install flex)."
  return
fi
wget http://www.brics.dk/mona/download/mona-1.4-18.tar.gz
tar -xzf mona-1.4-18.tar.gz
rm mona-1.4-18.tar.gz
cd ./mona-1.4
./configure --enable-static --enable-shared=no
make
make install-strip
if [ $? != 0 ]; then
  echo "Previous attempt at make failed - trying again with sudo."
  sudo make install-strip
fi

dpkg -s graphviz
if [ $? == 0 ]; then
  sudo apt install graphviz
fi