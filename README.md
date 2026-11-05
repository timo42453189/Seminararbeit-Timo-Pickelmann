# Die Mathematik des Blackjack – Simulationsprogramme

Begleitmaterial zur Seminararbeit **„Die Mathematik des Blackjack: Wahrscheinlichkeitsrechnung und optimale Strategien“**
W-Seminar *Mathematik im Spiel* · Abiturjahrgang 2027 · Verfasser: Timo Pickelmann · Kursleiter: R. Huber, StR

Dieses Repository enthält die beiden Python-Programme, mit denen die simulierten Werte der Seminararbeit erzeugt wurden. Alle Ergebnisse lassen sich mit den unten angegebenen Befehlen exakt nachvollziehen.

---

## Inhalt

| Datei | Zweck | Verwendet in der Arbeit |
|---|---|---|
| `simulation-bust-wahrscheinlichkeit-dealer.py` | Überkaufwahrscheinlichkeit des Dealers je offener Karte sowie Zwischenwerte B(12) … B(16); erzeugt das Säulendiagramm | Kapitel 5, Abbildung 1 |
| `dealer_simulation.py` | Vollständige Endverteilung des Dealers (17, 18, 19, 20, 21, Bust) je offener Karte; Export als CSV | Kapitel 6.2 (Erwartungswerte bei harter 16 gegen 10), Tabelle im Anhang |
| `dealer_ergebnisse_2mio.csv` | Ergebnisse von `dealer_simulation.py` mit den Einstellungen der Arbeit | Anhang |
| `abbildung1_bust_dealer.png` | Diagramm aus `simulation-bust-wahrscheinlichkeit-dealer.py` | Abbildung 1 |
| `requirements.txt` | Benötigte Zusatzbibliothek (nur für das Diagramm) | – |

---

## Voraussetzungen

- **Python 3.8 oder neuer** ([python.org/downloads](https://www.python.org/downloads/))
- Für das Diagramm zusätzlich **matplotlib**. Alle anderen Funktionen kommen ohne Zusatzbibliotheken aus.

```bash
pip install -r requirements.txt
```

> **Hinweis:** Unter Windows heißt der Befehl meist `python` oder `py`, unter macOS/Linux `python3`.

---

## Schnellstart: Ergebnisse der Arbeit reproduzieren

1. Repository herunterladen: grüner Button **Code → Download ZIP**, dann entpacken.
   Alternativ: `git clone <URL dieses Repositorys>`
2. Im entpackten Ordner ein Terminal bzw. die Eingabeaufforderung öffnen.
3. Die folgenden zwei Befehle ausführen:

```bash
# Abbildung 1 und Werte aus Kapitel 5 (Laufzeit ca. 25 Sekunden)
python simulation-bust-wahrscheinlichkeit-dealer.py -n 2000000 --seed 42 --diagramm abbildung1_bust_dealer.png

# Endverteilung des Dealers für Kapitel 6.2 (Laufzeit ca. 20 Sekunden)
python dealer_simulation.py -n 2000000 --seed 42 --csv dealer_ergebnisse_2mio.csv
```

Durch den festen Startwert des Zufallsgenerators (`--seed 42`) entstehen bei jedem Aufruf genau dieselben Zahlen.

---

## Erwartete Ausgabe

### `simulation-bust-wahrscheinlichkeit-dealer.py`

**Teil 1 – Zwischenwerte B(t)** (Dealer hat harte Summe t):

| t | Simulation | exakt (Rekursion) | Abweichung |
|---|---|---|---|
| 16 | 0,6156 | 0,6154 | +0,0002 |
| 15 | 0,5854 | 0,5858 | −0,0004 |
| 14 | 0,5536 | 0,5539 | −0,0003 |
| 13 | 0,5199 | 0,5196 | +0,0002 |
| 12 | 0,4822 | 0,4827 | −0,0005 |

Die exakten Werte stimmen mit der rekursiven Handrechnung in Kapitel 5.1 der Arbeit überein.

**Teil 2 – Überkaufwahrscheinlichkeit je offener Karte** (Grundlage für Abbildung 1):

| Offene Karte | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | A |
|---|---|---|---|---|---|---|---|---|---|---|
| Simulation | 35,43 % | 37,37 % | 39,40 % | 41,72 % | 42,33 % | 26,20 % | 24,43 % | 22,81 % | 21,19 % | 11,54 % |
| exakt | 35,36 % | 37,39 % | 39,45 % | 41,64 % | 42,32 % | 26,23 % | 24,47 % | 22,84 % | 21,21 % | 11,53 % |

### `dealer_simulation.py`

Simulierte Endverteilung des Dealers (2.000.000 Durchläufe je Startkarte):

| Start | 17 | 18 | 19 | 20 | 21 | Bust |
|---|---|---|---|---|---|---|
| 2 | 13,98 % | 13,49 % | 12,97 % | 12,38 % | 11,78 % | 35,40 % |
| 3 | 13,51 % | 13,11 % | 12,54 % | 12,03 % | 11,44 % | 37,38 % |
| 4 | 13,05 % | 12,60 % | 12,11 % | 11,66 % | 11,09 % | 39,49 % |
| 5 | 12,24 % | 12,23 % | 11,81 % | 11,33 % | 10,83 % | 41,56 % |
| 6 | 16,58 % | 10,64 % | 10,62 % | 10,09 % | 9,72 % | 42,35 % |
| 7 | 36,90 % | 13,81 % | 7,87 % | 7,83 % | 7,42 % | 26,17 % |
| 8 | 12,83 % | 35,94 % | 12,85 % | 6,91 % | 6,96 % | 24,50 % |
| 9 | 11,99 % | 11,96 % | 35,06 % | 12,00 % | 6,12 % | 22,87 % |
| **10** | **11,18 %** | **11,11 %** | **11,11 %** | **34,21 %** | **11,15 %** | **21,24 %** |
| A | 13,07 % | 13,07 % | 13,12 % | 13,13 % | 36,10 % | 11,51 % |

Die fett gedruckte Zeile (offene 10) ist die Grundlage für die Berechnung von E(Stand) und E(Hit) bei einer harten 16 gegen eine 10 in Kapitel 6.2.

Am Ende gibt das Programm zusätzlich die exakten Werte und die größte Abweichung aus: **0,08 Prozentpunkte**.

> Die beiden Programme verwenden unterschiedliche Zufallszahlen-Folgen. Deshalb unterscheiden sich ihre Simulationswerte in der zweiten Nachkommastelle leicht (z. B. offene 10: 21,19 % bzw. 21,24 %). Beide liegen innerhalb des 95-%-Konfidenzintervalls um den exakten Wert von 21,21 %.

---

## Optionen

### `simulation-bust-wahrscheinlichkeit-dealer.py`

| Option | Bedeutung | Standard |
|---|---|---|
| `-n ZAHL` | Durchläufe pro Wert | 200000 |
| `--seed ZAHL` | Startwert des Zufallsgenerators (reproduzierbare Ergebnisse) | zufällig |
| `--decks ZAHL` | Anzahl Decks im Schuh, `0` = unendlich viele | 0 |
| `--diagramm DATEI` | Säulendiagramm als PNG speichern | aus |

### `dealer_simulation.py`

| Option | Bedeutung | Standard |
|---|---|---|
| `-n ZAHL` | Durchläufe je Startkarte | 10000 |
| `--seed ZAHL` | Startwert des Zufallsgenerators | zufällig |
| `--decks ZAHL` | Anzahl Decks, `0` = unendlich viele | 0 |
| `--h17` | Dealer zieht auch auf Soft 17 (sonst: steht auf Soft 17) | aus |
| `--csv DATEI` | Ergebnisse zusätzlich als CSV speichern (Trennzeichen `;`) | aus |

Beispiel für eine eigene Variante, mit 6 Decks und H17-Regel:

```bash
python dealer_simulation.py -n 2000000 --seed 42 --decks 6 --h17
```

---

## Modellannahmen

Die Annahmen entsprechen Kapitel 2.3 der Seminararbeit:

- Der Dealer zieht bis einschließlich 16 und steht ab 17, auch bei Soft 17 (**S17-Regel**).
- Ein Ass zählt 11, solange die Summe dadurch 21 nicht überschreitet, sonst 1.
- **Unendlich viele Decks:** Jede Karte hat immer dieselbe Wahrscheinlichkeit (2–9 und Ass je 1/13, Zehnerwerte 4/13). Das entspricht Ziehen mit Zurücklegen. Mit `--decks` lässt sich ein echter Schuh ohne Zurücklegen simulieren.
- Der Dealer erhält seine zweite Karte erst nach den Spielern (europäische Variante, wie bei den Spielbanken Bayern). Ein Blackjack des Dealers zählt deshalb als Endsumme 21 und wird nicht vorab geprüft.

---

## Genauigkeit der Simulation

Für eine simulierte Wahrscheinlichkeit p bei n Durchläufen gilt für den Standardfehler

  σ = √( p · (1 − p) / n ).

Das 95-%-Konfidenzintervall ist ungefähr p ± 1,96 · σ. Der Fehler nimmt also mit 1/√n ab:

| Durchläufe n | max. 95-%-Intervall | größte Abweichung vom exakten Wert |
|---|---|---|
| 10.000 | ± 0,98 Prozentpunkte | 1,33 Prozentpunkte |
| 2.000.000 | ± 0,07 Prozentpunkte | 0,08 Prozentpunkte |

Die 200-fache Anzahl an Durchläufen verkleinert den Fehler um den Faktor √200 ≈ 14. Deshalb wurden in der Arbeit 2.000.000 Durchläufe je Startkarte verwendet.

---

## Hinweis zur Entstehung

Die Programme wurden mithilfe des KI-Sprachmodells **Claude** (Anthropic, 2026) erstellt. Der Verfasser hat sie ausgeführt und die Ergebnisse überprüft: Die Simulationswerte wurden mit der exakten rekursiven Rechnung (Kapitel 5.1) verglichen, die auch in beiden Programmen zur Kontrolle enthalten ist. Danach wurden die Ergebnisse in der Seminararbeit ausgewertet. Siehe auch das Quellenverzeichnis und den Anhang der Arbeit.
