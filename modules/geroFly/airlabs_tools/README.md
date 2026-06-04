# CDG Flight Assistant

Agent IA pour interroger l'aéroport Charles de Gaulle (CDG / Roissy) via l'API Airlabs.

## Lancement

```bash
uv run flight-tools
```

## Questions de test — CDG Roissy

### Tableau des départs / arrivées
- Quels sont les prochains départs depuis CDG ?
- Montre-moi les arrivées à Roissy dans l'heure
- Quels vols partent de CDG ce soir ?
- Donne-moi les 10 prochains vols au départ de Charles de Gaulle

### Vols en cours dans les airs
- Quels avions sont actuellement en vol au départ de CDG ?
- Combien de vols sont en route vers Roissy en ce moment ?
- Montre-moi le trafic aérien en temps réel autour de CDG

### Retards
- Est-ce qu'il y a des retards à CDG en ce moment ?
- Quels vols au départ de Roissy ont plus de 30 minutes de retard ?
- Y a-t-il des arrivées retardées à CDG ?

### Statut d'un vol spécifique
- Quel est le statut du vol AF1234 ?
- Où en est le vol BA303 ?
- Le vol LH1234 est-il à l'heure ?

### Informations aéroport & compagnies
- Donne-moi les infos sur l'aéroport CDG
- Combien de pistes y a-t-il à Roissy ?
- Parle-moi d'Air France
- Quelle est la taille de la flotte d'Air France ?

---

## Airlabs API v9 — Tous les endpoints disponibles

  Base URL : https://airlabs.co/api/v9/
  Formats : JSON (défaut), XML (.xml), CSV (.csv)
  Params communs : api_key (obligatoire), _fields (sélection de champs), _view=array

  ---
  Temps réel

  /flights — Positions live des avions en vol

  Filtres : bbox, zoom, hex, reg_number, airline_iata/icao, flight_iata/icao/number, dep_iata/icao,
  arr_iata/icao, flag

  Champs retournés :
  - Position : lat, lng, alt, dir, speed, v_speed
  - Avion : hex, reg_number, aircraft_icao, squawk, flag
  - Vol : flight_iata, flight_icao, flight_number, airline_iata, airline_icao
  - Aéroports : dep_iata/icao, arr_iata/icao
  - status (scheduled / en-route / landed), updated (timestamp dernier signal)

  /schedules — Tableau des vols (départs / arrivées)

  Filtres obligatoires (au moins un) : dep_iata/icao, arr_iata/icao, airline_iata/icao,
  flight_iata/icao
  Options : limit (max 1000 / 200 / 50 free), offset

  Champs : vol complet avec dep_time, dep_estimated, dep_actual, arr_time, arr_estimated, arr_actual
  (+ variantes _ts, _utc), dep_terminal, dep_gate, arr_terminal, arr_gate, arr_baggage, duration,
  dep_delayed, arr_delayed, status, codeshares (cs_*)

  /flight — Statut d'un vol spécifique

  Filtre obligatoire : flight_iata ou flight_icao

  Champs : tout le schedule + position live (lat/lng/alt/speed) + données avion (model, manufacturer,
  msn, type, engine, engine_count, built, age)

  /delays — Vols retardés

  Paramètres obligatoires : delay (minutes, > 30), type (departures ou arrivals)
  Filtres : dep_iata/icao, arr_iata/icao, airline_iata/icao, flight_iata/icao/number
  Limit : max 500 (50 free), offset

  Champs : identiques à /schedules + delayed (retard en minutes)

  /alert — Webhooks de suivi de vol

  - Listen : crée un listener avec webhook_url + filtres (airline, flight, dep/arr
  airport+date+heure). Retourne un listener_id
  - Unlisten : supprime via listener_id
  - Payload webhook : push automatique sur chaque changement avec changed[] (liste des champs
  modifiés) + snapshot complet du vol

  ---
  Géolocalisation

  /nearby — Aéroports/villes proches

  Paramètres obligatoires : lat, lng, distance (km)
  Retourne : listes airports et cities triées par distance avec distance (km), popularity

  /suggest — Autocomplete

  Paramètre obligatoire : q (3–30 chars, nom d'aéroport / ville / pays)
  Retourne 7 catégories : airports, cities_by_airports, cities, airports_by_cities, countries,
  airports_by_countries, cities_by_countries

  ---
  Bases de données de référence

  /airports — DB des aéroports

  Filtres : iata_code, icao_code, city_code, country_code

  Champs : name, iata_code, icao_code, lat, lng, alt (feet), city, city_code, un_locode, timezone,
  country_code, names (multilingue), runways, departures (vols/an), connections, is_major,
  is_international, website, facebook, twitter, instagram, linkedin, slug

  /airlines — DB des compagnies

  Filtres : iata_code, iata_prefix, iata_accounting, icao_code, callsign, name, country_code

  Champs : name, codes IATA/ICAO, callsign, country_code, iosa_registered, is_scheduled,
  is_passenger, is_cargo, is_international, total_aircrafts, average_fleet_age, accidents_last_5y,
  crashes_last_5y, réseaux sociaux, slug

  /routes — Routes entre aéroports

  Filtres (au moins un) : dep_iata/icao, arr_iata/icao, airline_iata/icao, flight_iata/icao/number
  Limit : max 500 (50 free)

  Champs : codes vol + aéroports + dep_time/arr_time, dep_terminals, arr_terminals, duration, days
  (jours de semaine : sun/mon/…), aircraft_icao, updated

  /fleets — Flotte d'avions

  Filtres : airline_iata/icao, hex, reg_number, msn, flag
  Limit : max 500 (50 free)

  Champs : hex, reg_number, airline_iata/icao, icao/iata (type avion), model, manufacturer, msn,
  line, type, category (J/H/M/L wake turbulence), engine, engine_count, built, age, + position live
  si en vol (lat/lng/alt/dir/speed/v_speed/squawk/last_seen)

  /cities — DB des villes

  Filtres : city_code, country_code

  Champs : name, city_code, un_locode, lat, lng, alt, timezone, country_code, population, names
  (multilingue), wikipedia, slug

  /countries — DB des pays

  Filtres : code (ISO 2), code3 (ISO 3), continent (AF/AN/AS/EU/NA/OC/SA)

  Champs : name, code, code3, population, continent, currency, names (multilingue)

  /timezones — Liste des fuseaux horaires

  Pas de filtre. Champs : timezone, country_code, gmt, dst

  /taxes — Codes taxes aériennes IATA

  Pas de filtre. Champs : code, tax (description)

  ---
  Ce qu'on n'a pas encore dans nos outils

  Par rapport à ce qu'on a implémenté, ces endpoints sont absents du projet actuel :

  ┌──────────────────────┬───────────────────────────────────────────────┐
  │       Endpoint       │          Valeur ajoutée potentielle           │
  ├──────────────────────┼───────────────────────────────────────────────┤
  │ /routes              │ Routes opérées depuis CDG + jours d'opération │
  ├──────────────────────┼───────────────────────────────────────────────┤
  │ /fleets              │ Flotte Air France / avions en service à CDG   │
  ├──────────────────────┼───────────────────────────────────────────────┤
  │ /nearby              │ Aéroports alternatifs autour de Paris         │
  ├──────────────────────┼───────────────────────────────────────────────┤
  │ /suggest             │ Autocomplete pour l'UI                        │
  ├──────────────────────┼───────────────────────────────────────────────┤
  │ /alert               │ Webhook temps réel sur changement de vol      │
  ├──────────────────────┼───────────────────────────────────────────────┤
  │ /cities + /countries │ Enrichissement de contexte géo                │
  └──────────────────────┴───────────────────────────────────────────────┘

---

## Intégration dans un autre agent IA

`airlabs_tools.py` est autonome et ne dépend d'aucun framework. Pour l'intégrer dans un agent existant, copie uniquement ce fichier et importe les deux objets dont tu as besoin :

```python
from airlabs_tools import TOOLS, TOOL_REGISTRY
```

- **`TOOLS`** — liste de schemas OpenAI à passer dans `tools=` lors de l'appel `chat.completions.create`
- **`TOOL_REGISTRY`** — dict `{ nom_outil: fonction }` pour dispatcher les appels retournés par le modèle

### Exemple minimal

```python
import json
from openai import OpenAI
from airlabs_tools import TOOLS, TOOL_REGISTRY

client = OpenAI()
messages = [{"role": "user", "content": "Y a-t-il des retards à CDG ?"}]

response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=TOOLS,
    tool_choice="auto",
)

# dispatcher les tool calls
for tool_call in response.choices[0].message.tool_calls or []:
    fn = TOOL_REGISTRY[tool_call.function.name]
    result = fn(**json.loads(tool_call.function.arguments))
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(result),
    })
```

### Variable d'environnement requise

```
AIRLABS_API_KEY=xxxxxxxxxxxxxxxxxxxx
```

La clé est lue automatiquement par `airlabs_tools.py` via `os.environ`.