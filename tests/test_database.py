# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : tests/test_database.py
# ROLE : Tests de base pour la configuration PostgreSQL
# AUTEUR : Girandoux Fandio
# ============================================================

from config import database

# ============================================================
# 1. INFORMATIONS DE CONNEXION SECURISEES
# ============================================================

def test_database_information_cache_le_mot_de_passe():
    """Verifie que l'URL affichee ne montre pas le mot de passe."""
    info = database.database_information()
    assert "database" in info
    assert "user" in info
    assert "***" in info["url_hidden"]

# ============================================================
# 2. TESTS DE CONNEXION SANS POSTGRESQL REEL
# ============================================================

# Les objets factices isolent les tests de toute base PostgreSQL reelle.
def test_test_connection_success(monkeypatch):
    """Simule une connexion SQLAlchemy reussie."""

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, *args, **kwargs):
            return True

    class FakeEngine:
        def connect(self):
            return FakeConnection()

    monkeypatch.setattr(database, "engine", FakeEngine())

    assert database.test_connection() is True

def test_fetch_one_retourne_dict(monkeypatch):
    """Verifie que fetch_one convertit une ligne SQLAlchemy en dictionnaire."""

    class FakeResult:
        def mappings(self):
            return self

        def first(self):
            return {"total": 5}

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def execute(self, *args, **kwargs):
            return FakeResult()

    class FakeEngine:
        def connect(self):
            return FakeConnection()

    monkeypatch.setattr(database, "engine", FakeEngine())

    assert database.fetch_one("SELECT 1") == {"total": 5}
