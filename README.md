# ☕ Afficionado Coffee Roasters: Retail Business Intelligence & Menu Engineering

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://afficionado-roasters-bi-dashboard-gxhznyk5jednzcbb5hhygk.streamlit.app)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19346843.svg)](https://doi.org/10.5281/zenodo.19346843)

## 📌 Project Overview
This repository contains a specialized Exploratory Data Analysis (EDA) framework designed for the specialty coffee industry. Moving beyond simple descriptive statistics, this tool implements formal **Menu Engineering** and **Revenue Concentration** models to transform raw transactional data into high-level business strategy.

This project was developed to provide stakeholders with a "single pane of glass" view of operational efficiency, inventory risk, and profitability across multiple locations.

## 🔬 Research & Analytical Frameworks
The analysis is grounded in two primary business-mathematical frameworks:

1. **Pareto Principle (80/20 Analysis):** Identification of "Revenue Anchors." We calculate the cumulative contribution of each unique product SKU to determine the 20% of the menu driving 80% of total cash flow.
2. **Menu Engineering Matrix (BCG Adaptation):** A four-quadrant scatter analysis plotting **Popularity (Units Sold)** against **Profitability (Total Revenue)** to classify products as:
    * **Stars:** High volume, high revenue.
    * **Workhorses:** High volume, low revenue (Traffic drivers).
    * **Puzzles:** Low volume, high revenue (Niche/Premium).
    * **Dogs:** Low volume, low revenue (Operational drag).

## 🚀 Key Features
* **Dynamic Data Engine:** Processes 200k+ transactions with real-time filtering for store location and product category.
* **Peak Hour Analysis:** Temporal heatmaps identifying the "Double Peak" morning and afternoon surges for staffing optimization.
* **Revenue Concentration Treemap:** A hierarchical visualization of menu balance and diversification risk.
* **Inventory Performance Tracking:** Automated ranking of top and bottom performers by volume and revenue.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Dashboard:** Streamlit
* **Data Manipulation:** Pandas
* **Visualization:** Plotly Express & Plotly Graph Objects (Publication Quality)

## 📊 Business Insights (Executive Summary)
* **Menu Balance:** The analysis revealed a **42.9% Concentration Ratio**, indicating a healthy, well-diversified menu that is not overly reliant on a single product.
* **Operational Staffing:** Peak demand identified between 08:00–10:00 and 15:00–17:00, providing a data-driven roadmap for labor allocation.
* **Inventory Rationalization:** Identified "Dogs" (Low-volume/Low-profit items) which are candidates for removal to reduce overhead and simplify the supply chain.

## 📂 Repository Structure
```text
├── .streamlit/           # Custom theme configuration
├── data/                 # Sample transactional dataset (encrypted/anonymized)
├── src/
│   └── main_app.py       # Core Streamlit application (370 lines of optimized code)
├── requirements.txt      # Project dependencies
└── README.md
