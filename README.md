# CNAI
Cloud Native AI

## Teil 1

### Aufgabe 1:
The container *modell-laden* depends on *ollama* container. The container *modell-laden* is used to load an ollama model into memory and connects to *ollama* container at ollama:11434. Once the models are downloaded, they're stored in the *ollama* container's volume, and the *modell-laden* container terminates.
The app is started after *modell-laden* was successful and the container then can be used to query the model in the *ollama* container.

### Aufgabe 2:
- ("Wie melde ich mich zu einer Prüfung an?")
  - Time to First Token: 3596 ms
  - Gesamtdauer:         18445 ms
- ("Wann sind die AIN7 Kurse?")
  - Time to First Token: 1023 ms
  - Gesamtdauer:         14297 ms
- ("Wie lautet der Link zur HTWG Website?")
  - Time to First Token: 763 ms
  - Gesamtdauer:         2239 ms


## Teil 2

### Aufgabe 1

| Frage | Modell | TTFT (ms) | Gesamt (ms) | Antwort brauchbar? |
|-------|--------|------------|-------------|-------------------|
| "Wie melde ich mich zu einer Prüfung an?" | qwen2.5:0.5b | 4189 | 5532 | Teilweise: fragt über die spezifische Prüfung |
| "Wann sind die AIN7 Kurse?" | qwen2.5:0.5b | 221 | 1926 | Nein: halluziniert, Thema nicht erkannt |
| "Wie lautet der Link zur HTWG Website?" | qwen2.5:0.5b | 200 | 1084 | Nein: falscher Link (htwg.conic.at) |
| "Wie melde ich mich zu einer Prüfung an?" | llama3.2:3b | 930 | 11361 | Teilweise: plausibel aber Details erfunden |
| "Wann sind die AIN7 Kurse?" | llama3.2:3b | 817 | 13550 | Teilweise: keine konkrete Antwort, aber ehrlich (verweist auf Website) |
| "Wie lautet der Link zur HTWG Website?" | llama3.2:3b | 743 | 3924 | Nein: falscher Link (htwk.de) |

### Aufgabe 2
**"Ist die HTWG Konstanz eine private oder eine staatliche Hochschule?"**

============================================================

```pwsh
Hallo!

Die Hochschule für Technologie, Wirtschaft und Gesellschaft (HTWG) Konstanz ist eine staatliche Hochschule, die von der Landesregierung Baden-Württemberg gefördert wird.

Modell:              llama3.2:3b @ http://ollama:11434/v1
Time to First Token: 11630 ms
Gesamtdauer:         15452 ms
Zeichen Antwort:     177
```

============================================================

```pwsh
HTWG Konstanz ist auffallend empfehlenswert und ist eine staatliche Hochschule.

Modell:              qwen2.5:0.5b @ http://ollama:11434/v1
Time to First Token: 266 ms
Gesamtdauer:         727 ms
Zeichen Antwort:     79
```

============================================================

## Teil 3

### **Sampling**

#### Aufgabe 1

```pwsh
> docker compose run --rm app sampling.py
...
Modell: llama3.2:3b

Prompt: Erfinde einen Namen für ein neues Gericht in der Mensa. Antworte nur mit dem Namen.

Temperature 0.0: 1 verschiedene Antworten bei 5 Durchläufen
  - 5× "Sonnenblume"

Temperature 0.7: 4 verschiedene Antworten bei 5 Durchläufen
  - 2× "Sonnenblume"
  - 1× "Sunna-Schwarzpulver"
  - 1× "Sunriser"
  - 1× "Solara Frittata"

Temperature 1.2: 5 verschiedene Antworten bei 5 Durchläufen
  - 1× "Floraisonstier" oder "Fruchtkaleido"
  - 1× "TurboTorte"
  - 1× Bayerischer Blumenhain
  - 1× Tuscan Sunset Salad
  - 1× TerraSaison
```

#### Aufgabe 2
Es liegt an Caching, eine niedrige Temperature und ein fester Seed für den Zufallsgenerator. Eine Garantie gibt es trotzdem nicht, weil selbst die Hardware das Ergebnis beeinflussen kann.

#### Aufgabe 3
Die Abkürzung HTWG wird aus zwei Gründen nicht korrekt aufgelöst:

1. Bei niedriger Temperatur wiederholt das Modell die falsche Auflösung immer wieder, weil es nur das wahrscheinlichste Token auswählt und der Fehler dadurch stabil bleibt.
2. Je höher die Temperatur, desto mehr halluziniert das Modell, weil es beim Sampling auch unwahrscheinlichere Wörter auswählt und versucht, die Lücken mit etwas zu füllen, das plausibel klingt, aber nicht korrekt ist.

Also der Fehler bei Temperatur 0 kommt aus den Trainingsdaten (das Modell hat die Abkürzung nie korrekt gelernt) während die zusätzlichen Fehler bei höheren Temperaturen durch das Sampling entstehen.

### **Token**

#### Aufgabe 1

```pwsh
> docker compose run --rm app tokens.py
...
Modell: qwen2.5:0.5b

Deutsch    69 Tokens für 21 Wörter
Englisch   53 Tokens für 21 Wörter

Deutsch braucht 16 Tokens mehr (+30%).
```

#### Aufgabe 2

```pwsh
docker compose run --rm app tokens.py
...
Modell: qwen2.5:0.5b

Deutsch    82 Tokens für 14 Wörter
Englisch   59 Tokens für 29 Wörter

Deutsch braucht 23 Tokens mehr (+39%).
```

## Teil 4
