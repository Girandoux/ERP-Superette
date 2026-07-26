-- ============================================================
-- PROJET : GESTION DE SUPERETTE
-- FICHIER : 01_Create_Database.sql
-- BASE DE DONNEES : PostgreSQL
-- AUTEUR : Girandoux Fandio
-- DESCRIPTION : Creation des 13 tables principales du projet V1.
-- ============================================================
--
-- ORDRE D'EXECUTION :
-- 1. Suppression des tables existantes
-- 2. Création des dimensions
-- 3. Création des achats et des ventes
-- 4. Création des dépenses, pertes, trésorerie et inventaire
-- 5. Index complémentaires conservés dans le bloc commenté
--
-- Les tables parentes sont créées avant les tables dépendantes.
-- ============================================================

-- ============================================================

DROP TABLE IF EXISTS dim_lignes_vente CASCADE;
DROP TABLE IF EXISTS dim_lignes_achat CASCADE;
DROP TABLE IF EXISTS dim_pertes CASCADE;
DROP TABLE IF EXISTS fact_inventaire CASCADE;
DROP TABLE IF EXISTS fact_tresorerie CASCADE;
DROP TABLE IF EXISTS fact_depenses CASCADE;
DROP TABLE IF EXISTS fact_ventes CASCADE;
DROP TABLE IF EXISTS fact_achats CASCADE;
DROP TABLE IF EXISTS dim_produits CASCADE;
DROP TABLE IF EXISTS dim_categories CASCADE;
DROP TABLE IF EXISTS dim_acheteurs CASCADE;
DROP TABLE IF EXISTS dim_vendeurs CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

-- ============================================================
-- 2. TABLES DIMENSIONS
-- ============================================================

CREATE TABLE dim_date (
    date_id DATE PRIMARY KEY,
    jour INTEGER NOT NULL CHECK (jour BETWEEN 1 AND 31),
    mois INTEGER NOT NULL CHECK (mois BETWEEN 1 AND 12),
    annee INTEGER NOT NULL CHECK (annee >= 2000),
    trimestre VARCHAR(2) NOT NULL CHECK (trimestre IN ('T1','T2','T3','T4')),
    nom_mois VARCHAR(20) NOT NULL
);

CREATE TABLE dim_categories (
    categorie_id SERIAL PRIMARY KEY,
    code_categorie VARCHAR(10) NOT NULL UNIQUE,
    nom_categorie VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    date_creation TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dim_produits (
    produit_id SERIAL PRIMARY KEY,
    code_produit VARCHAR(20) NOT NULL UNIQUE,
    nom_produit VARCHAR(150) NOT NULL UNIQUE,
    categorie_id INTEGER NOT NULL,
    unite VARCHAR(20) NOT NULL,
    qte_par_carton INTEGER NOT NULL CHECK (qte_par_carton > 0),
    stock_min INTEGER NOT NULL DEFAULT 0 CHECK (stock_min >= 0),
    stock_actuel INTEGER NOT NULL DEFAULT 0 CHECK (stock_actuel >= 0),
    actif BOOLEAN NOT NULL DEFAULT TRUE,
    date_creation TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_produit_categorie FOREIGN KEY (categorie_id)
 REFERENCES dim_categories(categorie_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE dim_acheteurs (
    acheteur_id SERIAL PRIMARY KEY,
    nom_acheteur VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE dim_vendeurs (
    vendeur_id SERIAL PRIMARY KEY,
    nom_vendeur VARCHAR(100) NOT NULL UNIQUE
);

-- ============================================================
-- 3. TABLES ACHATS
-- ============================================================

CREATE TABLE fact_achats (
    achat_id SERIAL PRIMARY KEY,
    date_achat DATE NOT NULL,
    date_id DATE NOT NULL,
    numero_facture VARCHAR(50) NOT NULL UNIQUE,
    acheteur_id INTEGER NOT NULL,
    frais_enlevement NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (frais_enlevement >= 0),
    total_facture NUMERIC(12,2) NOT NULL CHECK (total_facture >= 0),
    type_achat VARCHAR(50) NOT NULL DEFAULT 'Achat fournisseur',
    CONSTRAINT fk_achat_date FOREIGN KEY (date_id)
 REFERENCES dim_date(date_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_achat_acheteur FOREIGN KEY (acheteur_id)
 REFERENCES dim_acheteurs(acheteur_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE dim_lignes_achat (
    ligne_achat_id SERIAL PRIMARY KEY,
    achat_id INTEGER NOT NULL,
    produit_id INTEGER NOT NULL,
    qte_cartons NUMERIC(10,2) NOT NULL CHECK (qte_cartons > 0),
    qte_par_carton INTEGER NOT NULL CHECK (qte_par_carton > 0),
    quantite_achat INTEGER NOT NULL CHECK (quantite_achat > 0),
    pu_achat_carton NUMERIC(12,2) NOT NULL CHECK (pu_achat_carton >= 0),
    pu_achat_piece NUMERIC(12,2) NOT NULL CHECK (pu_achat_piece >= 0),
    total_achat NUMERIC(12,2) NOT NULL CHECK (total_achat >= 0),
    date_fabrication DATE,
    date_peremption DATE,
    CONSTRAINT chk_quantite_achat CHECK (quantite_achat = ROUND(qte_cartons * qte_par_carton)),
    CONSTRAINT chk_dates_produit CHECK (date_peremption IS NULL OR date_fabrication IS NULL OR date_peremption >= date_fabrication),
    CONSTRAINT fk_ligne_achat_achat FOREIGN KEY (achat_id)
 REFERENCES fact_achats(achat_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_ligne_achat_produit FOREIGN KEY (produit_id)
 REFERENCES dim_produits(produit_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ============================================================
-- 4. TABLES VENTES
-- ============================================================

CREATE TABLE fact_ventes (
    vente_id SERIAL PRIMARY KEY,
    date_vente DATE NOT NULL,
    date_id DATE NOT NULL,
    vendeur_id INTEGER NOT NULL,
    total_vente NUMERIC(12,2) NOT NULL CHECK (total_vente >= 0),
    CONSTRAINT fk_vente_date FOREIGN KEY (date_id)
 REFERENCES dim_date(date_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_vente_vendeur FOREIGN KEY (vendeur_id)
 REFERENCES dim_vendeurs(vendeur_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE dim_lignes_vente (
    ligne_vente_id SERIAL PRIMARY KEY,
    vente_id INTEGER NOT NULL,
    produit_id INTEGER NOT NULL,
    qte_vente INTEGER NOT NULL CHECK (qte_vente > 0),
    pu_vente NUMERIC(12,2) NOT NULL CHECK (pu_vente >= 0),
    montant_ligne NUMERIC(12,2) NOT NULL CHECK (montant_ligne >= 0),
    cout_unitaire NUMERIC(12,2) CHECK (cout_unitaire >= 0),
    cout_total NUMERIC(12,2) CHECK (cout_total >= 0),
    type_vente VARCHAR(40) NOT NULL DEFAULT 'Normale' CHECK (type_vente IN ('Normale','Declassee - produit abime','Promotion','Don')),
    CONSTRAINT fk_ligne_vente_vente FOREIGN KEY (vente_id)
 REFERENCES fact_ventes(vente_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_ligne_vente_produit FOREIGN KEY (produit_id)
 REFERENCES dim_produits(produit_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

-- ============================================================
-- 5. TABLES FINANCE, PERTES ET INVENTAIRE
-- ============================================================

CREATE TABLE fact_depenses (
    depense_id SERIAL PRIMARY KEY,
    date_depense DATE NOT NULL,
    date_id DATE NOT NULL,
    categorie_depense VARCHAR(50) NOT NULL,
    montant NUMERIC(12,2) NOT NULL CHECK (montant >= 0),
    motif VARCHAR(255) NOT NULL,
    utilisateur VARCHAR(100),
    CONSTRAINT fk_depense_date FOREIGN KEY (date_id)
 REFERENCES dim_date(date_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE dim_pertes (
    perte_id SERIAL PRIMARY KEY,
    date_perte DATE NOT NULL,
    date_id DATE NOT NULL,
    produit_id INTEGER NOT NULL,
    qte_perte INTEGER NOT NULL CHECK (qte_perte > 0),
    motif_perte VARCHAR(50) NOT NULL CHECK (motif_perte IN ('Perime','Casse','Vole','Don','Inventaire','Consommation_Interne')),
    valeur_unitaire NUMERIC(12,2) NOT NULL CHECK (valeur_unitaire >= 0),
    valeur_totale NUMERIC(12,2) NOT NULL CHECK (valeur_totale >= 0),
    utilisateur VARCHAR(100),
    CONSTRAINT fk_perte_date FOREIGN KEY (date_id)
 REFERENCES dim_date(date_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_perte_produit FOREIGN KEY (produit_id)
 REFERENCES dim_produits(produit_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE fact_tresorerie (
    mouvement_id SERIAL PRIMARY KEY,
    date_mouvement DATE NOT NULL,
    date_id DATE NOT NULL,
    type_mouvement VARCHAR(30) NOT NULL CHECK (type_mouvement IN ('Apport','Retrait','Depot_Banque','Retrait_Banque','Correction')),
    montant NUMERIC(12,2) NOT NULL CHECK (montant > 0),
    description VARCHAR(255),
    utilisateur VARCHAR(100),
    CONSTRAINT fk_tresorerie_date FOREIGN KEY (date_id)
 REFERENCES dim_date(date_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

CREATE TABLE fact_inventaire (
    inventaire_id SERIAL PRIMARY KEY,
    date_inventaire DATE NOT NULL,
    date_id DATE NOT NULL,
    produit_id INTEGER NOT NULL,
    stock_theorique INTEGER NOT NULL CHECK (stock_theorique >= 0),
    stock_physique INTEGER NOT NULL CHECK (stock_physique >= 0),
    ecart INTEGER NOT NULL,
    valeur_ecart NUMERIC(12,2),
    commentaire VARCHAR(255),
    utilisateur VARCHAR(100),
    cloture BOOLEAN NOT NULL DEFAULT FALSE,
    date_cloture TIMESTAMP,
    perte_id INTEGER,
    ajustement_stock INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT fk_inventaire_perte FOREIGN KEY (perte_id)
 REFERENCES dim_pertes(perte_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_inventaire_date FOREIGN KEY (date_id)
 REFERENCES dim_date(date_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_inventaire_produit FOREIGN KEY (produit_id)
 REFERENCES dim_produits(produit_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

/*
-- ============================================================
-- 6. INDEXES POUR LES PERFORMANCES
-- ============================================================

CREATE INDEX idx_produits_categorie ON dim_produits(categorie_id);
CREATE INDEX idx_achats_date_id ON fact_achats(date_id);
CREATE INDEX idx_achats_acheteur ON fact_achats(acheteur_id);
CREATE INDEX idx_lignes_achat_achat ON dim_lignes_achat(achat_id);
CREATE INDEX idx_lignes_achat_produit ON dim_lignes_achat(produit_id);
CREATE INDEX idx_ventes_date_id ON fact_ventes(date_id);
CREATE INDEX idx_ventes_vendeur ON fact_ventes(vendeur_id);
CREATE INDEX idx_lignes_vente_vente ON dim_lignes_vente(vente_id);
CREATE INDEX idx_lignes_vente_produit ON dim_lignes_vente(produit_id);
CREATE INDEX idx_lignes_vente_type ON dim_lignes_vente(type_vente);
CREATE INDEX idx_depenses_date_id ON fact_depenses(date_id);
CREATE INDEX idx_pertes_date_id ON dim_pertes(date_id);
CREATE INDEX idx_pertes_produit ON dim_pertes(produit_id);
CREATE INDEX idx_tresorerie_date_id ON fact_tresorerie(date_id);
CREATE INDEX idx_tresorerie_type ON fact_tresorerie(type_mouvement);
CREATE INDEX idx_inventaire_date_id ON fact_inventaire(date_id);
CREATE INDEX idx_inventaire_produit ON fact_inventaire(produit_id);

-- ============================================================
-- 7. INDEXES COMPOSITES POUR ANALYSES
-- ============================================================

CREATE INDEX idx_achat_produit_achat ON dim_lignes_achat(produit_id, achat_id);
CREATE INDEX idx_vente_produit_vente ON dim_lignes_vente(produit_id, vente_id);
CREATE INDEX idx_perte_date_produit ON dim_pertes(date_id, produit_id);
CREATE INDEX idx_inventaire_date_produit ON fact_inventaire(date_id, produit_id);

-- ============================================================
-- FIN DU SCRIPT
-- ============================================================
*/
