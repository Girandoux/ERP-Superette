# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/__init__.py
# ROLE : Initialisation du package utils
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations

# ============================================================
# 1. INFORMATIONS DU PACKAGE
# ============================================================

__version__="1.0.0"
__author__="Girandoux Fandio"
__project__="Gestion de Superette"

# ============================================================
# 2. MODULES PUBLICS DU PACKAGE
# ============================================================

# Liste des modules exposes lors d'un import explicite du package utils.
__all__=[
    "helpers",
    "validation",
    "calculs",
    "produits",
    "categories",
    "stock",
    "achats",
    "ventes",
    "inventaire",
    "depenses",
    "tresorerie",
    "pertes",
    "imports",
    "exports",
    "dashboard",
    "charts"
]
