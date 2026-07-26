-- ============================================================
-- PROJET : GESTION DE SUPERETTE
-- FICHIER : 07_Indexes.sql
-- BASE DE DONNEES : PostgreSQL
-- AUTEUR : Girandoux Fandio
-- DESCRIPTION : Creation des indexes pour optimiser les recherches,
-- les jointures, les rapports, le dashboard et Power BI.
-- ============================================================

-- ============================================================
-- 1. INDEXES SUR LES TABLES DE DIMENSION
-- ============================================================

-- ------------------------------------------------------------
-- Index    : idx_dim_produits_categorie
-- Table    : dim_produits
-- Colonnes : categorie_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_produits_categorie
    ON dim_produits (categorie_id);

-- ------------------------------------------------------------
-- Index    : idx_dim_produits_code
-- Table    : dim_produits
-- Colonnes : code_produit
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_produits_code
    ON dim_produits (code_produit);

-- ------------------------------------------------------------
-- Index    : idx_dim_produits_nom
-- Table    : dim_produits
-- Colonnes : nom_produit
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_produits_nom
    ON dim_produits (nom_produit);

-- ------------------------------------------------------------
-- Index    : idx_dim_produits_actif
-- Table    : dim_produits
-- Colonnes : actif
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_produits_actif
    ON dim_produits (actif);

-- ------------------------------------------------------------
-- Index    : idx_dim_categories_code
-- Table    : dim_categories
-- Colonnes : code_categorie
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_categories_code
    ON dim_categories (code_categorie);

-- ------------------------------------------------------------
-- Index    : idx_dim_categories_nom
-- Table    : dim_categories
-- Colonnes : nom_categorie
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_categories_nom
    ON dim_categories (nom_categorie);

-- ------------------------------------------------------------
-- Index    : idx_dim_date_annee
-- Table    : dim_date
-- Colonnes : annee
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_date_annee
    ON dim_date (annee);

-- ------------------------------------------------------------
-- Index    : idx_dim_date_mois
-- Table    : dim_date
-- Colonnes : mois
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_date_mois
    ON dim_date (mois);

-- ------------------------------------------------------------
-- Index    : idx_dim_date_trimestre
-- Table    : dim_date
-- Colonnes : trimestre
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_date_trimestre
    ON dim_date (trimestre);

-- ------------------------------------------------------------
-- Index    : idx_dim_date_annee_mois
-- Table    : dim_date
-- Colonnes : annee, mois
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_date_annee_mois
    ON dim_date (annee, mois);

-- ============================================================
-- 2. INDEXES SUR LES ACHATS
-- ============================================================

-- ------------------------------------------------------------
-- Index    : idx_fact_achats_date_id
-- Table    : fact_achats
-- Colonnes : date_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_achats_date_id
    ON fact_achats (date_id);

-- ------------------------------------------------------------
-- Index    : idx_fact_achats_date_achat
-- Table    : fact_achats
-- Colonnes : date_achat
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_achats_date_achat
    ON fact_achats (date_achat);

-- ------------------------------------------------------------
-- Index    : idx_fact_achats_acheteur
-- Table    : fact_achats
-- Colonnes : acheteur_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_achats_acheteur
    ON fact_achats (acheteur_id);

-- ------------------------------------------------------------
-- Index    : idx_fact_achats_numero_facture
-- Table    : fact_achats
-- Colonnes : numero_facture
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_achats_numero_facture
    ON fact_achats (numero_facture);

-- ------------------------------------------------------------
-- Index    : idx_lignes_achat_achat
-- Table    : dim_lignes_achat
-- Colonnes : achat_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_lignes_achat_achat
    ON dim_lignes_achat (achat_id);

-- ------------------------------------------------------------
-- Index    : idx_lignes_achat_produit
-- Table    : dim_lignes_achat
-- Colonnes : produit_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_lignes_achat_produit
    ON dim_lignes_achat (produit_id);

-- ------------------------------------------------------------
-- Index    : idx_lignes_achat_peremption
-- Table    : dim_lignes_achat
-- Colonnes : date_peremption
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_lignes_achat_peremption
    ON dim_lignes_achat (date_peremption);

-- ------------------------------------------------------------
-- Index    : idx_lignes_achat_produit_achat
-- Table    : dim_lignes_achat
-- Colonnes : produit_id, achat_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_lignes_achat_produit_achat
    ON dim_lignes_achat (produit_id, achat_id);

-- ============================================================
-- 3. INDEXES SUR LES VENTES
-- ============================================================

-- ------------------------------------------------------------
-- Index    : idx_fact_ventes_date_id
-- Table    : fact_ventes
-- Colonnes : date_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_ventes_date_id
    ON fact_ventes (date_id);

-- ------------------------------------------------------------
-- Index    : idx_fact_ventes_date_vente
-- Table    : fact_ventes
-- Colonnes : date_vente
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_ventes_date_vente
    ON fact_ventes (date_vente);

-- ------------------------------------------------------------
-- Index    : idx_fact_ventes_vendeur
-- Table    : fact_ventes
-- Colonnes : vendeur_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_ventes_vendeur
    ON fact_ventes (vendeur_id);

-- ------------------------------------------------------------
-- Index    : idx_lignes_vente_vente
-- Table    : dim_lignes_vente
-- Colonnes : vente_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_lignes_vente_vente
    ON dim_lignes_vente (vente_id);

-- ------------------------------------------------------------
-- Index    : idx_lignes_vente_produit
-- Table    : dim_lignes_vente
-- Colonnes : produit_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_lignes_vente_produit
    ON dim_lignes_vente (produit_id);

-- ------------------------------------------------------------
-- Index    : idx_lignes_vente_produit_vente
-- Table    : dim_lignes_vente
-- Colonnes : produit_id, vente_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_lignes_vente_produit_vente
    ON dim_lignes_vente (produit_id, vente_id);

-- ============================================================
-- 4. INDEXES SUR LES DEPENSES
-- ============================================================

-- ------------------------------------------------------------
-- Index    : idx_fact_depenses_date_id
-- Table    : fact_depenses
-- Colonnes : date_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_depenses_date_id
    ON fact_depenses (date_id);

-- ------------------------------------------------------------
-- Index    : idx_fact_depenses_date_depense
-- Table    : fact_depenses
-- Colonnes : date_depense
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_depenses_date_depense
    ON fact_depenses (date_depense);

-- ------------------------------------------------------------
-- Index    : idx_fact_depenses_categorie
-- Table    : fact_depenses
-- Colonnes : categorie_depense
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_depenses_categorie
    ON fact_depenses (categorie_depense);

-- ------------------------------------------------------------
-- Index    : idx_fact_depenses_utilisateur
-- Table    : fact_depenses
-- Colonnes : utilisateur
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_depenses_utilisateur
    ON fact_depenses (utilisateur);

-- ============================================================
-- 5. INDEXES SUR LES PERTES
-- ============================================================

-- ------------------------------------------------------------
-- Index    : idx_dim_pertes_date_id
-- Table    : dim_pertes
-- Colonnes : date_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_pertes_date_id
    ON dim_pertes (date_id);

-- ------------------------------------------------------------
-- Index    : idx_dim_pertes_date_perte
-- Table    : dim_pertes
-- Colonnes : date_perte
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_pertes_date_perte
    ON dim_pertes (date_perte);

-- ------------------------------------------------------------
-- Index    : idx_dim_pertes_produit
-- Table    : dim_pertes
-- Colonnes : produit_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_pertes_produit
    ON dim_pertes (produit_id);

-- ------------------------------------------------------------
-- Index    : idx_dim_pertes_motif
-- Table    : dim_pertes
-- Colonnes : motif_perte
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_pertes_motif
    ON dim_pertes (motif_perte);

-- ------------------------------------------------------------
-- Index    : idx_dim_pertes_date_produit
-- Table    : dim_pertes
-- Colonnes : date_id, produit_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_dim_pertes_date_produit
    ON dim_pertes (date_id, produit_id);

-- ============================================================
-- 6. INDEXES SUR LA TRESORERIE
-- ============================================================

-- ------------------------------------------------------------
-- Index    : idx_fact_tresorerie_date_id
-- Table    : fact_tresorerie
-- Colonnes : date_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_tresorerie_date_id
    ON fact_tresorerie (date_id);

-- ------------------------------------------------------------
-- Index    : idx_fact_tresorerie_date_mouvement
-- Table    : fact_tresorerie
-- Colonnes : date_mouvement
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_tresorerie_date_mouvement
    ON fact_tresorerie (date_mouvement);

-- ------------------------------------------------------------
-- Index    : idx_fact_tresorerie_type
-- Table    : fact_tresorerie
-- Colonnes : type_mouvement
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_tresorerie_type
    ON fact_tresorerie (type_mouvement);

-- ------------------------------------------------------------
-- Index    : idx_fact_tresorerie_utilisateur
-- Table    : fact_tresorerie
-- Colonnes : utilisateur
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_tresorerie_utilisateur
    ON fact_tresorerie (utilisateur);

-- ------------------------------------------------------------
-- Index    : idx_fact_tresorerie_date_type
-- Table    : fact_tresorerie
-- Colonnes : date_id, type_mouvement
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_tresorerie_date_type
    ON fact_tresorerie (date_id, type_mouvement);

-- ============================================================
-- 7. INDEXES SUR L'INVENTAIRE
-- ============================================================

-- ------------------------------------------------------------
-- Index    : idx_fact_inventaire_date_id
-- Table    : fact_inventaire
-- Colonnes : date_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_inventaire_date_id
    ON fact_inventaire (date_id);

-- ------------------------------------------------------------
-- Index    : idx_fact_inventaire_date_inventaire
-- Table    : fact_inventaire
-- Colonnes : date_inventaire
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_inventaire_date_inventaire
    ON fact_inventaire (date_inventaire);

-- ------------------------------------------------------------
-- Index    : idx_fact_inventaire_produit
-- Table    : fact_inventaire
-- Colonnes : produit_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_inventaire_produit
    ON fact_inventaire (produit_id);

-- ------------------------------------------------------------
-- Index    : idx_fact_inventaire_utilisateur
-- Table    : fact_inventaire
-- Colonnes : utilisateur
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_inventaire_utilisateur
    ON fact_inventaire (utilisateur);

-- ------------------------------------------------------------
-- Index    : idx_fact_inventaire_date_produit
-- Table    : fact_inventaire
-- Colonnes : date_id, produit_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_inventaire_date_produit
    ON fact_inventaire (date_id, produit_id);

-- ------------------------------------------------------------
-- Index    : idx_fact_inventaire_cloture
-- Table    : fact_inventaire
-- Colonnes : cloture
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_fact_inventaire_cloture
    ON fact_inventaire (cloture);

-- ============================================================
-- 8. INDEXES COMPOSITES POUR RAPPORTS ET POWER BI
-- ============================================================

-- ------------------------------------------------------------
-- Index    : idx_achats_date_acheteur
-- Table    : fact_achats
-- Colonnes : date_id, acheteur_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_achats_date_acheteur
    ON fact_achats (date_id, acheteur_id);

-- ------------------------------------------------------------
-- Index    : idx_ventes_date_vendeur
-- Table    : fact_ventes
-- Colonnes : date_id, vendeur_id
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_ventes_date_vendeur
    ON fact_ventes (date_id, vendeur_id);

-- ------------------------------------------------------------
-- Index    : idx_depenses_date_categorie
-- Table    : fact_depenses
-- Colonnes : date_id, categorie_depense
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_depenses_date_categorie
    ON fact_depenses (date_id, categorie_depense);

-- ------------------------------------------------------------
-- Index    : idx_produits_categorie_actif
-- Table    : dim_produits
-- Colonnes : categorie_id, actif
-- Objectif : accélérer les filtres, recherches et jointures
--            utilisant cette clé d'accès.
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_produits_categorie_actif
    ON dim_produits (categorie_id, actif);

-- ============================================================
-- FIN DU SCRIPT
-- ============================================================
