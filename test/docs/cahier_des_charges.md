 CAHIER DES CHARGES :
Système de Gestion des Déchets

1.	Informations générales

	Titre du projet : Plateforme de collecte et d'optimisation du traitement des déchets urbains.
	NIE de l’étudiant : SE20240191
	Nom et prénom de l’étudiant : RAVELOSON Andrianavalona Andoniaina


2.	Contexte et justification

1)	Problématique rencontrée : Actuellement, la gestion des ordures ménagères souffre de bacs qui débordent, de circuits de ramassage irréguliers et d'un manque de visibilité pour les citoyens. Cela cause des pollutions de l'air, des blocages de canaux et des risques sanitaires graves.

2)	Importance du projet : Une ville propre est essentielle pour la santé publique et le développement touristique. Le numérique peut transformer les déchets en ressources (recyclage) plutôt qu'en nuisances.


3)	Objectifs du projet :
o	Optimiser les trajets des camions de ramassage pour gagner du temps et du carburant.
o	Permettre aux citoyens de signaler des bacs pleins ou des dépôts sauvages.
o	Centraliser les données sur la quantité de déchets produite par quartier.
o	Encourager le tri sélectif via un système de récompenses numériques.


3.	Périmètre du projet
•	Gestion des points de collecte : Inventaire des bacs, état de remplissage et localisation.
•	Optimisation des tournées : Calcul du meilleur itinéraire pour les camions
•	Interface citoyenne : Application pour signaler un problème ou voir l'heure de passage du camion.
•	Suivi du matériel : Gestion de l'état des camions de collecte et planning de maintenance.
•	Statistiques : Rapports sur le tonnage collecté et le taux de recyclage.








4.	Analyse des besoins 

Priorité	Fonctionnalité	Description
Must	Authentification & Profils	Connexion sécurisée selon le rôle (Citoyen, Chauffeur, Administrateur)
Must	Gestion des Inscriptions	Validation de l’inscription des citoyens par l’administrateur 
Must	Itinéraire & Optimisation	Calcul du trajet le plus court pour collecter les bacs pleins et déchets signalés
Must	Signalement Citoyen	Envoi de photos et position GPS pour les déchets ou anomalies constatées
Must	Module Événements & Social	Publication d'actions écologiques avec interactions (likes, commentaires)
Must	Système de Récompenses	Attribution d'Eco-Points après validation du tri par l’administrateur
Must	Dashboard Administrateur	Pilotage en temps réel de la propreté et des statistiques de tonnage
Should	Gestion informations	Mise à jour des profils, édition des points de collecte et gestion des stocks de bacs vides
Should	Justification refus	Saisie obligatoire d'un motif par le chauffeur en cas de collecte impossible (ex: accès bloqué, déchet non conforme)
Could	Suivi de Présence	Validation de la participation réelle aux événements pour l'octroi des points
Could	Contrôle & Liaison	Messagerie chauffeur-association et gestion des motifs de refus de collecte
5.	Description détaillée des fonctionnalités

Titre	Description	Données manipulées	Acteurs concernés	Résultats attendus	Contraintes techniques
Authentification	Accès sécurisé à l'espace personnel	Nom de l’utilisateur, Rôle, mdp	Tous	Accès restreint selon les permissions	Basse consommation 
Gestion des inscriptions	Vérification et activation manuelle des nouveaux comptes	Informations personnelles, Pièces jointes (ID, justificatif) 	Administrateur	Accès sécurisé et filtré à la plateforme	Obligation de validation avant connexion
Signalement citoyen	Transmission d'une alerte concernant un dépôt sauvage ou un bac plein	Photo, Géolocalisation, Type de déchet	Citoyen	Signalement immédiat d'un point à nettoyer	Précision des coordonnées
Dashboard	Visualisation globale de l'état du réseau et des performances de collecte	Statistiques de tonnage, Cartographie des bacs pleins	Administrateur	Aide à la décision et suivi de l'impact écologique	Mise à jour en temps réel
Gestion du réseau	Mise à jour des points de collecte et des routes	Informations sur les centres 	Administrateur	Informations bien mise à jour	Intégrité des données géographiques
Optimisation Tournées	Guidage des camions vers les urgences.	Graphes, Coordonnées, Capacités.	Chauffeurs	Gain de temps et économie de carburant	Prise en compte du gabarit du camion
Récompenses	Valorisation du tri sélectif	Poids (kg), Type, Solde points.	Citoyens	Augmentation du taux de recyclage	Calcul instantané du barème
Réseau Social Éco	Interaction sur les projets collectifs	Likes, Commentaires, Inscriptions	Citoyens, Administrateur 	Dynamisation de la communauté	Modération des contenus par l'association
Contrôle Collecte	Justification des refus d'enlèvement	Photos, Motif	Chauffeurs, Citoyens	Transparence et preuve du refus
	Horodatage et géolocalisation du refus
6.	Acteurs du système

•	Citoyens : Utilisent l'application pour signaler des déchets, des problèmes et suivre les passages
•	Chauffeurs de camions : Suivent l'itinéraire optimisé sur leur tablette et récupèrent les déchets
•	Administrateurs : Supervisent l’ensemble de la plateforme


7.	Scénarios utilisateurs

Scénario 1 : Inscription soumise à validation
Titre : Inscription et validation de compte citoyen 
Acteur principal : Visiteur
Acteurs secondaires : Administrateur
Pré-conditions : Le visiteur possède ses pièces justificatives numérisées.
	Déroulement Nominal :
o	Le visiteur clique sur "S'inscrire" et remplit le formulaire.
o	Le visiteur télécharge ses pièces jointes (certificat de résidence, ID).
o	Le système enregistre la demande avec le statut "En attente".
o	L'administrateur se connecte à son dashboard et consulte la liste des demandes.
o	L'administrateur vérifie les documents et clique sur "Valider".
o	Le système active le compte et envoie un email de confirmation au citoyen.
Scénario 2 : Signalement et gestion de collecte
Titre : Signalement de déchets et mise à jour de l'itinéraire
Acteur principal : Citoyen connecté
Acteurs secondaires : Camionneur, SI (Système d’information)
Pré-conditions : Le citoyen est géo-localisé à proximité du déchet.
Déroulement Nominal :	
o	Le citoyen remplit le formulaire de signalement (photo, type de déchet, position GPS).
o	Le système crée un ticket et notifie le camionneur le plus proche.
o	Le camionneur consulte le signalement sur son smartphone.
o	Le camionneur valide la conformité du signalement.
o	Le système recalcule l'itinéraire optimisé en incluant ce nouveau point.
Variante (Refus) : 
2a. Le camionneur juge le signalement non conforme (ex: accès impossible). 
2b. Le camionneur clique sur "Refuser" et saisit le motif (Justification de refus).


Scénario 3 : Organisation et participation à un événement
Titre : Création et inscription à une action écologique
Acteur principal : Administrateur
Acteurs secondaires : Citoyen connecté
Pré-conditions : L'administrateur est connecté à l'espace de gestion.
Déroulement Nominal :
o	L'administrateur crée un événement (ex: "Nettoyage Anosy") avec date, lieu et description.
o	Le système publie l'annonce sur le Réseau Social Éco.
o	Le citoyen consulte le fil d'actualité et clique sur "Participer" sur l'annonce d'Anosy.
o	Le système transmet la postulation à l'administrateur
o	Le système ajoute le citoyen à la liste des participants et met à jour le compteur de volontaires




8.	Contraintes du projet 

•	Coupures d'énergie : Le système doit être léger pour économiser la batterie des appareils mobiles.
•	Multilingue : Interface obligatoire en Français et Malagasy.
•	Accessibilité : Interface adaptée pour les sourds et muets


9.	Technologies utilisées

•	Backend : Django
•	Mobile : React native 
•	Web : React
•	Base de données : SqLite

10.	Exigences algorithmiques 

Famille d'algorithme	Algorithme choisi	Utilisation dans le projet
Graphes / Réseaux 	Dijkstra ou A*	Calculer le trajet le plus court entre le dépôt et les bacs à ordures prioritaires (ceux qui sont pleins)

Optimisation 	Algorithme Glouton (Greedy)	Définir l'ordre de ramassage en choisissant toujours le bac le plus urgent à proximité pour remplir le camion efficacement



