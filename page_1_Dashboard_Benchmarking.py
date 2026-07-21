import altair as alt
import pandas as pd
import streamlit as st

from utils import BRAND_COLORS, load_products

st.set_page_config(page_title="Dashboard Benchmarking", page_icon="📊", layout="wide")
st.title("📊 Dashboard Benchmarking")
st.caption("Positionnement prix de Klarstein face à Cecotec et H.Koenig")

df = load_products()

# --- Filtres ---
with st.sidebar:
    st.header("Filtres")
    categories = sorted(df["categorie"].unique())
    selected_categories = st.multiselect(
        "Catégories", categories, default=categories
    )
    marques = sorted(df["marque"].unique())
    selected_marques = st.multiselect("Marques", marques, default=marques)

filtered = df[df["categorie"].isin(selected_categories) & df["marque"].isin(selected_marques)]

if filtered.empty:
    st.warning("Aucun produit pour cette sélection.")
    st.stop()

# --- KPIs ---
st.subheader("Vue d'ensemble")
kpi_cols = st.columns(len(selected_marques) if selected_marques else 1)
for col, marque in zip(kpi_cols, selected_marques):
    sub = filtered[filtered["marque"] == marque]
    col.metric(
        marque,
        f"{sub['prix'].mean():.0f} €",
        help=f"{len(sub)} produits — prix moyen",
    )

if "Klarstein" in selected_marques and len(selected_marques) > 1:
    klarstein_avg = filtered[filtered["marque"] == "Klarstein"]["prix"].mean()
    concurrents_avg = filtered[filtered["marque"] != "Klarstein"]["prix"].mean()
    if pd.notna(klarstein_avg) and pd.notna(concurrents_avg):
        ecart = (klarstein_avg - concurrents_avg) / concurrents_avg * 100
        st.info(
            f"Sur cette sélection, Klarstein est en moyenne **{ecart:+.1f}%** "
            f"{'plus cher' if ecart > 0 else 'moins cher'} que ses concurrents "
            f"({klarstein_avg:.0f} € vs {concurrents_avg:.0f} €)."
        )

st.divider()

# --- Prix moyen par marque ---
st.subheader("Prix moyen par marque")
avg_by_brand = filtered.groupby("marque", as_index=False)["prix"].mean()
chart1 = (
    alt.Chart(avg_by_brand)
    .mark_bar()
    .encode(
        x=alt.X("marque:N", title="Marque", sort="-y"),
        y=alt.Y("prix:Q", title="Prix moyen (€)"),
        color=alt.Color(
            "marque:N",
            scale=alt.Scale(domain=list(BRAND_COLORS.keys()), range=list(BRAND_COLORS.values())),
            legend=None,
        ),
        tooltip=[alt.Tooltip("marque:N", title="Marque"), alt.Tooltip("prix:Q", format=".1f")],
    )
    .properties(height=350)
)
st.altair_chart(chart1, width="stretch")

# --- Prix moyen par marque et catégorie ---
st.subheader("Prix moyen par marque et catégorie")
avg_by_cat = filtered.groupby(["categorie", "marque"], as_index=False)["prix"].mean()
chart2 = (
    alt.Chart(avg_by_cat)
    .mark_bar()
    .encode(
        x=alt.X("categorie:N", sort="-y", title="Catégorie"),
        y=alt.Y("prix:Q", title="Prix moyen (€)"),
        color=alt.Color(
            "marque:N",
            title="Marque",
            scale=alt.Scale(domain=list(BRAND_COLORS.keys()), range=list(BRAND_COLORS.values())),
        ),
        xOffset="marque:N",
        tooltip=[
            alt.Tooltip("categorie:N", title="Catégorie"),
            alt.Tooltip("marque:N", title="Marque"),
            alt.Tooltip("prix:Q", format=".1f"),
        ],
    )
    .properties(height=450)
)
st.altair_chart(chart2, width="stretch")

# --- Distribution des prix ---
st.subheader("Distribution des prix par marque")
chart3 = (
    alt.Chart(filtered)
    .mark_boxplot(extent="min-max")
    .encode(
        x=alt.X("marque:N", title="Marque"),
        y=alt.Y("prix:Q", title="Prix (€)"),
        color=alt.Color(
            "marque:N",
            scale=alt.Scale(domain=list(BRAND_COLORS.keys()), range=list(BRAND_COLORS.values())),
            legend=None,
        ),
    )
    .properties(height=350)
)
st.altair_chart(chart3, width="stretch")

with st.expander("Voir les données filtrées"):
    st.dataframe(
        filtered[["nom", "categorie", "marque", "prix"]]
        .rename(columns={"categorie": "Catégorie", "marque": "Marque", "prix": "Prix", "nom": "Nom"})
        .sort_values("Prix"),
        width="stretch",
        hide_index=True,
    )
