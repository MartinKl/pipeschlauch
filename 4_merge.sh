annatto run --in-memory merge2exb.toml
for f in data/4/SeiKo/*_seg.exb
do
	mv $f $(dirname $f)/$(basename -s _seg.exb $f)_pos.exb
done
