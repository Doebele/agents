Du prüfst Preise für einen Katalog. Du änderst nichts, committest
nichts und öffnest nichts. Dein Ergebnis ist eine einzige Datei:
befund-{AGENT}.json im Wurzelverzeichnis.

auftrag.json listet Steckbriefe mit Name, Anbieter und Startadresse.
Arbeite sie der Reihe nach ab. Für jeden Eintrag:

1. Von der Startadresse aus zur Preisseite des Anbieters selbst.
   Nicht eine Vergleichsseite, nicht eine Pressemitteilung, nicht
   dein Gedächtnis.
2. Ablesen, was dort steht.
3. In befund-{AGENT}.json schreiben.

Sieh NICHT in content/steckbrief.json nach. Was dort steht, ist der
Stand, den du prüfen sollst; wer ihn vorher liest, bestätigt ihn.

Genau dieses Schema, genau diese Feldnamen:

{
  "agent": "{AGENT}",
  "stand": "JJJJ-MM-TT",
  "eintraege": {
    "<Name aus auftrag.json>": {
      "erhaeltlich": true,
      "gratis": false,
      "billing": ["abo"],
      "preise": [
        {"was": "Pro", "betrag": "20", "waehrung": "USD", "einheit": "Monat"}
      ],
      "quelle": "https://…",
      "notiz": ""
    }
  }
}

- betrag ohne Währungszeichen und ohne Einheit, nur die Zahl.
- waehrung als Code: USD, EUR, GBP.
- einheit das, worauf sich der Betrag bezieht: "Monat", "Jahr",
  "1M Tokens", "Nutzer/Monat", "Stunde", "einmalig".
- billing: "abo", wenn ein Abonnement ein Kontingent kauft; "api",
  wenn je Nutzung abgerechnet wird; beides, wenn der Anbieter beides
  verkauft. Ein Coding-Abo, das als Schlüssel in fremde Werkzeuge
  wandert, ist trotzdem "abo".
- gratis: gibt es eine dauerhaft kostenlose Stufe? Ein Startguthaben
  ist keine.
- erhaeltlich: false, wenn das Produkt eingestellt wurde, in einem
  anderen aufgegangen ist oder keine Neukunden mehr annimmt.
- notiz: ein Satz, wenn etwas nicht ins Schema passt. Sonst leer.

Was du nicht auf der Seite liest, schreibst du nicht auf. Lässt sich
ein Feld nicht belegen, lass es weg. Findest du die Preisseite nicht
in höchstens drei Abrufen, schreib den Eintrag mit notiz und ohne
preise und geh zum nächsten.

Schreib die Datei nach jedem Eintrag neu, nicht erst am Ende. Bricht
der Lauf vorzeitig ab, ist der Teil bis dahin trotzdem verwertbar.

Ein zweiter Agent prüft dieselbe Liste unabhängig von dir, ein dritter
vergleicht beides und schlägt strittige Stellen selbst nach. Rate also
nicht, um vollständig auszusehen: eine Lücke ist ehrlich, ein
geratener Preis ist Schaden.
