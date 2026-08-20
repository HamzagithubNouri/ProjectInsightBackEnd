import secrets
import requests

from app.config import settings

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com"

# Associe un "state" temporaire (anti-CSRF) a l'id de l'utilisateur qui a
# initie la connexion. En memoire uniquement : suffisant pour un seul
# serveur de dev, se vide si le serveur redemarre (a remplacer par Redis
# ou une table DB si un jour deploye en production multi-instances).
_pending_states: dict[str, int] = {}


def generate_state_for_user(user_id: int) -> str:
    state = secrets.token_urlsafe(24)
    _pending_states[state] = user_id
    return state


def pop_user_id_for_state(state: str) -> int | None:
    """Recupere l'utilisateur associe a ce state, puis l'oublie (usage unique)."""
    return _pending_states.pop(state, None)


def build_authorize_url(state: str) -> str:
    params = (
        f"client_id={settings.github_client_id}"
        f"&redirect_uri={settings.github_redirect_uri}"
        f"&scope=repo"
        f"&state={state}"
        f"&prompt=select_account"
    )
    return f"{GITHUB_AUTHORIZE_URL}?{params}"


def exchange_code_for_token(code: str) -> str:
    """Echange le code temporaire recu de GitHub contre un vrai access_token.
    Cet appel se fait serveur-a-serveur : c'est le SEUL endroit ou le
    client_secret est utilise, jamais expose au navigateur."""
    response = requests.post(
        GITHUB_TOKEN_URL,
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "code": code,
            "redirect_uri": settings.github_redirect_uri,
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    if "access_token" not in data:
        raise ValueError(f"Reponse GitHub inattendue : {data}")
    return data["access_token"]


def get_github_username(access_token: str) -> str:
    response = requests.get(
        f"{GITHUB_API_URL}/user",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["login"]
