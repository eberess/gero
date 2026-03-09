# Project GERO

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation](https://img.shields.io/badge/docs-Wiki-brightgreen.svg)](https://github.com/eberess/GERO/wiki)

> **Humanoid Intelligence for Complex Environment Navigation & Interaction.**

GERO (Ground Expert Robot Operator) est un projet de R&D axé sur le déploiement opérationnel du robot **Unitree G1 Edu**. L'objectif est de pousser les limites de l'interaction humain-robot (HRI), de la vision par ordinateur en milieu dense et de la manipulation tactile fine.

---

## Table des Matières

1. [Vision du Projet](#-vision-du-projet)
2. [Stack Technique](#-stack-technique-lab-standards)
3. [Architecture Logicielle](#-architecture-logicielle)
4. [Feuille de Route (Roadmap)](#-feuille-de-route-roadmap)
5. [Structure du Dépôt](#-structure-du-dépôt)
6. [Installation & Usage](#-installation--usage)

---

## Vision du Projet
Développer une couche logicielle robuste permettant à un robot humanoïde de :
* **Percevoir :** Analyse sémantique de l'espace et reconnaissance de flux.
* **Interagir :** Communication multimodale (audio/visuel) et retour tactile.
* **Opérer :** Navigation autonome sécurisée dans des zones à haute densité de passage.

## Stack Technique
* **Hardware :** Unitree G1 Edu (U6 High-Performance 100 TOPS).
* **Physique & Simulation :** MuJoCo (pour la validation des algorithmes de marche et d'interaction).
* **Communication :** DDS (Data Distribution Service) via Unitree SDK 2.
* **IA :** Architecture modulaire pour l'intégration de LLM et de Vision Transformers.

## Architecture Logicielle
Le projet GERO repose sur une architecture découplée pour garantir la sécurité et la performance temps-réel :
* **Layer 1 (Perception) :** Traitement des flux LiDAR et caméras via Vision Transformers.
* **Layer 2 (Decision) :** Moteur logique gérant les états de mission et l'interaction HRI.
* **Layer 3 (Control) :** Interface avec `unitree_sdk2` pour la conversion des commandes en mouvements fluides.

## Feuille de Route (Roadmap)
- [ ] **Phase 1 : Simulation (Digital Twin)** : Intégration complète du modèle URDF G1 dans MuJoCo.
- [ ] **Phase 2 : Perception Lab** : Développement des algorithmes de détection d'objets en zones denses.
- [ ] **Phase 3 : HRI & Tactile** : Implémentation du feedback des mains U6 et synthèse vocale.
- [ ] **Phase 4 : Field Tests** : Déploiement en environnement contrôlé (Lab-scale).

## Installation & Usage (Quickstart)

*Note : L'environnement est entièrement conteneurisé.*

```bash
# Clone le dépôt
git clone [git@github.com:eberess/gero.git](git@github.com:eberess/gero.git)

# Build de l'environnement Lab (Docker)
docker build -t gero-lab:latest .
```

## Structure du Dépôt
* `/docs` : Spécifications techniques et Wiki.
* `/simulation` : Environnements virtuels et "Digital Twin" du G1.
* `/src` : Modules de perception, décision et contrôle.
* `/scripts` : Utilitaires de déploiement et Dockerisation.

## Sécurité et Confidentialité
Ce projet suit des protocoles de sécurité stricts. Aucun identifiant réseau ou donnée de capture réelle ne doit être stocké sur ce dépôt public. Référez-vous au fichier `.gitignore` et aux templates de configuration.

> ### Éthique et Conformité
> Le projet GERO est développé dans le respect des directives éthiques sur l'IA et la robotique. Les algorithmes de vision sont conçus pour garantir l'anonymat dans les espaces publics (traitement on-device, aucune conservation de données biométriques).

---
*Ceci est un projet de recherche indépendant. Les mentions de partenaires tiers sont soumises à accord préalable.*