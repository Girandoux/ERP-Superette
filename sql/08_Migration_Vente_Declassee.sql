-- ============================================================
-- PROJET : GESTION DE SUPERETTE
-- FICHIER : 08_Migration_Vente_Declassee.sql
-- BASE DE DONNEES : PostgreSQL
-- AUTEUR : Girandoux Fandio
-- DESCRIPTION : Gestion du type de vente pour les produits
-- normaux, déclassés, promotionnels ou donnés.
-- ============================================================
--
-- ORDRE DE LA MIGRATION :
-- 1. Ajouter la colonne type_vente si elle n'existe pas
-- 2. Remplacer la contrainte de validation
-- 3. Normaliser les anciennes lignes sans type de vente
-- 4. Créer l'index utilisé par les filtres et rapports
--
-- La logique métier et les valeurs autorisées restent inchangées.
-- ============================================================

-- ============================================================
-- 1. AJOUT DE LA COLONNE TYPE_VENTE
-- ============================================================
ALTER TABLE dim_lignes_vente
ADD COLUMN IF NOT EXISTS type_vente VARCHAR(40) NOT NULL DEFAULT 'Normale';

-- ============================================================
-- 2. REMPLACEMENT DE LA CONTRAINTE DE VALIDATION
-- ============================================================

ALTER TABLE dim_lignes_vente
DROP CONSTRAINT IF EXISTS chk_lignes_vente_type_vente;

ALTER TABLE dim_lignes_vente
ADD CONSTRAINT chk_lignes_vente_type_vente
CHECK (type_vente IN ('Normale','Declassee - produit abime','Promotion','Don'));

-- ============================================================
-- 3. NORMALISATION DES DONNEES EXISTANTES
-- ============================================================

-- Les valeurs nulles ou vides sont ramenées à la valeur par défaut.
UPDATE dim_lignes_vente
SET type_vente='Normale'
WHERE type_vente IS NULL OR TRIM(type_vente)='';

-- ============================================================
-- 4. INDEX POUR LES FILTRES PAR TYPE DE VENTE
-- ============================================================

-- Accélère les analyses par type de vente.
CREATE INDEX IF NOT EXISTS idx_lignes_vente_type
    ON dim_lignes_vente (type_vente);
