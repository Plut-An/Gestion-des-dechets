"""
Services algorithmiques — collecte et optimisation d'itinéraires.

Conformité ESMIA (projet transversal L2) :
  - Structure de données avancée : tas binaire (min-heap) implémenté à la main.
  - Algorithme de graphe : Dijkstra implémenté à la main (file de priorité = notre tas).
  - Baseline naïve : ordre des points sans critère de distance.
  - Simulation : comparaison temps d'exécution et distance totale.

Aucune boîte noire : pas de heapq, pas de networkx, pas de scipy.
Seuls modules standards autorisés pour la logique : time, math (si besoin).
"""
from __future__ import annotations

import time
from typing import Any

# ---------------------------------------------------------------------------
# 1. Tas binaire (min-heap) — implémentation manuelle
# ---------------------------------------------------------------------------


class MinHeap:
    """
    Tas binaire minimal implémenté avec un tableau dynamique (liste Python).

    Invariant : pour tout nœud d'indice i > 0,
        priorité(parent(i)) <= priorité(i)

    Chaque entrée est un couple (priorité: float, élément: Any).
  """

    def __init__(self) -> None:
        self._tas: list[tuple[float, Any]] = []

    def __len__(self) -> int:
        return len(self._tas)

    def est_vide(self) -> bool:
        return len(self._tas) == 0

    @staticmethod
    def _parent(index: int) -> int:
        return (index - 1) // 2

    @staticmethod
    def _gauche(index: int) -> int:
        return 2 * index + 1

    @staticmethod
    def _droite(index: int) -> int:
        return 2 * index + 2

    def _echanger(self, i: int, j: int) -> None:
        self._tas[i], self._tas[j] = self._tas[j], self._tas[i]

    def _remonter(self, index: int) -> None:
        """Restaure l'invariant après insertion en fin de tableau."""
        while index > 0:
            p = self._parent(index)
            if self._tas[index][0] < self._tas[p][0]:
                self._echanger(index, p)
                index = p
            else:
                break

    def _descendre(self, index: int) -> None:
        """Restaure l'invariant après extraction de la racine."""
        taille = len(self._tas)
        while True:
            g = self._gauche(index)
            d = self._droite(index)
            plus_petit = index

            if g < taille and self._tas[g][0] < self._tas[plus_petit][0]:
                plus_petit = g
            if d < taille and self._tas[d][0] < self._tas[plus_petit][0]:
                plus_petit = d

            if plus_petit != index:
                self._echanger(index, plus_petit)
                index = plus_petit
            else:
                break

    def inserer(self, priorite: float, element: Any) -> None:
        """Insère un élément avec sa clé de priorité (coût cumulé Dijkstra)."""
        self._tas.append((priorite, element))
        self._remonter(len(self._tas) - 1)

    def extraire_min(self) -> tuple[float, Any]:
        """
        Retire et renvoie le couple (priorité minimale, élément associé).

        Complexité amortie O(log n).
        """
        if self.est_vide():
            raise IndexError("Tas vide : extraire_min() impossible.")

        priorite_min, element_min = self._tas[0]
        dernier = self._tas.pop()

        if self._tas:
            self._tas[0] = dernier
            self._descendre(0)

        return priorite_min, element_min


# ---------------------------------------------------------------------------
# 2. Graphe routier — liste d'adjacence depuis les modèles Django
# ---------------------------------------------------------------------------


def construire_liste_adjacence(
    routes: list | None = None,
    *,
    bidirectionnel: bool = True,
    utiliser_poids: bool = False,
) -> dict[int, list[tuple[int, float]]]:
    """
    Construit la liste d'adjacence à partir des arêtes ``Route`` du modèle.

    Format : { id_noeud: [(id_voisin, cout_arête), ...], ... }

    Par défaut le coût est ``Route.distance`` (km) pour mesurer la distance
    parcourue. Si ``utiliser_poids=True``, on utilise ``Route.poids`` (utile
    pour des pondérations métier distinctes de la distance géographique).

    Args:
        routes: queryset / liste de ``Route`` ; si None, lecture en base.
        bidirectionnel: duplique chaque arête dans les deux sens (voirie urbaine).
    """
    if routes is None:
        from .models import Route

        routes = Route.objects.select_related("depart", "arrivee").all()

    adjacence: dict[int, list[tuple[int, float]]] = {}

    def _ajouter(u: int, v: int, cout: float) -> None:
        adjacence.setdefault(u, []).append((v, cout))

    for route in routes:
        cout = float(route.poids if utiliser_poids else route.distance)
        u, v = route.depart_id, route.arrivee_id
        _ajouter(u, v, cout)
        if bidirectionnel:
            _ajouter(v, u, cout)

    return adjacence


def obtenir_ids_points_prioritaires() -> list[int]:
    """
    Retourne les identifiants (pk hérité de ``Noeud``) des ``PointDeCollecte``
    marqués prioritaires (``est_prioritaire=True``).
    """
    from .models import PointDeCollecte

    return list(
        PointDeCollecte.objects.filter(est_prioritaire=True)
        .order_by("pk")
        .values_list("pk", flat=True)
    )


def resoudre_noeud_depart(
    *,
    noeud_id: int | None = None,
    centre_tri_id: int | None = None,
) -> int:
    """
    Détermine le nœud de départ d'une tournée.

    Priorité : ``noeud_id`` explicite > ``centre_tri_id`` (pk du centre).
    Un ``Camion`` n'est pas un nœud du graphe : on part du dépôt / centre
    associé à la tournée (voir modèle ``Tournee.destination``).
    """
    if noeud_id is not None:
        return noeud_id
    if centre_tri_id is not None:
        from .models import CentreDeTri

        centre = CentreDeTri.objects.get(pk=centre_tri_id)
        return centre.pk
    raise ValueError(
        "Fournir noeud_id ou centre_tri_id comme point de départ du graphe."
    )


# ---------------------------------------------------------------------------
# 3. Dijkstra — implémentation manuelle (file de priorité = MinHeap)
# ---------------------------------------------------------------------------


def dijkstra(
    adjacence: dict[int, list[tuple[int, float]]],
    depart: int,
) -> tuple[dict[int, float], dict[int, int | None]]:
    """
    Algorithme de Dijkstra — plus courts chemins depuis un sommet source.

    Étapes (prouvables sur papier) :
      1. Initialiser dist[depart] = 0, file de priorité {(0, depart)}.
      2. Tant que la file n'est pas vide :
         a. Extraire le sommet u de coût minimal (notre MinHeap).
         b. Si u déjà traité, ignorer (insertions multiples tolérées).
         c. Pour chaque voisin v de u avec arête de poids w :
            si dist[u] + w < dist[v], mettre à jour dist[v] et pred[v] = u.
      3. Renvoyer les tables de distances et de prédécesseurs.

    Complexité : O((V + E) log V) avec un tas binaire.

    Returns:
        distances: { sommet: distance_minimale depuis depart }
        predecesseurs: { sommet: parent sur le plus court chemin }
    """
    distances: dict[int, float] = {depart: 0.0}
    predecesseurs: dict[int, int | None] = {depart: None}
    visites: set[int] = set()
    file = MinHeap()
    file.inserer(0.0, depart)

    while not file.est_vide():
        dist_u, u = file.extraire_min()

        if u in visites:
            continue
        if dist_u > distances.get(u, float("inf")):
            continue

        visites.add(u)

        for voisin, poids_arete in adjacence.get(u, []):
            nouvelle_distance = dist_u + poids_arete
            if nouvelle_distance < distances.get(voisin, float("inf")):
                distances[voisin] = nouvelle_distance
                predecesseurs[voisin] = u
                file.inserer(nouvelle_distance, voisin)

    return distances, predecesseurs


def reconstruire_chemin(
    predecesseurs: dict[int, int | None],
    depart: int,
    arrivee: int,
) -> list[int]:
    """
    Reconstruit la liste ordonnée des nœuds du plus court chemin depart → arrivee.

    Remonte la chaîne des prédécesseurs ; renvoie [] si arrivee inaccessible.
    """
    if arrivee not in predecesseurs:
        return []

    chemin: list[int] = []
    courant: int | None = arrivee

    while courant is not None:
        chemin.append(courant)
        courant = predecesseurs.get(courant)

    chemin.reverse()

    if not chemin or chemin[0] != depart:
        return []

    return chemin


def dijkstra_chemin(
    adjacence: dict[int, list[tuple[int, float]]],
    depart: int,
    arrivee: int,
) -> tuple[list[int], float]:
    """
    Raccourci : exécute Dijkstra puis reconstruit le chemin vers ``arrivee``.

    Returns:
        (chemin_noeuds, distance_totale) ; distance = inf si inaccessible.
    """
    distances, predecesseurs = dijkstra(adjacence, depart)
    distance = distances.get(arrivee, float("inf"))
    if distance == float("inf"):
        return [], float("inf")
    chemin = reconstruire_chemin(predecesseurs, depart, arrivee)
    return chemin, distance


# ---------------------------------------------------------------------------
# 4. Ordonnancement des collectes — optimisé (glouton + Dijkstra) vs baseline
# ---------------------------------------------------------------------------


def _ordonner_points_baseline(points: list[int]) -> list[int]:
    """
    Baseline naïve : tri par identifiant croissant uniquement.

    Aucune prise en compte de la distance ou de la priorité géographique.
    """
    return sorted(points)


def _ordonner_points_glouton_dijkstra(
    adjacence: dict[int, list[tuple[int, float]]],
    depart: int,
    points: list[int],
) -> list[int]:
    """
    Heuristique gloutonne (cahier des charges — famille « Optimisation ») :

    À chaque étape, parmi les points restants, choisir le plus proche du
    nœud courant selon les distances issues de Dijkstra (plus court chemin
    sur le graphe routier, pas à vol d'oiseau).
    """
    restants = set(points)
    ordre: list[int] = []
    courant = depart

    while restants:
        distances, _ = dijkstra(adjacence, courant)
        prochain = min(
            restants,
            key=lambda pid: distances.get(pid, float("inf")),
        )
        ordre.append(prochain)
        restants.remove(prochain)
        courant = prochain

    return ordre


def _construire_tournee(
    adjacence: dict[int, list[tuple[int, float]]],
    depart: int,
    ordre_points: list[int],
) -> dict[str, Any]:
    """
    Enchaîne les plus courts chemins Dijkstra entre dépôt et chaque point,
    puis entre points consécutifs.

    Returns:
        dict avec ordre_visite, chemin_complet (sans répétition de jonctions),
        distance_totale, segments.
    """
    chemin_complet: list[int] = []
    distance_totale = 0.0
    segments: list[dict[str, Any]] = []
    position = depart

    for point in ordre_points:
        segment, dist = dijkstra_chemin(adjacence, position, point)
        if dist == float("inf"):
            segments.append(
                {
                    "de": position,
                    "vers": point,
                    "chemin": [],
                    "distance": None,
                    "accessible": False,
                }
            )
            continue

        distance_totale += dist
        segments.append(
            {
                "de": position,
                "vers": point,
                "chemin": segment,
                "distance": dist,
                "accessible": True,
            }
        )

        if not chemin_complet:
            chemin_complet.extend(segment)
        else:
            chemin_complet.extend(segment[1:])

        position = point

    return {
        "depart": depart,
        "ordre_visite": ordre_points,
        "chemin_complet": chemin_complet,
        "distance_totale": distance_totale,
        "segments": segments,
    }


def itineraire_optimise_dijkstra(
    adjacence: dict[int, list[tuple[int, float]]],
    depart: int,
    points_prioritaires: list[int] | None = None,
) -> dict[str, Any]:
    """
    Solution optimisée : ordre glouton par distances Dijkstra + chemins minimaux.

    Args:
        adjacence: liste d'adjacence du réseau (``construire_liste_adjacence``).
        depart: id du nœud de départ (centre de tri, dépôt, etc.).
        points_prioritaires: ids des ``PointDeCollecte`` ; si None, chargés en BDD.
    """
    if points_prioritaires is None:
        points_prioritaires = obtenir_ids_points_prioritaires()

    ordre = _ordonner_points_glouton_dijkstra(adjacence, depart, list(points_prioritaires))
    resultat = _construire_tournee(adjacence, depart, ordre)
    resultat["strategie"] = "dijkstra_glouton"
    return resultat


def itineraire_baseline(
    adjacence: dict[int, list[tuple[int, float]]],
    depart: int,
    points_collecte: list[int] | None = None,
) -> dict[str, Any]:
    """
    Solution naïve : ordre par identifiant, même calcul de distance sur le graphe
    (seul l'ordonnancement change — comparaison équitable pour le dossier).
    """
    if points_collecte is None:
        points_collecte = obtenir_ids_points_prioritaires()

    ordre = _ordonner_points_baseline(list(points_collecte))
    resultat = _construire_tournee(adjacence, depart, ordre)
    resultat["strategie"] = "baseline_tri_par_id"
    return resultat


# ---------------------------------------------------------------------------
# 5. Simulation comparative — métriques pour le dossier algorithmique
# ---------------------------------------------------------------------------


def simuler_comparaison_algorithmes(
    adjacence: dict[int, list[tuple[int, float]]] | None = None,
    depart: int | None = None,
    points: list[int] | None = None,
    *,
    centre_tri_id: int | None = None,
    repetitions: int = 1,
) -> dict[str, Any]:
    """
    Compare baseline et solution Dijkstra : temps CPU et distance totale.

    Args:
        adjacence: graphe ; construit depuis la BDD si None.
        depart: nœud source ; résolu via ``centre_tri_id`` si None.
        points: liste de points à visiter ; prioritaires en BDD si None.
        centre_tri_id: raccourci pour le nœud de départ (``CentreDeTri.pk``).
        repetitions: nombre d'exécutions pour lisser le temps (moyenne).

    Returns:
        Rapport structuré prêt pour le dossier algorithmique ESMIA.
    """
    if adjacence is None:
        adjacence = construire_liste_adjacence()

    if depart is None:
        depart = resoudre_noeud_depart(centre_tri_id=centre_tri_id)

    if points is None:
        points = obtenir_ids_points_prioritaires()

    # --- Mesure baseline ---
    temps_baseline_debut = time.perf_counter()
    for _ in range(repetitions):
        resultat_baseline = itineraire_baseline(adjacence, depart, points)
    temps_baseline = (time.perf_counter() - temps_baseline_debut) / repetitions

    # --- Mesure optimisée (Dijkstra + glouton) ---
    temps_optimise_debut = time.perf_counter()
    for _ in range(repetitions):
        resultat_optimise = itineraire_optimise_dijkstra(adjacence, depart, points)
    temps_optimise = (time.perf_counter() - temps_optimise_debut) / repetitions

    dist_baseline = resultat_baseline["distance_totale"]
    dist_optimise = resultat_optimise["distance_totale"]

    if dist_baseline > 0:
        gain_distance_pct = round((1 - dist_optimise / dist_baseline) * 100, 2)
    else:
        gain_distance_pct = 0.0

    if temps_baseline > 0:
        ratio_temps = round(temps_optimise / temps_baseline, 4)
    else:
        ratio_temps = None

    return {
        "parametres": {
            "noeud_depart": depart,
            "nombre_points": len(points),
            "nombre_aretes": sum(len(v) for v in adjacence.values()) // 2,
            "repetitions_chronometrage": repetitions,
        },
        "baseline": {
            "strategie": resultat_baseline["strategie"],
            "ordre_visite": resultat_baseline["ordre_visite"],
            "distance_totale_km": round(dist_baseline, 4),
            "temps_execution_s": round(temps_baseline, 6),
            "chemin_complet": resultat_baseline["chemin_complet"],
        },
        "optimise_dijkstra": {
            "strategie": resultat_optimise["strategie"],
            "ordre_visite": resultat_optimise["ordre_visite"],
            "distance_totale_km": round(dist_optimise, 4),
            "temps_execution_s": round(temps_optimise, 6),
            "chemin_complet": resultat_optimise["chemin_complet"],
        },
        "comparaison": {
            "gain_distance_pct": gain_distance_pct,
            "economie_distance_km": round(dist_baseline - dist_optimise, 4),
            "ratio_temps_optimise_sur_baseline": ratio_temps,
            "conclusion": _generer_conclusion(dist_baseline, dist_optimise, gain_distance_pct),
        },
    }


def _generer_conclusion(
    dist_baseline: float,
    dist_optimise: float,
    gain_pct: float,
) -> str:
    if dist_baseline == dist_optimise:
        return (
            "Distances identiques sur cet instance : le graphe est symétrique "
            "ou l'ordre glouton coïncide avec le tri par identifiant."
        )
    if dist_optimise < dist_baseline:
        return (
            f"L'ordonnancement glouton guidé par Dijkstra réduit la distance "
            f"totale de {gain_pct} % par rapport à la baseline (tri par ID)."
        )
    return (
        "La baseline est plus courte sur cette instance (graphe dégénéré ou "
        "très peu de points) ; tester sur un réseau plus dense."
    )


# ---------------------------------------------------------------------------
# Graphe de démonstration (hors base) — tests unitaires / démonstration
# ---------------------------------------------------------------------------


def _graphe_demonstration() -> dict[int, list[tuple[int, float]]]:
    """
    Petit réseau non orienté pour valider Dijkstra sans base de données.

        (1)---2---(2)---3---(3)
         |               |
         4               1
         |               |
        (4)---1---(5)---2---(6)

    Les identifiants correspondent à des ``Noeud.pk`` fictifs.
    """
    return {
        1: [(2, 2.0), (4, 4.0)],
        2: [(1, 2.0), (3, 3.0), (5, 5.0)],
        3: [(2, 3.0), (6, 1.0)],
        4: [(1, 4.0), (5, 1.0)],
        5: [(2, 5.0), (4, 1.0), (6, 2.0)],
        6: [(3, 1.0), (5, 2.0)],
    }


def executer_demonstration() -> dict[str, Any]:
    """
    Lance la simulation sur le graphe de démonstration (aucune BDD requise).

    Usage (shell Django) ::
        from core.services import executer_demonstration
        print(executer_demonstration())
    """
    adj = _graphe_demonstration()
    depart = 1
    points = [3, 6, 4]
    return simuler_comparaison_algorithmes(
        adjacence=adj,
        depart=depart,
        points=points,
        repetitions=100,
    )
