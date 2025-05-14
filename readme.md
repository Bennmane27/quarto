# IA Quarto Client

## Matricules
- 12345
- 67890

## Stratégie
Cette IA utilise une stratégie améliorée pour le jeu Quarto :

1. **Début de jeu** : S'il n'y a pas de pion en attente, l'IA choisit aléatoirement un pion disponible à donner à l'adversaire.

2. **Coup gagnant** : L'IA vérifie d'abord si le pion actuel peut être placé pour gagner immédiatement. Si oui, elle place le pion à cette position et choisit un pion aléatoire pour l'adversaire.

3. **Coup défensif** : Si aucun coup gagnant n'est possible, l'IA évite de donner un pion qui permettrait à l'adversaire de gagner immédiatement.

4. **Coup par défaut** : Si aucune des stratégies ci-dessus n'est applicable, l'IA place le pion sur une case vide aléatoire et choisit un pion non-dangereux pour l'adversaire.

5. **Gestion des erreurs** : L'IA détecte correctement les pièces disponibles et évite de référencer celles qui ont déjà été jouées.

## Bibliothèques utilisées
- Python 3 (asyncio, argparse, json, random)

## Usage
1. Assurez-vous d'avoir Python 3 installé.
2. Dans un terminal PowerShell :
   ```pwsh
   cd C:\Users\Flutter\Desktop\Karina quentoin\quarto
   python client.py --host <IP_SERVEUR> --port-server <PORT_SERVEUR> --port-client <PORT_CLIENT> --name <NOM_BOT> --matricules 12345 67890
   ```
3. Alternative : utilisez le script PowerShell pour lancer automatiquement les deux IA :
   ```pwsh
   .\start_players.ps1
   ```

## Structure des fichiers
- `client.py` : client IA (connexion, abonnement, gestion des requêtes `ping` et `play`).
- `strategy.py` : génération intelligente de coups avec analyse du plateau.
- `players.json` : configuration des clients IA.
