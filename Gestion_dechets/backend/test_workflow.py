import os
import sys
import json
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta

def assert_status(response, expected_status, step_name):
    if response.status_code != expected_status:
        print(f"❌ ERREUR: {step_name}")
        print(f"Attendu: {expected_status}, Reçu: {response.status_code}")
        try:
            print(f"Détails: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"Détails: {response.content}")
        sys.exit(1)
    else:
        print(f"✅ {step_name}")

def run():
    client = APIClient()
    
    print("=== DÉMARRAGE DU TEST WORKFLOW ===")

    from accounts.models import CustomUser
    admin_user, _ = CustomUser.objects.get_or_create(
        email='admin@dechets.mg',
        defaults={'nom': 'Super Admin', 'role': 'admin', 'is_staff': True, 'is_superuser': True}
    )
    admin_user.set_password('Admin1234!')
    admin_user.save()

    # Login Admin
    resp = client.post('/api/auth/login/', {'email': 'admin@dechets.mg', 'password': 'Admin1234!'})
    assert_status(resp, 200, "Login Admin")
    token_admin = resp.json()['access']
    client_admin = APIClient()
    client_admin.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)

    # 2. Inscription Citoyen
    citoyen_data = {
        'email': 'citoyen1@test.com',
        'nom': 'Jean Citoyen',
        'password': 'Password123!',
        'password2': 'Password123!',
        'adresse': 'Antananarivo'
    }
    resp = client.post('/api/auth/register/citoyen/', citoyen_data)
    assert_status(resp, 201, "Inscription Citoyen")
    citoyen_id = resp.json()['user']['id']
    token_citoyen = resp.json()['access']
    client_citoyen = APIClient()
    client_citoyen.credentials(HTTP_AUTHORIZATION='Bearer ' + token_citoyen)

    # 3. Inscription Camioneur
    camioneur_data = {
        'email': 'camion1@test.com',
        'nom': 'Marc Camioneur',
        'password': 'Password123!',
        'password2': 'Password123!',
        'numero_permis': 'PERMIS-12345'
    }
    resp = client.post('/api/auth/register/camioneur/', camioneur_data)
    assert_status(resp, 201, "Inscription Camioneur")
    camioneur_id = resp.json()['user']['id']
    token_camioneur = resp.json()['access']
    client_camioneur = APIClient()
    client_camioneur.credentials(HTTP_AUTHORIZATION='Bearer ' + token_camioneur)

    # Fetch exact IDs from admin endpoints
    resp = client_admin.get('/api/admin/citoyens/')
    citoyens = resp.json()['results']
    citoyen_id = next(c['id'] for c in citoyens if c['email'] == 'citoyen1@test.com')

    resp = client_admin.get('/api/admin/camioneurs/')
    camioneurs = resp.json()['results']
    camioneur_id = next(c['id'] for c in camioneurs if c['email'] == 'camion1@test.com')

    # 4. Validation par Admin
    resp = client_admin.post(f'/api/admin/citoyens/{citoyen_id}/valider/', {'action': 'accepter'})
    assert_status(resp, 200, "Admin valide Citoyen")
    
    resp = client_admin.post(f'/api/admin/camioneurs/{camioneur_id}/valider/', {'action': 'accepter'})
    assert_status(resp, 200, "Admin valide Camioneur")

    # Changement mot de passe obligatoire camioneur
    resp = client_camioneur.post('/api/auth/change-password/', {
        'ancien_mot_de_passe': 'Password123!',
        'nouveau_mot_de_passe': 'NewPass123!',
        'confirmation': 'NewPass123!'
    })
    assert_status(resp, 200, "Camioneur change mdp")

    # 5. Création Association par Admin
    resp = client_admin.post('/api/admin/associations/', {
        'nom': 'Asso Ecolo Mada',
        'ville': 'Antananarivo',
        'description': 'Association écologique de Mada',
        'email': 'asso@test.mg',
        'password': 'Password123!'
    })
    assert_status(resp, 201, "Admin crée Association")
    asso_id = resp.json()['id']

    # Login Association
    resp = client.post('/api/auth/login/', {'email': 'asso@test.mg', 'password': 'Password123!'})
    assert_status(resp, 200, "Login Association")
    token_asso = resp.json()['access']
    client_asso = APIClient()
    client_asso.credentials(HTTP_AUTHORIZATION='Bearer ' + token_asso)

    # 6. Citoyen rejoint Association
    resp = client_citoyen.post(f'/api/associations/{asso_id}/rejoindre/')
    assert_status(resp, 201, "Citoyen demande à rejoindre l'Association")

    # L'association accepte l'adhésion
    resp = client_asso.get('/api/associations/adhesions/')
    assert_status(resp, 200, "Liste des adhésions en attente")
    adhesions = resp.json()['results']
    if len(adhesions) == 0:
        print("❌ ERREUR: Adhésion non trouvée")
        sys.exit(1)
    adhesion_id = adhesions[0]['id']

    resp = client_asso.post(f'/api/associations/adhesions/{adhesion_id}/action/', {'action': 'accepter'})
    assert_status(resp, 200, "Association accepte l'adhésion")

    # 7. Création Evénement
    date_ev = (timezone.now() + timedelta(days=2)).isoformat()
    resp = client_asso.post('/api/mobile/association/evenements/', {
        'titre': 'Nettoyage Analakely',
        'description': 'On nettoie le centre ville',
        'date_evenement': date_ev,
        'lieu': 'Analakely',
        'statut': 'a_venir'
    })
    assert_status(resp, 201, "Association crée un Événement")
    ev_id = resp.json()['id']

    # 8. Citoyen s'inscrit à l'Evénement
    resp = client_citoyen.post(f'/api/mobile/evenements/{ev_id}/participer/')
    assert_status(resp, 201, "Citoyen participe à l'Événement")

    # L'association valide la présence
    resp = client_asso.get(f'/api/mobile/association/evenements/{ev_id}/participants/')
    assert_status(resp, 200, "Liste participants")
    participants = resp.json()['results']
    part_id = participants[0]['id']

    resp = client_asso.post(f'/api/mobile/association/evenements/{ev_id}/participants/{part_id}/confirmer/')
    assert_status(resp, 200, "Association confirme la présence (+10 points)")

    # 8.5 Test Commentaires
    resp = client_citoyen.post(f'/api/mobile/evenements/{ev_id}/commentaires/', {
        'contenu': 'Super événement, hâte d\'y être !'
    })
    assert_status(resp, 201, "Membre (citoyen) poste un commentaire")
    comment_id = resp.json()['id']

    # Liste des commentaires
    resp = client_citoyen.get(f'/api/mobile/evenements/{ev_id}/commentaires/')
    assert_status(resp, 200, "Liste des commentaires")
    if len(resp.json()['results']) == 0:
        print("❌ ERREUR: Commentaire non trouvé dans la liste")
        sys.exit(1)

    # Inscription Citoyen 2 (non membre)
    client_citoyen2 = APIClient()
    resp = client_citoyen2.post('/api/auth/register/citoyen/', {
        'email': 'citoyen2@test.com',
        'nom': 'Paul NonMembre',
        'password': 'Password123!',
        'password2': 'Password123!'
    })
    token_citoyen2 = resp.json()['access']
    client_citoyen2.credentials(HTTP_AUTHORIZATION='Bearer ' + token_citoyen2)

    # Test qu'un non-membre ne peut pas commenter
    resp = client_citoyen2.post(f'/api/mobile/evenements/{ev_id}/commentaires/', {
        'contenu': 'Puis-je commenter ?'
    })
    assert_status(resp, 403, "Non-membre est rejeté en tentant de commenter")

    # Admin Asso poste un commentaire
    resp = client_asso.post(f'/api/mobile/evenements/{ev_id}/commentaires/', {
        'contenu': 'N\'oubliez pas vos gants !'
    })
    assert_status(resp, 201, "Admin Asso poste un commentaire")

    # Admin Asso supprime le commentaire du citoyen
    resp = client_asso.delete(f'/api/mobile/commentaires/{comment_id}/')
    assert_status(resp, 204, "Admin supprime le commentaire du citoyen")

    # 9. Citoyen signale un déchet
    # On simule un upload d'image en text (test uniquement)
    import tempfile
    valid_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDAT\x08\x99c\xf8\x0f\x04\x00\t\xfb\x03\xfd\xe3U\xf2\x9c\x00\x00\x00\x00IEND\xaeB`\x82'
    with tempfile.NamedTemporaryFile(suffix='.png') as f:
        f.write(valid_png)
        f.flush()
        
        with open(f.name, 'rb') as photo:
            resp = client_citoyen.post('/api/mobile/signalements/', {
                'latitude': '-18.91368',
                'longitude': '47.53613',
                'description': 'Tas de plastique près du marché',
                'type_dechet': 'plastique',
                'photo': photo
            }, format='multipart')
    
    assert_status(resp, 201, "Citoyen signale un déchet")
    signalement_id = resp.json()['id']

    # 10. Camioneur se connecte et update sa position
    # 5 km de distance env.
    resp = client_camioneur.put('/api/mobile/camioneur/position/', {
        'latitude': '-18.89368',
        'longitude': '47.51613',
        'disponible': True
    })
    assert_status(resp, 200, "Camioneur met à jour sa position")

    # 11. Camioneur regarde les signalements proches
    resp = client_camioneur.get(f'/api/mobile/camioneur/signalements/?lat=-18.89368&lng=47.51613&rayon=50')
    assert_status(resp, 200, "Camioneur voit les signalements proches")
    sig_proches = resp.json()['signalements']
    if len(sig_proches) == 0:
        print("❌ ERREUR: Signalement non vu par le camioneur")
        sys.exit(1)
    
    # 12. Camioneur accepte
    resp = client_camioneur.post(f'/api/mobile/camioneur/signalements/{signalement_id}/accepter/')
    assert_status(resp, 200, "Camioneur accepte le signalement")

    # 13. Camioneur valide
    resp = client_camioneur.post(f'/api/mobile/camioneur/signalements/{signalement_id}/valider/')
    assert_status(resp, 200, "Camioneur valide le ramassage (+5 points)")

    # 14. Vérification des points du Citoyen
    resp = client_citoyen.get('/api/auth/me/')
    assert_status(resp, 200, "Check Profil Citoyen")
    pts = resp.json()['profil_citoyen']['solde_eco_points']
    if pts == 15:
        print("✅ Points corrects (10 pour événement + 5 pour ramassage)")
    else:
        print(f"❌ ERREUR: Points = {pts} (Attendu: 15)")
        sys.exit(1)

    print("\n=== TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS ===")

if __name__ == '__main__':
    run()
