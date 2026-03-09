# Politique de Sécurité - Projet GERO

### 1. Politique de Divulgation Responsable
La sécurité des systèmes robotiques est critique. Si vous découvrez une vulnérabilité logicielle ou un vecteur d'exploitation affectant le projet GERO, nous vous demandons de ne pas l'exposer publiquement via les "Issues".
Veuillez signaler toute vulnérabilité en ouvrant une "Advisory" privée via l'onglet Security de GitHub ou en contactant l'équipe de maintenance à l'adresse suivante : el[at]beress[at]gmail[dot]com

### 2. Versions Supportées
Seule la branche principale (`main`) fait l'objet de mises à jour de sécurité actives.

| Version | Supportée |
| :--- | :--- |
| GERO-v1.x | Oui |
| < v1.0 | Non |

### 3. Analyse et Scanning
Le projet utilise les outils suivants pour garantir l'intégrité du code :
* **Secret Scanning :** Détection automatique des clés API ou tokens accidentellement poussés.
* **CodeQL :** Analyse statique du code pour identifier les failles de logique et les vulnérabilités courantes (C++ et Python).

### 4. Sécurité Physique et Hardware
Note : Cette politique concerne uniquement la couche logicielle. Pour tout incident lié au matériel Unitree G1 (batterie, actionneurs, structure), veuillez vous référer aux protocoles de sécurité constructeur et aux pages dédiées du Wiki GERO.
