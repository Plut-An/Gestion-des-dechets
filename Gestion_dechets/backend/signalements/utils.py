"""
Utilitaire — calcul de distance Haversine
"""
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcule la distance en kilomètres entre deux points GPS
    en utilisant la formule de Haversine.

    Args:
        lat1, lon1: coordonnées du point de départ
        lat2, lon2: coordonnées du point d'arrivée

    Returns:
        Distance en kilomètres (float)
    """
    R = 6371  # Rayon moyen de la Terre en km

    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def get_signalements_proches(signalements_qs, lat: float, lon: float, rayon_km: float = 50):
    """
    Filtre et trie les signalements par distance croissante depuis (lat, lon).

    Args:
        signalements_qs: QuerySet de Signalement
        lat, lon: position du camioneur
        rayon_km: rayon maximum de recherche (défaut 50km)

    Returns:
        Liste de (signalement, distance_km) triée par distance croissante
    """
    resultats = []
    for signalement in signalements_qs:
        dist = haversine_distance(lat, lon, signalement.latitude, signalement.longitude)
        if dist <= rayon_km:
            resultats.append((signalement, round(dist, 2)))

    # Trier par distance croissante
    resultats.sort(key=lambda x: x[1])
    return resultats
