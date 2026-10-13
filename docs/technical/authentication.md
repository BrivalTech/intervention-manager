# Authentification et gestion des rôles
## 1. Objectif
Le système d'authentification du Gestionnaire d'interventions permet de
sécuriser l'accès à l'application et d'adapter l'interface au profil de
l'utilisateur connecté.

Il repose sur le système d'authentification natif de Django et sur un modèle
utilisateur personnalisé.

Les principaux objectifs sont :
- Authentifier les utilisateurs avec un identifiant et un mot de passe.
- Protéger les pages nécessitant une authentification
- Permettre une déconnexion sécurisée
- Adapter la navigation et le tableau de bord au rôle utilisateur
- Préparer la mise en place des autorisations métier

L'implémentation privilégie les composants natifs de Django afin de limiter
le code spécifique et de faciliter la maintenance.
## 2. Architecture technique
### 2.1. Organisation
L'authentification est principalement organisée autour des éléments suivants :
- `apps/accounts/models.py`: modèle utilisateur et définition des rôles
- `apps/accounts/urls.py`: routes de connexion et de déconnexion
- `apps/accounts/templates/accounts/login.html`: formulaire de connexion
- `apps/accounts/tests/`: tests d'authentification et de navigation
- `apps/core/views.py`: vue avec protection de la page d'accueil
- `templates/base.html`: navigation commune et état de connexion
- `templates/home.html`: tableau de bord adapté au rôle
- `config/settings.py`: configuration de l'authentification Django
### 2.2. Composants Django
Le système utilise :

- `AbstractUser` pour le modèle utilisateur personnalisé.
- `LoginView` pour la connexion.
- `LogoutView` pour la déconnexion.
- `login_required` pour protéger les vues concernées.
- Les sessions Django pour maintenir l'authentification.
- La protection CSRF pour sécuriser les formulaires POST.
## 3. Modèle utilisateur
### 3.1. Modèle personnalisé
L'application utilise le modèle `accounts.User`, qui hérite de `AbstractUser`.
La configuration Django référence ce modèle :
```python
AUTH_USER_MODEL = "accounts.User"
```
Le modèle conserve les fonctionnalités natives de Django et ajoute un champ
`role` permettant de distinguer les profils métier.
### 3.2. Rôles disponibles
Les rôles sont définis avec `models.TextChoices`.
- `ADMIN` -> Administrateur = administration et supervision
- `MANAGER` ->  Gestionnaire = gestion des clients et des interventions
- `TECHNICIAN` ->  Technicien = suivi des interventions attribuées

La méthode `get_role_display()` permet d'obtenir le libellé du rôle dans les
templates.
### 3.3. Utilisateurs sans rôle valide
L'interface prévoit un affichage spécifique lorsqu'un utilisateur
authentifié ne possède pas de rôle valide.
Ce comportement évite de lui attribuer implicitement les fonctionnalités
d'un autre profil.
La validation des rôles et les contrôles d'autorisation métier restent des
responsabilités distinctes de l'affichage du tableau de bord.
## 4. Connexion
### 4.1. Fonctionnement
La connexion repose sur la vue native `LoginView`.
L'utilisateur saisit son nom d'utilisateur et son mot de passe dans un
formulaire HTML.
Lorsque les identifiants sont valides, Django authentifie l'utilisateur et
crée une session authentifiée.

En cas d'échec, le formulaire est ré-affiché avec les erreurs de validation.
### 4.2. Redirections
La configuration utilise :
```python
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "accounts:login"
```

Après une connexion réussie :

- L'utilisateur est redirigé vers la page initialement demandée si le
  paramètre `next` est valide.
- En l'absence de destination valide, il est redirigé vers le tableau de bord.

Django vérifie la sécurité des destinations de redirection afin de refuser
les URL externes non autorisées.
### 4.3. Gestion des erreurs
Les erreurs d'authentification sont présentées dans un composant visuel du
Design System.
Le message utilise :

- Une présentation explicite
- Un titre descriptif
- Une icône décorative
- L'attribut `role="alert"`

L'information ne repose pas uniquement sur la couleur.
Les champs de saisie restent associés à leurs libellés et le mot de passe
est masqué avec `type="password"`.
## 5. Déconnexion et sessions
### 5.1. Déconnexion
La déconnexion repose sur `LogoutView`.
Elle est déclenchée par un formulaire utilisant la méthode HTTP POST et
contenant un jeton CSRF.
Une requête GET sur la route de déconnexion est refusée.
### 5.2. Invalidation de session
Lors de la déconnexion, Django invalide la session authentifiée.
L'utilisateur est ensuite redirigé vers la page de connexion.
Toute nouvelle tentative d'accès à une page protégée nécessite une nouvelle
authentification.
Une reconnexion reste possible avec des identifiants valides.
## 6. Protection des pages
### 6.1. Authentification obligatoire
La page d'accueil est protégée par le décorateur `login_required`.
Un utilisateur non authentifié est redirigé vers la page de connexion.
Le paramètre `next` conserve la destination initialement demandée.
### 6.2. Distinction entre authentification et autorisation
L'authentification confirme l'identité d'un utilisateur.
L'autorisation détermine les opérations qu'il peut effectuer.
## 7. Navigation conditionnelle
### 7.1. Navigation commune
La navigation est définie dans `templates/base.html`.
Son contenu dépend de l'état d'authentification.
- Accueil -> Visiteur : Masqué -> Utilisateur connecté : Visible
- Design System -> Visiteur :Visible -> Utilisateur connecté : Visible
- Se connecter -> Visiteur :Visible -> Utilisateur connecté : Masqué
- Rôle utilisateur -> Visiteur :Masqué -> Utilisateur connecté : Visible
- Se déconnecter -> Visiteur :Masqué -> Utilisateur connecté : Visible
### 7.2. Page courante
Le lien correspondant à la page active utilise l'attribut :
```html
aria-current="page"
```
Cet attribut permet d'identifier la page courante, notamment pour les
technologies d'assistance.
### 7.3. Accessibilité
La navigation respecte les principes du Design System :

- Utilisation d'une structure HTML sémantique
- Navigation accessible au clavier
- Indicateurs de focus visibles
- Lien d'évitement vers le contenu principal
- Boutons et liens possédant des libellés explicites
- Déconnexion accessible via un formulaire POST
## 8. Tableau de bord par rôle
Le tableau de bord constitue la page d'accueil des utilisateurs authentifiés.
Son contenu est adapté au rôle associé au compte.
### 8.1. Administrateur
Le tableau de bord présente un espace d'administration.
### 8.2. Gestionnaire
Le tableau de bord présente un espace de gestion des activités.
### 8.3. Technicien
Le tableau de bord présente un espace consacré aux interventions attribuées.
## 9. Sécurité
### 9.1. Mesures mises en œuvre
Les mécanismes de sécurité reposent principalement sur Django :
- Authentification : vérification des identifiants
- Mots de passe : stockage sécurisé via le système de hachage Django
- Sessions : gestion native des sessions
- CSRF : protection des formulaires POST
- Pages protégées : décorateur `login_required`
- Redirections : validation des destinations
- Déconnexion : requête POST et invalidation de session
- Comptes désactivés : refus de connexion
### 9.2. Configuration de production
Les paramètres de sécurité destinés à la production doivent être adaptés à
l'environnement de déploiement.
Ils concernent notamment :

- `DEBUG`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`
- `SECURE_SSL_REDIRECT`
- `SECURE_HSTS_SECONDS`

Les paramètres HTTPS ne doivent pas être activés sans tenir compte de la
configuration réelle du serveur et du proxy éventuel.
