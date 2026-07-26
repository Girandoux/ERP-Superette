-- ============================================================
-- PROJET : GESTION DE SUPERETTE
-- FICHIER : 06_Triggers.sql
-- BASE DE DONNEES : PostgreSQL
-- AUTEUR : Girandoux Fandio
-- DESCRIPTION : Triggers pour calculs automatiques, stock,
-- totaux achats, totaux ventes, pertes et inventaire.
-- ============================================================

-- ============================================================
-- 1. AJOUT DE LA COLONNE STOCK_ACTUEL SI ABSENTE
-- ============================================================

ALTER TABLE dim_produits
ADD COLUMN IF NOT EXISTS stock_actuel INTEGER NOT NULL DEFAULT 0 CHECK (stock_actuel >= 0);

-- ============================================================
-- 2. CALCUL AUTOMATIQUE DES LIGNES D'ACHAT
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
    NEW.qte_cartons:=COALESCE(NEW.qte_cartons,0);
    NEW.qte_par_carton:=COALESCE(NEW.qte_par_carton,0);
    NEW.pu_achat_carton:=COALESCE(NEW.pu_achat_carton,0);
    NEW.quantite_achat:=ROUND(NEW.qte_cartons*NEW.qte_par_carton);
    NEW.pu_achat_piece:=CASE WHEN NEW.qte_par_carton>0 THEN ROUND(NEW.pu_achat_carton/NEW.qte_par_carton,2) ELSE 0 END;
    NEW.total_achat:=ROUND(NEW.qte_cartons*NEW.pu_achat_carton,2);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_calcul_ligne_achat ON dim_lignes_achat;
-- ------------------------------------------------------------
-- Trigger   : trg_calcul_ligne_achat
-- Processus : Achats
-- Rôle      : Calcule les quantités, prix unitaires et montants avant enregistrement.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_calcul_ligne_achat
BEFORE INSERT OR UPDATE ON dim_lignes_achat
FOR EACH ROW EXECUTE FUNCTION fn_calcul_ligne_achat();

-- ============================================================
-- 3. MISE A JOUR DU TOTAL DES ACHATS
-- ============================================================

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
    v_achat_id:=COALESCE(NEW.achat_id,OLD.achat_id);
    UPDATE fact_achats fa
    SET total_facture=COALESCE((SELECT SUM(total_achat) FROM dim_lignes_achat WHERE achat_id=v_achat_id),0)+COALESCE(fa.frais_enlevement,0)
    WHERE fa.achat_id=v_achat_id;
    RETURN COALESCE(NEW,OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_total_achat ON dim_lignes_achat;
-- ------------------------------------------------------------
-- Trigger   : trg_update_total_achat
-- Processus : Achats
-- Rôle      : Recalcule le total de la facture après modification des lignes.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_update_total_achat
AFTER INSERT OR UPDATE OR DELETE ON dim_lignes_achat
FOR EACH ROW EXECUTE FUNCTION fn_update_total_achat();

-- ============================================================
-- 4. MISE A JOUR DU STOCK APRES ACHAT
-- ============================================================

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
    IF TG_OP='INSERT' THEN
        UPDATE dim_produits SET stock_actuel=stock_actuel+COALESCE(NEW.quantite_achat,0) WHERE produit_id=NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP='UPDATE' THEN
        UPDATE dim_produits SET stock_actuel=GREATEST(stock_actuel-COALESCE(OLD.quantite_achat,0),0) WHERE produit_id=OLD.produit_id;
        UPDATE dim_produits SET stock_actuel=stock_actuel+COALESCE(NEW.quantite_achat,0) WHERE produit_id=NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP='DELETE' THEN
        UPDATE dim_produits SET stock_actuel=GREATEST(stock_actuel-COALESCE(OLD.quantite_achat,0),0) WHERE produit_id=OLD.produit_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_stock_apres_achat ON dim_lignes_achat;
-- ------------------------------------------------------------
-- Trigger   : trg_stock_apres_achat
-- Processus : Stock / Achats
-- Rôle      : Actualise le stock après insertion, modification ou suppression.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_stock_apres_achat
AFTER INSERT OR UPDATE OR DELETE ON dim_lignes_achat
FOR EACH ROW EXECUTE FUNCTION fn_stock_apres_achat();

-- ============================================================
-- 5. CALCUL AUTOMATIQUE DES LIGNES DE VENTE
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
    NEW.qte_vente:=COALESCE(NEW.qte_vente,0);
    NEW.pu_vente:=COALESCE(NEW.pu_vente,0);
    NEW.montant_ligne:=ROUND(NEW.qte_vente*NEW.pu_vente,2);
    IF NEW.cout_unitaire IS NULL THEN
        SELECT COALESCE(la.pu_achat_piece,0) INTO NEW.cout_unitaire
        FROM dim_lignes_achat la
        JOIN fact_achats a ON a.achat_id=la.achat_id
        JOIN fact_ventes v ON v.vente_id=NEW.vente_id
        WHERE la.produit_id=NEW.produit_id AND a.date_achat<=v.date_vente
        ORDER BY a.date_achat DESC,la.ligne_achat_id DESC
        LIMIT 1;
        NEW.cout_unitaire:=COALESCE(NEW.cout_unitaire,0);
    END IF;
    NEW.cout_total:=ROUND(NEW.qte_vente*COALESCE(NEW.cout_unitaire,0),2);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_calcul_ligne_vente ON dim_lignes_vente;
-- ------------------------------------------------------------
-- Trigger   : trg_calcul_ligne_vente
-- Processus : Ventes
-- Rôle      : Calcule le montant et les coûts avant enregistrement.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_calcul_ligne_vente
BEFORE INSERT OR UPDATE ON dim_lignes_vente
FOR EACH ROW EXECUTE FUNCTION fn_calcul_ligne_vente();

-- ============================================================
-- 6. CONTROLE DU STOCK AVANT VENTE
-- ============================================================

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
    SELECT stock_actuel INTO v_stock FROM dim_produits WHERE produit_id=NEW.produit_id;
    IF v_stock IS NULL THEN
        RAISE EXCEPTION 'Produit inexistant : %',NEW.produit_id;
    END IF;
    IF TG_OP='INSERT' AND v_stock<NEW.qte_vente THEN
        RAISE EXCEPTION 'Stock insuffisant pour le produit %. Stock disponible: %, quantite demandee: %',NEW.produit_id,v_stock,NEW.qte_vente;
    END IF;
    IF TG_OP='UPDATE' THEN
        IF OLD.produit_id=NEW.produit_id AND (v_stock+OLD.qte_vente)<NEW.qte_vente THEN
            RAISE EXCEPTION 'Stock insuffisant pour modifier la vente du produit %',NEW.produit_id;
        ELSIF OLD.produit_id<>NEW.produit_id AND v_stock<NEW.qte_vente THEN
            RAISE EXCEPTION 'Stock insuffisant pour le nouveau produit %',NEW.produit_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_verifier_stock_vente ON dim_lignes_vente;
-- ------------------------------------------------------------
-- Trigger   : trg_verifier_stock_vente
-- Processus : Ventes / Stock
-- Rôle      : Bloque une vente lorsque le stock disponible est insuffisant.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_verifier_stock_vente
BEFORE INSERT OR UPDATE ON dim_lignes_vente
FOR EACH ROW EXECUTE FUNCTION fn_verifier_stock_vente();

-- ============================================================
-- 7. MISE A JOUR DU STOCK APRES VENTE
-- ============================================================

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
    IF TG_OP='INSERT' THEN
        UPDATE dim_produits SET stock_actuel=GREATEST(stock_actuel-COALESCE(NEW.qte_vente,0),0) WHERE produit_id=NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP='UPDATE' THEN
        UPDATE dim_produits SET stock_actuel=stock_actuel+COALESCE(OLD.qte_vente,0) WHERE produit_id=OLD.produit_id;
        UPDATE dim_produits SET stock_actuel=GREATEST(stock_actuel-COALESCE(NEW.qte_vente,0),0) WHERE produit_id=NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP='DELETE' THEN
        UPDATE dim_produits SET stock_actuel=stock_actuel+COALESCE(OLD.qte_vente,0) WHERE produit_id=OLD.produit_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_stock_apres_vente ON dim_lignes_vente;
-- ------------------------------------------------------------
-- Trigger   : trg_stock_apres_vente
-- Processus : Stock / Ventes
-- Rôle      : Déduit ou restitue le stock après une opération de vente.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_stock_apres_vente
AFTER INSERT OR UPDATE OR DELETE ON dim_lignes_vente
FOR EACH ROW EXECUTE FUNCTION fn_stock_apres_vente();

-- ============================================================
-- 8. MISE A JOUR DU TOTAL DES VENTES
-- ============================================================

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
    v_vente_id:=COALESCE(NEW.vente_id,OLD.vente_id);
    UPDATE fact_ventes
    SET total_vente=COALESCE((SELECT SUM(montant_ligne) FROM dim_lignes_vente WHERE vente_id=v_vente_id),0)
    WHERE vente_id=v_vente_id;
    RETURN COALESCE(NEW,OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_total_vente ON dim_lignes_vente;
-- ------------------------------------------------------------
-- Trigger   : trg_update_total_vente
-- Processus : Ventes
-- Rôle      : Recalcule le total de l'entête après modification des lignes.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_update_total_vente
AFTER INSERT OR UPDATE OR DELETE ON dim_lignes_vente
FOR EACH ROW EXECUTE FUNCTION fn_update_total_vente();

-- ============================================================
-- 9. CALCUL ET STOCK DES PERTES
-- ============================================================

-- ------------------------------------------------------------
-- Fonction : fn_calcul_perte
-- Rôle     : Calculer automatiquement la valeur d'une perte.
-- Flux     :
--   1. Entrée     : Nouvelle ligne de perte.
--   2. Calcul     : Valeur unitaire et valeur totale.
--   3. Validation : Normalisation des valeurs nécessaires au calcul.
--   4. Retour     : Ligne NEW complétée.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_calcul_perte()
RETURNS TRIGGER AS $$
BEGIN
    NEW.qte_perte:=COALESCE(NEW.qte_perte,0);
    NEW.valeur_unitaire:=COALESCE(NEW.valeur_unitaire,0);
    NEW.valeur_totale:=ROUND(NEW.qte_perte*NEW.valeur_unitaire,2);
    NEW.utilisateur:=COALESCE(NULLIF(TRIM(NEW.utilisateur),''),'SYSTEM');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_calcul_perte ON dim_pertes;
-- ------------------------------------------------------------
-- Trigger   : trg_calcul_perte
-- Processus : Pertes
-- Rôle      : Calcule la valeur unitaire et la valeur totale d'une perte.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_calcul_perte
BEFORE INSERT OR UPDATE ON dim_pertes
FOR EACH ROW EXECUTE FUNCTION fn_calcul_perte();

-- ------------------------------------------------------------
-- Fonction : fn_stock_apres_perte
-- Rôle     : Mettre à jour le stock après une perte.
-- Flux     :
--   1. Entrée     : Ligne de perte insérée, modifiée ou supprimée.
--   2. Calcul     : Déduction, correction ou restitution de la quantité perdue.
--   3. Validation : Traitement adapté à TG_OP.
--   4. Retour     : Stock actualisé et ligne du trigger retournée.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_stock_apres_perte()
RETURNS TRIGGER AS $$
DECLARE v_stock INTEGER;
BEGIN
    IF TG_OP='INSERT' THEN
        SELECT stock_actuel INTO v_stock FROM dim_produits WHERE produit_id=NEW.produit_id;
        IF v_stock<NEW.qte_perte THEN
            RAISE EXCEPTION 'Stock insuffisant pour perte du produit %',NEW.produit_id;
        END IF;
        UPDATE dim_produits SET stock_actuel=stock_actuel-NEW.qte_perte WHERE produit_id=NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP='UPDATE' THEN
        UPDATE dim_produits SET stock_actuel=stock_actuel+OLD.qte_perte WHERE produit_id=OLD.produit_id;
        SELECT stock_actuel INTO v_stock FROM dim_produits WHERE produit_id=NEW.produit_id;
        IF v_stock<NEW.qte_perte THEN
            RAISE EXCEPTION 'Stock insuffisant pour modifier la perte du produit %',NEW.produit_id;
        END IF;
        UPDATE dim_produits SET stock_actuel=stock_actuel-NEW.qte_perte WHERE produit_id=NEW.produit_id;
        RETURN NEW;
    ELSIF TG_OP='DELETE' THEN
        UPDATE dim_produits SET stock_actuel=stock_actuel+OLD.qte_perte WHERE produit_id=OLD.produit_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_stock_apres_perte ON dim_pertes;
-- ------------------------------------------------------------
-- Trigger   : trg_stock_apres_perte
-- Processus : Stock / Pertes
-- Rôle      : Déduit ou restitue le stock après une opération de perte.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_stock_apres_perte
AFTER INSERT OR UPDATE OR DELETE ON dim_pertes
FOR EACH ROW EXECUTE FUNCTION fn_stock_apres_perte();

-- ============================================================
-- 10. CALCUL AUTOMATIQUE DE L'INVENTAIRE
-- ============================================================

ALTER TABLE fact_inventaire ADD COLUMN IF NOT EXISTS cloture BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE fact_inventaire ADD COLUMN IF NOT EXISTS date_cloture TIMESTAMP;
ALTER TABLE fact_inventaire ADD COLUMN IF NOT EXISTS perte_id INTEGER;
ALTER TABLE fact_inventaire ADD COLUMN IF NOT EXISTS ajustement_stock INTEGER NOT NULL DEFAULT 0;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='fk_inventaire_perte') THEN
        ALTER TABLE fact_inventaire
        ADD CONSTRAINT fk_inventaire_perte FOREIGN KEY (perte_id)
        REFERENCES dim_pertes(perte_id)
        ON UPDATE CASCADE ON DELETE SET NULL;
    END IF;
END $$;

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
DECLARE
    v_stock INTEGER;
    v_cout NUMERIC(12,2);
BEGIN
    IF TG_OP='UPDATE' AND COALESCE(NEW.cloture,FALSE)<>COALESCE(OLD.cloture,FALSE) THEN
        RETURN NEW;
    END IF;
    SELECT COALESCE(stock_actuel,0) INTO v_stock
    FROM dim_produits
    WHERE produit_id=NEW.produit_id;
    SELECT COALESCE(la.pu_achat_piece,0) INTO v_cout
    FROM dim_lignes_achat la
    WHERE la.produit_id=NEW.produit_id
    ORDER BY la.ligne_achat_id DESC
    LIMIT 1;
    NEW.stock_physique:=COALESCE(NEW.stock_physique,0);
    NEW.stock_theorique:=COALESCE(v_stock,0);
    NEW.ecart:=NEW.stock_physique-NEW.stock_theorique;
    NEW.valeur_ecart:=ROUND(NEW.ecart*COALESCE(v_cout,0),2);
    NEW.utilisateur:=COALESCE(NULLIF(TRIM(NEW.utilisateur),''),'SYSTEM');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_calcul_inventaire ON fact_inventaire;
-- ------------------------------------------------------------
-- Trigger   : trg_calcul_inventaire
-- Processus : Inventaire
-- Rôle      : Calcule l'écart physique et sa valeur avant enregistrement.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_calcul_inventaire
BEFORE INSERT OR UPDATE ON fact_inventaire
FOR EACH ROW EXECUTE FUNCTION fn_calcul_inventaire();

-- ============================================================
-- 11. VALEURS PAR DEFAUT UTILISATEUR
-- ============================================================

-- ------------------------------------------------------------
-- Fonction : fn_default_utilisateur
-- Rôle     : Renseigner un utilisateur par défaut.
-- Flux     :
--   1. Entrée     : Nouvelle ligne comportant un champ utilisateur.
--   2. Calcul     : Remplacement d'une valeur vide ou nulle.
--   3. Validation : Contrôle de la présence du nom d'utilisateur.
--   4. Retour     : Ligne NEW avec utilisateur renseigné.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION fn_default_utilisateur()
RETURNS TRIGGER AS $$
BEGIN
    NEW.utilisateur:=COALESCE(NULLIF(TRIM(NEW.utilisateur),''),'SYSTEM');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_default_utilisateur_depenses ON fact_depenses;
-- ------------------------------------------------------------
-- Trigger   : trg_default_utilisateur_depenses
-- Processus : Dépenses
-- Rôle      : Renseigne l'utilisateur par défaut avant enregistrement.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_default_utilisateur_depenses
BEFORE INSERT OR UPDATE ON fact_depenses
FOR EACH ROW EXECUTE FUNCTION fn_default_utilisateur();

DROP TRIGGER IF EXISTS trg_default_utilisateur_tresorerie ON fact_tresorerie;
-- ------------------------------------------------------------
-- Trigger   : trg_default_utilisateur_tresorerie
-- Processus : Trésorerie
-- Rôle      : Renseigne l'utilisateur par défaut avant enregistrement.
-- La table cible, l'événement et la fonction appelée sont
-- définis dans l'instruction CREATE TRIGGER ci-dessous.
-- ------------------------------------------------------------
CREATE TRIGGER trg_default_utilisateur_tresorerie
BEFORE INSERT OR UPDATE ON fact_tresorerie
FOR EACH ROW EXECUTE FUNCTION fn_default_utilisateur();

-- ============================================================
-- 12. SYNCHRONISATION DES INVENTAIRES DEJA IMPORTES
-- ============================================================

UPDATE fact_inventaire i
SET stock_theorique=COALESCE(p.stock_actuel,0),
    ecart=COALESCE(i.stock_physique,0)-COALESCE(p.stock_actuel,0),
    valeur_ecart=ROUND((COALESCE(i.stock_physique,0)-COALESCE(p.stock_actuel,0))*COALESCE(cout.pu_achat_piece,0),2),
    utilisateur=COALESCE(NULLIF(TRIM(i.utilisateur),''),'SYSTEM')
FROM dim_produits p
LEFT JOIN (
    SELECT DISTINCT ON (produit_id) produit_id,pu_achat_piece
    FROM dim_lignes_achat
    ORDER BY produit_id,ligne_achat_id DESC
) cout ON cout.produit_id=p.produit_id
WHERE i.produit_id=p.produit_id;

-- ============================================================
-- FIN DU SCRIPT
-- ============================================================
