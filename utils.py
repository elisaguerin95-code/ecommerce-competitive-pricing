"""Fonctions partagées entre les pages de l'app Streamlit."""

import pandas as pd
import streamlit as st

# Les CSV de données vivent au même niveau que app.py (pas de sous-dossier data/).

BRAND_COLORS = {
    "Klarstein": "#1f4e5f",
    "Cecotec": "#e07a5f",
    "HKoenig": "#81b29a",
}

# Seuil (en %) au-delà duquel un écart de prix est considéré comme un
# désalignement significatif plutôt qu'un simple bruit de mesure.
GAP_THRESHOLD_PCT = 10

REQUIRED_PRODUCT_COLUMNS = {"nom", "catégorie", "description", "prix", "image", "Marque"}
REQUIRED_MATCHING_COLUMNS = {
    "nom_klarstein",
    "categorie",
    "rang_match",
    "nom_concurrent",
    "marque_concurrent",
    "%_similarite_globale",
    "%_similarite_image",
    "%_similarite_description",
}


def _fail(message: str):
    """Affiche une erreur lisible côté utilisateur et arrête le rendu de la page."""
    st.error(message)
    st.stop()


@st.cache_data
def load_products():
    """Catalogue produit fusionné (Klarstein + concurrents).

    Colonnes normalisées en sortie : nom, categorie, description, prix, image,
    note_client, marque.
    """
    try:
        df = pd.read_csv("df_final.csv")
    except FileNotFoundError:
        _fail(
            "Fichier de données introuvable : `df_final.csv`. "
            "Vérifie qu'il est bien présent au même niveau que `app.py`."
        )

    missing = REQUIRED_PRODUCT_COLUMNS - set(df.columns)
    if missing:
        _fail(
            f"Le fichier `df_final.csv` ne contient pas les colonnes attendues : {sorted(missing)}. "
            "Le format du fichier source a probablement changé."
        )

    df = df.rename(columns={"catégorie": "categorie", "Marque": "marque"})
    df = df.dropna(subset=["prix"]).copy()
    df["prix"] = df["prix"].astype(float)
    return df


@st.cache_data
def load_matching():
    """Résultats du matching produit Klarstein <-> concurrents (texte + image)."""
    try:
        m = pd.read_csv("matching_klarstein_concurrents.csv")
    except FileNotFoundError:
        _fail(
            "Fichier de données introuvable : `matching_klarstein_concurrents.csv`. "
            "Vérifie qu'il est bien présent au même niveau que `app.py`."
        )

    missing = REQUIRED_MATCHING_COLUMNS - set(m.columns)
    if missing:
        _fail(
            f"Le fichier `matching_klarstein_concurrents.csv` ne contient pas les colonnes "
            f"attendues : {sorted(missing)}."
        )
    return m


@st.cache_data
def load_matching_with_prices():
    """Table de matching enrichie avec les prix (Klarstein + concurrent)."""
    df = load_products()
    m = load_matching()

    # Une seule ligne par (nom, marque) pour éviter les doublons de prix lors du merge
    df_unique = df.drop_duplicates(subset=["nom", "marque"], keep="first")

    klarstein_prices = df_unique[df_unique["marque"] == "Klarstein"][
        ["nom", "prix", "image", "description"]
    ]
    klarstein_prices = klarstein_prices.rename(
        columns={
            "nom": "nom_klarstein",
            "prix": "prix_klarstein",
            "image": "image_klarstein",
            "description": "description_klarstein",
        }
    )

    concurrent_prices = df_unique[["nom", "marque", "prix", "image", "description"]].rename(
        columns={
            "nom": "nom_concurrent",
            "marque": "marque_concurrent",
            "prix": "prix_concurrent",
            "image": "image_concurrent",
            "description": "description_concurrent",
        }
    )

    merged = m.merge(klarstein_prices, on="nom_klarstein", how="left")
    merged = merged.merge(
        concurrent_prices, on=["nom_concurrent", "marque_concurrent"], how="left"
    )
    merged = merged.dropna(subset=["prix_klarstein", "prix_concurrent"])

    # Le pipeline de matching (KNN texte + image) renvoie parfois le même produit
    # concurrent comme meilleur ET deuxième/troisième voisin (ex: plusieurs
    # variantes de couleur d'un même produit ont des descriptions quasi
    # identiques). On ne garde qu'une seule occurrence par (produit Klarstein,
    # produit concurrent) — la mieux classée — pour éviter d'afficher le même
    # concurrent en double ou triple dans la recommandation.
    merged = merged.sort_values(["nom_klarstein", "rang_match"])
    merged = merged.drop_duplicates(
        subset=["nom_klarstein", "nom_concurrent", "marque_concurrent"], keep="first"
    )
    merged["rang_match"] = merged.groupby("nom_klarstein").cumcount() + 1

    return merged


def _classify_gap(delta_pct: float) -> dict:
    """Classe un écart de prix (%) en verdict + message + couleur."""
    if delta_pct > GAP_THRESHOLD_PCT:
        return {
            "verdict": "Positionné au-dessus du marché",
            "message": (
                f"Le prix actuel est {delta_pct:.1f}% plus élevé que le prix concurrentiel pondéré. "
                "Risque de perte de compétitivité face aux produits similaires."
            ),
            "color": "#e07a5f",
            "categorie_ecart": "au-dessus",
        }
    if delta_pct < -GAP_THRESHOLD_PCT:
        return {
            "verdict": "Positionné en dessous du marché",
            "message": (
                f"Le prix actuel est {abs(delta_pct):.1f}% plus bas que le prix concurrentiel pondéré. "
                "Marge de manœuvre pour augmenter le prix sans perdre en compétitivité."
            ),
            "color": "#81b29a",
            "categorie_ecart": "en dessous",
        }
    return {
        "verdict": "Prix aligné avec le marché",
        "message": f"Écart de {delta_pct:+.1f}% seulement par rapport au prix concurrentiel pondéré.",
        "color": "#3d405b",
        "categorie_ecart": "aligné",
    }


def recommend_price(current_price: float, matches: pd.DataFrame) -> dict:
    """Recommandation de prix pondérée par la similarité des produits concurrents matchés.

    matches doit contenir les colonnes 'prix_concurrent' et '%_similarite_globale'.
    """
    if matches.empty or matches["%_similarite_globale"].sum() == 0:
        return None

    weights = matches["%_similarite_globale"]
    weighted_price = (matches["prix_concurrent"] * weights).sum() / weights.sum()
    delta_pct = (current_price - weighted_price) / weighted_price * 100

    result = _classify_gap(delta_pct)
    result["prix_recommande"] = round(weighted_price, 2)
    result["delta_pct"] = round(delta_pct, 1)
    return result


@st.cache_data
def compute_brand_gap_insights():
    """Écart de prix médian de Klarstein vs chaque marque concurrente, sur les
    produits effectivement comparables (meilleur match de chaque produit).

    La médiane est utilisée plutôt que la moyenne car quelques matchs imparfaits
    (produits de gammes très différentes malgré un score de similarité correct)
    peuvent créer des écarts extrêmes qui faussent une moyenne sur un aussi petit
    échantillon.
    """
    matching = load_matching_with_prices()
    best_matches = matching[matching["rang_match"] == matching.groupby("nom_klarstein")["rang_match"].transform("min")]

    insights = []
    for marque, group in best_matches.groupby("marque_concurrent"):
        gap_pct = ((group["prix_klarstein"] - group["prix_concurrent"]) / group["prix_concurrent"] * 100).median()
        insights.append({"marque": marque, "gap_pct": round(gap_pct, 1), "n_produits": len(group)})
    return insights


@st.cache_data
def compute_positioning_share():
    """Part des produits Klarstein matchés classés au-dessus / alignés / en dessous du marché."""
    matching = load_matching_with_prices()

    verdicts = []
    for nom, group in matching.groupby("nom_klarstein"):
        current_price = group["prix_klarstein"].iloc[0]
        reco = recommend_price(current_price, group)
        if reco:
            verdicts.append(reco["categorie_ecart"])

    if not verdicts:
        return {}

    total = len(verdicts)
    return {
        "au-dessus": round(verdicts.count("au-dessus") / total * 100, 1),
        "aligné": round(verdicts.count("aligné") / total * 100, 1),
        "en dessous": round(verdicts.count("en dessous") / total * 100, 1),
        "n_produits": total,
    }
