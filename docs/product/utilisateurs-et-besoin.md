# Utilisateurs et besoins
## Profils utilisateurs
### Administrateur
L'administrateur est responsable de la configuration et de la gestion 
globale de l'application.

Ses objectifs:
- gérer les comptes utilisateurs
- gérer les techniciens
- gérer les clients
- consulter toutes les interventions
- corriger une information si nécessaire
- superviser l'utilisation générale de l'application
### Gestionnaire
Profil central de l'application.

Il reçoit une demande d'intervention et doit pouvoir l'organiser.

Ses objectifs principaux:
```text
Créer un client
   │
Créer une intervention
   │
Création de l'intervention
   │
Définir une date et un horaire
   │
Affecter un technicien
   │
Suivre l'intervention
   │
Consulter son résultat
```
Il doit pouvoir :
- consulter les clients
- créer et modifier un client
- consulter les interventions
- créer une intervention
- modifier une intervention
- affecter un technicien
- modifier la planification
- suivre le statu
- retrouver rapidement une intervention passée
### Technicien
Le technicien utilise l'application principalement pour consulter et traiter 
les interventions qui lui sont affectées.

Il doit pouvoir:
- consulter les interventions
- connaître la prochaine intervention
- identifier le client
- connaître l'adresse
- consulter les informations utiles
- changer le statut lorsque cela est autorisé
- saisir éventuellement un compte rendu
## Matrice des besoins
| Fonction                           | Administrateur | Gestionnaire | Technicien |
| ---------------------------------- | -------------- | ------------ | ---------- |
| Consulter les clients              | oui            | oui          | limité     |
| créer un client                    | oui            | oui          | non        |
| modifier un client                 | oui            | oui          | non        |
| supprimer / archiver un client     | oui            | à définir    | non        |
| consulter toutes les interventions | oui            | oui          | non        |
| consulter ses interventions        | oui            | oui          | oui        |
| créer une intervention             | oui            | oui          | non        |
| modifier la planification          | oui            | oui          | non        |
| affecter un technicien             | oui            | oui          | non        |
| changer le statut                  | oui            | oui          | limité     |
| ajouter un compte rendu            | oui            | oui          | oui        |
| gérer les utilisateurs             | oui            | non          | non        |
## Parcours du gestionnaire
### Rechercher un client
Rechercher un client avant d'en créer un autre : 
- Si le client est trouvé alors on le sélectionne
- Dans le cas contraire on le crée.

Cela limite les doublons.
### Créer et planifier une intervention
Le gestionnaire renseigne uniquement les informations nécessaires:
- client
- type / objet
- description
- adresse d'intervention
- date / horaire
- technicien
### Suivre une intervention
L'intervention suit un cycle :
1. Planifiée
2. À réaliser
3. En cours
4. Terminée
## Parcours du technicien
1. Se connecter
2. Consulter ses interventions
3. Consulter une intervention
4. Démarrer une intervention
5. Terminer une intervention

C'est une décision d'éco-conception, en concevant un écran autour du besoin  
plutôt qu'autour des données disponibles.
## Principes d'accessibilité
- gestion au clavier
- zoom à 200%
- pas de statuts identifiables par un code couleur
## Principes d'éco-conception
La page initiale ne récupèrera que les informations nécessaires.
Par exemple:
```text
Aujourd'hui

09:00 - Client A
Maintenance
Terminée

14:00 - Client B
Dépannage
À réaliser
```
Les détails ne seront chargés que lorsque l'utilisateur ouvrira l'intervention.
## Gestion des droits
Un utilisateur ne doit accéder qu'aux informations nécessaires à son rôle.

Un technicien n'a aucune raison de pouvoir parcourir l'ensemble de la base 
clients. Il doit pouvoir accéder aux informations du client nécessaire à 
l'intervention qui lui est affectée.

Ce qui améliore simultanément:
- la sécurité
- la confidentialité
- la simplicité d'interface
- la quantité de données manipulées
## Archivage des données
Le choix a été porté sur l'archivage de la donnée, plutôt que la suppression,
afin de préserver son historique.