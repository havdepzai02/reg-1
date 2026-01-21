#!/bin/bash

pip install -r 1.txt || exit 1

(
  sleep 1.5
  printf "1\n"
  sleep 1.5
  printf "VN\n"
  sleep 1.5
  printf "10000\n"
  sleep 1.5
  printf "hav\n"
  sleep 1.5
  printf "hav\n"
  sleep 1.5
  printf "2\n"
  sleep 1.5
  printf "50\n"
) | python 1.py
