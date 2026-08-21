# Règles métier
## Interventions
### Création
Ube intervention doit obligatoirement avoir:
- un client actif
- un objet ou type d'intervention
- une date
- un horaire
- une adresse d'intervention
- un statut initial

Le technicien peut être affecté au moment de la création ou plus tard.

Le statut initial est `À réaliser`
### Affectation
Une intervention du MVP ne peut avoir qu'un seul technicien principal.

Un technicien peut être affecté uniquement s'il est `actif`.

Un technicien désactivé ou archivé:
- ne doit plus apparaître dans les nouvelles affectations
- reste associé aux anciennes interventions
### Statuts
Le workflow simple est :
1. `À réaliser`
2. `En cours`
3. `Terminée`

avec le statut supplémentaire `Annulée` comme état alternatif.
#### Qui peut changer le statut ?
##### Administrateur
Il peut modifier tous les statuts.
##### Gestionnaire
Il peut:
- annuler
- corriger le statut si nécessaire
- suivre toutes les interventions
##### Technicien
Il peut uniquement agir sur ses propres interventions.

Exemple:
```text
À réaliser -> En cours
En cours -> Terminée
```
Il n'a pas la possibilité d'annuler une intervention directement dans le MVP.
### Compte rendu
Une intervention ne peut être terminée qu si un compte rendu a été renseigné.
Si pas de compte rendu un message s'affiche, par exemple: `"Un compte rendu est
nécessaire pour terminer cette intervention"`
### Intervention terminée
Une fois terminée, l'intervention devient principalement consultative.

Le technicien ne doit plus pouvoir modifier:
- client
- date
- horaire
- affectation
- description métier
### Dates
Il sera interdit au gestionnaire de créer (accidentellement) une nouvelle
intervention avec une date dans le passé. La date/heure d'une nouvelle
intervention doit être dans le futur.

Les anciennes interventions restes consultables.
### Conflits de planning
Un technicien ne peut pas avoir duex interventions à la même heure. Pour
cela on stockera :
```text
date
heure de début
heure de fin
```
pour empêcher le chevauchement d'intervention.
### Archivage
Un client ne peut être archivé s'il possède une intervention non terminée ou
non annulée. Même principe pour un technicien, s'il possède des
interventions futures, la désactivation sera bloquée tant que les
interventions actives lui sont affectées. Cela oblige le gestionnaire à
réaffecter proprement les interventions avant de désactiver le compte du
technicien.
## Gestion des données
### Données minimales
Pour l'éco-conception et la protection des données, l'application ne stocke
aucunes données utilisateur ou client sans besoin fonctionnel identifié. Par
exemple, l'application ne collectera pas la date de naissance, photo ou les
réseaux sociaux du client, si elle n'en a pas besoin.
### Suppression
L'application MVP ne supprimera pas physiquement depuis l'interface métier
les clients, techniciens et interventions. Il sera utilisé le statut booléen
`is_active`.
## Critères d'acceptation
### Création d'intervention
```text
Étant donné un gestionnaire connecté
Et un client actif
Quand il crée une intervention valide
Alors l'intervention est enregistrée
Et son statut initial est "À réaliser"
```
### Client archivé
```text
Étant donné un client archivé
Quand un gestionnaire crée une intervention
Alors ce client ne peut pas être sélectionné
```
### Fin d'intervention
```text
Étant donné une intervention "En cours"
Et aucun compte rendu
Quand le technicien tente de la terminer
Alors la modification est refusée
```
### Technicien
```text
Étant donné une intervention affectée au technicien A
Quand le technicien B tente de la modifier
Alors l'accès est refusé
```
### Conflit de planning
```text
Étant donné une intervention attribuée à un technicien
Quand une seconde intervention chevauche la même plage horaire
Alors l'affectation est refusée
```
## Critères d'accessibilité
Pour chaque fonctionnalité interactive sera ajouté:
```text
- action réalisable au clavier
- focus visible
- message d'erreur textuel
- champ correctement étiqueté
- statut lisible sans couleur
- zoom 200%
```
