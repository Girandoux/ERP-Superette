-- ============================================================
-- PROJET : GESTION DE SUPERETTE
-- FICHIER : 03_SQL_Analytics.sql
-- BASE DE DONNEES : PostgreSQL
-- AUTEUR : Girandoux Fandio
-- DESCRIPTION : Analyses SQL pour Streamlit et Power BI.
-- ============================================================
--
-- DOMAINES ANALYSES :
-- Produits → Achats → Ventes → Stock → Dépenses
-- → Pertes → Inventaire → Trésorerie → KPI
--
-- Chaque requête reste indépendante et conserve son résultat attendu.
-- ============================================================

-- ============================================================

SELECT *
FROM Dim_Produits
ORDER BY nom_produit;

-- ============================================================
-- 02. NOMBRE TOTAL DE PRODUITS
-- ============================================================

SELECT COUNT(*) AS nombre_produits
FROM Dim_Produits;

-- ============================================================
-- 03. NOMBRE DE PRODUITS PAR CATEGORIE
-- ============================================================

SELECT
    c.nom_categorie,
    COUNT(*) AS nombre_produits
FROM Dim_Produits p
INNER JOIN Dim_Categories c
ON p.categorie_id = c.categorie_id
GROUP BY c.nom_categorie
ORDER BY nombre_produits DESC;

-- ============================================================
-- 04. STOCK ACHETE PAR PRODUIT
-- ============================================================

SELECT

    p.code_produit,
    p.nom_produit,

    SUM(a.quantite_achat) AS stock_achete

FROM Dim_Lignes_Achat a

INNER JOIN Dim_Produits p
ON a.produit_id = p.produit_id

GROUP BY

    p.code_produit,
    p.nom_produit

ORDER BY stock_achete DESC;

-- ============================================================
-- 05. QUANTITE VENDUE PAR PRODUIT
-- ============================================================

SELECT

    p.code_produit,
    p.nom_produit,

    SUM(v.qte_vente) AS quantite_vendue

FROM Dim_Lignes_Vente v

INNER JOIN Dim_Produits p
ON v.produit_id = p.produit_id

GROUP BY

    p.code_produit,
    p.nom_produit

ORDER BY quantite_vendue DESC;

-- ============================================================
-- 06. QUANTITE PERDUE PAR PRODUIT
-- ============================================================

SELECT

    p.code_produit,
    p.nom_produit,

    SUM(pe.qte_perte) AS quantite_perdue

FROM Dim_Pertes pe

INNER JOIN Dim_Produits p
ON pe.produit_id = p.produit_id

GROUP BY

    p.code_produit,
    p.nom_produit

ORDER BY quantite_perdue DESC;

-- ============================================================
-- 07. STOCK REEL PAR PRODUIT
--
-- Stock =
-- Achats
-- - Ventes
-- - Pertes
-- ============================================================

SELECT

    p.produit_id,

    p.code_produit,

    p.nom_produit,

    COALESCE(a.stock_achete,0)
    -
    COALESCE(v.stock_vendu,0)
    -
    COALESCE(pe.stock_perdu,0)

    AS stock_reel

FROM Dim_Produits p

LEFT JOIN
(

SELECT

produit_id,

SUM(quantite_achat) AS stock_achete

FROM Dim_Lignes_Achat

GROUP BY produit_id

) a

ON p.produit_id=a.produit_id

LEFT JOIN
(

SELECT

produit_id,

SUM(qte_vente) AS stock_vendu

FROM Dim_Lignes_Vente

GROUP BY produit_id

) v

ON p.produit_id=v.produit_id

LEFT JOIN
(

SELECT

produit_id,

SUM(qte_perte) AS stock_perdu

FROM Dim_Pertes

GROUP BY produit_id

) pe

ON p.produit_id=pe.produit_id

ORDER BY stock_reel DESC;

-- ============================================================
-- 08. PRODUITS EN RUPTURE DE STOCK
-- ============================================================

SELECT *

FROM
(

SELECT

    p.produit_id,

    p.code_produit,

    p.nom_produit,

    COALESCE(a.stock_achete,0)
    -
    COALESCE(v.stock_vendu,0)
    -
    COALESCE(pe.stock_perdu,0)

    AS stock_reel

FROM Dim_Produits p

LEFT JOIN
(
SELECT produit_id,
SUM(quantite_achat) stock_achete
FROM Dim_Lignes_Achat
GROUP BY produit_id
)a

ON p.produit_id=a.produit_id

LEFT JOIN
(
SELECT produit_id,
SUM(qte_vente) stock_vendu
FROM Dim_Lignes_Vente
GROUP BY produit_id
)v

ON p.produit_id=v.produit_id

LEFT JOIN
(
SELECT produit_id,
SUM(qte_perte) stock_perdu
FROM Dim_Pertes
GROUP BY produit_id
)pe

ON p.produit_id=pe.produit_id

)x

WHERE stock_reel<=0;

-- ============================================================
-- 09. PRODUITS SOUS LE STOCK MINIMUM
-- ============================================================

SELECT *

FROM
(

SELECT

p.code_produit,

p.nom_produit,

p.stock_min,

COALESCE(a.stock_achete,0)
-
COALESCE(v.stock_vendu,0)
-
COALESCE(pe.stock_perdu,0)

AS stock_reel

FROM Dim_Produits p

LEFT JOIN
(
SELECT produit_id,
SUM(quantite_achat) stock_achete
FROM Dim_Lignes_Achat
GROUP BY produit_id
)a
ON p.produit_id=a.produit_id

LEFT JOIN
(
SELECT produit_id,
SUM(qte_vente) stock_vendu
FROM Dim_Lignes_Vente
GROUP BY produit_id
)v
ON p.produit_id=v.produit_id

LEFT JOIN
(
SELECT produit_id,
SUM(qte_perte) stock_perdu
FROM Dim_Pertes
GROUP BY produit_id
)pe
ON p.produit_id=pe.produit_id

)x

WHERE stock_reel<stock_min

ORDER BY stock_reel;

-- ============================================================
-- 10. VALEUR DU STOCK ACTUEL
--
-- Stock réel × Dernier coût unitaire
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

s.stock_reel,

c.pu_achat_piece,

ROUND(

s.stock_reel*c.pu_achat_piece

,2)

AS valeur_stock

FROM

(

SELECT

produit_id,

COALESCE(SUM(quantite_achat),0)

-
COALESCE
(
(
SELECT SUM(qte_vente)

FROM Dim_Lignes_Vente v

WHERE v.produit_id=a.produit_id
),0)

-
COALESCE
(
(
SELECT SUM(qte_perte)

FROM Dim_Pertes pe

WHERE pe.produit_id=a.produit_id
),0)

AS stock_reel

FROM Dim_Lignes_Achat a

GROUP BY produit_id

)s

INNER JOIN Dim_Produits p

ON s.produit_id=p.produit_id

INNER JOIN

(

SELECT DISTINCT ON (produit_id)

produit_id,

pu_achat_piece

FROM Dim_Lignes_Achat

ORDER BY produit_id,
ligne_achat_id DESC

)c

ON s.produit_id=c.produit_id

ORDER BY valeur_stock DESC;

-- ============================================================
-- 11. MONTANT TOTAL DES ACHATS
-- ============================================================

SELECT

SUM(total_facture) AS total_achats

FROM Fact_Achats;

-- ============================================================
-- 12. ACHATS PAR MOIS
-- ============================================================

SELECT

d.annee,

d.mois,

SUM(a.total_facture) AS achats

FROM Fact_Achats a

INNER JOIN Dim_Date d

ON a.date_id=d.date_id

GROUP BY

d.annee,
d.mois

ORDER BY

d.annee,
d.mois;

-- ============================================================
-- 13. ACHATS PAR FOURNISSEUR
-- ============================================================

SELECT

ac.nom_acheteur,

SUM(a.total_facture) AS montant

FROM Fact_Achats a

INNER JOIN Dim_Acheteurs ac

ON a.acheteur_id=ac.acheteur_id

GROUP BY ac.nom_acheteur

ORDER BY montant DESC;

-- ============================================================
-- 14. TOP 10 DES PRODUITS LES PLUS ACHETES
-- ============================================================

SELECT

p.nom_produit,

SUM(a.quantite_achat) AS quantite

FROM Dim_Lignes_Achat a

INNER JOIN Dim_Produits p

ON a.produit_id=p.produit_id

GROUP BY p.nom_produit

ORDER BY quantite DESC

LIMIT 10;

-- ============================================================
-- FIN DE LA PARTIE 1
-- ============================================================

-- ============================================================
-- PARTIE 2A : VENTES ET CHIFFRE D'AFFAIRES
-- ============================================================

-- ============================================================
-- 15. CHIFFRE D'AFFAIRES TOTAL
-- ============================================================

SELECT

SUM(total_vente) AS chiffre_affaires

FROM Fact_Ventes;

-- ============================================================
-- 16. CHIFFRE D'AFFAIRES PAR JOUR
-- ============================================================

SELECT

date_vente::DATE AS date,

SUM(total_vente) AS chiffre_affaires

FROM Fact_Ventes

GROUP BY date_vente::DATE

ORDER BY date;

-- ============================================================
-- 17. CHIFFRE D'AFFAIRES PAR MOIS
-- ============================================================

SELECT

d.annee,

d.mois,

SUM(v.total_vente) AS chiffre_affaires

FROM Fact_Ventes v

INNER JOIN Dim_Date d

ON v.date_id=d.date_id

GROUP BY

d.annee,
d.mois

ORDER BY

d.annee,
d.mois;

-- ============================================================
-- 18. CHIFFRE D'AFFAIRES PAR ANNEE
-- ============================================================

SELECT

d.annee,

SUM(v.total_vente) AS chiffre_affaires

FROM Fact_Ventes v

INNER JOIN Dim_Date d

ON v.date_id=d.date_id

GROUP BY d.annee

ORDER BY d.annee;

-- ============================================================
-- 19. CHIFFRE D'AFFAIRES PAR VENDEUR
-- ============================================================

SELECT

ve.nom_vendeur,

SUM(v.total_vente) AS chiffre_affaires

FROM Fact_Ventes v

INNER JOIN Dim_Vendeurs ve

ON v.vendeur_id=ve.vendeur_id

GROUP BY ve.nom_vendeur

ORDER BY chiffre_affaires DESC;

-- ============================================================
-- 20. CHIFFRE D'AFFAIRES PAR PRODUIT
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

SUM(lv.qte_vente) AS quantite_vendue,

SUM(lv.montant_ligne) AS chiffre_affaires

FROM Dim_Lignes_Vente lv

INNER JOIN Dim_Produits p

ON lv.produit_id=p.produit_id

GROUP BY

p.code_produit,
p.nom_produit

ORDER BY chiffre_affaires DESC;

-- ============================================================
-- 21. CHIFFRE D'AFFAIRES PAR CATEGORIE
-- ============================================================

SELECT

c.nom_categorie,

SUM(lv.montant_ligne) AS chiffre_affaires,

SUM(lv.qte_vente) AS quantite_vendue

FROM Dim_Lignes_Vente lv

INNER JOIN Dim_Produits p

ON lv.produit_id=p.produit_id

INNER JOIN Dim_Categories c

ON p.categorie_id=c.categorie_id

GROUP BY

c.nom_categorie

ORDER BY chiffre_affaires DESC;

-- ============================================================
-- 22. EVOLUTION DES VENTES PAR MOIS
-- ============================================================

SELECT

d.annee,

d.mois,

COUNT(DISTINCT v.vente_id) AS nombre_ventes,

SUM(v.total_vente) AS chiffre_affaires,

AVG(v.total_vente) AS ticket_moyen

FROM Fact_Ventes v

INNER JOIN Dim_Date d

ON v.date_id=d.date_id

GROUP BY

d.annee,
d.mois

ORDER BY

d.annee,
d.mois;

-- ============================================================
-- FIN DE LA PARTIE 2A
-- ============================================================
-- ============================================================
-- PARTIE 2B : BENEFICES, TOP PRODUITS, TOP VENDEURS
-- ============================================================

-- ============================================================
-- 23. BENEFICE TOTAL
-- ============================================================

SELECT

SUM(montant_ligne - cout_total) AS benefice_total

FROM Dim_Lignes_Vente;

-- ============================================================
-- 24. BENEFICE PAR JOUR
-- ============================================================

SELECT

v.date_vente::DATE AS date,

SUM(lv.montant_ligne - lv.cout_total) AS benefice

FROM Fact_Ventes v

INNER JOIN Dim_Lignes_Vente lv

ON v.vente_id = lv.vente_id

GROUP BY

v.date_vente::DATE

ORDER BY

date;

-- ============================================================
-- 25. BENEFICE PAR MOIS
-- ============================================================

SELECT

d.annee,

d.mois,

SUM(lv.montant_ligne - lv.cout_total) AS benefice

FROM Fact_Ventes v

INNER JOIN Dim_Date d

ON v.date_id = d.date_id

INNER JOIN Dim_Lignes_Vente lv

ON v.vente_id = lv.vente_id

GROUP BY

d.annee,
d.mois

ORDER BY

d.annee,
d.mois;

-- ============================================================
-- 26. BENEFICE PAR ANNEE
-- ============================================================

SELECT

d.annee,

SUM(lv.montant_ligne - lv.cout_total) AS benefice

FROM Fact_Ventes v

INNER JOIN Dim_Date d

ON v.date_id = d.date_id

INNER JOIN Dim_Lignes_Vente lv

ON v.vente_id = lv.vente_id

GROUP BY

d.annee

ORDER BY

d.annee;

-- ============================================================
-- 27. BENEFICE PAR PRODUIT
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

SUM(lv.qte_vente) AS quantite_vendue,

SUM(lv.montant_ligne) AS chiffre_affaires,

SUM(lv.cout_total) AS cout_total,

SUM(lv.montant_ligne - lv.cout_total) AS benefice

FROM Dim_Lignes_Vente lv

INNER JOIN Dim_Produits p

ON lv.produit_id = p.produit_id

GROUP BY

p.code_produit,
p.nom_produit

ORDER BY benefice DESC;

-- ============================================================
-- 28. BENEFICE PAR CATEGORIE
-- ============================================================

SELECT

c.nom_categorie,

SUM(lv.montant_ligne) AS chiffre_affaires,

SUM(lv.cout_total) AS cout_total,

SUM(lv.montant_ligne - lv.cout_total) AS benefice

FROM Dim_Lignes_Vente lv

INNER JOIN Dim_Produits p

ON lv.produit_id = p.produit_id

INNER JOIN Dim_Categories c

ON p.categorie_id = c.categorie_id

GROUP BY

c.nom_categorie

ORDER BY benefice DESC;

-- ============================================================
-- 29. PERFORMANCE DES VENDEURS
-- ============================================================

SELECT

ve.nom_vendeur,

COUNT(DISTINCT v.vente_id) AS nombre_ventes,

SUM(v.total_vente) AS chiffre_affaires,

SUM(lv.cout_total) AS cout_total,

SUM(lv.montant_ligne - lv.cout_total) AS benefice

FROM Fact_Ventes v

INNER JOIN Dim_Vendeurs ve

ON v.vendeur_id = ve.vendeur_id

INNER JOIN Dim_Lignes_Vente lv

ON v.vente_id = lv.vente_id

GROUP BY

ve.nom_vendeur

ORDER BY benefice DESC;

-- ============================================================
-- 30. TOP 10 DES PRODUITS LES PLUS RENTABLES
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

SUM(lv.montant_ligne - lv.cout_total) AS benefice,

SUM(lv.qte_vente) AS quantite_vendue

FROM Dim_Lignes_Vente lv

INNER JOIN Dim_Produits p

ON lv.produit_id = p.produit_id

GROUP BY

p.code_produit,
p.nom_produit

ORDER BY benefice DESC

LIMIT 10;

-- ============================================================
-- 31. TOP 10 DES PRODUITS LES PLUS VENDUS
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

SUM(lv.qte_vente) AS quantite_vendue,

SUM(lv.montant_ligne) AS chiffre_affaires

FROM Dim_Lignes_Vente lv

INNER JOIN Dim_Produits p

ON lv.produit_id = p.produit_id

GROUP BY

p.code_produit,
p.nom_produit

ORDER BY quantite_vendue DESC

LIMIT 10;

-- ============================================================
-- 32. TOP 10 DES PRODUITS LES MOINS VENDUS
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

COALESCE(SUM(lv.qte_vente),0) AS quantite_vendue

FROM Dim_Produits p

LEFT JOIN Dim_Lignes_Vente lv

ON p.produit_id = lv.produit_id

GROUP BY

p.code_produit,
p.nom_produit

ORDER BY quantite_vendue ASC

LIMIT 10;

-- ============================================================
-- 33. MARGE MOYENNE PAR PRODUIT
-- ============================================================

SELECT

p.nom_produit,

ROUND(

AVG(lv.montant_ligne - lv.cout_total)

,2)

AS marge_moyenne

FROM Dim_Lignes_Vente lv

INNER JOIN Dim_Produits p

ON lv.produit_id = p.produit_id

GROUP BY

p.nom_produit

ORDER BY marge_moyenne DESC;
-- ============================================================
-- FIN DE LA PARTIE 2B
-- ============================================================
-- ============================================================
-- PARTIE 3 : DEPENSES + PERTES + INVENTAIRE
-- ============================================================

-- ============================================================
-- 34. TOTAL DES DEPENSES
-- ============================================================

SELECT

SUM(montant) AS total_depenses

FROM Fact_Depenses;

-- ============================================================
-- 35. DEPENSES PAR CATEGORIE
-- ============================================================

SELECT

categorie_depense,

SUM(montant) AS montant_total

FROM Fact_Depenses

GROUP BY categorie_depense

ORDER BY montant_total DESC;

-- ============================================================
-- 36. DEPENSES PAR MOIS
-- ============================================================

SELECT

d.annee,

d.mois,

SUM(dp.montant) AS total_depenses

FROM Fact_Depenses dp

INNER JOIN Dim_Date d

ON dp.date_id=d.date_id

GROUP BY

d.annee,
d.mois

ORDER BY

d.annee,
d.mois;

-- ============================================================
-- 37. EVOLUTION DES DEPENSES
-- ============================================================

SELECT

date_depense,

SUM(montant) AS depenses

FROM Fact_Depenses

GROUP BY date_depense

ORDER BY date_depense;

-- ============================================================
-- 38. TOTAL DES PERTES
-- ============================================================

SELECT

SUM(valeur_totale) AS pertes_totales

FROM Dim_Pertes;

-- ============================================================
-- 39. PERTES PAR MOTIF
-- ============================================================

SELECT

motif_perte,

SUM(valeur_totale) AS montant

FROM Dim_Pertes

GROUP BY motif_perte

ORDER BY montant DESC;

-- ============================================================
-- 40. PERTES PAR PRODUIT
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

SUM(pe.qte_perte) AS quantite_perdue,

SUM(pe.valeur_totale) AS montant

FROM Dim_Pertes pe

INNER JOIN Dim_Produits p

ON pe.produit_id=p.produit_id

GROUP BY

p.code_produit,
p.nom_produit

ORDER BY montant DESC;

-- ============================================================
-- 41. PERTES PAR CATEGORIE
-- ============================================================

SELECT

c.nom_categorie,

SUM(pe.valeur_totale) AS pertes

FROM Dim_Pertes pe

INNER JOIN Dim_Produits p

ON pe.produit_id=p.produit_id

INNER JOIN Dim_Categories c

ON p.categorie_id=c.categorie_id

GROUP BY c.nom_categorie

ORDER BY pertes DESC;

-- ============================================================
-- 42. PERTES PAR MOIS
-- ============================================================

SELECT

d.annee,

d.mois,

SUM(pe.valeur_totale) AS pertes

FROM Dim_Pertes pe

INNER JOIN Dim_Date d

ON pe.date_id=d.date_id

GROUP BY

d.annee,
d.mois

ORDER BY

d.annee,
d.mois;

-- ============================================================
-- 43. PRODUITS LES PLUS PERDUS
-- ============================================================

SELECT

p.nom_produit,

SUM(pe.qte_perte) AS quantite

FROM Dim_Pertes pe

INNER JOIN Dim_Produits p

ON pe.produit_id=p.produit_id

GROUP BY p.nom_produit

ORDER BY quantite DESC

LIMIT 10;

-- ============================================================
-- 44. INVENTAIRES EFFECTUES
-- ============================================================

SELECT

date_inventaire,

COUNT(*) AS nombre_produits

FROM Fact_Inventaire

GROUP BY date_inventaire

ORDER BY date_inventaire;

-- ============================================================
-- 45. DIFFERENCE DE STOCK
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

i.stock_theorique,

i.stock_physique,

i.ecart

FROM Fact_Inventaire i

INNER JOIN Dim_Produits p

ON i.produit_id=p.produit_id

ORDER BY

ABS(i.ecart) DESC;

-- ============================================================
-- 46. INVENTAIRE AVEC VALEUR DE L'ECART
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

i.stock_theorique,

i.stock_physique,

i.ecart,

i.valeur_ecart

FROM Fact_Inventaire i

INNER JOIN Dim_Produits p

ON i.produit_id=p.produit_id

ORDER BY valeur_ecart DESC;

-- ============================================================
-- 47. DETECTION DES VOLS POTENTIELS
--
-- Ecart négatif important
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

i.stock_theorique,

i.stock_physique,

i.ecart,

i.valeur_ecart

FROM Fact_Inventaire i

INNER JOIN Dim_Produits p

ON i.produit_id=p.produit_id

WHERE i.ecart<0

ORDER BY i.valeur_ecart DESC;

-- ============================================================
-- 48. PRODUITS EN SURPLUS
-- ============================================================

SELECT

p.code_produit,

p.nom_produit,

i.stock_theorique,

i.stock_physique,

i.ecart

FROM Fact_Inventaire i

INNER JOIN Dim_Produits p

ON i.produit_id=p.produit_id

WHERE i.ecart>0

ORDER BY i.ecart DESC;

-- ============================================================
-- 49. HISTORIQUE DES INVENTAIRES
-- ============================================================

SELECT

d.annee,

d.mois,

COUNT(*) AS lignes_inventaire,

SUM(ABS(ecart)) AS total_ecarts

FROM Fact_Inventaire i

INNER JOIN Dim_Date d

ON i.date_id=d.date_id

GROUP BY

d.annee,
d.mois

ORDER BY

d.annee,
d.mois;

-- ============================================================
-- 50. POURCENTAGE DE PRODUITS AVEC ECART
-- ============================================================

SELECT

ROUND(

100.0*

SUM(

CASE

WHEN ecart<>0

THEN 1

ELSE 0

END

)

/

COUNT(*)

,2)

AS pourcentage_ecarts

FROM Fact_Inventaire;

-- ============================================================
-- FIN DE LA PARTIE 3
-- ============================================================

-- ============================================================
-- PARTIE 4 : TRESORERIE + DASHBOARD POWER BI + KPI
-- ============================================================

-- ============================================================
-- 51. SOLDE TOTAL DE LA TRESORERIE
-- ============================================================

SELECT

SUM(

CASE

WHEN type_mouvement IN ('Apport','Retrait_Banque')

THEN montant

WHEN type_mouvement IN ('Retrait','Depot_Banque')

THEN -montant

ELSE montant

END

) AS solde_tresorerie

FROM Fact_Tresorerie;

-- ============================================================
-- 52. MOUVEMENTS DE TRESORERIE PAR TYPE
-- ============================================================

SELECT

type_mouvement,

COUNT(*) AS nombre_operations,

SUM(montant) AS montant

FROM Fact_Tresorerie

GROUP BY type_mouvement

ORDER BY montant DESC;

-- ============================================================
-- 53. EVOLUTION DE LA TRESORERIE PAR MOIS
-- ============================================================

SELECT

d.annee,

d.mois,

SUM(

CASE

WHEN type_mouvement IN ('Apport','Retrait_Banque')

THEN montant

WHEN type_mouvement IN ('Retrait','Depot_Banque')

THEN -montant

ELSE montant

END

) AS solde

FROM Fact_Tresorerie t

INNER JOIN Dim_Date d

ON t.date_id=d.date_id

GROUP BY

d.annee,
d.mois

ORDER BY

d.annee,
d.mois;

-- ============================================================
-- 54. APPORTS DU PROPRIETAIRE
-- ============================================================

SELECT

SUM(montant) AS total_apports

FROM Fact_Tresorerie

WHERE type_mouvement='Apport';

-- ============================================================
-- 55. RETRAITS DU PROPRIETAIRE
-- ============================================================

SELECT

SUM(montant) AS total_retraits

FROM Fact_Tresorerie

WHERE type_mouvement='Retrait';

-- ============================================================
-- 56. BENEFICE NET
--
-- Benefice
-- - Depenses
-- - Pertes
-- ============================================================

SELECT

(
SELECT SUM(montant_ligne-cout_total)

FROM Dim_Lignes_Vente

)

-

COALESCE(

(
SELECT SUM(montant)

FROM Fact_Depenses

),0)

-

COALESCE(

(
SELECT SUM(valeur_totale)

FROM Dim_Pertes

),0)

AS benefice_net;

-- ============================================================
-- 57. TAUX DE MARGE
-- ============================================================

SELECT

ROUND(

100*

SUM(montant_ligne-cout_total)

/

SUM(montant_ligne)

,2)

AS taux_marge

FROM Dim_Lignes_Vente;

-- ============================================================
-- 58. TICKET MOYEN
-- ============================================================

SELECT

ROUND(

AVG(total_vente)

,2)

AS ticket_moyen

FROM Fact_Ventes;

-- ============================================================
-- 59. NOMBRE TOTAL DE VENTES
-- ============================================================

SELECT

COUNT(*) AS nombre_ventes

FROM Fact_Ventes;

-- ============================================================
-- 60. NOMBRE TOTAL D'ACHATS
-- ============================================================

SELECT

COUNT(*) AS nombre_achats

FROM Fact_Achats;

-- ============================================================
-- 61. VALEUR TOTALE DU STOCK
-- ============================================================

SELECT

SUM(stock_reel*pu_achat_piece)

AS valeur_stock

FROM

(

SELECT

produit_id,

SUM(quantite_achat)

-

COALESCE(

(
SELECT SUM(qte_vente)

FROM Dim_Lignes_Vente v

WHERE v.produit_id=a.produit_id

),0)

-

COALESCE(

(
SELECT SUM(qte_perte)

FROM Dim_Pertes p

WHERE p.produit_id=a.produit_id

),0)

AS stock_reel

FROM Dim_Lignes_Achat a

GROUP BY produit_id

)s

INNER JOIN

(

SELECT DISTINCT ON (produit_id)

produit_id,

pu_achat_piece

FROM Dim_Lignes_Achat

ORDER BY produit_id,
ligne_achat_id DESC

)c

ON s.produit_id=c.produit_id;

-- ============================================================
-- 62. PRODUITS ACTIFS
-- ============================================================

SELECT

COUNT(*) AS produits_actifs

FROM Dim_Produits

WHERE actif=TRUE;

-- ============================================================
-- 63. PRODUITS INACTIFS
-- ============================================================

SELECT

COUNT(*) AS produits_inactifs

FROM Dim_Produits

WHERE actif=FALSE;

-- ============================================================
-- 64. DASHBOARD : CHIFFRE D'AFFAIRES / BENEFICE / DEPENSES
-- ============================================================

SELECT

(
SELECT SUM(total_vente)

FROM Fact_Ventes

) AS chiffre_affaires,

(

SELECT SUM(montant_ligne-cout_total)

FROM Dim_Lignes_Vente

) AS benefice_brut,

(

SELECT SUM(montant)

FROM Fact_Depenses

) AS depenses,

(

SELECT SUM(valeur_totale)

FROM Dim_Pertes

) AS pertes;

-- ============================================================
-- 65. DASHBOARD : INDICATEURS GENERAUX
-- ============================================================

SELECT

(SELECT COUNT(*) FROM Dim_Produits) AS produits,

(SELECT COUNT(*) FROM Fact_Achats) AS achats,

(SELECT COUNT(*) FROM Fact_Ventes) AS ventes,

(SELECT COUNT(*) FROM Dim_Pertes) AS pertes,

(SELECT COUNT(*) FROM Fact_Inventaire) AS inventaires,

(SELECT COUNT(*) FROM Fact_Tresorerie) AS mouvements_tresorerie;

-- ============================================================
-- 66. DASHBOARD : TOP 5 CATEGORIES
-- ============================================================

SELECT

c.nom_categorie,

SUM(v.montant_ligne) AS chiffre_affaires

FROM Dim_Lignes_Vente v

INNER JOIN Dim_Produits p

ON v.produit_id=p.produit_id

INNER JOIN Dim_Categories c

ON p.categorie_id=c.categorie_id

GROUP BY c.nom_categorie

ORDER BY chiffre_affaires DESC

LIMIT 5;

-- ============================================================
-- 67. DASHBOARD : KPI PRINCIPAUX
-- ============================================================

SELECT

(SELECT SUM(total_vente)
FROM Fact_Ventes)
AS chiffre_affaires,

(SELECT SUM(montant_ligne-cout_total)
FROM Dim_Lignes_Vente)
AS benefice,

(SELECT SUM(montant)
FROM Fact_Depenses)
AS depenses,

(SELECT SUM(valeur_totale)
FROM Dim_Pertes)
AS pertes,

(SELECT COUNT(*)
FROM Fact_Ventes)
AS ventes,

(SELECT COUNT(*)
FROM Dim_Produits)
AS produits,

(SELECT COUNT(*)
FROM Fact_Inventaire)
AS inventaires;

-- ============================================================
-- FIN DE LA PARTIE 4
-- ============================================================
select *
from Dim_Date

select *
from dim_date

SELECT table_name
FROM information_schema.tables
WHERE table_schema='public'
ORDER BY table_name;
