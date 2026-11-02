"""Variante 1: File-based Retrieval, Dateien per Textsuche finden.

Aufruf:
    docker compose run --rm app datei_suche.py "Wann hat die Mensa offen?"
    docker compose run --rm app datei_suche.py --woerter "Wann hat die Mensa offen?"

So arbeiten Coding-Agenten wie Claude Code: kein Index, keine Embeddings.
Erst Suchbegriffe überlegen, dann mit grep suchen, dann die passenden
Dateien lesen. Die Suchbegriffe kommen entweder vom Modell (Standard)
oder mit --woerter einfach aus den Wörtern der Frage.
"""

import argparse
import math
import re
import time

from pydantic import BaseModel, Field

from einordnen import schema_von
from llm import MODEL, client
from prompts import lade
from wissen import Treffer, antworten, dokumente, zeigen

MAX_DATEIEN = 3
MAX_BEGRIFFE = 6

# BM25-Parameter: k1 begrenzt den Einfluss der Term-Frequenz (Sättigung),
# b mischt die Dokumentlänge ein. 1.5 und 0.75 sind übliche Werte.
K1 = 1.5
B = 0.75

# Wörter, die in fast jedem Dokument stehen und nichts über das Thema sagen.
STOPPWOERTER = {
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "einer",
    "und", "oder", "ich", "mein", "meine", "meinen", "mir", "mich", "wir",
    "ist", "sind", "bin", "hat", "habe", "kann", "darf", "muss", "wie", "was",
    "wo", "wer", "wann", "warum", "wofür", "noch", "mit", "für", "von", "bis",
    "auf", "aus", "bei", "zu", "zum", "zur", "im", "in", "am", "an", "es",
    "nicht", "viel", "kostet", "oft", "total",
}


class Suchbegriffe(BaseModel):
    begriffe: list[str] = Field(max_length=MAX_BEGRIFFE)


def woerter_der_frage(frage: str) -> list[str]:
    """Die naive Variante: jedes Wort der Frage ist ein Suchbegriff."""
    woerter = re.findall(r"[\wÄÖÜäöüß§-]+", frage.lower())
    return [w for w in woerter if w not in STOPPWOERTER and len(w) > 2]


def begriffe_vom_modell(frage: str) -> list[str]:
    """Das Modell überlegt sich Suchbegriffe, auch Synonyme und Fachwörter."""
    prompt = lade("prompts/suchbegriffe.v1.yaml")
    antwort = client.chat.completions.create(
        model=MODEL,
        temperature=prompt.temperature,
        messages=prompt.nachrichten(frage),
        response_format=schema_von(Suchbegriffe),
        max_tokens=100,
    )
    try:
        return Suchbegriffe.model_validate_json(antwort.choices[0].message.content or "").begriffe
    except ValueError:  # ungültiges JSON oder zu viele Begriffe
        return woerter_der_frage(frage)


def suche(begriffe: list[str], max_dateien: int = MAX_DATEIEN) -> list[Treffer]:
    """Unser grep, verbessert mit BM25 (Teil 4.5): seltene Begriffe zählen mehr.

    Wie vorher: Groß- und Kleinschreibung spielt keine Rolle, ein Begriff
    zählt auch als Teil eines längeren Worts ("karte" findet "Campuskarte").
    Neu ist die Bewertung: Statt der rohen Trefferzahl gewichtet jeder
    Begriff mit seinem IDF (in wenigen Dateien = wertvoll, "F-201" bringt
    mehr als "Raum"), und die Term-Frequenz läuft gegen einen Sättigungswert
    (k1), damit zehnfaches Vorkommen eines Allerweltsworts nicht zehnfach
    zählt. Die Dokumentlänge geht über b ein. Dateien ohne Treffer kommen
    nie zurück, sonst nur die besten max_dateien.
    """
    dokumente_ = dokumente()
    texte = {d: t.lower() for d, t in dokumente_.items()}
    n = len(texte)
    durchschnitt = sum(len(t.split()) for t in texte.values()) / n
    df = {b: sum(1 for t in texte.values() if b.lower() in t) for b in begriffe}
    treffer: list[Treffer] = []
    for datei, text in texte.items():
        laenge = len(text.split())
        wert = 0.0
        for begriff in begriffe:
            tf = text.count(begriff.lower())
            if tf == 0:
                continue
            idf = math.log((n - df[begriff] + 0.5) / (df[begriff] + 0.5) + 1)
            wert += (
                idf * tf * (K1 + 1)
                / (tf + K1 * (1 - B + B * laenge / durchschnitt))
            )
        if wert > 0:
            treffer.append(Treffer(datei, dokumente_[datei], wert))
    treffer.sort(key=lambda t: t.wert, reverse=True)
    return treffer[:max_dateien]


def abrufen(frage: str, nur_woerter: bool = False) -> tuple[list[Treffer], list[str], float]:
    start = time.perf_counter()
    begriffe = woerter_der_frage(frage) if nur_woerter else begriffe_vom_modell(frage)
    treffer = suche(begriffe)
    return treffer, begriffe, time.perf_counter() - start


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("frage", nargs="+")
    parser.add_argument("--woerter", action="store_true", help="Wörter der Frage statt Modell")
    args = parser.parse_args()
    frage = " ".join(args.frage)
    treffer, begriffe, sekunden = abrufen(frage, args.woerter)
    print(f"Suchbegriffe: {begriffe}")
    for t in treffer:
        print(f"  {t.wert:>4.0f}  {t.datei}")
    print()
    zeigen(antworten(frage, treffer, sekunden))
