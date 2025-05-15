# Quarto IA – Projet ECAM

Bienvenue sur le projet Quarto IA développé par **Karina** et **Ladifa**.

## Description

Ce projet propose plusieurs intelligences artificielles pour jouer au jeu Quarto, dont :
- **KarinaStrong** : une IA stratégique, robuste et difficile à battre.
- **KarinaUltimate** : une IA très avancée, utilisant des techniques de recherche et d’anticipation poussées.
- **LadifaRandom** : une IA qui joue de façon aléatoire (pour tester la robustesse des autres stratégies).

Le code permet de lancer des parties entre différentes IA, de tester leur performance et d’analyser leur comportement.

## Structure du projet

- `strategy.py` : stratégie de base (aléatoire ou simple).
- `strategy_strong.py` : stratégie avancée, forte et défensive.
- `strategy_ultimate.py` : stratégie ultime, avec anticipation et évaluation poussée.
- `strategy_random.py` : IA totalement aléatoire.
- `client.py` / `client_modular.py` : clients pour communiquer avec le serveur Quarto.
- `start_players.py` / `start_players_modular.py` : scripts pour lancer des parties entre IA.
- `test_strategy.py`, `test_unitaire.py` : tests unitaires pour garantir la robustesse du code.
- `players.json`, `players_modular.json`, `players_ultimate.json` : configurations des joueurs.
- `validate_pieces.py` : utilitaire pour vérifier les pièces restantes.

## Lancer une partie

1. **Installer les dépendances** (Python 3 requis) :
   ```bash
   pip install -r requirements.txt
   ```
   *(si besoin, créer un environnement virtuel)*

2. **Configurer les joueurs** dans le fichier `players_modular.json` ou `players_ultimate.json`.

3. **Démarrer le serveur Quarto** (fourni par l’enseignant ou le projet).

4. **Lancer les IA** :
   ```bash
   python start_players_modular.py
   ```
   ou
   ```bash
   python start_players_ultimate.py
   ```

## Tests unitaires

Pour vérifier la robustesse et la couverture du code :
```bash
python -m unittest test_strategy.py
python -m unittest test_unitaire.py
```

## Auteurs

- **Karina** – 22269@ecam.be
- **Ladifa**

Projet réalisé dans le cadre du cours d’IA à l’ECAM.

---

*Bon jeu et que la meilleure IA gagne !*