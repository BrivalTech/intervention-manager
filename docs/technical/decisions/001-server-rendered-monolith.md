# ADR-001 — Monolithe Django avec rendu serveur
## Statut
Accepté
## Contexte
Le Gestionnaire d'interventions est une application métier dont les
principaux parcours reposent sur des formulaires, des listes, des
filtres et la consultation de données.

Le MVP ne nécessite ni interactions temps réel ni interface de type SPA.

## Décision
L'application sera développée sous forme de monolithe Django avec
rendu HTML côté serveur.

JavaScript ne sera ajouté que lorsqu'un besoin utilisateur identifié
le justifie.

## Conséquences
### Positives
- architecture plus simple ;
- moins de dépendances ;
- réduction du JavaScript côté client ;
- utilisation des comportements natifs du navigateur ;
- maintenance facilitée ;
- infrastructure de production plus simple.
### Contraintes
- certaines améliorations interactives pourront nécessiter du
  progressive enhancement ;
- cette décision devra être réévaluée si les besoins fonctionnels
  évoluent significativement.