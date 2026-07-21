# 💶 Outil de Positionnement Prix E-commerce

Outil d'aide au pricing pour l'e-commerce, basé sur le benchmark concurrentiel et le matching produit (texte + image). Cas d'usage simulé : la marque **Klarstein** (petit électroménager) face à ses concurrents **Cecotec** et **H.Koenig**.

---

## 🎯 Objectifs

Ce projet vise à répondre aux questions suivantes :

- Comment Klarstein est-elle positionnée face à ses concurrents ?
- Quels produits semblent surévalués ou sous-évalués par rapport au marché ?
- Quel prix recommander en s'appuyant sur des produits comparables ?
- Quels écarts de prix existent selon les catégories de produits ?

---

## 🛠️ Technologies

- Python
- Pandas
- BeautifulSoup / Selenium
- Machine Learning (KNN) — similarité texte + image (embeddings)
- Streamlit
- Altair

---

## 📋 Description

À partir des catalogues produits scrapés chez Klarstein et deux concurrents, ce projet identifie pour chaque produit Klarstein les produits concurrents les plus similaires (via un score combinant similarité textuelle et visuelle), compare les prix, et propose une recommandation de positionnement tarifaire. Le tout est exposé dans une application Streamlit à 4 pages.

---

## 🌐 Application en ligne

👉 [Accéder à l'application] (https://ecommerce-competitive-pricing.streamlit.app/)

---

## 📁 Structure du projet

| Fichier | Description |
|---------|-------------|
| `app.py` | Page d'accueil : KPIs globaux, insights business calculés automatiquement, méthodologie |
| `utils.py` | Chargement et nettoyage des données, calculs d'écarts de prix, logique de recommandation |
| `pages/page_1_Dashboard_Benchmarking.py` | Comparaison des prix par marque et par catégorie (filtres, distribution) |
| `pages/page_2_Analyse_par_categorie.py` | Analyse détaillée d'une catégorie de produits donnée |
| `pages/page_3_Simulateur_Pricing.py` | Recommandation de prix produit par produit, avec détail des concurrents similaires |
| `df_final.csv` | Catalogue produit consolidé (Klarstein + concurrents) |
| `matching_klarstein_concurrents.csv` | Résultats du matching produit (Klarstein ↔ concurrents) |
| `requirements.txt` | Librairies nécessaires à l'application |
| [`df_final_embeddings.pkl`](https://huggingface.co/datasets/Elisa-Guerin/ecommerce-competitive-pricing/blob/main/df_final_embeddings.pkl) *(Hugging Face)* | Embeddings texte/image utilisés pour le matching produit |

---

## ⚙️ Comment ça marche ?

### En amont : collecte et matching des données

1. **Scraping** des catalogues produits (nom, description, prix, image, avis) sur les sites de Klarstein, Cecotec et H.Koenig, avec `requests` / `BeautifulSoup` / `Selenium` selon que le contenu est statique ou généré en JavaScript
2. **Nettoyage et consolidation** des catalogues en un seul dataset (`df_final.csv`)
3. **Matching produit (KNN)** : pour chaque produit Klarstein, recherche des k produits concurrents les plus proches à partir d'un score combinant similarité textuelle (description) et visuelle (image), export des meilleurs matchs dans `matching_klarstein_concurrents.csv`

### L'application Streamlit

- **Accueil** — vue d'ensemble du catalogue, deux insights calculés automatiquement (écart de prix médian de Klarstein par rapport à chaque concurrent, part des produits positionnés au-dessus / alignés / en dessous du marché), et explication de la méthodologie de matching et des limites du périmètre actuel
- **Dashboard Benchmarking** — prix moyen par marque et par catégorie, distribution des prix, filtres par marque/catégorie
- **Analyse par catégorie** — zoom sur une catégorie de produits, comparaison des marques présentes
- **Recommandation de prix** — pour un produit Klarstein sélectionné : prix actuel, description, et pour chacun de ses concurrents les plus proches (dédupliqués pour éviter les doublons issus du matching) le détail des scores de similarité (globale / texte / image), la description et le prix ; recommandation d'un prix pondéré par la similarité, avec un verdict (aligné, au-dessus ou en dessous du marché)

---

## 🧠 Compétences mobilisées

**Collecte & préparation des données**
Web scraping (`requests`, `BeautifulSoup`, `Selenium`), nettoyage et consolidation de données (encodage, valeurs manquantes, déduplication), feature engineering

**Machine Learning / NLP**
Algorithme des k plus proches voisins (KNN) appliqué à des embeddings texte (NLP) et image, pour le matching automatique des produits concurrents

**Analyse métier**
Analyse concurrentielle et pricing (competitive pricing), construction d'indicateurs business, formulation d'insights à partir de données

**Développement & visualisation**
Streamlit (application multi-pages), Altair (data visualisation), Python / Pandas

---

## 🚀 Installation et utilisation

### Prérequis

```bash
pip install -r requirements.txt
```

### Lancer l'application

```bash
streamlit run app.py
```

---

## 🧭 Périmètre et limites

Le projet couvre pour l'instant le **benchmark concurrentiel** (Bloc 1). Deux évolutions sont envisagées mais nécessitent des données non disponibles à ce stade :

- **Élasticité prix** — estimer l'impact d'un changement de prix sur les ventes (nécessite un historique de ventes)
- **Optimisation du profit** — recommander un prix maximisant la marge, pas seulement la compétitivité (nécessite les coûts/marges produit)
