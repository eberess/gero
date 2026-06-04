# google-map-tools

Agent Google Maps pour le robot d'accueil Terminal 2F — CDG Roissy.
Position par défaut du robot : **Terminal 2F** (lat 49.0052, lng 2.5770).

---

## Endpoints API

| API | Méthode | URL |
|---|---|---|
| Places — Recherche proximité | `POST` | `https://places.googleapis.com/v1/places:searchNearby` |
| Places — Recherche texte | `POST` | `https://places.googleapis.com/v1/places:searchText` |
| Places — Détails | `GET` | `https://places.googleapis.com/v1/places/{place_id}` |
| Géocodage | `GET` | `https://maps.googleapis.com/maps/api/geocode/json` |
| Géocodage inverse | `GET` | `https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}` |
| Itinéraire | `POST` | `https://routes.googleapis.com/directions/v2:computeRoutes` |
| Matrice de distances | `GET` | `https://maps.googleapis.com/maps/api/distancematrix/json` |

Authentification : header `X-Goog-Api-Key` (Places, Routes) — paramètre `key` (Géocodage, Distance Matrix).

---

## Tools disponibles

| Tool | Description |
|---|---|
| `search_nearby_places` | Trouve des lieux à proximité filtrés par type (toilettes, restaurant, ATM…) |
| `search_places_text` | Recherche un lieu par nom ou description |
| `get_place_details` | Détails complets d'un lieu : horaires, téléphone, accessibilité |
| `geocode_address` | Convertit un nom de terminal ou adresse en coordonnées GPS |
| `reverse_geocode` | Convertit des coordonnées GPS en adresse lisible |
| `compute_route` | Calcule un itinéraire à pied avec étapes de navigation |
| `compute_route_matrix` | Compare les distances/durées vers plusieurs destinations en batch |

---

## Questions de test

### `search_nearby_places`
1. Où sont les toilettes les plus proches ?
2. Y a-t-il un distributeur de billets près d'ici ?
3. Je cherche un café ou une boulangerie ouverts maintenant
4. Y a-t-il une pharmacie à proximité ?
5. Je cherche une boutique de vêtements ou un cadeau à offrir
6. Où puis-je louer une voiture ?
7. Où est la station de taxi la plus proche ?
8. Y a-t-il un fast-food ou un sandwich shop près d'ici ?
9. Je cherche un hôtel autour de l'aéroport
10. Où est l'arrêt de navette ou de bus le plus proche ?

### `search_places_text`
1. Où est le salon Air France Terminal 2F ?
2. Où est le comptoir Avis location de voiture ?
3. Où est le bureau des objets trouvés ?
4. Où est le retrait des bagages Terminal 2F ?
5. Où est l'accès au RER B depuis le Terminal 2F ?

### `get_place_details`
1. Le salon Air France 2F est-il ouvert en ce moment ? Quels sont ses horaires ?
2. Le restaurant Olivine est-il accessible en fauteuil roulant ?
3. Quel est le numéro de téléphone du Courtyard Marriott CDG ?
4. Quel est le site web du salon Air France 2F ?
5. Quelle est la note et combien d'avis a le Bistro Demoiselle ?

### `geocode_address`
1. Où se trouve le Terminal 1 ?
2. Où est le Terminal 2E ?
3. Où est la gare RER CDG ?
4. Où est le Hall M de CDG ?
5. Où est Roissypole ?

### `reverse_geocode`
1. Où suis-je exactement en ce moment ?
2. Quel est le nom de la zone où se trouve le robot ?
3. Quelle est l'adresse complète du Terminal 2F ?
4. À quel terminal suis-je affecté ?
5. Quelle est l'adresse postale de ma position actuelle ?

### `compute_route`
1. Comment rejoindre le Terminal 1 à pied depuis ici ?
2. Combien de temps faut-il pour marcher jusqu'au Terminal 2E ?
3. Donne-moi les étapes pour aller au salon Air France 2E Hall L
4. Comment rejoindre le Terminal 2G depuis ici ?
5. Quel est le chemin à pied jusqu'à la gare RER CDG ?

### `compute_route_matrix`
1. Qu'est-ce qui est le plus proche — le Terminal 2E ou le Terminal 1 ?
2. Quel salon Air France est le plus rapide à atteindre depuis le Terminal 2F ?
3. À quelle distance suis-je de chacun des terminaux de CDG ?
4. Qu'est-ce qui est le plus près — la gare RER ou la station de taxi ?
5. Compare les temps de marche vers le Terminal 2E, 2G et Terminal 1
