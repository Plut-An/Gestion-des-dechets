classDiagram
    class Utilisateur {
        -int idUtilisateur
        -string nomUtilisateur
        -string email
        -string motDePasse
        -date dateInscription
        +seConnecter() bool
        +seDeconnecter() bool
        +modifierProfil() bool
    }
 
    class Citoyen {
        -int solde_eco_points
        +creerCompte() bool
        +creerSignalement()
        +participerEvenement()
    }
 
    class Chauffeur {
        -string numero_permis
        -boolean disponibilite
        +validerCollecte() bool
        +refuserCollecte() bool
    }
 
    class RefusCollecte {
        -int idRefus
        -string motifEcrit
        -string photoJustificative
        -datetime dateRefus
        +enregistrerRefus() bool
    }

    class Noeud {
        -int idNoeud
        -float latitude
        -float longitude
        -string nomLieu
    }
 
    class PointDeCollecte {
        -string typeBac
        -int capacite_bacs
        -int etat_remplissage
        -boolean est_prioritaire
        -string etat_proprete_alentours
        -datetime date_derniere_collecte
    }
 
    class CentreDeTri {
        -int idCentre
        -float capaciteMax
        -float stockActuel
        +mettreAJourStock() bool
    }

    class Bareme {
        -int id
        -string type_materiau
        -int points_par_kg
    }
 
    class DepotDechet {
        -int id
        -float poids
        -int points_attribues
        -datetime date_depot
        +calculerPoints()
    }
 
    class Route {
        -int id
        -float distance
        -float poids
    }
 
    class Camion {
        -int id
        -string immatriculation
        -string gabarit
        -float capacite_max
        -float charge_actuelle
    }
 
    class Tournee {
        -int id
        -datetime date_creation
        -string statut
        -list chemin_ordonne
    }
 
    class Signalement {
        -int id
        -string photo
        -float latitude
        -float longitude
        -string type_dechet
        -string statut
    }
 
    class EvenementEcologique {
        -int id
        -string titre
        -datetime date_evenement
        -int compteur_volontaires
    }
 
    %% Relations d'héritage
    Utilisateur <|-- Citoyen
    Utilisateur <|-- Chauffeur
    Noeud <|-- PointDeCollecte
    Noeud <|-- CentreDeTri

    %% Relations Logistique & Graphes
    Chauffeur "1" -- "1" Camion : conduit
    Camion "1" -- "*" Tournee : effectue
    Route "*" -- "1" Noeud : depart
    Route "*" -- "1" Noeud : arrivee
    Tournee "*" -- "1" CentreDeTri : destination

    %% Relations Citoyen & Social
    Citoyen "1" -- "*" Signalement : cree
    Citoyen "*" -- "*" EvenementEcologique : participe

    %% Relations Récompenses & Tri
    Citoyen "1" -- "*" DepotDechet : effectue
    Bareme "1" -- "*" DepotDechet : qualifie
    Chauffeur "1" -- "*" DepotDechet : valide

    %% Relations de Gestion des Refus
    Chauffeur "1" -- "*" RefusCollecte : emet
    Signalement "1" -- "0..1" RefusCollecte : fait l'objet de