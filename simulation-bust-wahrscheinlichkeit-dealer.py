"""
Blackjack: Überkaufwahrscheinlichkeit des Dealers
==================================================
Monte-Carlo-Simulation für
  1. die Zwischenwerte B(12) ... B(16)  (Dealer hat eine "harte" Summe t)
  2. die Gesamttabelle: Überkaufwahrscheinlichkeit je offener Karte (2 ... Ass)

Zur Kontrolle wird zusätzlich der exakte Wert (rekursive Rechnung,
unendlich viele Decks) ausgegeben.

Regeln:
  - Dealer zieht bis einschließlich 16, steht ab 17 (auch bei "Soft 17")
  - Ass zählt 11, solange die Summe dadurch nicht über 21 geht, sonst 1
  - kein "Peek" (Blackjack des Dealers wird nicht vorher geprüft)

Aufruf (Beispiele):
  python blackjack_simulation.py                  # unendlich viele Decks
  python blackjack_simulation.py --decks 6        # Schuh mit 6 Decks
  python blackjack_simulation.py -n 1000000       # mehr Durchläufe = genauer
  python blackjack_simulation.py --diagramm ergebnis.png   # zusätzlich Diagramm speichern
"""

import argparse
import math
import random
from functools import lru_cache

# Kartenwerte: 1 = Ass, 2-9, 10 = Zehn/Bube/Dame/König
KARTEN = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# Wahrscheinlichkeit jeder Karte bei unendlich vielen Decks
P_KARTE = {k: (4 / 13 if k == 10 else 1 / 13) for k in KARTEN}
# Eine "Liste" eines Decks: Zehnerkarten kommen viermal so oft vor
DECK = [1, 2, 3, 4, 5, 6, 7, 8, 9] + [10] * 4


# ----------------------------------------------------------------------
# Hilfsfunktion: eine Karte zur Hand hinzufügen
# ----------------------------------------------------------------------
def karte_hinzu(summe, weich, karte):
    """Gibt die neue (summe, weich) zurück.
    'weich' = True heißt: in der Hand zählt ein Ass gerade als 11."""
    if karte == 1 and summe + 11 <= 21:
        summe += 11
        weich = True
    else:
        summe += karte
    # Überkauft, aber ein Ass zählt noch als 11 -> Ass auf 1 umstellen
    if summe > 21 and weich:
        summe -= 10
        weich = False
    return summe, weich


# ----------------------------------------------------------------------
# Kartenquelle: unendlich viele Decks oder ein echter Schuh
# ----------------------------------------------------------------------
class Schuh:
    def __init__(self, decks):
        self.decks = decks  # 0 = unendlich viele Decks

    def neue_runde(self, entfernte_karten=()):
        """Vor jeder Runde neu mischen; bereits liegende Karten entfernen."""
        if self.decks == 0:
            return
        self.karten = DECK * 4 * self.decks
        for k in entfernte_karten:
            self.karten.remove(k)
        random.shuffle(self.karten)

    def ziehe(self):
        if self.decks == 0:
            return random.choice(DECK)  # Ziehen mit Zurücklegen
        return self.karten.pop()


# ----------------------------------------------------------------------
# Simulation
# ----------------------------------------------------------------------
def dealer_spielt(summe, weich, schuh):
    """Dealer zieht, bis er mindestens 17 hat. True = überkauft."""
    while summe < 17:
        summe, weich = karte_hinzu(summe, weich, schuh.ziehe())
    return summe > 21


def simuliere_offene_karte(offene_karte, n, schuh):
    ueberkauft = 0
    for _ in range(n):
        schuh.neue_runde(entfernte_karten=[offene_karte])
        summe, weich = karte_hinzu(0, False, offene_karte)
        if dealer_spielt(summe, weich, schuh):
            ueberkauft += 1
    return ueberkauft / n


def simuliere_harte_summe(t, n, schuh):
    """B(t): Dealer startet mit harter Summe t (kein Ass, das als 11 zählt).
    Hinweis: Bei endlichem Schuh werden hier keine Startkarten entfernt."""
    ueberkauft = 0
    for _ in range(n):
        schuh.neue_runde()
        if dealer_spielt(t, False, schuh):
            ueberkauft += 1
    return ueberkauft / n


# ----------------------------------------------------------------------
# Exakte Rechnung (unendlich viele Decks) zum Vergleich
# B(t) = Summe über alle Karten k von P(k) * B(t + k)
# ----------------------------------------------------------------------
@lru_cache(maxsize=None)
def B_exakt(summe, weich=False):
    if summe > 21:
        return 1.0
    if summe >= 17:
        return 0.0
    return sum(P_KARTE[k] * B_exakt(*karte_hinzu(summe, weich, k)) for k in KARTEN)


def offene_karte_exakt(karte):
    return B_exakt(*karte_hinzu(0, False, karte))


def konfidenz(p, n):
    """Halbe Breite des 95-%-Konfidenzintervalls"""
    return 1.96 * math.sqrt(p * (1 - p) / n)


# ----------------------------------------------------------------------
# Diagramm für die Arbeit (benötigt matplotlib: pip install matplotlib)
# ----------------------------------------------------------------------
def zeichne_diagramm(namen, werte, gesamt, dateiname):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    BLAU, ORANGE = "#2a78d6", "#eb6834"
    TEXT, TEXT2, GITTER = "#0b0b0b", "#52514e", "#e4e3df"

    farben = [BLAU if n in "23456" else ORANGE for n in namen]
    prozent = [w * 100 for w in werte]

    fig, ax = plt.subplots(figsize=(7, 3.8), dpi=300)
    balken = ax.bar(namen, prozent, color=farben, width=0.68, zorder=3)
    for b, p in zip(balken, prozent):
        ax.text(b.get_x() + b.get_width() / 2, p + 0.8, f"{p:.1f}".replace(".", ","),
                ha="center", va="bottom", fontsize=8, color=TEXT, zorder=4,
                bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor="none"))

    ax.axhline(gesamt * 100, color=TEXT2, linestyle="--", linewidth=1, zorder=2)
    ax.text(9.45, gesamt * 100 + 0.8,
            f"Durchschnitt {gesamt * 100:.1f} %".replace(".", ","),
            ha="right", va="bottom", fontsize=8, color=TEXT2)

    ax.set_xlabel("Offene Karte des Dealers", fontsize=9, color=TEXT)
    ax.set_ylabel("Überkaufwahrscheinlichkeit in %", fontsize=9, color=TEXT)
    ax.set_ylim(0, 50)
    ax.yaxis.grid(True, color=GITTER, linewidth=0.8, zorder=0)
    ax.tick_params(colors=TEXT2, labelsize=8.5, length=0)
    for seite in ("top", "right", "left"):
        ax.spines[seite].set_visible(False)
    ax.spines["bottom"].set_color(TEXT2)

    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=BLAU, label="niedrige Karte (2–6)"),
                       Patch(color=ORANGE, label="hohe Karte (7–A)")],
              loc="upper right", fontsize=8, frameon=False, ncol=2,
              bbox_to_anchor=(1, 1.08))
    fig.tight_layout()
    fig.savefig(dateiname, dpi=300)
    print(f"\nDiagramm gespeichert: {dateiname}")


# ----------------------------------------------------------------------
# Hauptprogramm
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Überkaufwahrscheinlichkeit des Dealers")
    parser.add_argument("-n", type=int, default=200_000,
                        help="Durchläufe pro Wert (Standard: 200000)")
    parser.add_argument("--decks", type=int, default=0,
                        help="Anzahl Decks im Schuh, 0 = unendlich (Standard: 0)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Startwert des Zufallsgenerators (für reproduzierbare Ergebnisse)")
    parser.add_argument("--diagramm", metavar="DATEI", default=None,
                        help="Säulendiagramm als Bild speichern, z. B. --diagramm ergebnis.png")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)
    schuh = Schuh(args.decks)
    n = args.n
    deckinfo = "unendlich viele Decks" if args.decks == 0 else f"{args.decks} Deck(s), vor jeder Runde neu gemischt"

    print("=" * 66)
    print(" Blackjack – Überkaufwahrscheinlichkeit des Dealers")
    print(f" {n:,} Durchläufe pro Wert | {deckinfo}".replace(",", "."))
    print(" Regel: Dealer zieht bis 16, steht ab 17")
    print("=" * 66)

    # --- Teil 1: Zwischenwerte B(t) ---
    print("\nTeil 1: Zwischenwerte B(t) – Dealer hat harte Summe t\n")
    print(f"{'t':>4} | {'Simulation':>10} | {'± 95%-KI':>8} | {'exakt*':>8} | {'Abw.':>7}")
    print("-" * 50)
    for t in range(16, 11, -1):
        p = simuliere_harte_summe(t, n, schuh)
        ex = B_exakt(t)
        print(f"{t:>4} | {p:>10.4f} | {konfidenz(p, n):>8.4f} | {ex:>8.4f} | {p - ex:>+7.4f}")

    # --- Teil 2: Gesamttabelle nach offener Karte ---
    print("\nTeil 2: Überkaufwahrscheinlichkeit nach offener Karte\n")
    print(f"{'offen':>5} | {'Simulation':>10} | {'± 95%-KI':>8} | {'exakt*':>8} | {'Abw.':>7}")
    print("-" * 50)
    gesamt_sim = 0.0
    gesamt_ex = 0.0
    namen, werte = [], []
    for karte in [2, 3, 4, 5, 6, 7, 8, 9, 10, 1]:
        p = simuliere_offene_karte(karte, n, schuh)
        ex = offene_karte_exakt(karte)
        gesamt_sim += P_KARTE[karte] * p
        gesamt_ex += P_KARTE[karte] * ex
        name = "A" if karte == 1 else str(karte)
        namen.append(name)
        werte.append(p)
        print(f"{name:>5} | {p:>10.4f} | {konfidenz(p, n):>8.4f} | {ex:>8.4f} | {p - ex:>+7.4f}")
    print("-" * 50)
    print(f"{'ges.':>5} | {gesamt_sim:>10.4f} | {'':>8} | {gesamt_ex:>8.4f} | {gesamt_sim - gesamt_ex:>+7.4f}")

    print("\n* exakt = rekursive Rechnung für unendlich viele Decks.")
    print("  'ges.' = Überkaufwahrscheinlichkeit insgesamt (gewichtet nach Häufigkeit der offenen Karte).")
    if args.decks:
        print("  Bei endlichem Schuh sind kleine systematische Abweichungen zum exakten Wert normal.")

    if args.diagramm:
        zeichne_diagramm(namen, werte, gesamt_sim, args.diagramm)


if __name__ == "__main__":
    main()
