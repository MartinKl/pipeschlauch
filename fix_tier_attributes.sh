for f in ./data/4/SeiKo/*.exb
do
	# lemma, auto_lemma, pos, auto_pos von typ "t" auf typ "a"
	xmlstarlet ed -L -u '//tier[@category="auto_lemma"]/@type' -v "a" $f
	# speaker von ID SPK0 auf PART_CLEAN
	xmlstarlet ed -L -u '//tier[@speaker="SPK0"]/@speaker' -v "PART_CLEAN" $f
	# speaker mit ID SPK0 löschen
	xmlstarlet ed -L -d '//speaker[@id="SPK0"]' $f
done
