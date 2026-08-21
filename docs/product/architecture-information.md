# Architecture de l'information
## Principes de navigation
La conception de l'application se fait à partir des tâches des utilisateur
et non à partir des modèles.
## Architecture générale
```text
Gestionnaire d'interventions
│
├-- Tableau de bord
│
├-- Interventions
│   ├-- Liste
│   ├-- Détail
│   ├--- Nouvelle intervention
│   └-- Modifier
│
├-- Clients
│   ├-- Liste
│   ├-- Détail
│   ├-- Nouveau client
│   └-- Modifier
│
└-- Administration
    └-- Utilisateurs
```
Le menu de l'administrateur ne sera visible que pour l'administrateur.

Pour le technicien, l'architecture se réduit essentiellement à:
```text
Tableau de bord
      │
      └-- Mes interventions
               │
               └-- Détail
```
## Tableau de bord
### Gestionnaire
L'interface répond à la question : "Quelle intervention nécessitent mon
attention aujourd'hui ?"

Exemple d'interface:
```text
Tableau de bord

Bonjour Marie

Interventions aujourd'hui
------------------------------------------

09:00 – 10:00
Entreprise Dupont
Maintenance
Martin Dupuis
Terminée

11:00 – 12:30
Entreprise Durand
Dépannage
Sophie Martin
En cours

14:00 – 15:00
Entreprise Bernard
Installation
Non affectée
À réaliser

[Voir toutes les interventions]
```
### Technicien
L'interface répond à la question : "Quelle est ma prochaine intervention ?"

Exemple d'interface:
```text
Bonjour Sophie

Votre prochaine intervention

Aujourd'hui
14:00 – 15:30

Entreprise Dupont

Dépannage imprimante

12 rue des Lilas
75000 Paris

Statut
À réaliser

[Voir l'intervention]


Mes interventions aujourd'hui

09:00  Maintenance       Terminée
14:00  Dépannage         À réaliser
17:00  Installation      À réaliser

[Voir toutes mes interventions]
```
## Interventions
### Filtres
L'application MVP utilise un formulaire HTML classique en GET.

Les avantages:
- fonctionne sans Javascript
- URL partageable
- bouton précédent fonctionnel
- comportement navigateur standard
- implémentation simple

Ce qui allie accessibilité, robustesse et sobriété.
## Authentification
La page de connexion est simple:
```text
Gestionnaire d'intervention

Connexion

Adresse e-mail
[                      ]

Mot de passe
[                      ]

[ Se connecter ]
```
Il n'y a pas:
- d'inscription
- d'illustration lourde
- de vidéo
- de slider
- de dépendance JavaScript
## Gestion des messages et erreurs
Chaque message doit être lisible, compréhensible et correspondant à son
objectif.

Une erreur doit être:
1. annoncée globalement
2. associée au champ concerné lorsque pertinent
3. expliquée textuellement
## Principes d'éco-conception
L'architecture du MVP ne nécessite :
- aucun dashboard graphique
- aucune carte
- aucun SPA
- aucune aPI frontend
- aucun WebSocket
- aucune bibliothèque de calendrier
- aucune bibliothèque UI
- aucune police externe obligatoire
- aucune image fonctionnelle
- aucune dépendance JavaScript identifiée
## Carte de navigation
```text
Connexion
   │
Tableau de bord
   │
   ├--------------- Interventions
   │                       │
   │                       ├-- Liste / filtres
   │                       │
   │                       ├-- Détail
   │                       │      │
   │                       │      ├-- Modifier
   │                       │      ├-- Démarrer
   │                       │      └-- Terminer
   │                       │
   │                       └-- Créer
   │
   ├--------------- Clients
   │                   │
   │                   ├-- Liste / recherche
   │                   ├-- Détail
   │                   │      └-- Interventions
   │                   ├-- Créer
   │                   └-- Modifier
   │
   └---------------- Utilisateurs
                           │
                           ├-- Liste
                           ├-- Créer
                           └-- Modifier

Déconnexion
```
