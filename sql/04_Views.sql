-- ============================================================
-- PROJET : GESTION DE SUPERETTE
-- FICHIER : 04_Views.sql
-- BASE DE DONNEES : PostgreSQL
-- AUTEUR : Girandoux Fandio
-- DESCRIPTION : Vues pour Streamlit, rapports et Power BI.
-- ============================================================
--
-- FLUX :
-- Tables PostgreSQL → Vues détaillées → Agrégats et KPI
-- → Streamlit / Rapports / Power BI
--
-- Les jointures, filtres, calculs et noms de colonnes restent inchangés.
-- ============================================================

-- ============================================================

CREATE OR REPLACE VIEW vw_produits_stock AS
WITH dernier_cout AS (
SELECT DISTINCT ON (la.produit_id) la.produit_id,
    la.pu_achat_piece,
    la.pu_achat_carton,
    la.qte_par_carton,
    a.date_achat
FROM dim_lignes_achat la
JOIN fact_achats a ON a.achat_id=la.achat_id
ORDER BY la.produit_id,
    a.date_achat DESC,
    la.ligne_achat_id DESC )
SELECT p.produit_id,
    p.code_produit,
    p.nom_produit,
    p.categorie_id,
    c.code_categorie,
    c.nom_categorie,
    p.unite,
    p.qte_par_carton,
    p.stock_min,
    COALESCE(p.stock_actuel,
    0) AS stock_actuel,
    COALESCE(dc.pu_achat_piece,
    0) AS cout_unitaire_estime,
    ROUND(COALESCE(p.stock_actuel,
    0)*COALESCE(dc.pu_achat_piece,
    0),
    2) AS valeur_stock_estimee,
    p.actif,
    p.date_creation,
    dc.date_achat AS date_dernier_achat,
    CASE WHEN COALESCE(p.stock_actuel,
    0)<=0 THEN 'RUPTURE' WHEN COALESCE(p.stock_actuel,
    0)<=p.stock_min THEN 'ALERTE' ELSE 'NORMAL' END AS statut_stock
FROM dim_produits p
    LEFT
JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT
JOIN dernier_cout dc ON dc.produit_id=p.produit_id;

CREATE OR REPLACE VIEW vw_stock_alertes AS
SELECT *
FROM vw_produits_stock
WHERE COALESCE(stock_actuel,
    0)<=COALESCE(stock_min,
    0);

-- ============================================================
-- 2. ACHATS DETAILLES
-- ============================================================

CREATE OR REPLACE VIEW vw_achats_detail AS
SELECT a.achat_id,
    a.date_achat,
    a.date_id,
    d.jour,
    d.mois,
    d.annee,
    d.trimestre,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    a.numero_facture,
    a.type_achat,
    a.acheteur_id,
    ac.nom_acheteur,
    la.ligne_achat_id,
    la.produit_id,
    p.code_produit,
    p.nom_produit,
    c.code_categorie,
    c.nom_categorie,
    la.qte_cartons,
    la.qte_par_carton,
    la.quantite_achat,
    la.pu_achat_carton,
    la.pu_achat_piece,
    la.total_achat,
    a.frais_enlevement,
    a.total_facture,
    la.date_fabrication,
    la.date_peremption,
    CASE WHEN la.date_peremption IS NOT NULL AND la.date_peremption<CURRENT_DATE THEN 'EXPIRE' WHEN la.date_peremption IS NOT NULL AND la.date_peremption<=CURRENT_DATE+INTERVAL '30 days' THEN 'BIENTOT' ELSE 'OK' END AS statut_peremption
FROM fact_achats a
JOIN dim_lignes_achat la ON la.achat_id=a.achat_id
JOIN dim_produits p ON p.produit_id=la.produit_id
    LEFT
JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT
JOIN dim_acheteurs ac ON ac.acheteur_id=a.acheteur_id
    LEFT
JOIN dim_date d ON d.date_id=a.date_id;

-- ============================================================
-- 3. VENTES DETAILLEES
-- ============================================================

CREATE OR REPLACE VIEW vw_ventes_detail AS
SELECT v.vente_id,
    v.date_vente,
    v.date_id,
    d.jour,
    d.mois,
    d.annee,
    d.trimestre,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    v.vendeur_id,
    ve.nom_vendeur,
    lv.ligne_vente_id,
    lv.produit_id,
    p.code_produit,
    p.nom_produit,
    c.code_categorie,
    c.nom_categorie,
    lv.qte_vente,
    lv.pu_vente,
    lv.montant_ligne,
    lv.cout_unitaire,
    lv.cout_total,
    COALESCE(lv.type_vente,
    'Normale') AS type_vente,
    ROUND(lv.montant_ligne-COALESCE(lv.cout_total,
    0),
    2) AS marge_ligne,
    ROUND(CASE WHEN lv.montant_ligne>0 THEN ((lv.montant_ligne-COALESCE(lv.cout_total,
    0))/lv.montant_ligne)*100 ELSE 0 END,
    2) AS taux_marge_ligne,
    v.total_vente
FROM fact_ventes v
JOIN dim_lignes_vente lv ON lv.vente_id=v.vente_id
JOIN dim_produits p ON p.produit_id=lv.produit_id
    LEFT
JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT
JOIN dim_vendeurs ve ON ve.vendeur_id=v.vendeur_id
    LEFT
JOIN dim_date d ON d.date_id=v.date_id;

CREATE OR REPLACE VIEW vw_ventes_par_type AS
SELECT type_vente,
    COUNT(*) AS nombre_lignes,
    COALESCE(SUM(qte_vente),
    0) AS quantite_vendue,
    COALESCE(SUM(montant_ligne),
    0) AS chiffre_affaires,
    COALESCE(SUM(cout_total),
    0) AS cout_total,
    COALESCE(SUM(marge_ligne),
    0) AS marge_brute
FROM vw_ventes_detail
GROUP BY type_vente;

-- ============================================================
-- 4. DEPENSES
-- ============================================================

CREATE OR REPLACE VIEW vw_depenses AS
SELECT de.depense_id,
    de.date_depense,
    de.date_id,
    d.jour,
    d.mois,
    d.annee,
    d.trimestre,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    de.categorie_depense,
    de.montant,
    de.motif,
    de.utilisateur
FROM fact_depenses de
    LEFT
JOIN dim_date d ON d.date_id=de.date_id;

-- ============================================================
-- 5. PERTES DETAILLEES
-- ============================================================

CREATE OR REPLACE VIEW vw_pertes_detail AS
SELECT pe.perte_id,
    pe.date_perte,
    pe.date_id,
    d.jour,
    d.mois,
    d.annee,
    d.trimestre,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    pe.produit_id,
    p.code_produit,
    p.nom_produit,
    c.code_categorie,
    c.nom_categorie,
    pe.qte_perte,
    pe.motif_perte,
    pe.valeur_unitaire,
    pe.valeur_totale,
    pe.utilisateur
FROM dim_pertes pe
JOIN dim_produits p ON p.produit_id=pe.produit_id
    LEFT
JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT
JOIN dim_date d ON d.date_id=pe.date_id;

-- ============================================================
-- 6. INVENTAIRE DETAILLE AVEC CLOTURE
-- ============================================================

CREATE OR REPLACE VIEW vw_inventaire_detail AS
SELECT i.inventaire_id,
    i.date_inventaire,
    i.date_id,
    d.jour,
    d.mois,
    d.annee,
    d.trimestre,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    i.produit_id,
    p.code_produit,
    p.nom_produit,
    c.code_categorie,
    c.nom_categorie,
    i.stock_theorique,
    i.stock_physique,
    i.ecart,
    i.valeur_ecart,
    i.commentaire,
    i.utilisateur,
    COALESCE(i.cloture,
    FALSE) AS cloture,
    i.date_cloture,
    i.perte_id,
    COALESCE(i.ajustement_stock,
    0) AS ajustement_stock,
    CASE WHEN i.ecart=0 THEN 'CONFORME' WHEN i.ecart>0 THEN 'SURPLUS' ELSE 'MANQUANT' END AS statut_ecart,
    CASE WHEN COALESCE(i.cloture,
    FALSE)=TRUE THEN 'CLOTURE' ELSE 'OUVERT' END AS statut_cloture
FROM fact_inventaire i
JOIN dim_produits p ON p.produit_id=i.produit_id
    LEFT
JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT
JOIN dim_date d ON d.date_id=i.date_id;

-- ============================================================
-- 7. TRESORERIE ET CAISSE REELLE
-- ============================================================

CREATE OR REPLACE VIEW vw_tresorerie AS
SELECT t.mouvement_id,
    t.date_mouvement,
    t.date_id,
    d.jour,
    d.mois,
    d.annee,
    d.trimestre,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    t.type_mouvement,
    t.montant,
    t.description,
    t.utilisateur,
    CASE WHEN t.type_mouvement IN ('Apport',
    'Retrait_Banque') THEN t.montant ELSE 0 END AS entree,
    CASE WHEN t.type_mouvement IN ('Retrait',
    'Depot_Banque') THEN t.montant ELSE 0 END AS sortie,
    CASE WHEN t.type_mouvement IN ('Apport',
    'Retrait_Banque') THEN t.montant WHEN t.type_mouvement IN ('Retrait',
    'Depot_Banque') THEN -t.montant ELSE 0 END AS montant_signe
FROM fact_tresorerie t
    LEFT
JOIN dim_date d ON d.date_id=t.date_id;

CREATE OR REPLACE VIEW vw_caisse_reelle AS
SELECT source,
    date_mouvement AS date_operation,
    date_id,
    type_operation,
    montant,
    entree,
    sortie,
    montant_signe,
    description
FROM (
SELECT 'TRESORERIE' AS source,
    t.date_mouvement,
    t.date_id,
    t.type_mouvement AS type_operation,
    t.montant,
    t.entree,
    t.sortie,
    t.montant_signe,
    t.description
FROM vw_tresorerie t UNION ALL
SELECT 'VENTE',
    v.date_vente,
    v.date_id,
    'Vente',
    v.total_vente,
    v.total_vente,
    0,
    v.total_vente,
    'Vente client'
FROM fact_ventes v UNION ALL
SELECT 'ACHAT',
    a.date_achat,
    a.date_id,
    'Achat',
    a.total_facture,
    0,
    a.total_facture,
    -a.total_facture,
    a.numero_facture
FROM fact_achats a UNION ALL
SELECT 'DEPENSE',
    de.date_depense,
    de.date_id,
    'Depense',
    de.montant,
    0,
    de.montant,
    -de.montant,
    de.motif
FROM fact_depenses de ) caisse;

-- ============================================================
-- 8. SYNTHESES MENSUELLES
-- ============================================================

CREATE OR REPLACE VIEW vw_ventes_mensuelles AS
SELECT d.annee,
    d.mois,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    COUNT(DISTINCT v.vente_id) AS nombre_ventes,
    COALESCE(SUM(lv.qte_vente),
    0) AS quantite_vendue,
    COALESCE(SUM(lv.montant_ligne),
    0) AS chiffre_affaires,
    COALESCE(SUM(lv.cout_total),
    0) AS cout_total,
    COALESCE(SUM(lv.montant_ligne-COALESCE(lv.cout_total,
    0)),
    0) AS marge_brute
FROM fact_ventes v
JOIN dim_date d ON d.date_id=v.date_id
    LEFT
JOIN dim_lignes_vente lv ON lv.vente_id=v.vente_id
GROUP BY d.annee,
    d.mois,
    d.nom_mois;

CREATE OR REPLACE VIEW vw_achats_mensuels AS
WITH achats_lignes AS (
SELECT a.achat_id,
    a.date_id,
    COALESCE(SUM(la.quantite_achat),
    0) AS quantite_achetee,
    COALESCE(SUM(la.total_achat),
    0) AS total_lignes
FROM fact_achats a
    LEFT
JOIN dim_lignes_achat la ON la.achat_id=a.achat_id
GROUP BY a.achat_id,
    a.date_id )
SELECT d.annee,
    d.mois,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    COUNT(DISTINCT a.achat_id) AS nombre_achats,
    COALESCE(SUM(al.quantite_achetee),
    0) AS quantite_achetee,
    COALESCE(SUM(al.total_lignes),
    0) AS total_achats,
    COALESCE(SUM(a.frais_enlevement),
    0) AS frais_enlevement,
    COALESCE(SUM(a.total_facture),
    0) AS total_factures
FROM fact_achats a
JOIN dim_date d ON d.date_id=a.date_id
    LEFT
JOIN achats_lignes al ON al.achat_id=a.achat_id
GROUP BY d.annee,
    d.mois,
    d.nom_mois;

CREATE OR REPLACE VIEW vw_depenses_mensuelles AS
SELECT d.annee,
    d.mois,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    de.categorie_depense,
    COUNT(de.depense_id) AS nombre_depenses,
    COALESCE(SUM(de.montant),
    0) AS total_depenses
FROM fact_depenses de
JOIN dim_date d ON d.date_id=de.date_id
GROUP BY d.annee,
    d.mois,
    d.nom_mois,
    de.categorie_depense;

CREATE OR REPLACE VIEW vw_pertes_mensuelles AS
SELECT d.annee,
    d.mois,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    pe.motif_perte,
    COUNT(pe.perte_id) AS nombre_pertes,
    COALESCE(SUM(pe.qte_perte),
    0) AS quantite_perdue,
    COALESCE(SUM(pe.valeur_totale),
    0) AS valeur_perdue
FROM dim_pertes pe
JOIN dim_date d ON d.date_id=pe.date_id
GROUP BY d.annee,
    d.mois,
    d.nom_mois,
    pe.motif_perte;

-- ============================================================
-- 9. PERFORMANCE PRODUITS ET CATEGORIES
-- ============================================================

CREATE OR REPLACE VIEW vw_performance_produits AS
SELECT p.produit_id,
    p.code_produit,
    p.nom_produit,
    c.code_categorie,
    c.nom_categorie,
    COALESCE(p.stock_actuel,
    0) AS stock_actuel,
    p.stock_min,
    COALESCE(SUM(lv.qte_vente),
    0) AS quantite_vendue,
    COALESCE(SUM(lv.montant_ligne),
    0) AS chiffre_affaires,
    COALESCE(SUM(lv.cout_total),
    0) AS cout_total,
    COALESCE(SUM(lv.montant_ligne-COALESCE(lv.cout_total,
    0)),
    0) AS marge_brute,
    CASE WHEN COALESCE(SUM(lv.qte_vente),
    0)>0 THEN 'VENDU' ELSE 'NON_VENDU' END AS statut_vente
FROM dim_produits p
    LEFT
JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT
JOIN dim_lignes_vente lv ON lv.produit_id=p.produit_id
GROUP BY p.produit_id,
    p.code_produit,
    p.nom_produit,
    c.code_categorie,
    c.nom_categorie,
    p.stock_actuel,
    p.stock_min;

CREATE OR REPLACE VIEW vw_performance_categories AS
SELECT nom_categorie,
    COUNT(DISTINCT produit_id) AS nombre_produits,
    COALESCE(SUM(quantite_vendue),
    0) AS quantite_vendue,
    COALESCE(SUM(chiffre_affaires),
    0) AS chiffre_affaires,
    COALESCE(SUM(cout_total),
    0) AS cout_total,
    COALESCE(SUM(marge_brute),
    0) AS marge_brute,
    COALESCE(SUM(valeur_stock_estimee),
    0) AS valeur_stock_estimee
FROM (
SELECT pp.*,
    ps.valeur_stock_estimee
FROM vw_performance_produits pp
    LEFT
JOIN vw_produits_stock ps ON ps.produit_id=pp.produit_id ) x
GROUP BY nom_categorie;

-- ============================================================
-- 10. DASHBOARD GLOBAL POWER BI
-- ============================================================

CREATE OR REPLACE VIEW vw_dashboard_global AS
SELECT (
SELECT COUNT(*)
FROM dim_produits
WHERE actif=TRUE) AS total_produits_actifs,
    (
SELECT COUNT(*)
FROM dim_categories) AS total_categories,
    (
SELECT COALESCE(SUM(montant_ligne),
    0)
FROM dim_lignes_vente) AS chiffre_affaires,
    (
SELECT COALESCE(SUM(total_facture),
    0)
FROM fact_achats) AS total_achats,
    (
SELECT COALESCE(SUM(montant),
    0)
FROM fact_depenses) AS total_depenses,
    (
SELECT COALESCE(SUM(valeur_totale),
    0)
FROM dim_pertes) AS total_pertes,
    (
SELECT COALESCE(SUM(montant_ligne-COALESCE(cout_total,
    0)),
    0)
FROM dim_lignes_vente) AS marge_brute,
    (
SELECT COALESCE(SUM(stock_actuel),
    0)
FROM dim_produits) AS stock_total,
    (
SELECT COALESCE(SUM(valeur_stock_estimee),
    0)
FROM vw_produits_stock) AS valeur_stock,
    (
SELECT COUNT(*)
FROM dim_produits
WHERE COALESCE(stock_actuel,
    0)<=stock_min) AS produits_stock_alerte,
    (
SELECT COUNT(*)
FROM dim_produits
WHERE COALESCE(stock_actuel,
    0)<=0) AS produits_rupture,
    (
SELECT COUNT(*)
FROM fact_inventaire
WHERE COALESCE(cloture,
    FALSE)=FALSE AND ecart<>0) AS inventaires_ouverts_ecart,
    (
SELECT COALESCE(SUM(montant_signe),
    0)
FROM vw_tresorerie) AS solde_tresorerie_mouvements,
    (
SELECT COALESCE(SUM(montant_signe),
    0)
FROM vw_caisse_reelle) AS solde_reel_caisse;

-- ============================================================
-- 11. ALIAS COMPATIBLES POWER BI
-- ============================================================

CREATE OR REPLACE VIEW vue_date AS
SELECT *
FROM dim_date;

CREATE OR REPLACE VIEW vue_produits_stock AS
SELECT *
FROM vw_produits_stock;

CREATE OR REPLACE VIEW vue_stock_alertes AS
SELECT *
FROM vw_stock_alertes;

CREATE OR REPLACE VIEW vue_achats_detail AS
SELECT *
FROM vw_achats_detail;

CREATE OR REPLACE VIEW vue_ventes_detail AS
SELECT *
FROM vw_ventes_detail;

CREATE OR REPLACE VIEW vue_ventes_par_type AS
SELECT *
FROM vw_ventes_par_type;

CREATE OR REPLACE VIEW vue_depenses AS
SELECT *
FROM vw_depenses;

CREATE OR REPLACE VIEW vue_pertes AS
SELECT *
FROM vw_pertes_detail;

CREATE OR REPLACE VIEW vue_inventaire AS
SELECT *
FROM vw_inventaire_detail;

CREATE OR REPLACE VIEW vue_tresorerie AS
SELECT *
FROM vw_tresorerie;

CREATE OR REPLACE VIEW vue_caisse_reelle AS
SELECT *
FROM vw_caisse_reelle;

CREATE OR REPLACE VIEW vue_performance_produits AS
SELECT *
FROM vw_performance_produits;

CREATE OR REPLACE VIEW vue_performance_categories AS
SELECT *
FROM vw_performance_categories;

CREATE OR REPLACE VIEW vue_ventes_mensuelles AS
SELECT *
FROM vw_ventes_mensuelles;

CREATE OR REPLACE VIEW vue_achats_mensuels AS
SELECT *
FROM vw_achats_mensuels;

CREATE OR REPLACE VIEW vue_depenses_mensuelles AS
SELECT *
FROM vw_depenses_mensuelles;

CREATE OR REPLACE VIEW vue_pertes_mensuelles AS
SELECT *
FROM vw_pertes_mensuelles;

CREATE OR REPLACE VIEW vue_dashboard_global AS
SELECT *
FROM vw_dashboard_global;

-- ============================================================
-- Nettoyage avant correction : structure de pertes modifiee

    DROP VIEW IF EXISTS vue_pertes CASCADE;

    DROP VIEW IF EXISTS vue_pertes_mensuelles CASCADE;

    DROP VIEW IF EXISTS vue_dashboard_global CASCADE;

    DROP VIEW IF EXISTS vue_controle_stock CASCADE;

    DROP VIEW IF EXISTS vw_pertes_detail CASCADE;

    DROP VIEW IF EXISTS vw_pertes_mensuelles CASCADE;

    DROP VIEW IF EXISTS vw_dashboard_global CASCADE;

    DROP VIEW IF EXISTS vw_controle_stock CASCADE;

-- 12. CORRECTION POWER BI : PERTES INVENTAIRE ET CONTROLE STOCK
-- ============================================================

CREATE OR REPLACE VIEW vw_pertes_detail AS
SELECT pe.perte_id,
    pe.date_perte,
    pe.date_id,
    d.jour,
    d.mois,
    d.annee,
    d.trimestre,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    pe.produit_id,
    p.code_produit,
    p.nom_produit,
    c.code_categorie,
    c.nom_categorie,
    pe.qte_perte,
    pe.motif_perte,
    CASE WHEN UPPER(COALESCE(pe.motif_perte,
    ''))='INVENTAIRE' THEN 'INVENTAIRE' ELSE 'SIGNALEE' END AS type_perte_controle,
    CASE WHEN UPPER(COALESCE(pe.motif_perte,
    ''))='INVENTAIRE' THEN pe.qte_perte ELSE 0 END AS qte_perte_inventaire,
    CASE WHEN UPPER(COALESCE(pe.motif_perte,
    ''))<>'INVENTAIRE' THEN pe.qte_perte ELSE 0 END AS qte_perte_signalee,
    pe.valeur_unitaire,
    pe.valeur_totale,
    CASE WHEN UPPER(COALESCE(pe.motif_perte,
    ''))='INVENTAIRE' THEN pe.valeur_totale ELSE 0 END AS valeur_perte_inventaire,
    CASE WHEN UPPER(COALESCE(pe.motif_perte,
    ''))<>'INVENTAIRE' THEN pe.valeur_totale ELSE 0 END AS valeur_perte_signalee,
    pe.utilisateur
FROM dim_pertes pe
JOIN dim_produits p ON p.produit_id=pe.produit_id
    LEFT
JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT
JOIN dim_date d ON d.date_id=pe.date_id;

CREATE OR REPLACE VIEW vw_pertes_mensuelles AS
SELECT d.annee,
    d.mois,
    d.nom_mois,
    MAKE_DATE(d.annee,
    d.mois,
    1) AS mois_date,
    pe.motif_perte,
    CASE WHEN UPPER(COALESCE(pe.motif_perte,
    ''))='INVENTAIRE' THEN 'INVENTAIRE' ELSE 'SIGNALEE' END AS type_perte_controle,
    COUNT(pe.perte_id) AS nombre_pertes,
    COALESCE(SUM(pe.qte_perte),
    0) AS quantite_perdue,
    COALESCE(SUM(CASE WHEN UPPER(COALESCE(pe.motif_perte,
    ''))='INVENTAIRE' THEN pe.qte_perte ELSE 0 END),
    0) AS quantite_perdue_inventaire,
    COALESCE(SUM(CASE WHEN UPPER(COALESCE(pe.motif_perte,
    ''))<>'INVENTAIRE' THEN pe.qte_perte ELSE 0 END),
    0) AS quantite_perdue_signalee,
    COALESCE(SUM(pe.valeur_totale),
    0) AS valeur_perdue,
    COALESCE(SUM(CASE WHEN UPPER(COALESCE(pe.motif_perte,
    ''))='INVENTAIRE' THEN pe.valeur_totale ELSE 0 END),
    0) AS valeur_perdue_inventaire,
    COALESCE(SUM(CASE WHEN UPPER(COALESCE(pe.motif_perte,
    ''))<>'INVENTAIRE' THEN pe.valeur_totale ELSE 0 END),
    0) AS valeur_perdue_signalee
FROM dim_pertes pe
JOIN dim_date d ON d.date_id=pe.date_id
GROUP BY d.annee,
    d.mois,
    d.nom_mois,
    pe.motif_perte,
    type_perte_controle;

CREATE OR REPLACE VIEW vw_controle_stock AS
WITH dernier_inventaire AS (
SELECT DISTINCT ON (i.produit_id) i.produit_id,
    i.date_inventaire,
    GREATEST(COALESCE(i.stock_physique,
    0),
    0) AS stock_dernier_inventaire
FROM fact_inventaire i
WHERE COALESCE(i.cloture,
    FALSE)=TRUE
ORDER BY i.produit_id,
    i.date_inventaire DESC,
    i.inventaire_id DESC ),
    base_produits AS (
SELECT p.produit_id,
    p.code_produit,
    p.nom_produit,
    COALESCE(c.nom_categorie,
    'Non classe') AS nom_categorie,
    COALESCE(p.stock_actuel,
    0) AS stock_actuel,
    COALESCE(di.stock_dernier_inventaire,
    0) AS stock_dernier_inventaire,
    di.date_inventaire AS date_dernier_inventaire,
    COALESCE(di.date_inventaire,
    CURRENT_DATE) AS date_debut_mouvements,
    CURRENT_DATE AS date_fin_controle
FROM dim_produits p
    LEFT
JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT
JOIN dernier_inventaire di ON di.produit_id=p.produit_id
WHERE COALESCE(p.actif,
    TRUE)=TRUE ),
    achats_periode AS (
SELECT bp.produit_id,
    COALESCE(SUM(COALESCE(la.quantite_achat,
    0)),
    0) AS quantite_achetee
FROM base_produits bp
    LEFT
JOIN fact_achats a ON a.date_achat >= bp.date_debut_mouvements AND a.date_achat <= bp.date_fin_controle
    LEFT
JOIN dim_lignes_achat la ON la.achat_id=a.achat_id AND la.produit_id=bp.produit_id
GROUP BY bp.produit_id ),
    ventes_periode AS (
SELECT bp.produit_id,
    COALESCE(SUM(COALESCE(lv.qte_vente,
    0)),
    0) AS quantite_vendue
FROM base_produits bp
    LEFT
JOIN fact_ventes v ON v.date_vente >= bp.date_debut_mouvements AND v.date_vente <= bp.date_fin_controle
    LEFT
JOIN dim_lignes_vente lv ON lv.vente_id=v.vente_id AND lv.produit_id=bp.produit_id
GROUP BY bp.produit_id ),
    pertes_signalees AS (
SELECT bp.produit_id,
    COALESCE(SUM(COALESCE(pe.qte_perte,
    0)),
    0) AS quantite_perdue_signalee
FROM base_produits bp
    LEFT
JOIN dim_pertes pe ON pe.produit_id=bp.produit_id AND pe.date_perte >= bp.date_debut_mouvements AND pe.date_perte <= bp.date_fin_controle AND UPPER(COALESCE(pe.motif_perte,
    ''))<>'INVENTAIRE'
GROUP BY bp.produit_id ),
    pertes_inventaire AS (
SELECT bp.produit_id,
    COALESCE(SUM(COALESCE(pe.qte_perte,
    0)),
    0) AS quantite_perdue_inventaire
FROM base_produits bp
    LEFT
JOIN dim_pertes pe ON pe.produit_id=bp.produit_id AND pe.date_perte >= bp.date_debut_mouvements AND pe.date_perte <= bp.date_fin_controle AND UPPER(COALESCE(pe.motif_perte,
    ''))='INVENTAIRE'
GROUP BY bp.produit_id ),
    controle AS (
SELECT bp.produit_id,
    bp.code_produit,
    bp.nom_produit,
    bp.nom_categorie,
    bp.date_dernier_inventaire,
    bp.date_debut_mouvements,
    bp.date_fin_controle,
    bp.stock_dernier_inventaire,
    COALESCE(ap.quantite_achetee,
    0) AS quantite_achetee,
    COALESCE(vp.quantite_vendue,
    0) AS quantite_vendue,
    COALESCE(ps.quantite_perdue_signalee,
    0) AS quantite_perdue_signalee,
    COALESCE(pi.quantite_perdue_inventaire,
    0) AS quantite_perdue_inventaire,
    GREATEST(bp.stock_dernier_inventaire+COALESCE(ap.quantite_achetee,
    0)-COALESCE(vp.quantite_vendue,
    0)-COALESCE(ps.quantite_perdue_signalee,
    0),
    0) AS stock_theorique_attendu,
    bp.stock_actuel
FROM base_produits bp
    LEFT
JOIN achats_periode ap ON ap.produit_id=bp.produit_id
    LEFT
JOIN ventes_periode vp ON vp.produit_id=bp.produit_id
    LEFT
JOIN pertes_signalees ps ON ps.produit_id=bp.produit_id
    LEFT
JOIN pertes_inventaire pi ON pi.produit_id=bp.produit_id )
SELECT *,
    stock_actuel-stock_theorique_attendu AS ecart_controle,
    CASE WHEN stock_actuel-stock_theorique_attendu=0 THEN 'CONFORME' WHEN stock_actuel-stock_theorique_attendu>0 THEN 'SURPLUS' ELSE 'MANQUANT' END AS statut_controle
FROM controle;

CREATE OR REPLACE VIEW vw_dashboard_global AS
SELECT (
SELECT COUNT(*)
FROM dim_produits
WHERE actif=TRUE) AS total_produits_actifs,
    (
SELECT COUNT(*)
FROM dim_categories) AS total_categories,
    (
SELECT COALESCE(SUM(montant_ligne),
    0)
FROM dim_lignes_vente) AS chiffre_affaires,
    (
SELECT COALESCE(SUM(total_facture),
    0)
FROM fact_achats) AS total_achats,
    (
SELECT COALESCE(SUM(montant),
    0)
FROM fact_depenses) AS total_depenses,
    (
SELECT COALESCE(SUM(valeur_totale),
    0)
FROM dim_pertes) AS total_pertes,
    (
SELECT COALESCE(SUM(valeur_perte_signalee),
    0)
FROM vw_pertes_detail) AS total_pertes_signalees,
    (
SELECT COALESCE(SUM(valeur_perte_inventaire),
    0)
FROM vw_pertes_detail) AS total_pertes_inventaire,
    (
SELECT COALESCE(SUM(montant_ligne-COALESCE(cout_total,
    0)),
    0)
FROM dim_lignes_vente) AS marge_brute,
    (
SELECT COALESCE(SUM(stock_actuel),
    0)
FROM dim_produits) AS stock_total,
    (
SELECT COALESCE(SUM(valeur_stock_estimee),
    0)
FROM vw_produits_stock) AS valeur_stock,
    (
SELECT COUNT(*)
FROM dim_produits
WHERE COALESCE(stock_actuel,
    0)<=stock_min) AS produits_stock_alerte,
    (
SELECT COUNT(*)
FROM dim_produits
WHERE COALESCE(stock_actuel,
    0)<=0) AS produits_rupture,
    (
SELECT COUNT(*)
FROM fact_inventaire
WHERE COALESCE(cloture,
    FALSE)=FALSE AND ecart<>0) AS inventaires_ouverts_ecart,
    (
SELECT COUNT(*)
FROM vw_controle_stock
WHERE statut_controle='MANQUANT') AS controle_stock_manquants,
    (
SELECT COUNT(*)
FROM vw_controle_stock
WHERE statut_controle='SURPLUS') AS controle_stock_surplus,
    (
SELECT COALESCE(SUM(ABS(ecart_controle)),
    0)
FROM vw_controle_stock) AS controle_stock_ecart_total,
    (
SELECT COALESCE(SUM(montant_signe),
    0)
FROM vw_tresorerie) AS solde_tresorerie_mouvements,
    (
SELECT COALESCE(SUM(montant_signe),
    0)
FROM vw_caisse_reelle) AS solde_reel_caisse;

CREATE OR REPLACE VIEW vue_pertes AS
SELECT *
FROM vw_pertes_detail;

CREATE OR REPLACE VIEW vue_pertes_mensuelles AS
SELECT *
FROM vw_pertes_mensuelles;

CREATE OR REPLACE VIEW vue_controle_stock AS
SELECT *
FROM vw_controle_stock;

CREATE OR REPLACE VIEW vue_dashboard_global AS
SELECT *
FROM vw_dashboard_global;

-- ============================================================
-- FIN CORRECTION POWER BI
-- ============================================================
-- ============================================================
-- Nettoyage avant correction : structure controle stock modifiee

    DROP VIEW IF EXISTS vue_dashboard_global CASCADE;

    DROP VIEW IF EXISTS vue_controle_stock CASCADE;

    DROP VIEW IF EXISTS vw_dashboard_global CASCADE;

    DROP VIEW IF EXISTS vw_controle_stock CASCADE;

-- 13. CORRECTION POWER BI : VENTE EXCEDENTAIRE CONTROLE STOCK
-- ============================================================

CREATE OR REPLACE VIEW vw_controle_stock AS
WITH dernier_inventaire AS (
SELECT DISTINCT ON (i.produit_id) i.produit_id,
    i.date_inventaire,
    GREATEST(COALESCE(i.stock_physique,
    0),
    0) AS stock_dernier_inventaire
FROM fact_inventaire i
WHERE COALESCE(i.cloture,
    FALSE)=TRUE
ORDER BY i.produit_id,
    i.date_inventaire DESC,
    i.inventaire_id DESC ),
    base_produits AS (
SELECT p.produit_id,
    p.code_produit,
    p.nom_produit,
    COALESCE(c.nom_categorie,
    'Non classe') AS nom_categorie,
    COALESCE(p.stock_actuel,
    0) AS stock_actuel,
    COALESCE(di.stock_dernier_inventaire,
    0) AS stock_dernier_inventaire,
    di.date_inventaire AS date_dernier_inventaire,
    COALESCE(di.date_inventaire,
    CURRENT_DATE) AS date_debut_mouvements,
    CURRENT_DATE AS date_fin_controle
FROM dim_produits p
    LEFT
JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT
JOIN dernier_inventaire di ON di.produit_id=p.produit_id
WHERE COALESCE(p.actif,
    TRUE)=TRUE ),
    achats_periode AS (
SELECT bp.produit_id,
    COALESCE(SUM(COALESCE(la.quantite_achat,
    0)),
    0) AS quantite_achetee
FROM base_produits bp
    LEFT
JOIN fact_achats a ON a.date_achat >= bp.date_debut_mouvements AND a.date_achat <= bp.date_fin_controle
    LEFT
JOIN dim_lignes_achat la ON la.achat_id=a.achat_id AND la.produit_id=bp.produit_id
GROUP BY bp.produit_id ),
    ventes_periode AS (
SELECT bp.produit_id,
    COALESCE(SUM(COALESCE(lv.qte_vente,
    0)),
    0) AS quantite_vendue
FROM base_produits bp
    LEFT
JOIN fact_ventes v ON v.date_vente >= bp.date_debut_mouvements AND v.date_vente <= bp.date_fin_controle
    LEFT
JOIN dim_lignes_vente lv ON lv.vente_id=v.vente_id AND lv.produit_id=bp.produit_id
GROUP BY bp.produit_id ),
    pertes_signalees AS (
SELECT bp.produit_id,
    COALESCE(SUM(COALESCE(pe.qte_perte,
    0)),
    0) AS quantite_perdue_signalee
FROM base_produits bp
    LEFT
JOIN dim_pertes pe ON pe.produit_id=bp.produit_id AND pe.date_perte >= bp.date_debut_mouvements AND pe.date_perte <= bp.date_fin_controle AND UPPER(COALESCE(pe.motif_perte,
    ''))<>'INVENTAIRE'
GROUP BY bp.produit_id ),
    pertes_inventaire AS (
SELECT bp.produit_id,
    COALESCE(SUM(COALESCE(pe.qte_perte,
    0)),
    0) AS quantite_perdue_inventaire
FROM base_produits bp
    LEFT
JOIN dim_pertes pe ON pe.produit_id=bp.produit_id AND pe.date_perte >= bp.date_debut_mouvements AND pe.date_perte <= bp.date_fin_controle AND UPPER(COALESCE(pe.motif_perte,
    ''))='INVENTAIRE'
GROUP BY bp.produit_id ),
    controle_base AS (
SELECT bp.produit_id,
    bp.code_produit,
    bp.nom_produit,
    bp.nom_categorie,
    bp.date_dernier_inventaire,
    bp.date_debut_mouvements,
    bp.date_fin_controle,
    bp.stock_dernier_inventaire,
    COALESCE(ap.quantite_achetee,
    0) AS quantite_achetee,
    COALESCE(vp.quantite_vendue,
    0) AS quantite_vendue,
    COALESCE(ps.quantite_perdue_signalee,
    0) AS quantite_perdue_signalee,
    COALESCE(pi.quantite_perdue_inventaire,
    0) AS quantite_perdue_inventaire,
    bp.stock_dernier_inventaire+COALESCE(ap.quantite_achetee,
    0)-COALESCE(vp.quantite_vendue,
    0)-COALESCE(ps.quantite_perdue_signalee,
    0) AS stock_theorique_brut,
    bp.stock_actuel
FROM base_produits bp
    LEFT
JOIN achats_periode ap ON ap.produit_id=bp.produit_id
    LEFT
JOIN ventes_periode vp ON vp.produit_id=bp.produit_id
    LEFT
JOIN pertes_signalees ps ON ps.produit_id=bp.produit_id
    LEFT
JOIN pertes_inventaire pi ON pi.produit_id=bp.produit_id ),
    controle AS (
SELECT *,
    GREATEST(stock_theorique_brut,
    0) AS stock_theorique_attendu,
    ABS(LEAST(stock_theorique_brut,
    0)) AS vente_excedentaire
FROM controle_base )
SELECT *,
    CASE WHEN stock_theorique_brut<0 THEN stock_theorique_brut ELSE stock_actuel-stock_theorique_attendu END AS ecart_controle,
    CASE WHEN stock_theorique_brut<0 THEN 'MANQUANT' WHEN stock_actuel-stock_theorique_attendu=0 THEN 'CONFORME' WHEN stock_actuel-stock_theorique_attendu>0 THEN 'SURPLUS' ELSE 'MANQUANT' END AS statut_controle
FROM controle;

CREATE OR REPLACE VIEW vue_controle_stock AS
SELECT *
FROM vw_controle_stock;

CREATE OR REPLACE VIEW vw_dashboard_global AS
SELECT (
SELECT COUNT(*)
FROM dim_produits
WHERE actif=TRUE) AS total_produits_actifs,
    (
SELECT COUNT(*)
FROM dim_categories) AS total_categories,
    (
SELECT COALESCE(SUM(montant_ligne),
    0)
FROM dim_lignes_vente) AS chiffre_affaires,
    (
SELECT COALESCE(SUM(total_facture),
    0)
FROM fact_achats) AS total_achats,
    (
SELECT COALESCE(SUM(montant),
    0)
FROM fact_depenses) AS total_depenses,
    (
SELECT COALESCE(SUM(valeur_totale),
    0)
FROM dim_pertes) AS total_pertes,
    (
SELECT COALESCE(SUM(valeur_perte_signalee),
    0)
FROM vw_pertes_detail) AS total_pertes_signalees,
    (
SELECT COALESCE(SUM(valeur_perte_inventaire),
    0)
FROM vw_pertes_detail) AS total_pertes_inventaire,
    (
SELECT COALESCE(SUM(montant_ligne-COALESCE(cout_total,
    0)),
    0)
FROM dim_lignes_vente) AS marge_brute,
    (
SELECT COALESCE(SUM(stock_actuel),
    0)
FROM dim_produits) AS stock_total,
    (
SELECT COALESCE(SUM(valeur_stock_estimee),
    0)
FROM vw_produits_stock) AS valeur_stock,
    (
SELECT COUNT(*)
FROM dim_produits
WHERE COALESCE(stock_actuel,
    0)<=stock_min) AS produits_stock_alerte,
    (
SELECT COUNT(*)
FROM dim_produits
WHERE COALESCE(stock_actuel,
    0)<=0) AS produits_rupture,
    (
SELECT COUNT(*)
FROM fact_inventaire
WHERE COALESCE(cloture,
    FALSE)=FALSE AND ecart<>0) AS inventaires_ouverts_ecart,
    (
SELECT COUNT(*)
FROM vw_controle_stock
WHERE statut_controle='MANQUANT') AS controle_stock_manquants,
    (
SELECT COUNT(*)
FROM vw_controle_stock
WHERE statut_controle='SURPLUS') AS controle_stock_surplus,
    (
SELECT COALESCE(SUM(ABS(ecart_controle)),
    0)
FROM vw_controle_stock) AS controle_stock_ecart_total,
    (
SELECT COALESCE(SUM(vente_excedentaire),
    0)
FROM vw_controle_stock) AS controle_stock_ventes_excedentaires,
    (
SELECT COALESCE(SUM(montant_signe),
    0)
FROM vw_tresorerie) AS solde_tresorerie_mouvements,
    (
SELECT COALESCE(SUM(montant_signe),
    0)
FROM vw_caisse_reelle) AS solde_reel_caisse;

CREATE OR REPLACE VIEW vue_dashboard_global AS
SELECT *
FROM vw_dashboard_global;

-- ============================================================
-- FIN CORRECTION VENTE EXCEDENTAIRE
-- ============================================================
-- ============================================================
-- FIN DU SCRIPT
-- ============================================================
-- ============================================================
-- Nettoyage avant correction : controle prix

    DROP VIEW IF EXISTS vue_controle_prix CASCADE;

    DROP VIEW IF EXISTS vw_controle_prix CASCADE;

-- CONTROLE PRIX ET RENTABILITE PRODUITS
-- ============================================================

CREATE OR REPLACE VIEW vw_controle_prix AS
WITH dernier_achat AS (
SELECT DISTINCT ON (la.produit_id) la.produit_id,
    a.date_achat,
    la.pu_achat_piece,
    la.pu_achat_carton,
    la.qte_par_carton
FROM dim_lignes_achat la
JOIN fact_achats a ON a.achat_id=la.achat_id
ORDER BY la.produit_id,
    a.date_achat DESC,
    la.ligne_achat_id DESC ),
    derniere_vente AS (
SELECT DISTINCT ON (lv.produit_id) lv.produit_id,
    v.date_vente,
    lv.pu_vente,
    lv.cout_unitaire
FROM dim_lignes_vente lv
JOIN fact_ventes v ON v.vente_id=lv.vente_id
ORDER BY lv.produit_id,
    v.date_vente DESC,
    lv.ligne_vente_id DESC )
SELECT p.produit_id,
    p.code_produit,
    p.nom_produit,
    COALESCE(c.nom_categorie,
    'Non classe') AS nom_categorie,
    COALESCE(p.stock_actuel,
    0) AS stock_actuel,
    da.date_achat AS date_dernier_achat,
    COALESCE(da.pu_achat_piece,
    0) AS prix_achat_unitaire_dernier,
    COALESCE(da.pu_achat_carton,
    0) AS prix_achat_carton_dernier,
    COALESCE(da.qte_par_carton,
    p.qte_par_carton,
    1) AS qte_par_carton,
    dv.date_vente AS date_derniere_vente,
    COALESCE(dv.pu_vente,
    0) AS prix_vente_dernier,
    ROUND(COALESCE(dv.pu_vente,
    0)-COALESCE(da.pu_achat_piece,
    dv.cout_unitaire,
    0),
    2) AS marge_unitaire_estimee,
    CASE WHEN COALESCE(dv.pu_vente,
    0)>0 THEN ROUND(((COALESCE(dv.pu_vente,
    0)-COALESCE(da.pu_achat_piece,
    dv.cout_unitaire,
    0))/COALESCE(dv.pu_vente,
    0))*100,
    2) ELSE 0 END AS taux_marge_estime,
    CASE WHEN dv.produit_id IS NULL THEN 'SANS VENTE' WHEN da.produit_id IS NULL THEN 'SANS ACHAT' WHEN COALESCE(dv.pu_vente,
    0)<COALESCE(da.pu_achat_piece,
    0) THEN 'NON RENTABLE' WHEN COALESCE(dv.pu_vente,
    0)=COALESCE(da.pu_achat_piece,
    0) THEN 'A REVOIR' ELSE 'RENTABLE' END AS statut_prix
FROM dim_produits p
    LEFT
JOIN dim_categories c ON c.categorie_id=p.categorie_id
    LEFT
JOIN dernier_achat da ON da.produit_id=p.produit_id
    LEFT
JOIN derniere_vente dv ON dv.produit_id=p.produit_id
WHERE COALESCE(p.actif,
    TRUE)=TRUE;

CREATE OR REPLACE VIEW vue_controle_prix AS
SELECT *
FROM vw_controle_prix;
