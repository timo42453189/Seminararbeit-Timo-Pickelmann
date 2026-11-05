#!/usr/bin/env python3
"""
Blackjack: Monte-Carlo-Simulation der Endverteilung des Dealers
================================================================

Für jede mögliche offene Startkarte des Dealers (2-10, Ass) wird die
Dealerhand N-mal (Standard: 10.000) zu Ende gespielt. Ausgegeben werden
die relativen Häufigkeiten der Endsummen 17, 18, 19, 20, 21 sowie die
Überkaufwahrscheinlichkeit (Bust, Summe > 21).

Regeln / Annahmen (per Kommandozeile änderbar):
  * Dealer zieht bis mindestens 17.
  * Standard: Dealer steht auf Soft 17 (S17). Mit --h17 zieht er auf Soft 17.
  * Standard: unendlich viele Decks (jede Karte mit fester Wahrscheinlichkeit,
    10/B/D/K zusammen 4/13). Mit --decks 6 wird aus einem 6-Deck-Schuh ohne
    Zurücklegen gezogen (die Startkarte ist dabei bereits entnommen).
  * Ein Blackjack (Ass + 10 als erste zwei Karten) zählt als Endsumme 21.
  * Keine Bedingung auf "Dealer hat keinen Blackjack" (europäische Variante
    ohne Hole-Card-Peek).

Bei unendlich vielen Decks werden zusätzlich die exakten Wahrscheinlichkeiten
(rekursiv berechnet) und die Abweichung der Simulation davon ausgegeben.

Aufruf-Beispiele:
  python dealer_simulation.py
  python dealer_simulation.py -n 10000 --seed 42 --csv ergebnisse.csv
  python dealer_simulation.py --decks 6 --h17
"""

import argparse
import csv
import math
import random
from functools import lru_cache

# Kartenwerte: 2-9, 10 (für 10, Bube, Dame, König), 11 = Ass
STARTKARTEN = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
# Ein Deck mit 13 Rängen: die 10 kommt viermal vor (10, B, D, K)
DECK_13 = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11]
ERGEBNISSE = [17, 18, 19, 20, 21, "Bust"]


def name(karte):
    return "A" if karte == 11 else str(karte)


# ---------------------------------------------------------------------------
# Spiellogik
# ---------------------------------------------------------------------------

def karte_hinzufuegen(summe, weiche_asse, karte):
    """Fügt eine Karte hinzu. weiche_asse = Anzahl Asse, die gerade als 11 zählen."""
    summe += karte
    if karte == 11:
        weiche_asse += 1
    # Bei Überkauf ein Ass von 11 auf 1 abwerten, solange möglich
    while summe > 21 and weiche_asse > 0:
        summe -= 10
        weiche_asse -= 1
    return summe, weiche_asse


def muss_ziehen(summe, weiche_asse, h17):
    if summe < 17:
        return True
    # Soft 17: nur bei H17-Regel wird weitergezogen
    return h17 and summe == 17 and weiche_asse > 0


def dealer_spielen(startkarte, ziehe_karte, h17):
    """Spielt eine Dealerhand zu Ende und liefert 17..21 oder 'Bust'."""
    summe, weich = karte_hinzufuegen(0, 0, startkarte)
    while muss_ziehen(summe, weich, h17):
        summe, weich = karte_hinzufuegen(summe, weich, ziehe_karte())
    return "Bust" if summe > 21 else summe


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

def simuliere(startkarte, n, decks, h17, rng):
    zaehler = {e: 0 for e in ERGEBNISSE}

    if decks == 0:
        # Unendlich viele Decks: Ziehen mit Zurücklegen
        def ziehe_karte():
            return rng.choice(DECK_13)

        for _ in range(n):
            zaehler[dealer_spielen(startkarte, ziehe_karte, h17)] += 1
    else:
        # Endlicher Schuh: Startkarte entnehmen, dann ohne Zurücklegen ziehen
        basis = DECK_13 * 4 * decks
        basis.remove(startkarte)
        for _ in range(n):
            schuh = basis.copy()

            def ziehe_karte():
                i = rng.randrange(len(schuh))
                schuh[i], schuh[-1] = schuh[-1], schuh[i]
                return schuh.pop()

            zaehler[dealer_spielen(startkarte, ziehe_karte, h17)] += 1

    return {e: zaehler[e] / n for e in ERGEBNISSE}


# ---------------------------------------------------------------------------
# Exakte Werte (nur für unendlich viele Decks)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def exakt_ab(summe, weiche_asse, h17):
    """Exakte Endverteilung ab einem Handzustand, als Tupel in Reihenfolge ERGEBNISSE."""
    if summe > 21:
        return (0, 0, 0, 0, 0, 1)
    if not muss_ziehen(summe, weiche_asse, h17):
        verteilung = [0] * 6
        verteilung[summe - 17] = 1
        return tuple(verteilung)
    verteilung = [0.0] * 6
    for karte in DECK_13:
        teil = exakt_ab(*karte_hinzufuegen(summe, weiche_asse, karte), h17)
        for i in range(6):
            verteilung[i] += teil[i] / 13
    return tuple(verteilung)


def exakt(startkarte, h17):
    werte = exakt_ab(*karte_hinzufuegen(0, 0, startkarte), h17)
    return dict(zip(ERGEBNISSE, werte))


# ---------------------------------------------------------------------------
# Ausgabe
# ---------------------------------------------------------------------------

def tabelle_drucken(titel, daten):
    kopf = "Start |" + "".join(f"{str(e):>9}" for e in ERGEBNISSE)
    print(f"\n{titel}")
    print(kopf)
    print("-" * len(kopf))
    for karte in STARTKARTEN:
        zeile = "".join(f"{100 * daten[karte][e]:8.2f}%" for e in ERGEBNISSE)
        print(f"{name(karte):>5} |{zeile}")


def main():
    parser = argparse.ArgumentParser(description="Endverteilung des Blackjack-Dealers (Monte-Carlo)")
    parser.add_argument("-n", type=int, default=10000, help="Simulationen pro Startkarte (Standard: 10000)")
    parser.add_argument("--decks", type=int, default=0, help="Anzahl Decks, 0 = unendlich (Standard: 0)")
    parser.add_argument("--h17", action="store_true", help="Dealer zieht auf Soft 17 (Standard: steht)")
    parser.add_argument("--seed", type=int, default=None, help="Zufalls-Seed für reproduzierbare Ergebnisse")
    parser.add_argument("--csv", type=str, default=None, help="Ergebnisse zusätzlich als CSV speichern")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    sim = {k: simuliere(k, args.n, args.decks, args.h17, rng) for k in STARTKARTEN}

    deck_text = "unendlich viele Decks" if args.decks == 0 else f"{args.decks} Deck(s)"
    regel_text = "H17 (zieht auf Soft 17)" if args.h17 else "S17 (steht auf Soft 17)"
    print(f"Simulation: {args.n} Durchläufe je Startkarte, {deck_text}, {regel_text}")

    tabelle_drucken("Simulierte Endverteilung des Dealers", sim)

    ex = None
    if args.decks == 0:
        ex = {k: exakt(k, args.h17) for k in STARTKARTEN}
        tabelle_drucken("Exakte Endverteilung (zum Vergleich)", ex)
        max_abw = max(abs(sim[k][e] - ex[k][e]) for k in STARTKARTEN for e in ERGEBNISSE)
        print(f"\nGrößte Abweichung Simulation vs. exakt: {100 * max_abw:.2f} Prozentpunkte")

    # Standardfehler einer Häufigkeit p bei n Versuchen: sqrt(p(1-p)/n), maximal bei p = 0,5
    se_max = math.sqrt(0.25 / args.n)
    print(f"Maximaler Standardfehler bei n = {args.n}: {100 * se_max:.2f} Prozentpunkte "
          f"(95%-Intervall ca. ± {196 * se_max:.2f} Prozentpunkte)")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            kopf = ["Startkarte"] + [f"sim_{e}" for e in ERGEBNISSE]
            if ex:
                kopf += [f"exakt_{e}" for e in ERGEBNISSE]
            w.writerow(kopf)
            for k in STARTKARTEN:
                zeile = [name(k)] + [f"{sim[k][e]:.4f}" for e in ERGEBNISSE]
                if ex:
                    zeile += [f"{ex[k][e]:.4f}" for e in ERGEBNISSE]
                w.writerow(zeile)
        print(f"CSV gespeichert: {args.csv}")


if __name__ == "__main__":
    main()
