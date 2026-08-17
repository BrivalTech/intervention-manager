# MVP — Gestionnaire d'interventions
## Objectif du MVP
Le MVP va permettre de réaliser le cycle suivant de bout en bout, sans 
chercher à reproduire une logiciel métier complet.

Cycle de vie:
```text
Client
   │
Demande d'intervention
   │
Création de l'intervention
   │
Planification
   │
Affectation d'un technicien
   │
Intervention à réaliser
   │
Intervention en cours
   │
Intervention terminée
   │
Historique
```
## Authentification
Inclus dans le MVP :
- connexion
- déconnexion
- accès selon le rôle
- utilisateur authentifié

Non inclus : 
- inscription publique
- connexion Google / Microsoft
- MFA applicatif

Tous les comptes sont créés par un administrateur.
## Utilisateurs et rôles
Trois rôles :
- Administrateur
- Gestionnaire
- Technicien

Un administrateur peut : 
- consulter les utilisateurs
- créer un utilisateur
- modifier les informations d'un utilisateur
- attribuer un rôle à un utilisateur
- désactiver l'accès
## Clients
Le gestionnaire doit pouvoir :
- rechercher un client
- consulter un client
- créer un client
- modifier un client
- archiver un client
- consulter ses interventions
## Interventions
Un gestionnaire doit pouvoir créer une intervention associé à un client.

Il peut aussi consulter :
- les interventions à venir
- les interventions en cours
- les interventions terminées
- le détail d'une intervention

Selon les règles métier, il pourra modifier :
- la date
- l'horaire
- le technicien affecté
- la description
- les informations d'intervention
## Cycle de vie d'une intervention
```text
À RÉALISER
   │
EN COURS
   │
TERMINÉE

+ ANNULÉE
```
## Compte rendu
À la fin d'une intervention, le technicien doit pouvoir saisir un compte 
rendu textuel.

Non inclus dans le MVP :
- l'ajout de photos et/ou de vidéos
- l'ajout de fichiers PDF
- la signature électronique
- l'ajout de pièces jointes
## Recherche et filtres
La recherche est utile pour éviter le chargement de données non nécessaires.
- la recherche client : par nom ou par e-mail
- la recherche d'intervention : par statut, par technicien, par date
## Tableau de bord
Cet écran n'affichera pas:
- de graphiques d'interventions
- de camemberts de statuts
- d'évolution annuelle
- de KPI décoratifs
Le tableau de bord doit aider l'utilisateur à agir.
Exemple pour le gestionnaire :
```text
Aujourd'hui
--------------------------------
 5 interventions
 
 09:00  Dupont      Martin      En cours
 11:00  STE         Durand      À réaliser
 14:00  Martin SA   Martin      À réaliser
 ----
 
 [Voir toutes les interventions]
```
Exemple pour le technicien :
```text
Mes interventions aujourd'hui
--------------------------------

09:00
Entreprise Dupont
Maintenance annuelle
Terminée

14:00
ACME
Dépannage
À réaliser

[Voir l'intervention]
```
## Accessibilité — Definition of Done
Une fonctionnalité ne sera pas considérée comme terminée uniquement parce 
qu'elle fonctionne à la souris.

Définition de "Done" :
- fonctionnelle
- utilisable au clavier
- focus visible
- HTML sémantique
- nom accessible des contrôles
- erreurs compréhensibles
- pas d'information uniquement par la couleur
- responsive
- zoom à 200%
## Éco-conception — Definition of Done
Pour chaque fonctionnalité, il faut se poser la question du besoin, est-il 
justifié ? Si c'est justifié, il faut trouver la solution la plus simple, 
avec des données minimales, des requêtes optimisées et des ressources front 
nécessaires ?
## Hors périmètre
- calendrier graphique
- drag-and-drop
- cartographie
- géolocalisation
- notifications push
- notifications temps réel
- WebSocket
- chat
- pièces jointes
- photos d'intervention
- signature électronique
- export PDF
- statistiques avancées
- graphiques
- application mobile native
- API publique
- application SPA
## Priorisation MoSCoW
| Priorité       | Fonctionnalités                                                                     |
| -------------- | ----------------------------------------------------------------------------------- |
| **Must**       | authentification, rôles, clients, interventions, affectation, statuts, compte rendu |
| **Should**     | recherche clients, filtres interventions, archivage                                 |
| **Could**      | historique plus détaillé, quelques améliorations ergonomiques                       |
| **Won't V2.0** | calendrier complexe, cartes, fichiers, graphiques, temps réel, SPA                  |
## Backlog fonctionnel initial
```text
EPIC 1 - Authentification
EPIC 2 - Utilisateurs et rôles
EPIC 3 - Clients
EPIC 4 - Interventions
EPIC 5 - Affectation
EPIC 6 - Suivi des statuts
EPIC 7 - Compte rendu
EPIC 8 - Recherche et filtre
EPICE 9 - Tableau de bord opérationnel
```