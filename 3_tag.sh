cd tools/treetagger
mkdir ../../data/3/
mkdir ../../data/3/SeiKo
for f in ../../data/2/SeiKo/*.tt; do
	bin/tree-tagger lib/german-spoken-stts2.par -token -sgml -lemma -no-unknown -eos-tag unit ${f} > ../../data/3/SeiKo/$(basename $f)
done
