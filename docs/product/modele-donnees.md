# Modèle de données métier
## Principes de conception
Trois entités principales:
- Utilisateur
- Intervention
- Client
## Utilisateur
### Rôles
Trois rôles métier:
- Administrateur
- Gestionnaire
- Technicien

L'application MVP utilise le `CustomUser` de Django. 
## Client
### Données
Application du principe de minimalisation des données.

Pour le MVP:
```text
Client
|-- name
|-- contact_name
|-- email
|-- phone
|-- address
|-- postal_code
|-- city
|-- notes
|-- is_active
|-- created_at
|-- updated_at
```
## Intervention
### Données
```text
Intervention
|-- client
|-- technician
|-- created_by
|-- title
|-- description
|-- address
|-- postal_code
|-- city
|-- starts_at
|-- ends_at
|-- status
|-- report
|-- create_at
|-- updated_at
```
### Adresse
Le stockage d'une autre adresse que celle indiqué dans la fiche du client 
est possible car l'adresse de l'intervention peut être différente. Si 
l'intervention archivée utilise le champ `address` du client, son ancienne 
adresse serait perdue.

L'interface de l'application pourra pré-remplir l'adresse du client si elle 
correspond à celle de l'intervention.
### Statut
Il y a quatre valeurs fixes:
- `TODO`
- `IN_PROGRESS`
- `COMPLETED`
- `CANCELLED`
### Compte rendu
Le champ `report` peut être vide tant que l'intervention n'est pas terminée.
## Relations
Une intervention appartient à un client. Un client peut avoir plusieurs 
interventions.

Une intervention possède au maximum un technicien principal dans le MVP. Une 
intervention peut être créée avant l'affectation d'un technicien.
## Contraintes métier
Les contraintes ci-dessous sont garanties par le code et/ou la base.
### Intervention
```text
- client obligatoire
- client actif lors d'une nouvelle intervention
- starts_at obligatoire
- ends_at obligatoire
- technician facultatif
- technician doit avoir le rôle TECHNICIAN
- technician doit être actif
- pas de chevauchement pour un même technicien
- report obligatoire si COMPLETED
- created_buy obligatoire
```
### Client
```text
- name obligatoire
- archivage plutôt que suppression
- client archivé non sélectionnable
- archivage interdit avec intervention active
```
### Utilisateur / technicien
```text
- rôle obligatoire
- technicien désactivé non affectable
d- désactivation interdite avec intervention active
```
## Schéma métier v1 du modèle
```text
┌─────────────────────┐
│ USER                │
├─────────────────────┤
│ identity            │
│ role                │
│ is_active           │
└─────────┬───────────┘
          │
          │ technician
          │ 0..N
          ▼
┌─────────────────────────┐
│ INTERVENTION            │
├─────────────────────────┤
│ client                  │
│ technician (optional)   │
│ created_by              │
│ title                   │
│ description             │
│ address                 │
│ postal_code             │
│ city                    │
│ starts_at               │
│ ends_at                 │
│ status                  │
│ report                  │
│ created_at              │
│ updated_at              │
└───────────┬─────────────┘
            │ N
            │
            │ 1
            ▼
┌─────────────────────┐
│ CLIENT              │
├─────────────────────┤
│ name                │
│ contact_name        │
│ email               │
│ phone               │
│ address             │
│ postal_code         │
│ city                │
│ notes               │
│ is_active           │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```