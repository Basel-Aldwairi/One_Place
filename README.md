<div align="center">

![Logo](src/UI/animated_logo_cropped.gif)


# ONEPlace

### A Hybrid Search Engine for the Local Electronics Market

*Stop driving across Amman to find out something's out of stock.*

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-00599C?style=flat-square)
![Sentence Transformers](https://img.shields.io/badge/Sentence--Transformers-all--MiniLM--L6--v2-yellow?style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Pipeline-150458?style=flat-square&logo=pandas&logoColor=white)
![AsyncIO](https://img.shields.io/badge/asyncio-aiohttp-3776AB?style=flat-square)
![MongoDB](https://img.shields.io/badge/MongoDB-Storage-47A248?style=flat-square&logo=mongodb&logoColor=white)
![License](https://img.shields.io/badge/License-Academic-lightgrey?style=flat-square)


</div>

---

## Executive Summary

There is no API, no aggregator, and no industry standard for comparing prices and stock across electronics retailers in
Amman, Jordan. Shoppers currently do this manually, visiting one vendor's website (or storefront) at a time. With no way
to know in advance whether a part is in stock or which store has the best price.

**ONEPlace** is a hybrid search and price-aggregation engine built to close that gap. It asynchronously ingests product
data from local retailers, unifies it into a single schema, and serves it through a three-method hybrid retrieval
engine: dense semantic search, sparse lexical search, and fuzzy exact-match. Fused with Reciprocal Rank Fusion (RRF).
The result is a single search box that returns the right product across every indexed store, with direct links for price
and stock comparison.

This is a senior graduation project for the Computer Engineering Department at the **German Jordanian University**.

---

## Key Architecture & System Flow

ONEPlace is a four-layer, strictly sequential pipeline that separates offline ETL from real-time querying:

```
Layer 1 - Data Ingestion (offline)     : Async crawling + scraping
Layer 2 - Preprocessing (offline)      : Schema unification + vector embedding + database storage
Layer 3 - Hybrid Search Engine (runtime): FAISS + BM25 + Fuzzy → RRF
Layer 4 - Presentation (runtime)       : Streamlit UI, real-time results
```

### 1. Asynchronous Ingestion (`async_manager.py`)

Data collection is a two-phase, per-store process orchestrated by `async_manager.py`:

1. **Crawl phase** : walks each store's category pages via pagination (`?page=N` style URLs) to collect canonical
   product URLs and their breadcrumb categories. Pagination was chosen deliberately over BFS/DFS link-following, which
   caused URL inflation from breadcrumb-encoded paths on these storefronts.
2. **Scrape phase** : fetches each product URL and extracts name, price, stock status, brand, specs table, description,
   and image URL.

Both phases run through `asyncio.Semaphore`, capped concurrent requests (default: 5). A limit added directly in response
to an IP ban triggered by an earlier uncapped async prototype.

### 2. Preprocessing (`preprocessing.py`)

Raw per-store CSVs are cleaned and combined with pandas: prices are cast and back-filled, specs dictionaries are parsed
and filtered down to the fields that matter for retrieval (CPU, GPU, RAM, storage), and a single `model_text` field is
constructed as the unified input for both the semantic and lexical retrieval stages:

```
model_text = product_name + specs + categories
```

Product descriptions are deliberately excluded from `model_text`, testing showed marketing copy degrades retrieval
accuracy more than it helps.

All products are saved into a MongoDB database.

### 3. Embeddings (`generate_embeddings.py`, `download_model.py`)

`model_text` is encoded with `sentence-transformers/all-MiniLM-L6-v2` (6-layer transformer, 384-dim output) into an
`(N × 384)` float32 matrix, serialized to `embeddings.npy`.

### 4. Hybrid Search Engine (`search_engine.py`)

Three independent retrieval methods run per query:

| Method                 | Role                          | Mechanism                                                                                                            |
|------------------------|-------------------------------|----------------------------------------------------------------------------------------------------------------------|
| **FAISS (dense)**      | Semantic gap bridging         | `IndexFlatL2` exact nearest-neighbor search over the embedding matrix, with an empirical L2 distance cutoff of `0.8` |
| **BM25Okapi (sparse)** | Exact keyword / term matching | Scores the tokenized `model_text` corpus; keeps only results scoring within 90% of the top match                     |
| **RapidFuzz (fuzzy)**  | Product-code / SKU lookup     | `WRatio` fuzzy match against product codes, threshold ≥ 90 in the implementation                                     |

**Reciprocal Rank Fusion (RRF)** then merges the three ranked lists into one, without requiring score normalization
across methods. Per the implementation (`combine_indicies`) and thesis §3.7.4, the score for a document `d` is:

```
RRF_Score(d) = Σ  1 / (rank(d) + 1)      - summed over every list containing d
             + 1.0   if d was returned by the fuzzy matcher
             + 0.5   if d is currently in stock
```

A final **multi-vendor expansion** step then finds every product sharing the same product code across all indexed stores
and surfaces them together, inheriting the parent product's RRF score. This is what enables direct cross-store price
comparison in the results grid.

### 5. Presentation (`DataPage.py`, `SearchPage.py`)

A two-page Streamlit app: a landing page with pre-computed market analytics (`calculate_graphs.py` writes static JSON so
the dashboard loads in O(1) time regardless of catalog size), and a search page that holds the `SearchEngine` instance
in `st.session_state` so the ~0.4s cold-start initialization cost is paid once, not on every interaction.

---

## Project Structure

```
.
├── data
│   ├── all/                     # Combined, preprocessed dataset + embeddings.npy
│   ├── citycenter/               # Raw crawl + scraped product CSVs
│   ├── compujordan/               # Raw crawl + scraped product CSVs
│   ├── igeek/                   # Experimental crawl data (not wired into pipeline)
│   └── oriental_store/           # Raw crawl + scraped product CSVs
├── markdowns/                   # Project planning notes
├── requirements.txt
└── src
    ├── database/
    │   ├── database.py           # MongoDB read/write layer (push_all / pull_all)
    │   ├── connection.py
    │   └── delete.py
    ├── data_collection_scripts/
    │   ├── async_manager.py      # Orchestrates crawl + scrape per store
    │   ├── crawler_citycenter.py
    │   ├── crawler_compujordan.py
    │   ├── crawler_igeek.py
    │   ├── crawler_orientalstore.py
    │   ├── scraper_citycenter.py
    │   ├── scraper_compujordan.py
    │   ├── scraper_igeek.py
    │   └── scraper_orientalstore.py
    ├── data_preprocessing_scripts/
    │   └── preprocessing.py      # Cleaning, schema unification, model_text
    ├── models/
    │   ├── download_model.py     # Pulls all-MiniLM-L6-v2 locally
    │   ├── generate_embeddings.py
    │   ├── embeddings_model/     # Cached sentence-transformer weights
    │   └── search_engine.py      # FAISS + BM25 + Fuzzy + RRF
    ├── testing/                  # Ad-hoc test scripts, live-demo prompts
    └── UI/
        ├── DataPage.py           # Landing page + analytics dashboard
        ├── calculate_graphs.py   # Pre-computes dashboard JSON cache
        ├── insight_date/         # Pre-computed dashboard JSON files
        └── pages/
            └── SearchPage.py     # Main search interface
```

> Notebooks, deprecated single-threaded scrapers, and early exploratory code live under `archive/` in the working repo
> and are intentionally omitted here - they are not part of the production pipeline.

---

## System Metrics & Performance

Evaluated against a manually-labeled ground-truth query set at a cutoff of **K=5**, per Chapter 5 of the thesis.
Precision@5 is the fraction of the top 5 results judged relevant; Recall@5 is measured as Hit Rate (did at least one
relevant product appear in the top 5); F1@5 is their harmonic mean.

| Method           | Precision@5 | Recall@5 (Hit Rate) |   F1@5   |
|------------------|:-----------:|:-------------------:|:--------:|
| Fuzzy alone      |    0.20     |        0.20         |   0.20   |
| BM25 alone       |    0.60     |        0.70         |   0.65   |
| FAISS alone      |    0.58     |        0.80         |   0.67   |
| **Hybrid (RRF)** |  **0.82**   |      **1.00**       | **0.90** |

The hybrid RRF model outperforms every individual retrieval method across all three metrics.

**Query & system performance:**

| Operation                           | Measured Duration |
|-------------------------------------|-------------------|
| SearchEngine cold start (full init) | ~0.4 s            |
| Average end-to-end query latency    | ~54 ms            |
| FAISS top-5 search                  | ~14 ms            |
| BM25 top-5 search                   | ~7 ms             |
| Image fetch, 10 results (async)     | ~0.3 s            |
| Image fetch, 50 results (async)     | ~1.3 s            |

At the current catalog size (13,938 products, 384-dim vectors), the FAISS index consumes ~21.4 MB of RAM. Extrapolated
to a 100,000-product catalog, the index would require only ~153 MB, comfortably within reach of consumer-grade
hardware.

---

## Installation & Getting Started

### 1. Clone and set up the environment

```bash
git clone https://github.com/Basel-Aldwairi/One_Place.git
cd One_Place

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure MongoDB

Create a `.env` file with your MongoDB connection details:

```
MONGO_URI=your_connection_string
MONGO_DB=your_database_name
MONGO_COLLECTION=your_collection_name
```

### 3. Download the embedding model

```bash
cd src/models
python download_model.py
```

### 4. Run the data pipeline (crawl → scrape → preprocess → embed)

```bash
cd src/data_collection_scripts
python async_manager.py --store cc --operation both     # City Center
python async_manager.py --store os --operation both     # Oriental Store
python async_manager.py --store cj --operation both     # Compu Jordan

cd ../data_preprocessing_scripts
python preprocessing.py

cd ../models
python generate_embeddings.py
```

### 5. Launch the app

```bash
cd src/UI
streamlit run DataPage.py
```

---

## Supported Vendors

Six local vendors were evaluated over roughly six months of development. Two are currently active in the production
pipeline; four were rejected for concrete, documented technical reasons.

| Store                       | Status   | Notes                                                                                                           |
|-----------------------------|----------|-----------------------------------------------------------------------------------------------------------------|
| **City Center Electronics** | Active   | 8,737 products scraped. Static HTML, ~300 ms avg. response, full scrape ~30 min.                                |
| **Oriental Store**          | Active   | 5,201 products scraped. Static HTML, ~300 ms avg. response, full scrape ~30 min.                                |
| Compu Jordan                | Active   | 3,102 products scraped. Static HTML, ~300 ms avg. response, full scrape ~10 min.                                |
| GTS Computer Store          | Rejected | Server response latency of 2–5 s/request; full scrape estimated at ~70 hours - infeasible for periodic refresh. |
| Mikroelectron               | Rejected | Product listings are JavaScript-rendered; static HTTP scraping returns an empty shell.                          |
| White Angel                 | Rejected | Infinite-scroll product cards loaded via a background API too fragile to reverse-engineer reliably.             |

Combined active catalog: **17,471 products** (5,331 currently in stock).

---

## Authors & License

**Computer Engineering Senior Graduation Project - German Jordanian University, 2026**

- **Basel Al-Dwairi** - Lead Developer, Data & ML Engineering
- **Laith Al-Naimat** - UI/UX & Integrations, Documentation
- **Supervised by:** Dr. Nadia Al-Rousan

This project was developed for academic purposes as a graduation requirement in the School of Computing, Computer
Engineering Department. All rights reserved by the authors unless otherwise licensed.