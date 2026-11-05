# Die Mathematik des Blackjack – Simulationsprogramme

Beide Programme wurden mit **Claude Code (Opus 5.5)** geschrieben.

Voraussetzung: Python 3. Für das Diagramm zusätzlich `pip install matplotlib`.

---

## 1. `simulation-bust-wahrscheinlichkeit-dealer.py`

**Start:**

```bash
python simulation-bust-wahrscheinlichkeit-dealer.py -n 100000 --seed 1 --diagramm abbildung1_bust_dealer.png
```

**Prompt:**

> *Für meine Blackjack-Seminararbeit möchte ich eine Tabelle zur Überkaufwahrscheinlichkeit des Dealers in Abhängigkeit seiner offenen Karte erstellen. Da die Rechnung sehr aufwendig ist, möchte ich nur ein Beispiel per Hand rechnen und den Rest simulieren lassen. Erstelle mir dazu eine Python-Simulation, die sowohl die Zwischenwerte B(t) als auch die Überkaufwahrscheinlichkeiten für jede offene Startkarte (2 bis Ass) berechnet und im Terminal ausgibt. Die Ergebnisse sollen außerdem als Diagramm dargestellt werden, damit ich sie anschaulich in meine Word-Datei einbinden kann.*

---

## 2. `dealer_simulation.py`

**Start:**

```bash
python dealer_simulation.py -n 2000000 --seed 42 --csv dealer_ergebnisse_2mio.csv
```

**Prompt:**

> *Ich brauche für meine Blackjack-Seminararbeit ein Programm, das mir die Endverteilung des Dealers zwischen 17 und 21 in Abhängigkeit seiner Startkarte sowie die Überkaufwahrscheinlichkeit liefert, simuliert mit 2.000.000 Durchläufen. Ich brauche die Möglichkeit, einen seed anzugeben, um Reproduzierbarkeit zu gewährleisten und eine Exportmöglichkeit.*
