-- ============================================================
-- PROJET : GESTION DE SUPERETTE
-- FICHIER : 02_Import_CSV.sql
-- BASE DE DONNEES : PostgreSQL
-- AUTEUR : Girandoux Fandio
-- DESCRIPTION : Import des 13 fichiers CSV.
-- ============================================================
--
-- A exécuter avec psql depuis la racine du projet.
--
-- ORDRE D'IMPORT :
-- Nettoyage → Dimensions → Achats → Ventes
-- → Dépenses / Pertes / Trésorerie / Inventaire
-- → Séquences → Contrôles
--
-- Les commandes \copy restent volontairement sur une seule ligne.
-- ============================================================

-- ============================================================

TRUNCATE TABLE
    dim_lignes_vente,
    dim_lignes_achat,
    dim_pertes,
    fact_inventaire,
    fact_tresorerie,
    fact_depenses,
    fact_ventes,
    fact_achats,
    dim_produits,
    dim_categories,
    dim_acheteurs,
    dim_vendeurs,
    dim_date
RESTART IDENTITY CASCADE;

-- ============================================================
-- 2. IMPORT DES TABLES DIMENSIONS
-- ============================================================

\copy dim_date(date_id,jour,mois,annee,trimestre,nom_mois) FROM 'data/csv/dim_date.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy dim_categories(categorie_id,code_categorie,nom_categorie,description,date_creation) FROM 'data/csv/dim_categories.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy dim_produits(produit_id,code_produit,nom_produit,categorie_id,unite,qte_par_carton,stock_min,actif,date_creation) FROM 'data/csv/dim_produits.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy dim_acheteurs(acheteur_id,nom_acheteur) FROM 'data/csv/dim_acheteurs.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy dim_vendeurs(vendeur_id,nom_vendeur) FROM 'data/csv/dim_vendeurs.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

-- ============================================================
-- 3. IMPORT DES ACHATS
-- ============================================================

\copy fact_achats(achat_id,date_achat,date_id,numero_facture,acheteur_id,frais_enlevement,total_facture) FROM 'data/csv/fact_achats.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy dim_lignes_achat(ligne_achat_id,achat_id,produit_id,qte_cartons,qte_par_carton,quantite_achat,pu_achat_carton,pu_achat_piece,total_achat,date_fabrication,date_peremption) FROM 'data/csv/dim_lignes_achat.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

-- ============================================================
-- 4. IMPORT DES VENTES
-- ============================================================

\copy fact_ventes(vente_id,date_vente,date_id,vendeur_id,total_vente) FROM 'data/csv/fact_ventes.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy dim_lignes_vente(ligne_vente_id,vente_id,produit_id,qte_vente,pu_vente,montant_ligne,cout_unitaire,cout_total) FROM 'data/csv/dim_lignes_vente.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

-- ============================================================
-- 5. IMPORT DES DEPENSES, PERTES, TRESORERIE ET INVENTAIRE
-- ============================================================

\copy fact_depenses(depense_id,date_depense,date_id,categorie_depense,montant,motif,utilisateur) FROM 'data/csv/fact_depenses.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy dim_pertes(perte_id,date_perte,date_id,produit_id,qte_perte,motif_perte,valeur_unitaire,valeur_totale,utilisateur) FROM 'data/csv/dim_pertes.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy fact_tresorerie(mouvement_id,date_mouvement,date_id,type_mouvement,montant,description,utilisateur) FROM 'data/csv/fact_tresorerie.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

\copy fact_inventaire(inventaire_id,date_inventaire,date_id,produit_id,stock_theorique,stock_physique,ecart,valeur_ecart,commentaire,utilisateur) FROM 'data/csv/fact_inventaire.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',', ENCODING 'UTF8');

-- ============================================================
-- 6. SYNCHRONISATION DES SEQUENCES
-- ============================================================

SELECT setval(pg_get_serial_sequence('dim_categories','categorie_id'),COALESCE((SELECT MAX(categorie_id) FROM dim_categories),1),true);
SELECT setval(pg_get_serial_sequence('dim_produits','produit_id'),COALESCE((SELECT MAX(produit_id) FROM dim_produits),1),true);
SELECT setval(pg_get_serial_sequence('dim_acheteurs','acheteur_id'),COALESCE((SELECT MAX(acheteur_id) FROM dim_acheteurs),1),true);
SELECT setval(pg_get_serial_sequence('dim_vendeurs','vendeur_id'),COALESCE((SELECT MAX(vendeur_id) FROM dim_vendeurs),1),true);
SELECT setval(pg_get_serial_sequence('fact_achats','achat_id'),COALESCE((SELECT MAX(achat_id) FROM fact_achats),1),true);
SELECT setval(pg_get_serial_sequence('dim_lignes_achat','ligne_achat_id'),COALESCE((SELECT MAX(ligne_achat_id) FROM dim_lignes_achat),1),true);
SELECT setval(pg_get_serial_sequence('fact_ventes','vente_id'),COALESCE((SELECT MAX(vente_id) FROM fact_ventes),1),true);
SELECT setval(pg_get_serial_sequence('dim_lignes_vente','ligne_vente_id'),COALESCE((SELECT MAX(ligne_vente_id) FROM dim_lignes_vente),1),true);
SELECT setval(pg_get_serial_sequence('fact_depenses','depense_id'),COALESCE((SELECT MAX(depense_id) FROM fact_depenses),1),true);
SELECT setval(pg_get_serial_sequence('dim_pertes','perte_id'),COALESCE((SELECT MAX(perte_id) FROM dim_pertes),1),true);
SELECT setval(pg_get_serial_sequence('fact_tresorerie','mouvement_id'),COALESCE((SELECT MAX(mouvement_id) FROM fact_tresorerie),1),true);
SELECT setval(pg_get_serial_sequence('fact_inventaire','inventaire_id'),COALESCE((SELECT MAX(inventaire_id) FROM fact_inventaire),1),true);

-- ============================================================
-- 7. CONTROLE RAPIDE APRES IMPORT
-- ============================================================

SELECT 'dim_date' AS table_name,COUNT(*) AS lignes FROM dim_date
UNION ALL SELECT 'dim_categories',COUNT(*) FROM dim_categories
UNION ALL SELECT 'dim_produits',COUNT(*) FROM dim_produits
UNION ALL SELECT 'dim_acheteurs',COUNT(*) FROM dim_acheteurs
UNION ALL SELECT 'dim_vendeurs',COUNT(*) FROM dim_vendeurs
UNION ALL SELECT 'fact_achats',COUNT(*) FROM fact_achats
UNION ALL SELECT 'dim_lignes_achat',COUNT(*) FROM dim_lignes_achat
UNION ALL SELECT 'fact_ventes',COUNT(*) FROM fact_ventes
UNION ALL SELECT 'dim_lignes_vente',COUNT(*) FROM dim_lignes_vente
UNION ALL SELECT 'fact_depenses',COUNT(*) FROM fact_depenses
UNION ALL SELECT 'dim_pertes',COUNT(*) FROM dim_pertes
UNION ALL SELECT 'fact_tresorerie',COUNT(*) FROM fact_tresorerie
UNION ALL SELECT 'fact_inventaire',COUNT(*) FROM fact_inventaire
ORDER BY table_name;

-- ============================================================
-- FIN DU SCRIPT
-- ============================================================
