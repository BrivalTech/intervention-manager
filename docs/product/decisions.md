# Décisions produit
## DEC-001 — Rendu serveur
**Décision :**
Le MVP utilisera principalement le rendu serveur Django.

**Motivation :**
Les parcours métier identifiés ne nécessitent pas une SPA.

**Conséquences :**
Réduction du JavaScript, architecture plus simple et fonctionnement
natif des mécanismes du navigateur.

---
## DEC-002 — Technicien
**Décision :**
Un technicien est un utilisateur ayant le rôle `TECHNICIAN`.

**Motivation :**
Aucune donnée métier spécifique ne justifie actuellement une entité
Technician distincte.

---
## DEC-003 — Compte rendu
**Décision :**
Le compte rendu appartient directement à l'intervention.

**Motivation :**
Le MVP ne prévoit qu'un compte rendu textuel par intervention.
