# Cadrage du Gestionnaire d'intervention
## Contexte
Une PME spécialisée dans l'installation, l'entretien et le dépannage 
d'équipements technique intervient régulièrement chez des clients 
professionnels.

L'entreprise doit planifier les interventions, affecter les techniciens 
disponibles et permettre le suivi de leur réalisation.

Aujourd'hui, les informations sont dispersées entre différents outils : 
e-mails, téléphone, feuille de calculs et documents internes. Cela rend le 
suivi des interventions difficile et augmente le risque d'erreur ou de perte 
d'inormation.

L'entreprise souhate disposer d'une application web simple permettant de 
centraliser et de suivre son activité d'intervention.
## Problème
Comment permettre à une petite entreprise de gérer simplement le cycle de 
vie de ses interventions, depuis la demande du client jusqu'à leur réalisation
par un technicien ?

Plusieurs difficultés:
- informations clients dispersées
- difficulté à connaître les interventions à venir
- affectation des techniciens peu centralisée
- difficulté à connaître l'état d'une intervention
- manque d'historique
- risque de doublons ou d'oublis
- accès à l'information potentiellement difficile sur le terrain
## Objectif du produit
Centraliser la gestion des clients, des techniciens et des interventions 
dans une application web simple, accessible et sobre, permettant de planifier,
consulter et suivre efficacement les interventions.
## Objectifs secondaires
1. centralisation des informations nécessaires à une intervention
2. réduction du nombre d'actions nécessaires pour retrouver une information
3. facilitation de la planification des interventions
4. identification rapide du technicien affecté
5. suivi  de l'état d'avancement
6. conservation d'un historique exploitable
7. fonctionnement sur un ordinateur, tablette ou smartphone
8. utilisation eu clavier et avec des technologies d'assistance
9. limitation des ressources techniques et données transférées au strict 
   nécessaire
## Cycle de vie d'une intervention
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
## Principe d'accessibilité
Les fonctionnalités essentielles doivent pouvoir être réalisées sans souris.
## Principe d'éco-conception
Chaque fonctionnalité et chaque ressource technique doit répondre à un 
besoin utilisateur identifié.
## Hors périmètre
- ERP
- CRM complet
- application de comptabilité
- solution de facturation
- logiciel RH
- système de géolocalisation des salariés
- messagerie interne
- application de gestion des stocks
## Critères de réussite
#### Fonctionnels
Un utilisateur autorisé doit pouvoir retrouver rapidement:
- un client
- une intervention
- une date / heure
- le lieu d'intervention
- le technicien affecté
- le statut de l'intervention
#### Accessibilité
Les parcours essentiels doivent être :
- réalisables au clavier
- utilisables avec un zoom à 200%
- compréhensibles sans dépendre de la couleur
- structurés avec du HTML sémantique
- associés à des formulaires correctement étiquetés
- accompagnés d'erreurs compréhensibles
#### Éco-conception
- limiter les dépendances
- limiter le JavaScript
- éviter les ressources tiers inutiles
- optimiser les requêtes Django/SQL
- limiter le poids des pages
- éviter les médias sans utilité fonctionnelle
- dimensionner ultérieurement l'infrastructure selon l'usage réel