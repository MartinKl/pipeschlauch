[ ! -d data/1 ] && mkdir data/1
[ ! -d data/1/SeiKo ] && mkdir data/1/SeiKo/
python3 create_ctok.py data/original/ data/1/SeiKo/
