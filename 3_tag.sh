cd tools/treetagger
[ ! -d ../../data/3/ ] && mkdir ../../data/3/
[ ! -d ../../data/3/SeiKo ] && mkdir ../../data/3/SeiKo
for f in ../../data/2/SeiKo/*.txt; do
	bin/tree-tagger lib/german-spoken-stts2.par -token -sgml -lemma -no-unknown -eos-tag unit ${f} > ../../data/3/SeiKo/$(basename $f)
done
