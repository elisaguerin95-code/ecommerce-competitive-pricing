import streamlit as st

from utils import load_matching_with_prices, recommend_price

st.set_page_config(page_title="Recommandation de prix", page_icon="💰", layout="wide")
st.title("💰 Recommandation de prix")
st.caption(
    "Estimation d'un positionnement cohérent à partir des concurrents les plus similaires."
)

matching = load_matching_with_prices()

if matching.empty:
    st.warning("Aucune donnée de matching disponible.")
    st.stop()

produits_klarstein = sorted(matching["nom_klarstein"].unique())
produit = st.selectbox("Choisir un produit Klarstein", produits_klarstein)

produit_matches = matching[matching["nom_klarstein"] == produit].sort_values("rang_match")
current_price = produit_matches["prix_klarstein"].iloc[0]

col_img, col_info = st.columns([1, 3])
with col_img:
    image_url = produit_matches["image_klarstein"].iloc[0]
    if isinstance(image_url, str) and image_url.startswith("http"):
        st.image(image_url, width=180)
with col_info:
    st.subheader(produit)
    st.metric("Prix actuel", f"{current_price:.2f} €")
    description_klarstein = produit_matches["description_klarstein"].iloc[0]
    if isinstance(description_klarstein, str) and description_klarstein.strip():
        with st.expander("Voir la description du produit Klarstein"):
            st.write(description_klarstein)

st.divider()

reco = recommend_price(current_price, produit_matches)

if reco is None:
    st.info("Pas assez de données concurrentielles pour établir une recommandation.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Prix actuel", f"{current_price:.2f} €")
    col2.metric(
        "Prix concurrentiel recommandé",
        f"{reco['prix_recommande']:.2f} €",
        delta=f"{reco['delta_pct']:+.1f}%",
        delta_color="inverse",
    )
    col3.markdown(
        f"""
        <div style="padding:1rem;border-radius:0.5rem;background-color:{reco['color']}22;
        border-left:4px solid {reco['color']};">
        <b>{reco['verdict']}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write(reco["message"])
    st.caption(
        "Recommandation basée sur la moyenne des prix concurrents pondérée par leur % de similarité "
        "avec le produit Klarstein (pas d'historique de ventes disponible à ce stade)."
    )

st.divider()
st.subheader("Produits concurrents similaires")
st.caption(
    "Vérifie la pertinence de chaque match : titre, description et détail du score de similarité "
    "(texte + visuel) sont affichés ci-dessous."
)

for _, row in produit_matches.iterrows():
    c1, c2, c3 = st.columns([1, 3, 1])
    with c1:
        if isinstance(row["image_concurrent"], str) and row["image_concurrent"].startswith("http"):
            st.image(row["image_concurrent"], width=120)
    with c2:
        st.markdown(f"**#{int(row['rang_match'])} — {row['marque_concurrent']}**")
        st.write(row["nom_concurrent"])

        sim_cols = st.columns(3)
        sim_cols[0].metric("Similarité globale", f"{row['%_similarite_globale']:.0f}%")
        sim_cols[1].metric("Similarité texte", f"{row['%_similarite_description']:.0f}%")
        sim_cols[2].metric("Similarité image", f"{row['%_similarite_image']:.0f}%")

        description_concurrent = row.get("description_concurrent")
        if isinstance(description_concurrent, str) and description_concurrent.strip():
            with st.expander("Voir la description du produit concurrent"):
                st.write(description_concurrent)
    with c3:
        st.metric("Prix", f"{row['prix_concurrent']:.2f} €")
    st.divider()
