import requests

def get_auth_header(username, password, base_url="http://127.0.0.1:8000"):
    """
    1. Se connecte à l'API via /login
    2. Récupère le token
    3. Retourne la chaîne complète : "Bearer <token>"
    """
    # Attention : OAuth2 demande du form-data (paramètre 'data'), pas du JSON.
    response = requests.post(
        f"{base_url}/login", 
        data={"username": username, "password": password}
    )

    if response.status_code == 200:
        raw_token = response.json().get("access_token")
        
        # C'est ICI qu'on crée le format "Bearer Az..."
        formatted_token = f"Bearer {raw_token}"
        
        print(f"✅ Authentification réussie pour {username}")
        return formatted_token
    else:
        print(f"❌ Erreur Login : {response.text}")
        return None