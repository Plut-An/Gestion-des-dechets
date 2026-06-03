class MinHeapSignalements:
    """
    Structure de données de Tas Binaire (Min-Heap).
    Utilisée pour optimiser l'algorithme glouton (Greedy) en extrayant continuellement
    le signalement le plus proche en temps O(log N) au lieu de O(N).
    """
    def __init__(self):
        self.heap = []

    def ajouter(self, distance, signalement):
        self.heap.append((distance, signalement))
        self._entasser_vers_le_haut(len(self.heap) - 1)

    def extraire_minimum(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()[1]
        
        racine = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._entasser_vers_le_bas(0)
        return racine[1]

    def _entasser_vers_le_haut(self, index):
        parent = (index - 1) // 2
        if index > 0 and self.heap[index][0] < self.heap[parent][0]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._entasser_vers_le_haut(parent)

    def _entasser_vers_le_bas(self, index):
        gauche = 2 * index + 1
        droite = 2 * index + 2
        plus_petit = index

        if gauche < len(self.heap) and self.heap[gauche][0] < self.heap[plus_petit][0]:
            plus_petit = gauche
        if droite < len(self.heap) and self.heap[droite][0] < self.heap[plus_petit][0]:
            plus_petit = droite

        if plus_petit != index:
            self.heap[index], self.heap[plus_petit] = self.heap[plus_petit], self.heap[index]
            self._entasser_vers_le_bas(plus_petit)

    def est_vide(self):
        return len(self.heap) == 0


class TableHachagePerformance:
    """
    Structure de données de Table de Hachage personnalisée.
    Utilisée pour mémoriser/mettre en cache les calculs de distances ou les métriques
    de performance des camions afin de les récupérer en temps constant O(1).
    """
    def __init__(self, taille=100):
        self.taille = taille
        self.table = [[] for _ in range(self.taille)]

    def _fonction_hachage(self, cle):
        # Somme des valeurs ASCII de la clé textuelle modulo la taille de la table
        return sum(ord(char) for char in str(cle)) % self.taille

    def inserer(self, cle, valeur):
        index = self._fonction_hachage(cle)
        for i, kv in enumerate(self.table[index]):
            if kv[0] == cle:
                self.table[index][i] = (cle, valeur)
                return
        self.table[index].append((cle, valeur))

    def rechercher(self, cle):
        index = self._fonction_hachage(cle)
        for kv in self.table[index]:
            if kv[0] == cle:
                return kv[1]
        return None
    

class GrapheRoutierUrbain:
    """
    Structure de données en Liste d'Adjacence pour représenter le réseau routier.
    Gère les intersections (sommets) et les axes/distances réelles (arêtes).
    """
    def __init__(self):
        self.adjacence = {}

    def ajouter_intersection(self, nom):
        if nom not in self.adjacence:
            self.adjacence[nom] = []

    def ajouter_route(self, depart, arrivee, distance_km):
        self.ajouter_intersection(depart)
        self.ajouter_intersection(arrivee)
        self.adjacence[depart].append((arrivee, distance_km))
        self.adjacence[arrivee].append((depart, distance_km)) # Route à double sens

    def dijkstra(self, depart, destination):
        """
        Algorithme de Graphes/Réseaux : Trouve le chemin réel le plus court.
        Complexité optimisée par le Tas Binaire : O((V + E) log V).
        """
        distances = {sommet: float('inf') for sommet in self.adjacence}
        distances[depart] = 0
        
        # Utilisation directe de la classe parente du même fichier (évite l'import circulaire)
        tas = MinHeapSignalements()
        tas.ajouter(0, depart)

        parent = {sommet: None for sommet in self.adjacence}

        while not tas.est_vide():
            if not tas.heap: 
                break
            dist_actuelle, sommet_actuel = tas.heap[0][0], tas.heap[0][1]
            tas.extraire_minimum()

            if sommet_actuel == destination:
                break

            if dist_actuelle > distances[sommet_actuel]:
                continue

            for voisin, poids in self.adjacence[sommet_actuel]:
                distance = dist_actuelle + poids

                if distance < distances[voisin]:
                    distances[voisin] = distance
                    parent[voisin] = sommet_actuel
                    tas.ajouter(distance, voisin)

        # Reconstruction du chemin
        chemin = []
        actuel = destination
        while actuel is not None:
            chemin.insert(0, actuel)
            actuel = parent[actuel]

        return distances[destination], chemin