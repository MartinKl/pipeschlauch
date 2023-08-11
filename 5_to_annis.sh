cd tools/pepper/
./pepper.sh ../../exb2annis.pepper
if [[ $? -eq 0 ]]
then
	cd ../../
	zip annis-preview.zip -r data/5_annis/
fi
