"""
Test Complet — 50+ Endpoints avec Données Fictives
Vérifie l'ensemble du workflow et identifie les problèmes
"""
import os
import sys
import json
import django
import tempfile
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from django.utils import timezone
from accounts.models import CustomUser, Citoyen, Camioneur
from associations.models import Association, Adhesion, AcceptationCamioneur
from evenements.models import EvenementEcologique, Participation, Annonce
from signalements.models import Signalement

# Couleurs pour les tests
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def log_test(name, passed, details='', response=None):
    status = f"{GREEN}✅{RESET}" if passed else f"{RED}❌{RESET}"
    print(f"{status} {name}" + (f" — {details}" if details else ""))
    if not passed and response is not None:
        try:
            err_data = response.json()
            print(f"   ERROR: {json.dumps(err_data, ensure_ascii=False)}")
        except:
            print(f"   ERROR: {response.content}")
    return passed

def log_section(title):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

def run_comprehensive_tests():
    log_section("DÉMARRAGE DES TESTS COMPLETS — 50+ ENDPOINTS")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CLEANUP : Reset database for fresh tests
    # ═══════════════════════════════════════════════════════════════════════════
    print(f"🧹 Nettoyage de la base de données...")
    CustomUser.objects.all().delete()
    Citoyen.objects.all().delete()
    Camioneur.objects.all().delete()
    Association.objects.all().delete()
    Adhesion.objects.all().delete()
    EvenementEcologique.objects.all().delete()
    Participation.objects.all().delete()
    Annonce.objects.all().delete()
    Signalement.objects.all().delete()
    print(f"✅ Base de données nettoyée\n")
    
    tests_passed = 0
    tests_failed = 0
    
    client = APIClient()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 1 : SETUP ADMIN & USERS
    # ═══════════════════════════════════════════════════════════════════════════
    log_section("PHASE 1 : CRÉATION & AUTHENTIFICATION")
    
    # Créer admin
    admin_user, _ = CustomUser.objects.get_or_create(
        email='admin@test.mg',
        defaults={'nom': 'Admin Test', 'role': 'admin', 'is_staff': True, 'is_superuser': True}
    )
    admin_user.set_password('Admin123!')
    admin_user.save()
    
    # 1. Login Admin
    resp = client.post('/api/auth/login/', {'email': 'admin@test.mg', 'password': 'Admin123!'})
    if log_test("1. Admin Login", resp.status_code == 200):
        tests_passed += 1
        token_admin = resp.json()['access']
        client_admin = APIClient()
        client_admin.credentials(HTTP_AUTHORIZATION='Bearer ' + token_admin)
    else:
        tests_failed += 1
        print(f"   Status: {resp.status_code}, Response: {resp.json()}")
        return
    
    # 2. Admin Dashboard
    resp = client_admin.get('/api/admin/dashboard/')
    if log_test("2. Admin Dashboard KPI", resp.status_code == 200):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 2 : GESTION DES CITOYENS
    # ═══════════════════════════════════════════════════════════════════════════
    log_section("PHASE 2 : CITOYENS (10 tests)")
    
    citoyens_data = []
    for i in range(5):
        email = f'citoyen{i}@test.mg'
        
        # 3-7. Inscription citoyens
        resp = client.post('/api/auth/register/citoyen/', {
            'email': email,
            'nom': f'Citoyen Fictif {i}',
            'password': 'Password123!',
            'password2': 'Password123!',
            'adresse': f'Rue {i}, Antananarivo'
        })
        if log_test(f"3.{i+1}. Inscription Citoyen {i}", resp.status_code == 201):
            tests_passed += 1
            citoyen_data = resp.json()
            citoyens_data.append({
                'user_id': citoyen_data['user']['id'],
                'email': email,
                'token': citoyen_data['access'],
                'nom': f'Citoyen {i}'
            })
        else:
            tests_failed += 1
    
    # 8. Valider tous les citoyens
    resp = client_admin.get('/api/admin/citoyens/')
    if log_test("8. Admin Liste Citoyens", resp.status_code == 200):
        tests_passed += 1
        for c in resp.json()['results']:
            client_admin.post(f'/api/admin/citoyens/{c["id"]}/valider/', {'action': 'accepter'})
    else:
        tests_failed += 1
    
    # 9. Get Profile Citoyen
    if citoyens_data:
        client_citoyen = APIClient()
        client_citoyen.credentials(HTTP_AUTHORIZATION='Bearer ' + citoyens_data[0]['token'])
        resp = client_citoyen.get('/api/auth/me/')
        if log_test("9. Citoyen Me Profile", resp.status_code == 200):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 3 : GESTION DES CAMIONEURS
    # ═══════════════════════════════════════════════════════════════════════════
    log_section("PHASE 3 : CAMIONEURS (10 tests)")
    
    camioneurs_data = []
    for i in range(5):
        email = f'camioneur{i}@test.mg'
        
        # 10-14. Inscription camioneurs
        resp = client.post('/api/auth/register/camioneur/', {
            'email': email,
            'nom': f'Camioneur Fictif {i}',
            'password': 'Password123!',
            'password2': 'Password123!',
            'numero_permis': f'PERMIS-{1000+i}'
        })
        if log_test(f"10.{i+1}. Inscription Camioneur {i}", resp.status_code == 201):
            tests_passed += 1
            cam_data = resp.json()
            camioneurs_data.append({
                'user_id': cam_data['user']['id'],
                'email': email,
                'token': cam_data['access'],
                'nom': f'Camioneur {i}'
            })
        else:
            tests_failed += 1
    
    # 15. Valider tous les camioneurs
    resp = client_admin.get('/api/admin/camioneurs/')
    if log_test("15. Admin Liste Camioneurs", resp.status_code == 200):
        tests_passed += 1
        for c in resp.json()['results']:
            client_admin.post(f'/api/admin/camioneurs/{c["id"]}/valider/', {'action': 'accepter'})
    else:
        tests_failed += 1
    
    # 16. Camioneur change mot de passe
    if camioneurs_data:
        client_camioneur = APIClient()
        client_camioneur.credentials(HTTP_AUTHORIZATION='Bearer ' + camioneurs_data[0]['token'])
        resp = client_camioneur.post('/api/auth/change-password/', {
            'ancien_mot_de_passe': 'Password123!',
            'nouveau_mot_de_passe': 'NewPass123!',
            'confirmation': 'NewPass123!'
        })
        if log_test("16. Camioneur Change Password", resp.status_code == 200):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 4 : GESTION DES ASSOCIATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    log_section("PHASE 4 : ASSOCIATIONS (8 tests)")
    
    assos_data = []
    for i in range(2):
        # 17-18. Créer associations
        resp = client_admin.post('/api/admin/associations/', {
            'nom': f'Association Eco {i}',
            'ville': 'Antananarivo',
            'description': f'Descriptif asso {i}',
            'email': f'asso{i}@test.mg',
            'password': 'AssoPass123!'
        })
        if log_test(f"17.{i+1}. Admin Crée Association {i}", resp.status_code == 201):
            tests_passed += 1
            asso_data = resp.json()
            assos_data.append({
                'id': asso_data['id'],
                'email': f'asso{i}@test.mg',
                'nom': f'Association {i}'
            })
        else:
            tests_failed += 1
    
    # 19. Liste des associations (admin)
    resp = client_admin.get('/api/admin/associations/')
    if log_test("19. Admin Liste Associations", resp.status_code == 200):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 20. Login Association
    if assos_data:
        resp = client.post('/api/auth/login/', {'email': assos_data[0]['email'], 'password': 'AssoPass123!'})
        if log_test("20. Association Login", resp.status_code == 200):
            tests_passed += 1
            token_asso = resp.json()['access']
            client_asso = APIClient()
            client_asso.credentials(HTTP_AUTHORIZATION='Bearer ' + token_asso)
        else:
            tests_failed += 1
    
    # 21. Liste associations (citoyen)
    if citoyens_data:
        client_citoyen.credentials(HTTP_AUTHORIZATION='Bearer ' + citoyens_data[0]['token'])
        resp = client_citoyen.get('/api/associations/')
        if log_test("21. Citoyen Liste Associations", resp.status_code == 200):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 5 : ADHÉSIONS & MEMBRES
    # ═══════════════════════════════════════════════════════════════════════════
    log_section("PHASE 5 : ADHÉSIONS (6 tests)")
    
    # 22. Citoyen demande adhésion
    if citoyens_data and assos_data:
        resp = client_citoyen.post(f'/api/associations/{assos_data[0]["id"]}/rejoindre/')
        if log_test("22. Citoyen Demande Adhésion", resp.status_code == 201):
            tests_passed += 1
        else:
            tests_failed += 1
        
        # 23. Association liste adhésions en attente
        resp = client_asso.get('/api/associations/adhesions/')
        if log_test("23. Association Liste Adhésions", resp.status_code == 200):
            tests_passed += 1
            adhesions = resp.json()['results']
        else:
            tests_failed += 1
        
        # 24. Association accepte adhésion
        if adhesions:
            resp = client_asso.post(f'/api/associations/adhesions/{adhesions[0]["id"]}/action/', {'action': 'accepter'})
            if log_test("24. Association Accepte Adhésion", resp.status_code == 200):
                tests_passed += 1
            else:
                tests_failed += 1
        
        # 25. Association liste membres
        resp = client_asso.get('/api/associations/membres/')
        if log_test("25. Association Liste Membres", resp.status_code == 200):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 6 : ÉVÉNEMENTS & ANNONCES
    # ═══════════════════════════════════════════════════════════════════════════
    log_section("PHASE 6 : ÉVÉNEMENTS & ANNONCES (12 tests)")
    
    evenements_data = []
    
    # 26-27. Créer événements
    for i in range(2):
        date_ev = (timezone.now() + timedelta(days=2+i)).isoformat()
        resp = client_asso.post('/api/mobile/association/evenements/', {
            'titre': f'Événement Eco {i}',
            'description': f'Description événement {i}',
            'date_evenement': date_ev,
            'lieu': f'Lieu {i}, Antananarivo',
            'statut': 'a_venir'
        })
        if log_test(f"26.{i+1}. Créer Événement {i}", resp.status_code == 201):
            tests_passed += 1
            evenements_data.append(resp.json()['id'])
        else:
            tests_failed += 1
    
    # 28. Liste événements (association)
    resp = client_asso.get('/api/mobile/association/evenements/')
    if log_test("28. Association Liste Événements", resp.status_code == 200):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 29-30. Créer annonces
    for i in range(2):
        resp = client_asso.post('/api/mobile/association/annonces/', {
            'titre': f'Annonce {i}',
            'contenu': f'Contenu de l\'annonce {i}',
            'type': 'annonce'
        })
        if log_test(f"29.{i+1}. Créer Annonce {i}", resp.status_code == 201):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # 31. Liste annonces (mobile)
    resp = client_citoyen.get('/api/mobile/annonces/')
    if log_test("31. Citoyen Liste Annonces", resp.status_code == 200):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 32. Citoyen s'inscrit événement
    if evenements_data:
        resp = client_citoyen.post(f'/api/mobile/evenements/{evenements_data[0]}/participer/')
        if log_test("32. Citoyen S'inscrit Événement", resp.status_code == 201):
            tests_passed += 1
        else:
            tests_failed += 1
        
        # 33. Association liste participants
        resp = client_asso.get(f'/api/mobile/association/evenements/{evenements_data[0]}/participants/')
        if log_test("33. Association Liste Participants", resp.status_code == 200):
            tests_passed += 1
            participants = resp.json()['results']
        else:
            tests_failed += 1
        
        # 34. Association confirme présence
        if participants:
            resp = client_asso.post(f'/api/mobile/association/evenements/{evenements_data[0]}/participants/{participants[0]["id"]}/confirmer/')
            if log_test("34. Association Confirme Présence", resp.status_code == 200):
                tests_passed += 1
            else:
                tests_failed += 1
    
    # 35. Citoyen liste ses participations
    resp = client_citoyen.get('/api/mobile/evenements/mes-participations/')
    if log_test("35. Citoyen Mes Participations", resp.status_code == 200):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 7 : SIGNALEMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    log_section("PHASE 7 : SIGNALEMENTS & COLLECTES (10 tests)")
    
    signalements_data = []
    
    # 36-40. Créer signalements
    for i in range(5):
        valid_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0bIDAT\x08\x99c\xf8\x0f\x04\x00\t\xfb\x03\xfd\xe3U\xf2\x9c\x00\x00\x00\x00IEND\xaeB`\x82'
        with tempfile.NamedTemporaryFile(suffix='.png') as f:
            f.write(valid_png)
            f.flush()
            with open(f.name, 'rb') as photo:
                resp = client_citoyen.post('/api/mobile/signalements/', {
                    'latitude': str(-18.8792 + i*0.01),
                    'longitude': str(47.5079 + i*0.01),
                    'description': f'Déchet {i}',
                    'type_dechet': ['plastique', 'metal', 'verre', 'organique', 'mixte'][i],
                    'photo': photo
                }, format='multipart')
        if log_test(f"36.{i+1}. Citoyen Crée Signalement {i}", resp.status_code == 201):
            tests_passed += 1
            signalements_data.append(resp.json()['id'])
        else:
            tests_failed += 1
    
    # 41. Citoyen liste ses signalements
    resp = client_citoyen.get('/api/mobile/signalements/')
    if log_test("41. Citoyen Liste Signalements", resp.status_code == 200):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 42. Camioneur met à jour position
    if camioneurs_data:
        client_camioneur.credentials(HTTP_AUTHORIZATION='Bearer ' + camioneurs_data[0]['token'])
        resp = client_camioneur.put('/api/mobile/camioneur/position/', {
            'latitude': '-18.8792',
            'longitude': '47.5079',
            'disponible': True
        })
        if log_test("42. Camioneur Met à Jour Position", resp.status_code == 200):
            tests_passed += 1
        else:
            tests_failed += 1
        
        # 43. Camioneur voit signalements proches
        resp = client_camioneur.get('/api/mobile/camioneur/signalements/?lat=-18.8792&lng=47.5079&rayon=50')
        if log_test("43. Camioneur Voit Signalements Proches", resp.status_code == 200):
            tests_passed += 1
            proches = resp.json()['signalements']
        else:
            tests_failed += 1
        
        # 44. Camioneur accepte signalement
        if proches and signalements_data:
            resp = client_camioneur.post(f'/api/mobile/camioneur/signalements/{signalements_data[0]}/accepter/')
            if log_test("44. Camioneur Accepte Signalement", resp.status_code == 200):
                tests_passed += 1
            else:
                tests_failed += 1
        
        # 45. Camioneur valide collecte
        if signalements_data:
            resp = client_camioneur.post(f'/api/mobile/camioneur/signalements/{signalements_data[0]}/valider/')
            if log_test("45. Camioneur Valide Collecte", resp.status_code == 200):
                tests_passed += 1
            else:
                tests_failed += 1
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PHASE 8 : AUTRES ENDPOINTS
    # ═══════════════════════════════════════════════════════════════════════════
    log_section("PHASE 8 : ENDPOINTS ADDITIONNELS (10+ tests)")
    
    # 46. Admin Carte Positions
    resp = client_admin.get('/api/mobile/admin-camioneurs/carte/')
    if log_test("46. Admin Carte Positions Camioneurs", resp.status_code == 200):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 47. Admin Tous Signalements
    resp = client_admin.get('/api/mobile/admin-signalements/')
    if log_test("47. Admin Tous Signalements", resp.status_code == 200):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # 48. Historique positions camioneur
    if camioneurs_data:
        resp = client_camioneur.get('/api/mobile/camioneur/position/history/')
        if log_test("48. Historique Positions Camioneur", resp.status_code == 200):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # 49. Camioneur profil
    if camioneurs_data:
        resp = client_camioneur.get('/api/mobile/camioneur/profil/')
        if log_test("49. Camioneur Profil", resp.status_code == 200):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # 50. Camioneur mes collectes
    if camioneurs_data:
        resp = client_camioneur.get('/api/mobile/camioneur/collectes/')
        if log_test("50. Camioneur Mes Collectes", resp.status_code == 200):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RÉSUMÉ FINAL
    # ═══════════════════════════════════════════════════════════════════════════
    log_section("RÉSUMÉ FINAL")
    
    total = tests_passed + tests_failed
    percentage = (tests_passed / total * 100) if total > 0 else 0
    
    print(f"{GREEN}Tests réussis : {tests_passed}{RESET}")
    print(f"{RED}Tests échoués : {tests_failed}{RESET}")
    print(f"Taux de réussite : {percentage:.1f}%")
    
    if tests_failed == 0:
        print(f"\n{GREEN}{'🎉 TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS ! 🎉':^60}{RESET}")
    else:
        print(f"\n{YELLOW}{'⚠️  CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFIEZ LES ERREURS CI-DESSUS':^60}{RESET}")

if __name__ == '__main__':
    run_comprehensive_tests()
