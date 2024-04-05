cd tools/udpipe
mkdir ../../data/2_conll/
mkdir ../../data/2_conll/SeiKo
mkdir ../../data/2_conll-int/
mkdir ../../data/2_conll-int/SeiKo
./udpipe models/german-ud-2.0-170801.udpipe --tag $(ls ../../data/1_conll/SeiKo/*) --outfile ../../data/2_conll/SeiKo/{}.conllu
#./udpipe models/german-ud-2.0-170801.udpipe --tag $(ls ../../data/1_conll-int/*) --outfile ../../data/2_conll-int/SeiKo/{}.conllu
