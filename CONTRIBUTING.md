# Contribution au Projet GERO

Merci de l'intérêt que vous portez au projet GERO (Unitree G1). Pour maintenir la qualité et la sécurité du système, nous demandons de suivre ces directives.

## Processus de Pull Request
1. Ne poussez jamais directement sur la branche `main`.
2. Créez une branche descriptive (ex: `feature/ia-vision-v1` ou `fix/audio-latency`).
3. Assurez-vous que votre code respecte les standards **PEP 8** (pour Python).
4. La documentation dans le Wiki doit être mise à jour pour chaque nouvelle fonctionnalité.
5. Toute PR doit être approuvée par au moins un mainteneur avant d'être fusionnée.

## Standards de Code
* **Tests :** Chaque nouvelle fonction doit être accompagnée d'un test unitaire.
* **Docker :** Si vous ajoutez une dépendance, mettez à jour le `Dockerfile` en conséquence.
* **Sécurité :** Ne commitez JAMAIS de clés API ou de secrets réseau. Utilisez des variables d'environnement.

## Rapport de Bugs
Utilisez les "Issues" GitHub en fournissant :
* Une description claire du problème.
* Les étapes pour reproduire le bug.
* L'environnement (Version du SDK Unitree, OS, version de MuJoCo).