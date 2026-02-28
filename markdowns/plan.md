# One Place

#### Basel Al-Dwairi & Laith AlNaimat

___

### What is One Place:

- A marketplace for everything you need
- Helps you find what you are looking for quickly
- Helps find the best and cheapest way to find said things

___

### Scope:

- Small
  - 10 - 20 stores
  - Variety
- Electronics and PC parts
  - Emotional & true story
  - Mikroelctron
  - Citycenter
  - And more stores
  - We have places to scrap from and easy
    - already exists
    - We can get from more than one place
    - Multiple vendors per build
- Appliences:
  - Smartbuy
  - Darweesh
  - Leaders
- Groceries
  - Stealing from Talabat
  - Millitery Groceries
  - 3Roodcom
    - Computer Vision
    - Would succeed
    - Parents
- Clothes?
  - Side quest
- Automated Scraping and auto rescraping with n8n
- UI with streamlit

___

### Product Information

- URL
- SDK
- Product Name
- Product Description
- Availability
- Brand
- Original Price
- Current Price
- Currency


___

### Chatgbt

Feasible Redesign (for 2 students, 1 semester)

You can keep the core concept but cut down the scope into something buildable and impressive.

🔹 MVP Scope (Realistic)

Title:
“One Place: AI-based Multi-Store Shopping Optimizer”

Scenario:
Focus on a single city (e.g., Amman) and a small, structured dataset of stores (10–20 stores, manually input or scraped from Carrefour, Panda, local online shops).

Features (target for MVP):

🛍️ Input shopping list (user types: “milk, t-shirt, bread, HDMI cable”).

🧠 Store recommendation model (recommend which stores sell which items at the best price).

Use simple AI/ML filtering + similarity models (e.g., item embeddings or TF-IDF matching).

🗺️ Path optimization (shortest route visiting selected stores using Google Maps API or Dijkstra).

⚙️ Filters — price, distance, offers, delivery options (optional).

💻 Web/Streamlit/React UI with map and item list visualization.

That’s a clean, research-worthy, AI + algorithmic systems project.

🤖 AI Components You Could Add

Depending on your track’s requirement:

Recommender system: collaborative/content-based model trained on item-store-price data.

Route optimization: Dijkstra / A* + heuristics (or even simple genetic algorithm).

Smart filters: small regression/classifier to predict store “suitability score.”

Dynamic suggestion: predict missing items (e.g., milk → suggest bread, cereal).

🧮 Feasibility for 2 Students
Aspect	Effort	Feasibility
Data collection (manual/scraped)	2–3 weeks	✅ Feasible if you pick limited stores
AI/ML model	2–3 weeks	✅ Feasible (basic recommender)
Optimization algorithm	2–3 weeks	✅ Feasible (existing libs or custom Dijkstra)
Frontend (web/map)	2–3 weeks	✅ Feasible with Streamlit, Flask, or React
APIs integration	Optional (Google Maps only)	✅ Easy
Testing + polish	1–2 weeks	✅ Manageable