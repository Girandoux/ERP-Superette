# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : config/auth.py
# AUTEUR : Girandoux Fandio
# DESCRIPTION : Authentification simple pour la Version 1 avec
# Streamlit session_state et identifiants depuis le fichier .env.
# ============================================================

import hmac
from datetime import datetime, timedelta

import streamlit as st

from config.settings import (
    ADMIN_PASSWORD,
    ADMIN_USERNAME,
    APP_NAME,
    SESSION_TIMEOUT_MINUTES,
)


# ============================================================
# 1. INITIALISATION DE LA SESSION
# ============================================================

def init_auth_session():
    """Initialise les variables de session d'authentification."""
    default_values = {
        "authenticated": False,
        "username": None,
        "login_error": None,
        "login_time": None,
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_auth_session():
    """Reinitialise les informations de connexion."""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.login_error = None
    st.session_state.login_time = None


# ============================================================
# 2. VERIFICATION DES IDENTIFIANTS
# ============================================================

def check_credentials(username, password):
    """Verifie le nom d'utilisateur et le mot de passe."""
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        return False

    username_is_valid = hmac.compare_digest(
        username,
        ADMIN_USERNAME,
    )

    password_is_valid = hmac.compare_digest(
        password,
        ADMIN_PASSWORD,
    )

    return (
        username_is_valid
        and password_is_valid
    )


def session_has_expired():
    """Verifie si la duree maximale de la session est depassee."""
    login_time = st.session_state.get(
        "login_time"
    )

    if not login_time:
        return False

    expiration_time = login_time + timedelta(
        minutes=SESSION_TIMEOUT_MINUTES
    )

    return datetime.now() >= expiration_time


def is_authenticated():
    """Retourne True si l'utilisateur est connecte."""
    init_auth_session()

    if (
        st.session_state.authenticated
        and session_has_expired()
    ):
        reset_auth_session()
        st.session_state.login_error = (
            "Votre session a expire. "
            "Veuillez vous reconnecter."
        )

        return False

    return bool(
        st.session_state.authenticated
    )


def get_current_user():
    """Retourne l'utilisateur connecte."""
    if not is_authenticated():
        return None

    return st.session_state.username


# ============================================================
# 3. CONNEXION ET DECONNEXION
# ============================================================

def login(username, password):
    """Connecte l'utilisateur si les identifiants sont corrects."""
    init_auth_session()

    if check_credentials(
        username,
        password,
    ):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.login_error = None
        st.session_state.login_time = datetime.now()

        return True

    reset_auth_session()

    if not ADMIN_PASSWORD:
        st.session_state.login_error = (
            "Le mot de passe administrateur n'est pas configure "
            "dans le fichier .env."
        )

    else:
        st.session_state.login_error = (
            "Nom d'utilisateur ou mot de passe incorrect."
        )

    return False


def logout():
    """Deconnecte l'utilisateur."""
    reset_auth_session()
    st.rerun()


# ============================================================
# 4. INTERFACE DE CONNEXION STREAMLIT
# ============================================================

def show_login_form():
    """Affiche le formulaire de connexion."""
    init_auth_session()

    st.title(
        APP_NAME
    )

    st.subheader(
        "Connexion"
    )

    with st.form(
        "login_form"
    ):
        username = st.text_input(
            "Nom d'utilisateur"
        )

        password = st.text_input(
            "Mot de passe",
            type="password",
        )

        submitted = st.form_submit_button(
            "Se connecter"
        )

    if submitted:
        username = username.strip()

        if login(
            username,
            password,
        ):
            st.rerun()

        else:
            st.error(
                st.session_state.login_error
            )

    elif st.session_state.login_error:
        st.error(
            st.session_state.login_error
        )


def show_user_box():
    """Affiche l'utilisateur connecte dans la barre laterale."""
    current_user = get_current_user()

    if not current_user:
        return

    with st.sidebar:
        st.caption(
            f"Connecte : {current_user}"
        )

        if st.button(
            "Deconnexion",
            key="logout_button",
        ):
            logout()


# ============================================================
# 5. PROTECTION DES PAGES
# ============================================================

def require_login():
    """Bloque l'acces a une page si l'utilisateur n'est pas connecte."""
    if not is_authenticated():
        show_login_form()
        st.stop()

    show_user_box()


def optional_login():
    """Affiche l'utilisateur si connecte, sans bloquer la page."""
    if is_authenticated():
        show_user_box()
