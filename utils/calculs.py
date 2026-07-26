# ============================================================
# PROJET : GESTION DE SUPERETTE
# FICHIER : utils/calculs.py
# ROLE : Calculs metier achats, ventes, stock et finance
# AUTEUR : Girandoux Fandio
# ============================================================

from __future__ import annotations
from typing import Any

from utils.helpers import safe_divide, to_float, to_int

# ============================================================
# 1. CALCULS ACHATS
# ============================================================

def calcul_quantite_achat(qte_cartons:Any,qte_par_carton:Any)->float:
    """Calcule la quantite totale achetee en pieces."""
    return to_float(qte_cartons)*to_float(qte_par_carton)

def calcul_pu_achat_piece(pu_achat_carton:Any,qte_par_carton:Any)->float:
    """Calcule le prix d'achat unitaire par piece."""
    return round(safe_divide(pu_achat_carton,qte_par_carton),2)

def calcul_total_achat(qte_cartons:Any,pu_achat_carton:Any)->float:
    """Calcule le total d'une ligne d'achat."""
    return round(to_float(qte_cartons)*to_float(pu_achat_carton),2)

def calcul_ligne_achat(qte_cartons:Any,qte_par_carton:Any,pu_achat_carton:Any)->dict[str,float]:
    """Calcule toutes les valeurs d'une ligne d'achat."""
    quantite=calcul_quantite_achat(qte_cartons,qte_par_carton)
    pu_piece=calcul_pu_achat_piece(pu_achat_carton,qte_par_carton)
    total=calcul_total_achat(qte_cartons,pu_achat_carton)
    return {"quantite_achat":quantite,"pu_achat_piece":pu_piece,"total_achat":total}

def calcul_total_facture(lignes:list[dict[str,Any]],frais_enlevement:Any=0)->float:
    """Calcule le total facture achat avec frais."""
    total_lignes=sum(to_float(ligne.get("total_achat",0)) for ligne in lignes)
    return round(total_lignes+to_float(frais_enlevement),2)

# ============================================================
# 2. CALCULS VENTES
# ============================================================

def calcul_montant_ligne(qte_vente:Any,pu_vente:Any)->float:
    """Calcule le montant d'une ligne de vente."""
    return round(to_float(qte_vente)*to_float(pu_vente),2)

def calcul_cout_total(qte_vente:Any,cout_unitaire:Any)->float:
    """Calcule le cout total d'une ligne de vente."""
    return round(to_float(qte_vente)*to_float(cout_unitaire),2)

def calcul_marge(montant_ligne:Any,cout_total:Any)->float:
    """Calcule la marge brute."""
    return round(to_float(montant_ligne)-to_float(cout_total),2)

def calcul_taux_marge(marge:Any,montant_ligne:Any)->float:
    """Calcule le taux de marge sur chiffre d'affaires."""
    return round(safe_divide(marge,montant_ligne)*100,2)

def calcul_ligne_vente(qte_vente:Any,pu_vente:Any,cout_unitaire:Any=0)->dict[str,float]:
    """Calcule toutes les valeurs d'une ligne de vente."""
    montant=calcul_montant_ligne(qte_vente,pu_vente)
    cout=calcul_cout_total(qte_vente,cout_unitaire)
    marge=calcul_marge(montant,cout)
    return {"montant_ligne":montant,"cout_total":cout,"marge":marge,"taux_marge":calcul_taux_marge(marge,montant)}

def calcul_total_vente(lignes:list[dict[str,Any]])->float:
    """Calcule le total d'une vente."""
    return round(sum(to_float(ligne.get("montant_ligne",0)) for ligne in lignes),2)

# ============================================================
# 3. CALCULS STOCK
# ============================================================

def calcul_stock_final(stock_initial:Any,entrees:Any=0,sorties:Any=0,pertes:Any=0,ajustements:Any=0)->float:
    """Calcule le stock final."""
    return round(to_float(stock_initial)+to_float(entrees)-to_float(sorties)-to_float(pertes)+to_float(ajustements),2)

def calcul_ecart_stock(stock_theorique:Any,stock_physique:Any)->float:
    """Calcule l'ecart d'inventaire."""
    return round(to_float(stock_physique)-to_float(stock_theorique),2)

def calcul_valeur_ecart(ecart:Any,cout_unitaire:Any)->float:
    """Calcule la valeur financiere d'un ecart."""
    return round(to_float(ecart)*to_float(cout_unitaire),2)

def calcul_valeur_stock(stock_actuel:Any,cout_unitaire:Any)->float:
    """Calcule la valeur d'un stock."""
    return round(to_float(stock_actuel)*to_float(cout_unitaire),2)

def calcul_taux_rotation(quantite_vendue:Any,stock_moyen:Any)->float:
    """Calcule le taux de rotation stock."""
    return round(safe_divide(quantite_vendue,stock_moyen),2)

def get_statut_stock(stock_actuel:Any,stock_min:Any)->str:
    """Retourne le statut du stock."""
    stock=to_float(stock_actuel)
    minimum=to_float(stock_min)
    if stock<=0:
        return "RUPTURE"
    if stock<=minimum:
        return "ALERTE"
    return "NORMAL"

def calcul_qte_cartons_possible(stock_actuel:Any,qte_par_carton:Any)->int:
    """Calcule le nombre de cartons complets disponibles."""
    return to_int(safe_divide(stock_actuel,qte_par_carton))

# ============================================================
# 4. CALCULS DEPENSES, PERTES ET TRESORERIE
# ============================================================

def calcul_valeur_perte(qte_perte:Any,valeur_unitaire:Any)->float:
    """Calcule la valeur totale d'une perte."""
    return round(to_float(qte_perte)*to_float(valeur_unitaire),2)

def calcul_solde_tresorerie(entrees:Any,sorties:Any,solde_initial:Any=0)->float:
    """Calcule le solde de tresorerie."""
    return round(to_float(solde_initial)+to_float(entrees)-to_float(sorties),2)

def calcul_resultat_net(chiffre_affaires:Any,total_achats:Any,total_depenses:Any,total_pertes:Any=0)->float:
    """Calcule le resultat net simplifie."""
    return round(to_float(chiffre_affaires)-to_float(total_achats)-to_float(total_depenses)-to_float(total_pertes),2)

def calcul_panier_moyen(chiffre_affaires:Any,nombre_ventes:Any)->float:
    """Calcule le panier moyen."""
    return round(safe_divide(chiffre_affaires,nombre_ventes),2)

def calcul_pourcentage(part:Any,total:Any)->float:
    """Calcule la part en pourcentage."""
    return round(safe_divide(part,total)*100,2)

# ============================================================
# 5. CALCULS LISTES
# ============================================================

def somme_colonne(lignes:list[dict[str,Any]],colonne:str)->float:
    """Calcule la somme d'une colonne dans une liste de dictionnaires."""
    return round(sum(to_float(ligne.get(colonne,0)) for ligne in lignes),2)

def moyenne_colonne(lignes:list[dict[str,Any]],colonne:str)->float:
    """Calcule la moyenne d'une colonne dans une liste de dictionnaires."""
    if not lignes:
        return 0
    return round(somme_colonne(lignes,colonne)/len(lignes),2)

def total_par_cle(lignes:list[dict[str,Any]],cle:str,colonne:str)->dict[Any,float]:
    """Regroupe une somme par cle."""
    result={}
    for ligne in lignes:
        key=ligne.get(cle)
        result[key]=round(result.get(key,0)+to_float(ligne.get(colonne,0)),2)
    return result


__all__ = [
    "calcul_quantite_achat",
    "calcul_pu_achat_piece",
    "calcul_total_achat",
    "calcul_ligne_achat",
    "calcul_total_facture",
    "calcul_montant_ligne",
    "calcul_cout_total",
    "calcul_marge",
    "calcul_taux_marge",
    "calcul_ligne_vente",
    "calcul_total_vente",
    "calcul_stock_final",
    "calcul_ecart_stock",
    "calcul_valeur_ecart",
    "calcul_valeur_stock",
    "calcul_taux_rotation",
    "get_statut_stock",
    "calcul_qte_cartons_possible",
    "calcul_valeur_perte",
    "calcul_solde_tresorerie",
    "calcul_resultat_net",
    "calcul_panier_moyen",
    "calcul_pourcentage",
    "somme_colonne",
    "moyenne_colonne",
    "total_par_cle",
]
