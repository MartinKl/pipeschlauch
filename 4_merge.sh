cd tools/pepper/
./pepper.sh ../../merge2exb.pepper
for f in ../../data/4/SeiKo/*_seg.exb
do
	echo $f
	mv $f $(dirname $f)/$(basename -s _seg.exb $f)_pos.exb
done
