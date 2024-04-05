# Vereinbarungen

+ es gibt immer nur eine Transkriptionsebene pro Sprecher*in und das ist die tok-Ebene
+ tok der Interviewerin ist tok_int (speaker INT) -> INT::tok_int
+ für Interviewee: SPKCode::tok_part; SPKCode bleibt so
+ die tok-Ebenen sind vom Typ "t", alle anderen Ebenen vom Typ "a"
+ Korpusnamen nicht als Metadatum setzen (Projektname)
+ create_ctok erstellt die ctok-Ebene (generische Speaker-Abbreviation PART_CLEAN)
+ PART_CLEAN::unit ist eine Kopie der ursprünglichen unit-Ebene
+ tok_part-Token müssen entweder von einer unit-Spanne oder einer exclude-Spanne überspannt werden (es sei denn, es handelt sich um Pausenmarker, die eh gelöscht werden)
+ ist Letzteres nicht der Fall, lassen sich die getaggten CoNLL-Dateien nicht wieder mit den EXMARaLDA-Dateien zusammenbringen


