# Standortwettbewerb – wer vorwegnimmt, gewinnt – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-wettbewerbsstandort-demo.streamlit.app/)**

Fünftes Stück der **Standortplanungs-Linie** der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations Research und Machine Learning", Kind von [standortplanung-demo](https://github.com/sebastian-hanisch/standortplanung-demo) (Standortproblem ohne Kapazität):
anders als die Fall-Demos im Portfolio (ein Anwendungsfall, mehrere Verfahren im Vergleich) zeigt diese Demo **ein** Modell – **Standortwettbewerb zwischen einem Führer und einem Folger** ((r|p)-Centroid, Stackelberg) – an einem wachsenden Beispiel.
Bisher wählte ein Planer Standorte allein. Hier zieht ein **Führer** zuerst ($p$ Standorte), danach antwortet ein **Folger** ($r$ Standorte): jeder Kunde geht zum näheren Standort, bei Gleichstand teilen sie die Nachfrage. Wer zuerst zieht, muss die Antwort **vorwegnehmen** – wer nur „gute“ Standorte wählt (kleinste Wegesumme, p-Median), verschenkt Nachfrage.

**Einordnung in die Reihe (die Kanten des Graphen):** Kind von `standortplanung-demo` (dieselben Knoten als Standorte, aber ein Gegenspieler antwortet); Nachbarn `p-center-demo` und `standort-bestand-demo` (andere Ziele/Kosten, kein Wettbewerb). Zu den Spieltheorie-Demos des Portfolios: [stackelberg-demo](https://github.com/sebastian-hanisch/stackelberg-demo) behandelt Führer/Folger bei der **Torwahl von Lkw**, nicht den Standortwettbewerb; [nash-demo](https://github.com/sebastian-hanisch/nash-demo) zeigt Gleichgewichte allgemein; `ems_demo` (Max-Coverage) ähnelt der Folger-Antwort in anderer Kulisse.
```
standortplanung-demo (UFL, Wurzel: Fixkosten + Transport)                               [gebaut]
  ├─ kapazitierte-standortplanung-demo (Kapazität + Single-Sourcing, Lagrange)           [gebaut]
  ├─ p-center-demo (Maximum statt Summe: Farthest-first, exakt per Überdeckung)          [gebaut]
  ├─ standort-bestand-demo (Bestandskosten je Lager, Risk Pooling)                       [gebaut]
  ├─ wettbewerbsstandort-demo (Führer und Folger, (r|p)-Centroid)                        [dieses Stück]
  └─ p-hub-median-demo (Hub-Standorte mit Rabatt, Single Allocation)                     [gebaut]
```

## Modell

$n$ Knoten mit Nachfrage $w_j$; Standorte können nur an Knoten eröffnet werden. Der Führer wählt $L$ ($|L|=p$), der Folger antwortet mit $F$ ($|F|=r$, andere Knoten). Jeder Kunde geht zum näheren Standort, bei Gleichstand teilt sich die Nachfrage. Verglichen werden: der **Führer, der den Folger ignoriert** (p-Median, kleinste gewichtete Wegesumme), **Greedy** und **Swap-Lokalsuche** (beide gegen die exakte Antwort des Folgers) und der **optimale Führer** (max-min, alle $p$-Mengen aufgezählt). Bei $p=r$ werden zusätzlich alle **reinen Nash-Gleichgewichte** aufgezählt und **abwechselnde Bestantworten** simuliert.

## Ergebnis (Zahlen aus den Tests)

Jede hier genannte Zahl ist in `tests/test_claims.py` belegt: Beispielnetze über ihre Seeds, Verteilungen über 40 feste Netze (Seeds ab 100000), das Raster über 20 feste Netze, die Straße. Standard: 14 Knoten, $p=r=2$, Seed 1. Anteile sind in **Halbeinheiten** ganzzahlig gezählt (Sieg = doppelte Nachfrage, Gleichstand = einfache) – exakt und auf allen Plattformen dieselben; die Antwort des Folgers ist immer exakt (Aufzählung aller $r$-Mengen).

**Standardnetz.** Der p-Median-Führer (Knoten 7, 13) behält **45,5 %** der Nachfrage; der optimale Führer (Knoten 3, 13) **54,5 %**. Es gibt **kein reines Gleichgewicht**: abwechselnde Bestantworten laufen im Kreis (Wiederkehr nach 8 Zügen).

**Über 40 Netze** ($p=r=2$): p-Median-Führer im Mittel **46,1 %** (28,6–63,6), optimaler Führer **51,4 %** (45,3–63,6) – Vorwegnehmen bringt **5,3 Prozentpunkte**. Zufällige Führer 26,7 %, die schlechtesten 6,2 %. Der p-Median-Führer ist nur in **14 von 40** Netzen zugleich optimal. Greedy erreicht 49,2 % (optimal in 21 von 40, schlechtester Rückstand 11,7 Punkte), Swap-Lokalsuche 50,9 % (optimal in 34, Rückstand bis 4,7). Bei $p=r=1$ ist der Gewinn durch Vorwegnehmen klein (1,7 Punkte, p-Median in 31/40 optimal); bei $p=r=3$ groß (5,7 Punkte, nur 10/40).

**Reine Gleichgewichte sind selten, sobald jede Seite mehrere Standorte hat** (bei einem Standort je Seite haben gut die Hälfte der Netze eines). Bei $p=r=1/2/3$ existieren sie in **21 / 8 / 10 von 40** Netzen; abwechselnde Bestantworten ab der p-Median-Lösung kommen in 18 / 6 / 5 zur Ruhe und laufen in 22 / 34 / 34 im Kreis. Größere Netze haben noch seltener eines: bei $p=r=2$ (20 feste Netze) sinkt die Zahl der Netze mit einem Gleichgewicht von **16** (8 Knoten) über 8 (10 Knoten) und 2 (18 Knoten) auf **0** (22 Knoten).

**Asymmetrie: wer mehr Standorte hat, gewinnt.** Bei $p=2,r=1$ behält der optimale Führer im Mittel 72,4 % (in allen 40 Netzen mindestens die Hälfte); bei $p=1,r=2$ nur 23,5 % (in keinem Netz die Hälfte). Über alle Kombinationen (20 feste Netze, p-Median / optimal):

| p \ r | 1 | 2 | 3 |
|---|---|---|---|
| 1 | 49,6 / 51,9 | 20,5 / 24,6 | 10,4 / 14,0 |
| 2 | 68,5 / 71,7 | 44,1 / 50,3 | 30,0 / 36,1 |
| 3 | 75,3 / 80,4 | 58,5 / 65,5 | 47,1 / 53,4 |

**Die Straße (Hotelling).** Bei $p=r=1$ steht der optimale Führer in der Mitte (z. B. 9 Knoten: Knoten 5, 55,6 %) – p-Median und Optimum fallen zusammen, und es gibt stets ein Gleichgewicht (bei jeder getesteten Größe von 8 bis 24 Knoten, $p=r\in\{1,2,3\}$). Bei $p=r=3$ (14 Knoten) versagt **Greedy** aber deutlich: 21,4 % gegen das Optimum 53,6 % – erst Swap findet es (7 Züge); 20 Gleichgewichte existieren.

**Gleichstandsregel.** Bekäme der Führer bei Gleichstand die ganze Nachfrage statt der Hälfte, ändert sich das Bild kaum: $p=r=2$ 46,2 % / 51,5 % (statt 46,1 / 51,4), $p=r=3$ 47,8 % / 53,5 % (statt 47,7 / 53,5).

## Was nicht funktioniert hat / Vorab-Hypothesen

Vor dem Bau standen mehrere Vermutungen im Plan (Modellprüfung der Erweiterung E3). Gemessen:

- **„Der Erste ist im Nachteil“ – widerlegt.** Der optimale Führer behält in 24 von 40 Netzen mehr als die Hälfte (bei $p=r=2$); bei $p>r$ sogar immer.
- **„Der p-Median-Führer liegt ungefähr richtig“ – teilweise widerlegt.** Er ist nur in 14 von 40 Netzen ($p=r=2$) selbst optimal, verliert im Mittel 5,3 Punkte; bei $p=r=3$ sind es 5,7 Punkte.
- **„Ohne Reihenfolge gibt es meist kein Gleichgewicht“ – bestätigt ab zwei Standorten je Seite und verstärkt sich mit der Netzgröße.** Reine Gleichgewichte existieren bei $p=r=2$ und $3$ nur in 8 bzw. 10 von 40 Standardnetzen (bei $p=r=1$ in 21), und ihre Zahl sinkt mit wachsendem $n$ auf 0.
- **„Eine naheliegende Heuristik (Greedy) genügt“ – widerlegt, besonders auf der Straße.** Greedy verfehlt dort bei $p=r=3$ das Optimum um 32 Punkte; die Swap-Lokalsuche danach behebt es vollständig in den gemessenen Fällen.
- **„Die Gleichstandsregel ist entscheidend“ – widerlegt.** Ob der Führer Gleichstände ganz oder halb bekommt, ändert die Zahlen kaum.
- **Bestätigt:** wer mehr Standorte hat als der Gegner, gewinnt deutlich mehr als die Hälfte; auf der Straße gewinnt (mit einem Standort je Seite) immer die Mitte, und es gibt dort stets ein Gleichgewicht.

## Grenzen (was die Demo nicht zeigt)

Standorte nur an Knoten (kein kontinuierlicher Raum/Hotelling auf der Linie oder in der Ebene), nächster Standort gewinnt ohne Preise oder Attraktivität (kein Gravitationsmodell), genau ein Folger mit einer Antwort (keine mehrstufigen Spiele), keine Standortkosten, Aufzählung nur bis 24 Knoten und 3 Standorte je Seite, erzeugte Netze ohne Fremddaten.
Die abwechselnden Bestantworten sind eine Veranschaulichung, kein Verfahren, um Gleichgewichte zu finden (sie erreichen längst nicht jedes existierende Gleichgewicht).

## Dateien

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Oberfläche: Selbst probieren, Führer-Verfahren im Vergleich, Zug um Zug, Experimente auf Abruf |
| `cmp_scenario.py` | Netze (gleichverteilt, Cluster, Straße), SplitMix64-Zufallsstrom (Kopie aus den Vorgängern) |
| `cmp_game.py` | Anteile in Halbeinheiten, exakte Bestantwort (Aufzählung), Zulässigkeit |
| `cmp_leader.py` | p-Median-Führer, Greedy, Swap-Lokalsuche, exaktes Führer-Optimum |
| `cmp_equilibrium.py` | reine Nash-Gleichgewichte, abwechselnde Bestantworten (Gleichgewicht/Zyklus) |
| `cmp_evaluation.py`, `cmp_visualization.py` | Analyse, Verteilungen, Raster über (p, r); Karte, Anteilsbalken, Streudiagramm, Wärmekarte |
| `cmp_presets.py`, `cmp_constants.py` | Presets, Permalink, Regler-Grenzen, feste Seeds |
| `tests/` | 178 Tests: Szenario, Spiel und Führer-Verfahren gegen unabhängige reine Python-Implementierungen, Gleichgewichte, Presets, Zahlen (`test_claims.py`), App |

Lokal starten: `pip install -r requirements.txt`, dann `streamlit run app.py`; Tests: `pip install -r requirements-dev.txt`, dann `python -m pytest tests`.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Standortplanung: von der Wahl zum Wettbewerb](https://sebastianhanisch.net/konzepte-standortplanung.html).
