# Frontend — organisation et maintenance (Sprint 8)

## Rendu et principes
L'interface est rendue côté serveur par les templates Django. L'objectif est de limiter le JavaScript, de conserver une navigation clavier native et de privilégier les composants HTML sémantiques.

## Organisation CSS
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

Les huit fichiers intermédiaires remplacent `main.css`. `variables.css` et `accessibility.css` restent dédiés aux tokens et aux besoins d'accessibilité. L'ordre des liens `<link rel="stylesheet">` dans les templates est important : il préserve la cascade. Éviter les `@import` CSS qui créent des dépendances de chargement en chaîne.

## Navigation
La version mobile/tablette utilise `<details>` et `<summary>` ; la version desktop dispose de sa navigation horizontale. Les liens sont mutualisés dans un include Django. Les droits d'accès restent appliqués côté serveur, indépendamment de la présence d'un lien dans le menu.

## Cartes
La grille `.entity-list` est partagée entre les listes métier. Les cartes doivent s'adapter au contenu et au zoom, sans hauteur fixe. Les boutons des cartes de comptes sont disposés en bas de carte et leurs libellés peuvent passer à la ligne.

## Vérifications manuelles
Contrôler 320–375 px, 768 px et au moins 1 024 px, ainsi que le zoom à 200 %, le focus visible, l'ordre de tabulation, l'absence de défilement horizontal et la cohérence des pages d'erreur.

## Éco-conception
La modularisation facilite la maintenance, mais peut augmenter le nombre de requêtes CSS. Comparer les ressources réellement transférées avant/après avec les outils réseau du navigateur ; ne pas affirmer de gain sans mesure. Aucune bibliothèque JavaScript n'est nécessaire pour la navigation proposée.
