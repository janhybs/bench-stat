#!/bin/bash

# Jak spustit davku (vse se odehrava v terminulu fterm)
# 1) vytvorit soubor a ujistit se, se radku maji linuxove zakoncení (tj. \n)
# 2) soubor musi byt spustitelny, v linuxu je mozno napsat
#   chmod +x davka.sh
# 3) spustit davku:
#   ./davka.sh

flow123d -s soubor1.yaml -o vystup1
flow123d -s soubor2.yaml -o vystup2
flow123d -s soubor3.yaml -o vystup3