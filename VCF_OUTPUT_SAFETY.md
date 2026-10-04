# Schutz der VCF-Ausgabe

Eine Konvertierung schreibt zunächst in eine exklusiv reservierte temporäre Datei
im Zielordner. Erst nach vollständigem Schreiben, Schließen und erneuter Prüfung
von Abbruch und Zielidentität ersetzt `os.replace` die Ausgabedatei. Fehler vor
diesem Schritt lassen eine vorhandene Ausgabe unverändert. Die Bereinigung betrifft
ausschließlich die eigene temporäre Datei.

Die Pipeline schützt die Genotyp-Eingabedatei, den Metadaten-Cache, das ausführende
Python-Skript sowie konfigurierte und ausgewählte FASTA-Dateien mit ihren
`.fai`-Indizes und `.gz`-Archiven. Direkte Pfade, auflösbare Links und bestehende
Hardlinks werden geprüft. Bekannte Ressourcenpfade bleiben auch dann reserviert,
wenn die Ressource noch fehlt. Unter Windows werden außerdem alternative
Datenströme als Ausgabe abgelehnt und abschließende Punkte und Leerzeichen bei der
Pfadprüfung berücksichtigt. Ein Fehler beim Prüfen einer Identität gilt nicht als
Nachweis, dass die Dateien verschieden sind.

Die anfänglich bekannten Ressourcenpfade bleiben während des gesamten Vorgangs
geschützt. Ändert ein Callback die Konfiguration, berücksichtigt die letzte Prüfung
sowohl diese ursprünglichen Pfade als auch die aktuell konfigurierten Ressourcen.

Bei Abbruch liefert die Pipeline `None`; die GUI meldet keinen Erfolg. Die
bestehende öffentliche Funktion `create_vcf` liefert aus Kompatibilitätsgründen
weiterhin `0` bei Abbruch. Sie erhält eine bereits eingelesene Variantenliste und
kann deshalb eine unbekannte ursprüngliche Eingabedatei nicht selbst schützen.
Eine erfolgreich abgeschlossene Konvertierung mit null verwertbaren Varianten
darf weiterhin eine VCF-Datei mit Kopfzeilen erzeugen. Ein nach der Veröffentlichung
gesetztes Abbruchsignal macht diese abgeschlossene Konvertierung nicht rückgängig.

Die Fortschrittsmeldung von 100 Prozent erfolgt nach dem Schließen der temporären
Datei, aber vor der Veröffentlichung. Fehler oder Abbruch in diesem Callback
verhindern die Veröffentlichung. Die Erfolgsmeldung folgt erst nach dem Ersetzen.

Schreibgeschützte oder durch Windows gesperrte Ziele dürfen weiterhin einen Fehler
auslösen; ihre Rechte werden zum Erzwingen des Ersetzens nicht verändert. Mehrere
gleichzeitige Schreibvorgänge verwenden verschiedene temporäre Dateien. Wenn das
Betriebssystem mehrere Ersetzungen zulässt, gewinnt die letzte erfolgreiche Ausgabe.

Der Schutz umfasst keine Dateisystemsperre gegen externe Änderungen zwischen der
letzten Prüfung und dem Ersetzen, keine Garantie bei Stromausfall und keine
Bereinigung nach gewaltsamem Prozessabbruch. Cache- und FASTA-Schreibvorgänge haben
eigene Lebenszyklen und sind nicht Bestandteil dieser Änderung. Die Regressionen
verwenden synthetische Daten und unterbinden Netzwerkzugriffe. Eine neue EXE oder
Geräteabnahme ist daraus nicht abgeleitet.
