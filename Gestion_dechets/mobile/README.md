# ÉcoGestion — Application mobile (Expo)

Application React Native / Expo pour **citoyens** et **camioneurs**, connectée à l'API Django du projet.

## Prérequis

- Node.js 18+
- Backend Django lancé sur le port 8000
- [Expo Go](https://expo.dev/go) sur téléphone ou émulateur Android

## Installation

```bash
cd mobile
npm install
cp .env.example .env
# Adapter EXPO_PUBLIC_API_URL si besoin (IP locale pour téléphone physique)
```

## Lancement

```bash
npm start
# puis a (Android) ou scan QR code avec Expo Go
```

## Comptes de test

Utilisez un citoyen/camioneur validé par l'admin, ou inscrivez-vous depuis l'app.

Admin web (séparé) : `admin@test.mg` / `Admin123!`

## Fonctionnalités

### Citoyen
- Inscription / connexion
- Signalements (photo + GPS)
- Associations (demande d'adhésion)
- Événements (participer, commentaires)
- Flux d'annonces
- Profil & éco-points

### Camioneur
- Inscription / connexion
- Position GPS + disponibilité
- Signalements proches (Haversine)
- Accepter / valider / refuser collecte
- Historique des collectes
- Changement de mot de passe

## Configuration API

| Environnement | URL |
|---------------|-----|
| iOS Simulator | `http://127.0.0.1:8000` |
| Android Emulator | `http://10.0.2.2:8000` (défaut) |
| Téléphone réel | `http://<IP-LAN-PC>:8000` |

Assurez-vous que `DEBUG=True` côté Django (CORS ouvert) ou ajoutez l'origine Expo dans `CORS_ALLOWED_ORIGINS`.
