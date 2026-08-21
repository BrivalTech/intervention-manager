# Qualité du code
## 1. Objectifs
Le projet **Gestionnaire d'interventions** met en place des contrôles de
qualité dès le début du développement afin de maintenir une base de code
lisible, cohérente, testable et maintenable.

La stratégie de qualité repose sur plusieurs principes :

- automatiser les contrôles répétitifs
- détecter les erreurs le plus tôt possible
- conserver un formatage homogène
- tester les comportements métier
- mesurer la couverture des tests
- contrôler le code avant chaque commit
- limiter les dépendances aux outils réellement nécessaires
- intégrer l'accessibilité et l'éco-conception au processus de développement

Les principaux outils utilisés sont :

- **Ruff** pour l'analyse statique et le formatage du code Python
- **pytest** pour l'exécution des tests
- **pytest-django** pour l'intégration de pytest avec Django
- **coverage.py** pour mesurer la couverture des tests
- **pre-commit** pour automatiser les contrôles avant chaque commit

---
## 2. Ruff
### 2.1 Rôle
Ruff est utilisé comme outil principal de contrôle du code Python.

Il assure notamment :

- la détection d'erreurs Python
- le respect de règles de style
- le contrôle des imports
- la détection de certaines mauvaises pratiques
- des contrôles spécifiques à Django
- le formatage automatique du code

La configuration est centralisée dans :

```text
pyproject.toml
```
### 2.2 Configuration
La configuration prinipale du projet est:
```text
[tool.ruff]
target-version = "py312"
line-height = 88
exclude = [
    "E",
    "F",
    "I",
    "B",
    "DJ",
]

[tool.ruf.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
```
### 2.3 Règles activées
Les familles de règles suivantes sont utilisées :
```text
| Code | Rôle                                                 |
| ---- | ---------------------------------------------------- |
| `E`  | erreurs de style Python                              |
| `F`  | erreurs détectées par Pyflakes                       |
| `I`  | organisation et tri des imports                      |
| `B`  | détection de mauvaises pratiques avec flake8-bugbear |
| `DJ` | règles spécifiques aux projets Django                |
```
Cette sélection permet de conserver une configuration relativement stricte
sans multiplier les outils.
### 2.4 Vérifier le code
Pour analyser le projet :
```text
ruff check .
```
Ruff affiche les problèmes détectés sans modifier les fichiers.
### 2.5 Corriger automatiquement
Lorsque les corrections proposées peuvent être appliquées automatiquement :
```text
ruff check . --fix
```
Les corrections automatiques doivent toujours être vérifiées avant le commit.
### 2.6 Vérifier le formatage
Pour vérifier que les fichiers respecent le format attendu :
```text
ruff forat --check .
```
### 2.7 Formater le code
Pour appliquer automatiquement le formatage :
```text
ruff format .
```
---
## 3 Tests automatisés
###3.1 Framework de tests
Le projet utilise :
- pytest
- pytest-django

Les tests permettent notamment de vérifier :
- les modèles
- les règles métier
- les permissions
- les vues
- les formulaires
- les services
- les comportements attendus de l'application

Les tests doivent accompagner progressivement l'implémentation des
fonctionnalités.
### 3.2 Configuration
La configuration de pytest est centralisée dans :
```text
pyproject.toml
```
avec notamment :
```text
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = [
    "tests.py",
    "test_*.py",
    "*_tests.py",
]
```
`DJANGO_SETTINGS_MODULE` indique à pytest quels paramètres Django doit
utiliser lors de l'exécution des tests.
### 3.3 Organisation
Les tests propres à une application sont placés dans un répertoire `tests`.

Exemple :
```text
apps/
└-- accounts/
└-- tests/
    ├-- __init__.py
    └-- test_models.py
```
Les tests concernant le projet dans son ensemble peuvent être placés dans :
```text
tests/
```
Cette séparation permet de distinguer :
- les tests propres aux applications
- les tests transversaux concernant la configuration ou l'architecture du
  projet.
### 3.4 Convention de nommage
Les fichiers de tests utilisent le préfixe :
```text
test_
```
Exemple :
```text
test_models.py
test_views.py
test_permissions.py
```
Les fonctions de tests utilisent également le préfixe :
```text
def test_user_can_be_technician():
    ...
```
Le nom d'un test doit décrire clairement le comportement à vérifier.
### 3.5 Exécuter les tests
Pour lancer l'ensemble des tests :
```text
pytest -v
```
### 3.6 Tests utilisant la base de données
Les tests qui accèdent à la base de données Django doivent utiliser :
```text
@pytest.mark.django_db
```
Exemple :
```text
@pytest.mark.django_db
def test_user_can_be_technician():
    ...
```
Django utilise une base de données dédiée aux tests afin de ne pas modifier
les données de développement.

Avec PostgreSQL, l'utilisateur configuré pour exécuter les tests doit
disposer des droits nécessaires à la création de cette base de tests.
---
## 4. Couverture de tests
### 4.1 Objectif
`coverage.py` permet de mesurer les parties du code exécutées pendant les tests.

La couverture constitue un indicateur permettant d'identifier les portions
de code qui ne sont pas encore testées.

Un taux de couverture élevé ne garantit pas la qualité des tests.

La priorité reste de tester les comportements métier importants et les
scénarios susceptibles de provoquer des régressions.
### 3.2 Configuration
La configuration de `coverage.py` est centralisée dans :
```text
pyproject.toml
```
Les fichiers qui ne doivent pas être pris en compte dans la mesure peuvent y
être exclus :
- les migrations
- les fichiers générés
- certains fichiers d'infrastructure ne contenant pas de logique métier
### 4.3 Exécuter les tests avec couverture
Pour exécuter les tests avec `coverage.py`:
```text
coverage run -m pytest
```
Puis afficher le rapport :
```text
coverage report
```
Pour obtenir un rapport détaillé au format HTML :
```text
coverage html
```
Le rapport est alors généré dans :
```text
htmlcov/
```
et peut être consulté localement dans un navigateur.
### 4.4 Interprétation
La couverture doit être utilisée comme un outil d'aide et non comme un
objectif isolé.

Une fonctionnalité critique doit être correctement testée même si la
couverture globale du projet est déjà élevée.

A l'inverse, augmenter artificiellement la couverture avec des tests sans
valeur métier n'est pas recherché.
---
## 5. Pre-commit
### 5.1 Rôle
`pre-commit` permet d'exécuter automatiquement différents contrôles avant la
création d'un commit Git.

L'objectif est d'empêcher autant que possible l'intégration de problèmes
simples dans l'historique du projet.

La configuration est définie dans :
```text
.pre-commit-config.yaml
```
### 5.2 Installation
Après installation des dépendances de développement :
```text
pip install -r requirements/dev.txt
```
les hooks Git sont installés avec :
```text
pre-commit install
```
Cette commande doit être exécutés une fois après le clonage du dépôt.
### 5.3 Contrôles exécutés
La configuration du projet exécute notamment:
- `ruff-check`
- `ruff-format`
- suppression des espaces inutiles en fin de ligne
- vérification de la présence d'une fin de fichier correcte
- validation des fichiers YAML
- validation des fichiers TOML
- détection des marqueurs de conflits Git
- détection de clés privées
### 5.4 Exécution automatique
Après installation des hooks, les contrôles sont automatiquement lancés lors
de :
```text
git commit
```
Si un contrôle échoue, le commit est interrompu.

Certaines vérifications peuvent modifier automatiquement les fichiers. Dans
ce cas, les modifications doivent être contrôlées puis ajoutées de nouveau à
l'index Git avant de relancer le commit.
### 5.5 Exécution manuelle
Il es possible d'exécuter tous les hooks sans créer de commit :
```text
pre-commit run --all-files
```
Cette commande est utile avant de pousser une branche ou de créer un Pull
Request.
---
## 6. Dépendances de développement
Les outils utilisés uniquement pendant le développement sont déclarés dans :
```text
requirements/dev.txt
```
Ils comprennent notamment :
- `pytest`
- `pytest-django`
- `coverage`
- `ruff`
- `pre-commit`

Les dépendances nécessaires au fonctionnement de l'application restent
séparées des outils utilisés uniquement pour son développement.

Cette séparation permet notamment d'éviter d'installer inutilement les
outils de développement dans l'environnement de production.
---
## 7. Workflow qualité
Avant de considérer une modification comme terminée, le développeur doit
vérifier successivement:
### 7.1 Analyse statique
```text
ruff check .
```
Aucune erreur ne doit rester sans justification.
### 7.2 Formatage
```text
ruff format --check .
```
Si nécessaire
```text
ruff format .
```
### 7.3 Tests
```text
pytest
```
Tous les tests doivent réussir.
### 7.4 Couverture
Lorsque la modification introduit ou modifie une logique applicative :
```text
coverage run -m pytest
coverage report
```
Les nouvelles fonctionnalités doivent disposer de tests adaptés à leur
importance métier.
### 7.5 Pre-commit
Enfin:
```text
pre-commit run --all-files
```
Tous les hooks doivent réussir avant le commit.
---
## 8. Règles de développement
Chaque nouvelle fonctionnalité doit respecter les principes suivants :
1. le code doit rester simple et lisible
2. les noms doivent décrire clairement leur responsabilité
3. la logique métier doit être séparée autant que possible de la logique de
   présentation
4. les comportements métier important doivent être couverts par des tests
5. les erreurs détectées par les outils de qualité doivent être corrigées
   avant le commit
6. les dépendances inutiles doivent être évitées
7. les modifications doivent rester limitées au périmètre du changement réalisé
8. les secrets et données sensibles ne doivent jamais être ajoutés au dépôt Git
---
## 9. Définition de "terminé"
Une tâche de développement peut être considérée comme terminée lorsque :
- le comportement attendu est implémenté
- le code respecte les conventions du projet
- Ruff ne signale aucune erreur
- le formatage est valide
- les tests associés sont présents lorsque nécessaire
- tous les tests passent
- la couverture de tests des parties concernées est satisfaisante
- les hooks pre-commit passent
- aucune information sensible est présente dans les modifications
- la documentation technique est mise à jour lorsque le changement le nécessite
---
## 10. Commande de référence
```text
| Obectif                    | Commande                                      |
| -------------------------- | --------------------------------------------- |
| Vérification Ruff          | `ruff check .`                                |
| Vérification du formatage  | `ruff format --check .                        |
| Formatage                  | `ruff format .`                                |
| Tests                      | `pytest`                                      |
| Tests détaillés            | `pytest -v`                                   |
| Couverture                 | `coverage run -m pytest`<br>`coverage report` |
| Rapport HTML de couverture | `coverage html`                               |
| Tous les hooks pre-commit  | `pre-commit run --all-files`                  |
```
---
## 11. Évolution de la stratégie qualité
Cette startégie constitue la base qualité du projet.

Elle pourra évoluer avec l'application, notamment avec l'ajout futur de :
- tests d'intégration plus complexes
- tests fonctionnels
- contrôles d'accessibilité automatisés
- analyse de sécurité
- intégration continue
- exécution automatique des tests sur les Pull Requests
- contrôle de la couverture dans la CI

Les nouveaux outils ne seront ajoutés que lorsqu'ils apporteront une valeur
réelle au projet afin de conserver une chaîne de développement simple et
maintenable.
