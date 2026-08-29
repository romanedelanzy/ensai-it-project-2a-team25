# ensai-it-project-2a-team25

## Objectifs du groupe

### Fonctionnalités (récap)

* F1 gestion des utilisateurs (créer un compte, se connecter, consulter les données & stats, gérer ses stations favorites)

* F2 collecter les données : l'API doit être interrogée toutes les **15 mins** pour récupérer : 
station, date & heure, nb vélos simples dispos, nb vélos électriques dispos, nb places dispos, "état de la station"

* F3 : consulter une station en la cherchant pour afficher état / nb vélos dispos / capacité / taux remplissage / évolution disponibilité (dernières 24h, 7 derniers jours, 30 derniers jours)

* F4 : Afficher le score de fiabilité d'une station
une station est considérée comme :
    vide lorsqu’il n’y a plus de vélo disponible ;
    saturée lorsqu’il ne reste plus de place ;
    fonctionnelle dans les autres cas. À partir de l’historique, l’application calcule notamment :
    pourcentage du temps passé vide ;
    pourcentage du temps passé saturé ;
    durée moyenne des épisodes de saturation ;
    durée moyenne des épisodes de pénurie ;
    évolution du score au cours du temps. Le score global est défini par les étudiants à partir d’une formule documentée.

* F5 : Recommandation d'une station à proximité
 La recommandation doit prendre en compte plusieurs critères, par exemple :
    distance ;
    nombre de vélos actuellement disponibles ;
    fiabilité historique de la station ;
    disponibilité de vélos électriques ;
    tendance récente de la station. Deux stations à distance équivalente ne doivent donc pas nécessairement être classées de la même manière. La formule de classement devra être justifiée et testée.



Donc il faut : 

* créer aussi les fonctions : 
- calcul du nombre de vélos dispos (total)
- taux de remplissage
- évolution de la disponibilité sur une période donnée (options 24h, 7 derniers j, 30 derniers j)

* prévoir un endroit pour stocker les stations favorites

### Cas d'utilisations

[Diagramme](https://lucid.app/lucidchart/11385ae2-093a-4a4a-a18d-7719b361128d/edit?viewport_loc=24%2C-8%2C991%2C517%2C0_0&invitationId=inv_ad916afa-9387-41ec-bbb5-33822a07e556)

--> est-ce qu'il faut mettre sign up & sign in dans le diagramme ?
Si oui est-ce qu'il faut mettre le rôle admin & user après le sign up & sign in ?

## Ressources

[Site pour trouver une base de données](https://mobilitydatabase.org/feeds?gbfs=true)
A creuser : il faut une base de données qui contient les infos sur les stations dont 
* nom de la station
* date et heure
* nombre de vélos simples dispos
* nombres de places dispos
* capacité
* nombre des vélos électriques dispos
* état de la station
Il faut trouver une base de données utilisable en PostgreSQL

Fonctionnement API / base de données : 
* On choisit un flux Json GBFS actif sur le site
* On fait des requêtes toutes les 15 minutes vers ce flux en utilisant le backend
* On stocke ces données soi-même dans notre propre base PostgreSQL.
Chacun de nous aura son propre service postgre sql sur le SSPCloud & le reliera à l'application.

Lien vers des flux qui pourraient fonctionner : 

[7 Vallées vélo](https://mobilitydatabase.org/feeds/gbfs/gbfs-7vallees) Mais seulement 4 stations, et que des vélos électriques ou à assistance électrique

[Cité Cycle](https://mobilitydatabase.org/feeds/gbfs/gbfs-citecycle) pareil