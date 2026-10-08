# Design System — Gestionnaire d'interventions
## 1. Objectifs
Le Design System définit les fondations visuelles et les composants d'interface réutilisables du Gestionnaire d'interventions.

Il vise à garantir :

- une interface cohérente et maintenable
- une accessibilité intégrée dès la conception
- une conception mobile-first
- une utilisation prioritaire du HTML natif
- une limitation du CSS, du JavaScript et des dépendances externes
- une séparation entre présentation et logique métier
## 2. Organisation des fichiers
Les styles sont répartis en trois fichiers :
```text
| Fichier                        | Responsabilité
|--------------------------------|---------------------------------------------------------------------------------
| `static/css/variables.css`     | Design tokens : couleurs, typographie, espacements, bordures et dimensions
| `static/css/main.css`          | Styles globaux, disposition et composants réutilisables
| `static/css/accessibility.css` | Lien d'évitement, focus visible, masquage accessible et réduction des animations
```
Les feuilles de style sont chargées depuis `templates/base.html` avec le système de fichiers statiques de Django.

La page `templates/design-system.html` constitue la référence visuelle des composants.
Elle est accessible à l'adresse `/design-system/`.
## 3. Design tokens
Les valeurs communes sont centralisées dans `variables.css` sous forme de propriétés CSS personnalisées.

Elles couvrent :

- les couleurs primitives, sémantiques et d'interface
- les tailles et graisses typographiques
- les espacements
- les bordures et rayons
- les dimensions générales de mise en page

Les composants doivent privilégier ces variables plutôt que multiplier les valeurs codées en dur.
La typographie utilise les polices système afin d'éviter le chargement de polices externes.
Les dimensions relatives, notamment `rem`, sont privilégiées pour respecter les préférences de taille de texte des utilisateurs.
## 4. Principes de mise en page
Le Design System suit une approche mobile-first.
Les principaux outils de disposition sont :
```text
| Classe          | Utilisation
|-----------------|--------------------------------------------------------------
| `.container`    | Limiter et centrer la largeur du contenu
| `.stack`        | Organiser verticalement des éléments
| `.stack--large` | Augmenter l'espacement vertical
| `.cluster`      | Organiser horizontalement des éléments avec retour à la ligne
```
Les composants évitent les largeurs et hauteurs fixes lorsqu'elles risquent de limiter l'adaptation du contenu.
Les media queries ne sont introduites que lorsqu'un besoin réel de présentation le justifie.
## 5. Composants réutilisables
### Liens et boutons
Les liens `<a>` servent à la navigation. Les boutons `<button>` déclenchent des actions.

Les variantes disponibles sont :

- `.button--primary` : action principale ;
- `.button--secondary` : action secondaire.

L'état désactivé utilise prioritairement l'attribut HTML natif `disabled`.
L'attribut `aria-disabled="true"` ne désactive pas à lui seul le comportement d'un contrôle.
### Messages
Le composant `.message` possède quatre variantes :

- `.message--info`
- `.message--success`
- `.message--warning`
- `.message--error`

Chaque message comporte un libellé explicite.
La couleur ne constitue jamais l'unique moyen de communiquer sa nature.
Les rôles ARIA tels que `alert` sont réservés aux situations qui les nécessitent réellement.
### Cartes
Le composant `.card` permet de regrouper des informations.

Il comprend notamment `.card__title` et `.card__content`.

Une carte n'est pas considérée comme interactive par défaut. Les actions et liens qu'elle contient conservent leur propre sémantique HTML.
### Formulaires
Les formulaires utilisent les classes :

- `.form-field`
- `.form-label`
- `.form-control`
- `.form-help`
- `.form-error`

Les champs possèdent un label associé explicitement.
Les aides et erreurs peuvent être reliées aux champs avec `aria-describedby`.
Les champs invalides utilisent `aria-invalid="true"` lorsque cet état est applicable.
Les attributs HTML natifs, notamment `required`, sont privilégiés.
Les groupes de contrôles associés utilisent `fieldset` et `legend` lorsque nécessaire.
### Composants métier
Le Design System prévoit également :

- `.status` et ses variantes pour les statuts d'intervention
- `.data-list` pour les couples libellé/valeur
- `.empty-state` pour les listes sans résultat

Les statuts sont toujours accompagnés d'un libellé textuel.
Les composants métier restent indépendants des modèles Django et des règles de gestion.
## 6. Accessibilité
L'accessibilité est une contrainte de conception transversale.
Les principales conventions sont :

- utiliser une structure HTML sémantique
- conserver une hiérarchie cohérente des titres
- fournir un lien d'évitement vers le contenu principal
- garantir la navigation au clavier
- rendre le focus visible avec `:focus-visible`
- respecter les contrastes applicables des WCAG
- ne pas transmettre d'information uniquement par la couleur
- permettre l'agrandissement du texte et le reflow
- respecter `prefers-reduced-motion`
- privilégier les comportements natifs avant l'ajout de JavaScript ou d'ARIA

L'utilisation d'ARIA ne remplace pas une structure HTML correcte.
## 7. Éco-conception
Les choix techniques visent à limiter la complexité et le poids de l'interface.
Les principes retenus sont :

- rendu HTML côté serveur avec Django
- absence de framework CSS ou JavaScript pour les composants de base
- utilisation des polices système
- absence d'images purement décoratives dans le Design System
- réutilisation des composants et des variables
- limitation des animations et effets visuels non nécessaires
- ajout de dépendances uniquement lorsqu'un besoin est identifié

Ces choix doivent être réévalués selon les besoins fonctionnels réels.
## 8. Page de référence
La page `/design-system/` présente les composants disponibles et leurs différents états.
Elle permet notamment de vérifier :

- les styles et variantes
- les interactions clavier
- les états désactivés
- les messages d'information et d'erreur
- les champs de formulaire
- les statuts métier
- le comportement responsive

Les éléments affichés sont des exemples de présentation et ne déclenchent pas d'opérations métier.
Cette page est conservée comme support de référence et de vérification lors des futures évolutions du CSS.
## 9. Validation et évolution
Avant d'intégrer un nouveau composant ou de modifier un composant existant, vérifier :

- la possibilité de réutiliser un composant déjà disponible
- la pertinence du HTML sémantique
- les interactions au clavier
- les contrastes et le focus
- le reflow à 320 px et le zoom à 200 %
- la lisibilité des contenus longs
- la cohérence avec les design tokens
- l'absence de dépendance ou de complexité injustifiée

Les vérifications techniques du projet sont décrites dans `docs/technical/quality.md`.
Tout nouveau composant générique doit être ajouté à la page de référence et documenté ici lorsque cela apporte une information utile.
Le Design System évolue en fonction des besoins réels de l'application, sans anticipation excessive de fonctionnalités non utilisées.
