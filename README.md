# CNAI
Cloud Native AI

## Part 1

### Task 1:
The container *modell-laden* depends on *ollama* container. The container *modell-laden* is used to load an ollama model into memory and connects to *ollama* container at ollama:11434. Once the models are downloaded, they're stored in the *ollama* container's volume, and the *modell-laden* container terminates.
The app is started after *modell-laden* was successful and the container then can be used to query the model in the *ollama* container.

### Task 2:
- ("Wie melde ich mich zu einer Prüfung an?")
  - Time to First Token: 3596 ms
  - Gesamtdauer:         18445 ms
- ("Wann sind die AIN7 Kurse?")
  - Time to First Token: 1023 ms
  - Gesamtdauer:         14297 ms
- ("Wie lautet der Link zur HTWG Website?")
  - Time to First Token: 763 ms
  - Gesamtdauer:         2239 ms


## Part 2

### Task 1


### Task 2
**"Ist die HTWG Konstanz eine private oder eine staatliche Hochschule?"**

============================================================

Hallo!

Die Hochschule für Technologie, Wirtschaft und Gesellschaft (HTWG) Konstanz ist eine staatliche Hochschule, die von der Landesregierung Baden-Württemberg gefördert wird.

Modell:              llama3.2:3b @ http://ollama:11434/v1
Time to First Token: 11630 ms
Gesamtdauer:         15452 ms
Zeichen Antwort:     177

============================================================

HTWG Konstanz ist auffallend empfehlenswert und ist eine staatliche Hochschule.

Modell:              qwen2.5:0.5b @ http://ollama:11434/v1
Time to First Token: 266 ms
Gesamtdauer:         727 ms
Zeichen Antwort:     79

============================================================

## Part 3

## Part 4
