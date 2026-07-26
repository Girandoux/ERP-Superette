-- ============================================================
-- PROJET : GESTION DE SUPERETTE
-- FICHIER : 05_Functions.sql
-- BASE DE DONNEES : PostgreSQL
-- AUTEUR : Girandoux Fandio
-- DESCRIPTION : Fonctions PostgreSQL pour calculs automatiques,
-- stock, achats, ventes, pertes, inventaire et dashboard.
-- ============================================================

-- ============================================================
-- 1. FONCTIONS UTILITAIRES STOCK ET COUT
-- ============================================================

-- ------------------------------------------------------------
-- Fonction : fn_get_stock_produit
-- Rôle     : Retourner le stock actuel d'un produit.
-- Flux     :
--   1. Entrée     : Identifiant du produit.
--   2. Calcul     : Lecture du stock actuel.
--   3. Validation : Gestion d'une valeur absente avec COALESCE.
--   4. Retour     : Stock disponible sous forme d'entier.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_get_stock_produit(p_produit_id INTEGER)
RETURNS INTEGER AS $$
DECLARE v_stock INTEGER;
BEGIN
    SELECT COALESCE(stock_actuel,0) INTO v_stock FROM dim_produits WHERE produit_id = p_produit_id;
    RETURN COALESCE(v_stock,0);
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_get_dernier_cout_produit
-- Rôle     : Retourner le dernier coût d'achat unitaire connu.
-- Flux     :
--   1. Entrée     : Identifiant du produit.
--   2. Calcul     : Recherche de la ligne d'achat la plus récente.
--   3. Validation : Retour de zéro lorsqu'aucun coût n'est disponible.
--   4. Retour     : Dernier prix d'achat unitaire.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_get_dernier_cout_produit(p_produit_id INTEGER)
RETURNS NUMERIC(12,2) AS $$
DECLARE v_cout NUMERIC(12,2);
BEGIN
    SELECT pu_achat_piece INTO v_cout FROM dim_lignes_achat
    WHERE produit_id = p_produit_id
    ORDER BY ligne_achat_id DESC
    LIMIT 1;
    RETURN COALESCE(v_cout,0);
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_get_cout_moyen_produit
-- Rôle     : Calculer le coût moyen d'achat d'un produit.
-- Flux     :
--   1. Entrée     : Identifiant du produit.
--   2. Calcul     : Moyenne des prix unitaires d'achat enregistrés.
--   3. Validation : Gestion des résultats absents avec COALESCE.
--   4. Retour     : Coût moyen unitaire.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_get_cout_moyen_produit(p_produit_id INTEGER)
RETURNS NUMERIC(12,2) AS $$
DECLARE v_cout NUMERIC(12,2);
BEGIN
    SELECT AVG(pu_achat_piece) INTO v_cout FROM dim_lignes_achat WHERE produit_id = p_produit_id;
    RETURN COALESCE(v_cout,0);
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 2. FONCTIONS ACHATS
-- ============================================================

-- ------------------------------------------------------------
-- Fonction : fn_calcul_ligne_achat
-- Rôle     : Calculer automatiquement les valeurs d'une ligne d'achat.
-- Flux     :
--   1. Entrée     : Nouvelle ligne d'achat reçue par le trigger.
--   2. Calcul     : Quantité achetée, prix unitaire par pièce et total.
--   3. Validation : Normalisation des valeurs nulles avant calcul.
--   4. Retour     : Ligne NEW complétée.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_calcul_ligne_achat()
RETURNS TRIGGER AS $$
BEGIN
    NEW.quantite_achat := ROUND(NEW.qte_cartons * NEW.qte_par_carton);
    NEW.pu_achat_piece := ROUND(NEW.pu_achat_carton / NEW.qte_par_carton,2);
    NEW.total_achat := ROUND(NEW.qte_cartons * NEW.pu_achat_carton,2);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_update_total_achat
-- Rôle     : Recalculer le total d'une facture d'achat.
-- Flux     :
--   1. Entrée     : Identifiant d'achat issu de la ligne concernée.
--   2. Calcul     : Somme des lignes et prise en compte des frais.
--   3. Validation : Gestion des montants absents avec COALESCE.
--   4. Retour     : Entête d'achat mise à jour et ligne du trigger retournée.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_update_total_achat()
RETURNS TRIGGER AS $$
DECLARE v_achat_id INTEGER;
BEGIN
    v_achat_id := COALESCE(NEW.achat_id,OLD.achat_id);
    UPDATE fact_achats fa
    SET total_facture = COALESCE((SELECT SUM(total_achat) FROM dim_lignes_achat WHERE achat_id = v_achat_id),0) + COALESCE(fa.frais_enlevement,0)
    WHERE fa.achat_id = v_achat_id;
    RETURN COALESCE(NEW,OLD);
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_stock_apres_achat
-- Rôle     : Mettre à jour le stock après une opération d'achat.
-- Flux     :
--   1. Entrée     : Ligne d'achat insérée, modifiée ou supprimée.
--   2. Calcul     : Ajout, correction ou retrait de la quantité achetée.
--   3. Validation : Traitement adapté à TG_OP.
--   4. Retour     : Stock actualisé et ligne du trigger retournée.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_stock_apres_achat()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE dim_produits SET stock_actuel = stock_actuel + NEW.quantite_achat WHERE produit_id = NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE dim_produits SET stock_actuel = stock_actuel - OLD.quantite_achat WHERE produit_id = OLD.produit_id;
        UPDATE dim_produits SET stock_actuel = stock_actuel + NEW.quantite_achat WHERE produit_id = NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE dim_produits SET stock_actuel = stock_actuel - OLD.quantite_achat WHERE produit_id = OLD.produit_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 3. FONCTIONS VENTES
-- ============================================================

-- ------------------------------------------------------------
-- Fonction : fn_calcul_ligne_vente
-- Rôle     : Calculer les montants d'une ligne de vente.
-- Flux     :
--   1. Entrée     : Nouvelle ligne de vente.
--   2. Calcul     : Montant vendu, coût unitaire et coût total.
--   3. Validation : Normalisation des valeurs nulles avant calcul.
--   4. Retour     : Ligne NEW complétée.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_calcul_ligne_vente()
RETURNS TRIGGER AS $$
BEGIN
    NEW.montant_ligne := ROUND(NEW.qte_vente * NEW.pu_vente,2);
    IF NEW.cout_unitaire IS NULL THEN
        NEW.cout_unitaire := fn_get_cout_moyen_produit(NEW.produit_id);
    END IF;
    NEW.cout_total := ROUND(NEW.qte_vente * COALESCE(NEW.cout_unitaire,0),2);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_verifier_stock_vente
-- Rôle     : Vérifier que le stock permet l'enregistrement d'une vente.
-- Flux     :
--   1. Entrée     : Produit et quantité demandée.
--   2. Calcul     : Comparaison entre quantité vendue et stock disponible.
--   3. Validation : Blocage lorsque le stock est insuffisant.
--   4. Retour     : Ligne NEW autorisée ou exception métier.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_verifier_stock_vente()
RETURNS TRIGGER AS $$
DECLARE v_stock INTEGER;
BEGIN
    SELECT stock_actuel INTO v_stock FROM dim_produits WHERE produit_id = NEW.produit_id;
    IF v_stock IS NULL THEN
        RAISE EXCEPTION 'Produit inexistant : %', NEW.produit_id;
    END IF;
    IF TG_OP = 'INSERT' AND v_stock < NEW.qte_vente THEN
        RAISE EXCEPTION 'Stock insuffisant pour le produit %. Stock disponible: %, quantite demandee: %', NEW.produit_id,v_stock,NEW.qte_vente;
    END IF;
    IF TG_OP = 'UPDATE' THEN
        IF OLD.produit_id = NEW.produit_id AND (v_stock + OLD.qte_vente) < NEW.qte_vente THEN
            RAISE EXCEPTION 'Stock insuffisant pour modifier la vente du produit %', NEW.produit_id;
        ELSIF OLD.produit_id <> NEW.produit_id AND v_stock < NEW.qte_vente THEN
            RAISE EXCEPTION 'Stock insuffisant pour le nouveau produit %', NEW.produit_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_stock_apres_vente
-- Rôle     : Mettre à jour le stock après une opération de vente.
-- Flux     :
--   1. Entrée     : Ligne de vente insérée, modifiée ou supprimée.
--   2. Calcul     : Déduction, correction ou restitution de la quantité vendue.
--   3. Validation : Traitement adapté à TG_OP.
--   4. Retour     : Stock actualisé et ligne du trigger retournée.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_stock_apres_vente()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE dim_produits SET stock_actuel = stock_actuel - NEW.qte_vente WHERE produit_id = NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE dim_produits SET stock_actuel = stock_actuel + OLD.qte_vente WHERE produit_id = OLD.produit_id;
        UPDATE dim_produits SET stock_actuel = stock_actuel - NEW.qte_vente WHERE produit_id = NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE dim_produits SET stock_actuel = stock_actuel + OLD.qte_vente WHERE produit_id = OLD.produit_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_update_total_vente
-- Rôle     : Recalculer le total d'une vente.
-- Flux     :
--   1. Entrée     : Identifiant de vente issu de la ligne concernée.
--   2. Calcul     : Somme des montants des lignes de vente.
--   3. Validation : Gestion d'une vente sans ligne avec COALESCE.
--   4. Retour     : Entête de vente mise à jour et ligne du trigger retournée.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_update_total_vente()
RETURNS TRIGGER AS $$
DECLARE v_vente_id INTEGER;
BEGIN
    v_vente_id := COALESCE(NEW.vente_id,OLD.vente_id);
    UPDATE fact_ventes
    SET total_vente = COALESCE((SELECT SUM(montant_ligne) FROM dim_lignes_vente WHERE vente_id = v_vente_id),0)
    WHERE vente_id = v_vente_id;
    RETURN COALESCE(NEW,OLD);
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 4. FONCTIONS PERTES
-- ============================================================

-- ------------------------------------------------------------
-- Fonction : fn_perte_calcul_stock
-- Rôle     : Calculer la valeur d'une perte et ajuster le stock.
-- Flux     :
--   1. Entrée     : Produit, quantité perdue et informations de perte.
--   2. Calcul     : Valeur unitaire, valeur totale et diminution du stock.
--   3. Validation : Contrôle des valeurs nécessaires au traitement.
--   4. Retour     : Perte calculée et stock actualisé.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_perte_calcul_stock()
RETURNS TRIGGER AS $$
DECLARE v_stock INTEGER;
BEGIN
    IF TG_OP IN ('INSERT','UPDATE') THEN
        NEW.valeur_totale := ROUND(NEW.qte_perte * NEW.valeur_unitaire,2);
    END IF;
    IF TG_OP = 'INSERT' THEN
        SELECT stock_actuel INTO v_stock FROM dim_produits WHERE produit_id = NEW.produit_id;
        IF v_stock < NEW.qte_perte THEN
            RAISE EXCEPTION 'Stock insuffisant pour perte du produit %', NEW.produit_id;
        END IF;
        UPDATE dim_produits SET stock_actuel = stock_actuel - NEW.qte_perte WHERE produit_id = NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE dim_produits SET stock_actuel = stock_actuel + OLD.qte_perte WHERE produit_id = OLD.produit_id;
        SELECT stock_actuel INTO v_stock FROM dim_produits WHERE produit_id = NEW.produit_id;
        IF v_stock < NEW.qte_perte THEN
            RAISE EXCEPTION 'Stock insuffisant pour modifier la perte du produit %', NEW.produit_id;
        END IF;
        UPDATE dim_produits SET stock_actuel = stock_actuel - NEW.qte_perte WHERE produit_id = NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE dim_produits SET stock_actuel = stock_actuel + OLD.qte_perte WHERE produit_id = OLD.produit_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 5. FONCTIONS INVENTAIRE
-- ============================================================

-- ------------------------------------------------------------
-- Fonction : fn_calcul_inventaire
-- Rôle     : Calculer les écarts d'un inventaire physique.
-- Flux     :
--   1. Entrée     : Stock théorique et stock physique.
--   2. Calcul     : Écart de quantité et valorisation de cet écart.
--   3. Validation : Utilisation du coût disponible pour le produit.
--   4. Retour     : Ligne d'inventaire complétée.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_calcul_inventaire()
RETURNS TRIGGER AS $$
DECLARE v_stock INTEGER; v_cout NUMERIC(12,2);
BEGIN
    v_stock := fn_get_stock_produit(NEW.produit_id);
    v_cout := fn_get_cout_moyen_produit(NEW.produit_id);
    NEW.stock_theorique := COALESCE(v_stock,0);
    NEW.ecart := NEW.stock_physique - NEW.stock_theorique;
    NEW.valeur_ecart := ROUND(NEW.ecart * COALESCE(v_cout,0),2);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- 6. FONCTIONS DASHBOARD ET RAPPORTS
-- ============================================================

-- ------------------------------------------------------------
-- Fonction : fn_benefice_brut
-- Rôle     : Calculer le bénéfice brut sur une période.
-- Flux     :
--   1. Entrée     : Date de début et date de fin.
--   2. Calcul     : Chiffre d'affaires diminué du coût des ventes.
--   3. Validation : Gestion des agrégats vides avec COALESCE.
--   4. Retour     : Montant du bénéfice brut.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_benefice_brut()
RETURNS NUMERIC(12,2) AS $$
DECLARE v_benefice NUMERIC(12,2);
BEGIN
    SELECT SUM(montant_ligne - COALESCE(cout_total,0)) INTO v_benefice FROM dim_lignes_vente;
    RETURN COALESCE(v_benefice,0);
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_total_depenses
-- Rôle     : Calculer le total des dépenses sur une période.
-- Flux     :
--   1. Entrée     : Date de début et date de fin.
--   2. Calcul     : Somme des dépenses de la période.
--   3. Validation : Gestion des agrégats vides avec COALESCE.
--   4. Retour     : Montant total des dépenses.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_total_depenses()
RETURNS NUMERIC(12,2) AS $$
DECLARE v_total NUMERIC(12,2);
BEGIN
    SELECT SUM(montant) INTO v_total FROM fact_depenses;
    RETURN COALESCE(v_total,0);
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_total_pertes
-- Rôle     : Calculer la valeur totale des pertes sur une période.
-- Flux     :
--   1. Entrée     : Date de début et date de fin.
--   2. Calcul     : Somme des valeurs totales de perte.
--   3. Validation : Gestion des agrégats vides avec COALESCE.
--   4. Retour     : Montant total des pertes.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_total_pertes()
RETURNS NUMERIC(12,2) AS $$
DECLARE v_total NUMERIC(12,2);
BEGIN
    SELECT SUM(valeur_totale) INTO v_total FROM dim_pertes;
    RETURN COALESCE(v_total,0);
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_benefice_net
-- Rôle     : Calculer le bénéfice net sur une période.
-- Flux     :
--   1. Entrée     : Date de début et date de fin.
--   2. Calcul     : Bénéfice brut diminué des dépenses et des pertes.
--   3. Validation : Réutilisation des fonctions financières existantes.
--   4. Retour     : Montant du bénéfice net.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_benefice_net()
RETURNS NUMERIC(12,2) AS $$
BEGIN
    RETURN fn_benefice_brut() - fn_total_depenses() - fn_total_pertes();
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_valeur_stock
-- Rôle     : Calculer la valeur financière du stock disponible.
-- Flux     :
--   1. Entrée     : Aucun paramètre.
--   2. Calcul     : Stock actuel multiplié par le coût de référence.
--   3. Validation : Gestion des coûts et quantités absents.
--   4. Retour     : Valeur totale du stock.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_valeur_stock()
RETURNS NUMERIC(12,2) AS $$
DECLARE v_valeur NUMERIC(12,2);
BEGIN
    SELECT SUM(COALESCE(p.stock_actuel,0) * COALESCE(c.pu_achat_piece,0)) INTO v_valeur
    FROM dim_produits p
    LEFT JOIN (SELECT DISTINCT ON (produit_id) produit_id,pu_achat_piece FROM dim_lignes_achat ORDER BY produit_id,ligne_achat_id DESC) c ON c.produit_id = p.produit_id;
    RETURN COALESCE(v_valeur,0);
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- Fonction : fn_solde_tresorerie
-- Rôle     : Calculer le solde de trésorerie.
-- Flux     :
--   1. Entrée     : Aucun paramètre.
--   2. Calcul     : Agrégation des mouvements selon leur type.
--   3. Validation : Gestion d'une trésorerie sans mouvement.
--   4. Retour     : Solde courant de trésorerie.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_solde_tresorerie()
RETURNS NUMERIC(12,2) AS $$
DECLARE v_solde NUMERIC(12,2);
BEGIN
    SELECT SUM(CASE WHEN type_mouvement IN ('Apport','Depot_Banque','Correction') THEN montant WHEN type_mouvement IN ('Retrait','Retrait_Banque') THEN -montant ELSE 0 END) INTO v_solde
    FROM fact_tresorerie;
    RETURN COALESCE(v_solde,0);
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- FIN DU SCRIPT
-- ============================================================
