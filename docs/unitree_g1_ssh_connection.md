# 💻 Accéder au Unitree G1 depuis Windows (SSH + VS Code)

> Se connecter au Jetson Orin du robot depuis un PC Windows pour y déposer et exécuter du code Python.

---

## Objectif

```
💻  PC Windows
   VS Code + Remote SSH
        ↕ Câble Ethernet
   🤖 G1 — Jetson Orin (192.168.123.164)
    coder ET directement sur le robot
```

---

## Adresses réseau du G1 (confirmées)

| Appareil                    | IP fixe              |
| --------------------------- | -------------------- |
| Jetson Orin _(votre cible)_ | `192.168.123.164`    |
| RockChip — locomotion       | `192.168.123.161`    |
| LiDAR                       | `192.168.123.120`    |
| **Votre PC**                | `192.168.123.100` ✅ |

> **Username** : `unitree` — **Mot de passe** : `123`  
> Ces identifiants sont les mêmes sur tous les robots Unitree.

---

## Étape 1 — Configurer l'IP du PC Windows

Branchez le câble Ethernet entre le PC et le robot, puis :

```
Panneau de configuration
  → Réseau et Internet
  → Centre Réseau et partage
  → Modifier les paramètres de la carte
  → Clic droit sur Ethernet → Propriétés
  → Protocole Internet version 4 (TCP/IPv4)
  → Propriétés → Utiliser l'adresse IP suivante

  Adresse IP   : 192.168.123.100
  Masque       : 255.255.255.0
  Passerelle   : (laisser vide)
```

Cliquer **OK** pour valider.

---

## Étape 2 — Vérifier que le robot répond

Ouvrir **PowerShell** ou **CMD** puis :

```poershell
ping 192.168.123.164
```

✅ Si réponses reçues → le PC voit bien le robot  
❌ Si `Request timed out` → vérifier le câble et l'IP du PC

---

## Étape 4 — Installer l'extension Remote SSH

Dans VS Code :

```
① Cliquer sur l'icône Extensions dans la barre gauche (ou Ctrl+Shift+X)
② Rechercher : Remote - SSH
③ Installer l'extension signée Microsoft
```

---

## Étape 5 — Se connecter au robot

```
① Appuyer sur F1 (ou Ctrl+Shift+P)
② Taper : Remote-SSH: Connect to Host
③ Cliquer sur "+ Add New SSH Host..."
④ Entrer exactement : unitree@192.168.123.164
⑤ Choisisser le fichier de config (le premier proposé)
⑥ Cliquer sur "Connect"
⑦ Entrer le mot de passe quand demandé : 123
```

Une nouvelle fenêtre VS Code s'ouvre: **dans le Jetson du robot**. 🎉

---

## Étape 6 — Ouvrir un dossier de travail sur le robot

```
① File → Open Folder
② Choisir /home/unitree/
③ Confirmer avec OK
```

L'explorateur VS Code affiche maintenant les fichiers du robot.

---

## Étape 7 — Créer script Python

```
① File → New File
② Coller le code (ex: parler_g1.py)
③ Sauvegarder avec Ctrl+S
```

Le fichier est **directement sauvegardé sur le robot**.

---

## Étape 8 — Ouvrir un terminal sur le robot

```
Terminal → New Terminal  (ou Ctrl+`)
```

Le terminal est **directement sur le Jetson**.
Installer les dépendances et lancer :

```bash
# Installer les outils nécessaires (une seule fois)
pip install gtts
sudo apt install mpg123 -y

# Lancer script
python3 parler_g1.py
```

---

## Récapitulatif visuel complet

```
┌─────────────────────────────────────┐
│         💻 PC Windows               │
│                                     │
│  IP : 192.168.123.100               │
│  VS Code + Remote SSH               │
└──────────────┬──────────────────────┘
               │ Câble Ethernet
┌──────────────┴──────────────────────┐
│         🤖 Unitree G1               │
│                                     │
│  Jetson Orin : 192.168.123.164      │
│  user : unitree  /  mdp : 123       │
│                                     │
│  Fichiers Python sont ici ✅    │
│  Le terminal s'exécute ici ✅       │
└─────────────────────────────────────┘
```

---

## En cas de problème

| Problème                     | Cause                        | Solution                                                           |
| ---------------------------- | ---------------------------- | ------------------------------------------------------------------ |
| `ping` ne répond pas         | Mauvaise IP sur le PC        | Vérifier l'étape 1                                                 |
| `Connection refused`         | Robot pas encore démarré     | Attendre 30s après allumage                                        |
| Mot de passe refusé          | Mauvais mot de passe         | Essayer `unitree` ou `123`                                         |
| VS Code ne trouve pas l'hôte | SSH non installé sur Windows | Activer OpenSSH dans _Paramètres → Applications → Fonctionnalités_ |

---

> 💡 **Astuce** : Une fois la connexion établie, VS Code la mémorise. La prochaine fois, cliquer simplement sur `unitree@192.168.123.164` dans la liste des hôtes récents.
