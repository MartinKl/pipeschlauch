cd tools/treetagger
[ ! -d ../../data/3/ ] && mkdir ../../data/3/
[ ! -d ../../data/3/SeiKo-pos ] && mkdir ../../data/3/SeiKo-pos
[ ! -d ../../data/3/SeiKo-lemma ] && mkdir ../../data/3/SeiKo-lemma
for f in ../../data/2/SeiKo/*.txt; do
	bin/tree-tagger lib/german-spoken-stts2.par -token ${f} > ../../data/3/SeiKo-pos/$(basename $f)
	bin/tree-tagger lib/german.par -token -lemma ${f} > ../../data/3/SeiKo-lemma/$(basename $f)
done
