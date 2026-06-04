# geroTransport

`geroTransport` est un module d'intelligence décentralisé conçu pour la plateforme humanoïde **Unitree G1**. Il s'intègre dans une architecture orientée agents (Agentic Architecture) où un Modèle de Langage (LLM) utilise ce service comme un outil (*Tool*) pour renseigner les usagers en temps réel.

Ce module est spécifiquement calibré pour opérer dans des environnements complexes à fort trafic, comme le **Terminal 2F de l'aéroport Roissy-Charles de Gaulle (CDG)**.

---

## Philosophie & Architecture

L'objectif de ce dépôt est de fournir une interface standardisée (**FastAPI**) encapsulée dans un conteneur **Docker**. Cette approche offre une flexibilité totale et répond à trois piliers majeurs :

### 1. Abstraction pour le LLM
Le robot utilise un LLM local (sur Jetson Orin NX) faisant office de cerveau. Pour le LLM, `geroTransport` n'est qu'une description textuelle et une URL d'API. Le modèle n'a pas besoin de savoir *comment* récupérer l'information, il sait simplement qu'en appelant ce module, il obtient les données de transport à formuler à l'usager.

### 2. Agnosticisme de Localisation
Grâce à Docker, ce micro-service peut être déployé :
* **En Local :** Directement sur la Jetson Orin NX du robot.
* **À Distance :** Sur un serveur centralisé ou une infrastructure Proxmox dédiée.

### 3. Résilience par "Fallback" (Mode Dégradé)
Les environnements publics comme les terminaux d'aéroports sont sujets aux coupures ou saturations réseau (Wi-Fi/4G/5G). L'architecture de `geroTransport` est pensée pour la redondance :
* **Mode Online (Prioritaire) :** Le robot interroge le serveur externe pour obtenir le temps réel strict (retards du RER B, navettes, trains CDGVal).
* **Mode Offline (Fallback) :** En cas de perte de connexion, le système bascule automatiquement sur l'instance locale du conteneur (embarquée sur le G1), qui distribue les horaires théoriques, les plans et les données semi-statiques pour assurer la continuité du service.

---

## Spécifications Techniques (Conceptuelles)

* **Framework :** FastAPI (Asynchrone pour éviter de bloquer les threads du robot).
* **Conteneurisation :** Docker (Isolation complète des dépendances et de la logique métier).
* **Réseau :** API REST standardisée, compatible avec n'importe quel orchestrateur d'agents (LangChain, CrewAI, scripts Python natifs ou n8n).

---

## Extension du Modèle

Ce dépôt sert de blueprint pour l'écosystème du projet **Géro**. La structure standardisée de `geroTransport` a vocation à être dupliquée pour d'autres modules de services de l'aéroport :
* `geroFlights` (Horaires et portes d'embarquement)
* `geroHotels` (Navettes et disponibilités des hôtels environnants)
* `geroFood` (Restaurations et affluences dans le terminal)
* `geroWeather` (Météo locale et à destination)

---

*Ce projet s'inscrit dans la vision d'une robotique de service souveraine, résiliente et modulaire.*
