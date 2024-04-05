cd tools/treetagger
mkdir ../../data/2/
mkdir ../../data/2/SeiKo
for f in ../../data/1/SeiKo/*.tt; do
	bin/tree-tagger lib/german-spoken-stts2.par -token -sgml -lemma -no-unknown -eos-tag unit ${f} > ../../data/2/SeiKo/$(basename $f)
done
