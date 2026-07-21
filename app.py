import streamlit as st

from utils import compute_brand_gap_insights, compute_positioning_share, load_matching, load_products

st.set_page_config(
    page_title="Outil de positionnement prix e-commerce",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Outil de positionnement prix e-commerce")
st.caption(
    "Comparez chaque produit Klarstein à ses concurrents les plus similaires afin d'identifier "
    "les produits sous-positionnés, alignés ou surévalués par rapport au marché."
)

df = load_products()
matching = load_matching()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Produits au catalogue", f"{len(df):,}".replace(",", " "))
col2.metric("Marques suivies", df["marque"].nunique())
col3.metric("Catégories", df["categorie"].nunique())
col4.metric("Produits Klarstein matchés", matching["nom_klarstein"].nunique())

st.divider()

# --- Insights business calculés automatiquement ---
st.subheader("Ce que révèlent les données")

gap_insights = compute_brand_gap_insights()
positioning = compute_positioning_share()

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    if gap_insights:
        phrases = [
            f"**{'plus cher' if g['gap_pct'] > 0 else 'moins cher'}** de {abs(g['gap_pct']):.0f}% "
            f"que **{g['marque']}** (sur {g['n_produits']} produits comparés)"
            for g in gap_insights
        ]
        st.info(
            "Sur les produits comparables (meilleur match par produit), Klarstein est, en médiane, "
            + ", et ".join(phrases)
            + "."
        )
    else:
        st.info("Pas assez de produits matchés pour calculer un écart de prix par marque.")

with insight_col2:
    if positioning:
        st.info(
            f"Sur les **{positioning['n_produits']} produits Klarstein matchés**, "
            f"**{positioning['au-dessus']:.0f}%** sont positionnés au-dessus de leur marché concurrentiel, "
            f"**{positioning['aligné']:.0f}%** sont alignés, et **{positioning['en dessous']:.0f}%** "
            f"sont en dessous."
        )
    else:
        st.info("Pas assez de données pour estimer la répartition du positionnement.")

st.caption(
    "Ces chiffres sont recalculés automatiquement à partir du matching produit et des prix "
    "collectés — voir le détail par produit dans **Recommandation de prix**. La médiane est "
    "utilisée plutôt que la moyenne car l'échantillon est restreint et quelques matchs entre "
    "produits de gammes différentes peuvent créer des écarts extrêmes."
)

st.divider()

st.subheader("Comment les concurrents sont-ils sélectionnés ?")
st.markdown(
    """
Pour chaque produit Klarstein, les produits comparables sont identifiés à l'aide d'un score de
similarité combinant la **description textuelle** et le **visuel produit**. Les concurrents dont le
produit est le plus proche (score de similarité globale le plus élevé) servent de base à la
comparaison de prix et à la recommandation de positionnement.
"""
)

st.divider()

st.subheader("Navigation")
st.markdown(
    """
- **📊 Dashboard Benchmarking** — positionnement prix global de Klarstein par marque et par catégorie
- **🔍 Analyse par catégorie** — comparaison détaillée sur une catégorie de produit donnée
- **💰 Recommandation de prix** — estimation d'un positionnement cohérent pour un produit Klarstein, à partir de ses concurrents les plus similaires
"""
)

st.divider()

st.subheader("Périmètre méthodologique")
st.markdown(
    """
La recommandation actuelle repose sur le **benchmark concurrentiel** et la **similarité entre
produits**. Elle ne prend pas encore en compte l'élasticité de la demande ni la marge unitaire,
faute de données historiques de ventes et de coûts.
"""
)

with st.expander("Perspectives d'évolution"):
    st.markdown(
        """
- **Élasticité prix** — intégrer un historique de ventes pour estimer l'impact d'un changement de prix sur la demande
- **Optimisation du profit** — intégrer la marge produit pour recommander un prix qui maximise la rentabilité, pas seulement la compétitivité
"""
    )
