import altair as alt
import streamlit as st

from utils import BRAND_COLORS, load_products

st.set_page_config(page_title="Analyse par catégorie", page_icon="🔍", layout="wide")
st.title("🔍 Analyse par catégorie")

df = load_products()
categories = sorted(df["categorie"].unique())

category = st.selectbox("Choisir une catégorie", categories)
sub = df[df["categorie"] == category]

st.caption(f"{len(sub)} produits dans la catégorie **{category}**")

# --- KPIs par marque ---
brands_present = sorted(sub["marque"].unique())
cols = st.columns(len(brands_present))
for col, marque in zip(cols, brands_present):
    brand_sub = sub[sub["marque"] == marque]
    col.metric(
        marque,
        f"{brand_sub['prix'].mean():.0f} €",
        help=f"{len(brand_sub)} produits — min {brand_sub['prix'].min():.0f}€ / max {brand_sub['prix'].max():.0f}€",
    )

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Prix moyen par marque")
    avg = sub.groupby("marque", as_index=False)["prix"].mean()
    chart = (
        alt.Chart(avg)
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
    st.altair_chart(chart, width="stretch")

with col_b:
    st.subheader("Répartition des prix")
    chart2 = (
        alt.Chart(sub)
        .mark_tick(thickness=2, size=30)
        .encode(
            x=alt.X("prix:Q", title="Prix (€)"),
            y=alt.Y("marque:N", title=""),
            color=alt.Color(
                "marque:N",
                scale=alt.Scale(domain=list(BRAND_COLORS.keys()), range=list(BRAND_COLORS.values())),
                legend=None,
            ),
            tooltip=["nom", alt.Tooltip("prix:Q", format=".1f")],
        )
        .properties(height=350)
    )
    st.altair_chart(chart2, width="stretch")

st.divider()
st.subheader("Produits de la catégorie")

sort_option = st.radio("Trier par prix", ["Croissant", "Décroissant"], horizontal=True)
sub_sorted = sub.sort_values("prix", ascending=(sort_option == "Croissant"))

st.dataframe(
    sub_sorted[["nom", "marque", "prix", "note_client"]].rename(
        columns={"nom": "Nom", "marque": "Marque"}
    ),
    width="stretch",
    hide_index=True,
    column_config={
        "prix": st.column_config.NumberColumn("Prix (€)", format="%.2f €"),
        "note_client": st.column_config.NumberColumn("Note client", format="%.1f ⭐"),
    },
)
