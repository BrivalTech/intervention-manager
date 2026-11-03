# Déploiement en production
## 1. Présentation
Le Gestionnaire d'interventions est une application Django déployée sur
alwaysdata.
**Environnement de production :**
- URL : https://interventions.brivaltech.com
- Hébergement : alwaysdata
- Langage : Python 3.12
- Framework : Django 5.2
- Serveur applicatif : Python WSGI
- Base de données : PostgreSQL
- Gestion du code source : GitHub
- Branche de production : `main`

Le déploiement est manuel. GitHub Actions assure les contrôles de qualité et
les tests avant fusion des Pull Requests.
## 2. Organisation du serveur
Répertoire de l'application :
`/home/brivaltech/intervention-manager/`

Principaux éléments :
- `config/settings.py` : configuration Django.
- `config/wsgi.py` : point d'entrée WSGI.
- `.venv/` : environnement virtuel Python.
- `.env` : variables d'environnement de production.
- `staticfiles/` : ressources statiques collectées.
- `docs/` : documentation technique.

Le fichier `.env` ne doit jamais être ajouté au dépôt Git.
## 3. Configuration de production
Les paramètres sensibles sont définis dans le fichier `.env`.

Variables principales :

- `DJANGO_ENV=production`
- `DEBUG=False`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- Variables SMTP
- `SECURE_HSTS_SECONDS`

Les fichiers `.env.example` et `.env.production.example` documentent les
variables attendues sans contenir de secrets.
## 4. Procédure de déploiement
### 4.1. Prérequis
Avant chaque déploiement :
1. Vérifier que la Pull Request est validée.
2. Vérifier que la CI GitHub Actions est verte.
3. Fusionner les modifications dans `main`.
4. Vérifier les éventuelles migrations de base de données.
5. Prévoir une sauvegarde avant toute opération sensible.
### 4.2. Connexion au serveur
Se connecter en SSH à alwaysdata, puis :
```bash
cd ~/intervention-manager
source .venv/bin/activate
```
### 4.3. Mettre à jour le code
```bash
git status
git pull --ff-only origin main
```
Le répertoire de production doit être propre avant la mise à jour.
### 4.4. Installer les dépendances
Si les dépendances ont changé :
```bash
python -m pip install -r requirements/base.txt
```
### 4.5. Appliquer les migrations
Vérifier le plan :
```bash
python manage.py migrate --plan
```
Puis appliquer les migrations validées :
```bash
python manage.py migrate --noinput
```
### 4.6. Collecter les fichiers statiques
```bash
python manage.py collectstatic --noinput
```
Les ressources sont collectées dans `staticfiles/`, puis servies directement
par alwaysdata.
### 4.7. Vérifier Django
```bash
python manage.py check
python manage.py check --deploy
python manage.py migrate --check
```
Redémarrer le site Python WSGI depuis alwaysdata si nécessaire.
## 5. Sécurité
L'application utilise HTTPS.

Les protections comprennent :
- Redirection HTTP vers HTTPS.
- Cookies de session sécurisés.
- Protection CSRF.
- Contrôle des hôtes autorisés.
- En-têtes HTTP de sécurité.
- Permissions métier selon les rôles.
### HSTS
Configuration initiale :
```dotenv
SECURE_HSTS_SECONDS=300
```
Les options `SECURE_HSTS_INCLUDE_SUBDOMAINS` et `SECURE_HSTS_PRELOAD`
restent désactivées volontairement.

Les avertissements Django `security.W005` et `security.W021` sont connus et
acceptés.

Toute augmentation de la durée HSTS doit être précédée d'une vérification du
fonctionnement HTTPS.
## 6. Sauvegardes PostgreSQL
### Configuration des sauvegardes
Les sauvegardes de la base de données PostgreSQL sont assurées
automatiquement par l'hébergeur alwaysdata (offre Small).

| Paramètre       | Configuration                                |
|-----------------|----------------------------------------------|
| Hébergeur       | alwaysdata                                   |
| Base de données | `brivaltech_interventions_manager`           |
| Fréquence       | Quotidienne                                  |
| Conservation    | 7 jours glissants                            |
| Format          | SQL compressé avec Zstandard (`.sql.zst`)    |
| Accès           | Interface d'administration alwaysdata et SSH |

Les sauvegardes PostgreSQL sont indépendantes des fichiers de l'application
et de son dépôt Git.
### Localisation des sauvegardes
Les fichiers sont accessibles depuis le serveur SSH dans le répertoire :
```text
/home/brivaltech/admin/backup/latest/postgresql/
```
Le fichier correspondant à l'application est :
```text
brivaltech_interventions_manager.sql.zst
```
Le répertoire `latest` permet d'accéder à la dernière sauvegarde disponible.
### Vérifications
- Présence de la base `brivaltech_interventions_manager` dans l'interface de restauration alwaysdata.
- Présence de sauvegardes quotidiennes du 28 octobre au 3 novembre 2026.
- Vérification de la politique de conservation de 7 jours.
- Confirmation de l'accessibilité du fichier de sauvegarde depuis SSH.
- Vérification de l'intégrité du fichier compressé avec Zstandard.

Commande utilisée :
```bash
zstd -t \
  /home/brivaltech/admin/backup/latest/postgresql/brivaltech_interventions_manager.sql.zst
```
Résultat : commande exécutée sans erreur, avec une taille décompressée de 38
290 octets.
### Restauration
La restauration complète de la base PostgreSQL n'a pas été testée.

Cette décision est adaptée à la nature du projet : le Gestionnaire
d'interventions est une application de démonstration destinée au portfolio,
sans données clients réelles.

Le contrôle d'intégrité confirme que le fichier compressé est lisible,
mais ne garantit pas la restauration effective des données.

En cas de restauration, utiliser de préférence une base PostgreSQL
temporaire distincte afin de préserver la production.

Pour une exploitation avec des données clients réelles, des tests
périodiques de restauration et une politique de sauvegarde adaptée
devront être mis en place.
## 7. Contrôles après déploiement
Après chaque mise à jour, vérifier :
- L'accès à la page de connexion.
- La connexion et la déconnexion.
- Les fichiers CSS et le favicon.
- Les redirections HTTPS.
- Les permissions des utilisateurs.
- Les principales fonctionnalités métier concernées par la mise à jour.
- Les journaux d'erreurs alwaysdata.

Vérification des en-têtes HTTPS :
```bash
curl -sI https://interventions.brivaltech.com/accounts/login/
```
## 8. Principes de maintenance
- Ne jamais modifier directement le code de production sans validation préalable.
- Utiliser une branche dédiée pour chaque évolution.
- Faire valider les modifications par la CI.
- Déployer uniquement le code fusionné dans `main`.
- Ne jamais enregistrer de secrets dans Git.
- Vérifier les sauvegardes avant toute modification sensible de PostgreSQL.
- Documenter les incidents et leurs corrections.
