#!/bin/bash

pyinstaller -F textsearch.py
mv dist/textsearch.exe .
rm -Rf dist/ build/
