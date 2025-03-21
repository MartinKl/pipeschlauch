cd tools/treetagger
[ ! -d ../../data/3-pos/ ] && mkdir ../../data/3-pos/
[ ! -d ../../data/3-pos/SeiKo ] && mkdir ../../data/3-pos/SeiKo
[ ! -d ../../data/3-lemma/ ] && mkdir ../../data/3-lemma/
[ ! -d ../../data/3-lemma/SeiKo ] && mkdir ../../data/3-lemma/SeiKo
for f in ../../data/2/SeiKo/*.txt; do
	bin/tree-tagger lib/german-spoken-stts2.par -token ${f} > ../../data/3-pos/SeiKo/$(basename $f)
	bin/tree-tagger lib/german.par -token -lemma ${f} > ../../data/3-lemma/SeiKo/$(basename $f)
done
