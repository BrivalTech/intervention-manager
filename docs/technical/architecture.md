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
Les styles sont organisés par responsabilité. Les feuilles sont référencées dans `templates/base.html` et `templates/500.html` dans un ordre explicite, pour préserver la cascade CSS.

```text
static/css/
├── variables.css
├── base.css
├── layout-navigation.css
├── buttons-links.css
├── messages.css
├── cards-entities.css
├── forms-status.css
├── dashboards.css
├── responsive.css
└── accessibility.css
```

`variables.css` centralise les tokens ; `accessibility.css` porte les ajustements d'accessibilité. `responsive.css` contient les adaptations tablette et desktop. L'ancien `main.css` est remplacé par les huit modules intermédiaires.

## JavaScript
Le fonctionnement métier ne dépend pas de JavaScript sauf justification
documentée.
## Stratégie de tests
Les tests `pytest` sont regroupés par domaine dans `apps/accounts/tests/`, `apps/clients/tests/`, `apps/interventions/tests/` et `apps/core/tests/`. Les fichiers de vues, services et modèles sont découpés par fonctionnalité (liste, création, détail, permissions, transitions, etc.). Les fixtures communes sont placées dans les `conftest.py` appropriés. La fixture HTTP `client` de pytest-django ne doit pas être masquée par une fixture métier homonyme.

Les tests couvrent les règles métier, les autorisations, les réponses HTTP et la structure des interfaces. Les pages d'erreur personnalisées 403, 404 et 500 disposent de tests dédiés.

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

## Identifiants publics (Sprint 8.1)
Les modèles `User`, `Client` et `Intervention` conservent leur clé primaire interne et possèdent un champ `public_id` de type UUID. Les relations entre modèles restent basées sur les clés internes ; les URL de consultation et de modification exposent les UUID publics.

L'UUID évite d'exposer un identifiant séquentiel, mais **ne constitue pas un mécanisme d'autorisation** : chaque vue doit continuer à vérifier l'authentification, le rôle et les règles de visibilité. Les migrations ont été réalisées en plusieurs étapes pour attribuer un UUID unique aux enregistrements existants.

## Pages d'erreur (Sprint 8.3)
Les templates `templates/403.html`, `templates/404.html` et `templates/500.html` présentent des messages compréhensibles sans exposer d'informations techniques. La page 500 doit rester autonome autant que possible, car une erreur serveur peut empêcher l'accès au contexte applicatif habituel. Les tests de rendu des pages personnalisées utilisent `DEBUG=False`.
