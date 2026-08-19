# Architecture technique
## Objectifs
L'application doit rester :
- simple à maintenir
- accessible par conception
- sobre côté navigateur
- testable
- sécurisable
- évolutive sans surcharger l'architecture
- compatible avec un futur déploiement

Pas de frontend SPA, ni d'API REST pour faire fonctionner l'interface 
  principale.
## Architecture applicative
### Monolithe Django
Le gestionnaire d'intervention a trois domaines principaux:
- Comptes
- Clients
- Interventions
Django peut les gérer dans une seule application déployable.
Cela réduit:
- - les dépendances
- les échanges réseau
- l'infrastructure
- les besoins d'hébergement
- la maintenance

Cette décision est cohérente avec l'objectif d'éco-conception.
## Stack technique
```text
| Domaine                   | Choix technique                   |
| ------------------------- | --------------------------------- |
| Langage                   | Python 3.12                       |
| Framework                 | Django                            |
| Base de données           | PostgreSQL                        |
| Frontend                  | HTML + CSS                        |
| JavaScript                | Vanilla JS uniquement si justifié |
| Tests                     | pytest + pytest-django            |
| Couverture                | coverage.py                       |
| Qualité                   | Ruff                              |
| Hooks Git                 | pre-commit                        |
| Variables d'environnement | python-dotenv                     |
| Gestionnaire de version   | Git                               |
```
## Découpage des applications Django
### accounts
Responsabilité : 
- authentification
- utilisateurs
- droits associés aux utilisateurs
- activation / désactivation

Elle contiendra le futur `CustomUser`.
### clients
Responsabilités : 
- clients
- coordonnées
- archivage
- recherche clients
- historique des interventions d'un client
### interventions
C'est le coeur métier, avec les responsabilités suivantes :
- interventions
- planification
- affectation
- status
- compte rendu
- conflits de planning
### core
Responsabilités :
- dashboard
- pages communes authentifiées
- éléments transversaux
## Dépendances entre domaines
Une `Intervention` connaît : 
- `Client`
- `User` comme technicien
- `User` comme créateur

En revanche, `Client` n'a pas besoin de connaître directement 
`Intervention` dans son modèle. La relation inverse fournie par Django 
permet de retrouver les interventions reliées au client.
## Gestion des règles métier
Au démarrage du projet, les r!gles métiers seront intégrés dans un fichier 
`services.py`. Ce fichier regroupera les opérations métier qui dépassent la 
responsabilité d'un formulaire ou d'un modèle. 
## Validation des données
Plusieurs niveaux:
- Formulaire, pour les erreurs directement liées à une saisie utilisateur
- Métier : technicien inactif, client archivé, compte rendu absent, conflit 
  de planning et transition de statut interdite
  - Base de données : contrainte de base, par exemple pour le chevauchement 
    de date.
## Architecture des templates
L'architecture des templates comprendra des templates globaux et des 
templates propres aux applications.
```text
templates/
├-- base.html
├-- includes/
│   ├-- header.html
│   ├-- navigation.html
│   ├-- messages.html
│   └-- footer.html
│
├-- accounts/
├-- clients/
├-- interventions/
└-- core/
```
## Architecture CSS
```text
static/
└-- css/
    ├-- variables.css
    ├-- reset.css
    ├-- base.css
    ├-- accessibility.css
    │
    ├-- components/
    │   ├-- button.css
    │   ├-- form.css
    │   ├-- message.css
    │   ├-- navigation.css
    │   ├-- status.css
    │   └-- table.css
    │
    └-- pages/
```
Le dossier `pages/` ne comprendra des fichiers pour les besoins spécifiques.
## JavaScript
Le fonctionnement métier ne dépend pas de JavaScript sauf justification 
documentée.
## Stratégie de tests
```text
apps/
├-- accounts/
│   └-- tests/
│       ├-- test_models.py
│       ├-- test_forms.py
│       └-- test_views.py
│
├-- clients/
│   └-- tests/
│
└-- interventions/
    └-- tests/
        ├-- test_models.py
        ├-- test_forms.py
        ├-- test_services.py
        └-- test_views.py
```
Les tests suivront ces catégories :
1. métier : est-ce que la règle fonctionne ?
2. HTTP : l'utilisateur peut-il réaliser l'action ?
3. présentation / accessibilité : l'interface contient-elle les éléments 
   attendus ?
## Gestion des dépendances
Les dépendances sont gérées selon les nécessités de l'application.
- `base.txt`: uniquement ce qui est nécessaire à l'application
- `dev.txt`

Les dépendances sont ajoutées uniquement si elles répondent à un besoin 
identifié.
## Configuration Django
```text
config/
├-- __init__.py
├-- settings.py
├-- urls.py
├-- asgi.py
└-- wsgi.py
```
avec utilisation des variables d'environnements.
## Structure cible du projet
```text
intervention-manager/
│
├-- apps/
│   ├-- accounts/
│   ├-- clients/
│   ├-- core/
│   └-- interventions/
│
├-- config/
│
├-- docs/
│   ├-- product/
│   └-- technical/
│
├-- static/
│   └-- css/
│
├-- templates/
│   ├-- includes/
│   ├-- accounts/
│   ├-- clients/
│   ├-- core/
│   └-- interventions/
│
├-- requirements/
│   ├-- base.txt
│   └-- dev.txt
│
├-- .env.example
├-- .gitignore
├-- .pre-commit-config.yaml
├-- manage.py
├-- pyproject.toml
├-- pytest.ini
└-- README.md
```
## Décisions reportées
- hébergement
- serveur web de production
- CI/CD
- stratégie de sauvegarde
- monitoring
- SMTP
- architecture de déploiement définitive