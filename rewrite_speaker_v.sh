mkdir data/3/
cp -r data/0/SeiKo data/3/
for f in data/3/SeiKo/*.exb
do
	for spk_id in $(xmlstarlet sel -t -v '//tier[@category="v"]/@speaker' $f)
	do 
		abbr=$(echo $spk_id | sed 's:_CLEAN::g')
		xp='//speakertable/speaker[abbreviation="'$abbr'"]/@id'
		spk=$(xmlstarlet sel -t -v $xp $f)
		xmlstarlet ed -L --update '//tier[@category="v"][@speaker="'$spk_id'"]/@speaker' --value $spk $f
	done
done
