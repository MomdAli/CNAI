"""Teil D: Anfragen an den Campus-Assistenten strukturiert einordnen.

Das Modell soll aus einer Mail drei Dinge herauslesen: das Anliegen,
den Studiengang und eine Frist. Das Ergebnis verarbeitet ein Programm
weiter, es muss also immer die gleiche Form haben.

Aufruf:
    docker compose run --rm app einordnen.py
    docker compose run --rm app einordnen.py "Eure eigene Mail"

Eure Aufgaben stehen bei den TODO-Kommentaren.
"""

import json
import sys
from typing import Literal

from pydantic import BaseModel, ValidationError

from llm import MODEL, client

SYSTEM_PROMPT = (
    "Du ordnest Mails von Studierenden an die HTWG Konstanz ein. "
    "Antworte ausschließlich mit JSON. "
    "anliegen ist pruefung, mensa, bibliothek oder sonstiges. "
    "studiengang ist das Kürzel (z. B. AIN, WIN, MSI) oder null. "
    "frist ist die Frist aus der Mail, so wie sie dort steht, oder null."
)


class Anfrage(BaseModel):
    anliegen: Literal["pruefung", "mensa", "bibliothek", "sonstiges"]
    studiengang: str | None
    frist: str | None

def schema_von(modell: type[BaseModel]) -> dict:
    """Verpackt das JSON-Schema einer Pydantic-Klasse für response_format."""
    return {
        "type": "json_schema",
        "json_schema": {
            "name": modell.__name__.lower(),
            "schema": modell.model_json_schema(),
        },
    }


def einordnen(mail: str, versuche: int = 3) -> Anfrage:
    """Fragt das Modell und gibt eine geprüfte Anfrage zurück."""
    nachricht = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": mail},
    ]
    # TODO 1: Ruft das Modell auf. Wählt eine passende temperature
    #         und übergebt response_format=schema_von(Anfrage).
    for versuch in range(versuche):
        try:
            antwort = client.chat.completions.create(
                model=MODEL,
                messages=nachricht,
                temperature=0.0,
                response_format=schema_von(Anfrage),
            )
            antwort_text = antwort.choices[0].message.content or ""

            # TODO 2: Prüft die Antwort mit Anfrage.model_validate_json(...).
            return Anfrage.model_validate_json(antwort_text)

        except ValidationError as e:
            # TODO 3: Schlägt die Prüfung fehl (ValidationError), versucht es
            #         erneut, höchstens `versuche`-mal. Gebt bei jedem
            #         Fehlversuch eine kurze Meldung aus. Klappt es gar
            #         nicht, werft einen RuntimeError.
            print(f"Validierungsfehler bei Versuch {versuch + 1}/{versuche}: {e}")
            if versuch == versuche - 1:
                raise RuntimeError(
                    f"Konnte nach {versuche} Versuchen keine gültige Antwort erhalten"
                ) from e

    raise RuntimeError("Unerwarteter Fehler in einordnen()")


def auswerten() -> None:
    """Ordnet alle Test-Mails ein und vergleicht mit dem Erwarteten."""
    with open("mails.json", encoding="utf-8") as f:
        faelle = json.load(f)
    richtig = 0
    for fall in faelle:
        ergebnis = einordnen(fall["mail"])
        erwartet = fall["erwartet"]

        # TODO 4: Vergleicht ergebnis mit fall["erwartet"]. Zählt einen
        #         Fall als richtig, wenn das Anliegen stimmt. Gebt für
        #         jeden Fall Mail, Ergebnis und ✓ oder ✗ aus.
        ist_richtig = ergebnis.anliegen == erwartet["anliegen"] and ergebnis.studiengang == erwartet["studiengang"] and ergebnis.frist == erwartet["frist"]
        if ist_richtig:
            richtig += 1

        symbol = "✓" if ist_richtig else "✗"
        print(f"\n{symbol} Mail: {fall['mail'][:60]}...")
        print(f"  Erwartet: {erwartet}")
        print(f"  Ergebnis: {ergebnis.model_dump()}")

    print(f"\n{richtig} von {len(faelle)} Anliegen richtig ({MODEL})")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(einordnen(" ".join(sys.argv[1:])).model_dump_json(indent=2))
    else:
        auswerten()
