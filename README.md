# final-project-dsci510
Final Project by group members: 
1. Mrunmayee Khilare
- Mail ID: khilare@usc.edu
- PRN: 2849110690
2. Sathvika Priya
- Mail ID: chakka@usc.edu
- PRN: 3994472051

## Project Overview
This project compares book prices across online sources by matching the same books using ISBN-13. We:
1) build a seed list of ISBNs using the Open Library API,
2) scrape price listings for those ISBNs from AbeBooks and BookFinder,
3) clean and standardize the scraped outputs into analysis-ready tables,
4) run summary analysis and generate visualizations.
The main goal is to understand how much prices vary for the same ISBN across different sources, and which source tends to offer lower prices more often.

## Setup Instructions:
### Create virtual environment
- python3 -m venv .venv

##### Activate (Mac/Linux)
- source .venv/bin/activate

#### Activate (Windows)
- .venv\Scripts\activate

### Install dependencies
- pip install -r requirements.txt





## 3. Repository Structure

```text
├── data/
│   ├── raw/ # raw API and scraped outputs 
│   └── processed/ # cleaned datasets for analysis
├── notebooks/
│   ├── get_isbn.ipynb  # notebook version of seed step
│   ├── scrape_abebooks.ipynb #  notebook version of AbeBooks scrape
│   ├── scrape_amazn_data.ipynb #  notebook version of BookFinder/Amazon scrape
│   └── analysis_and_viz.ipynb # exploratory analysis/plots
├── results/
│   ├── figures/ # saved plots
├── src/
│   ├── get_isbn_seed.py # builds ISBN-13 seed list from Open Library
│   ├── scrape_abebooks.py # scrapes AbeBooks listings by ISBN
│   ├── scrape_bookfinder_amazon.py # scrapes BookFinder ISBN pages (Amazon.com offers)
│   ├── clean_data.py # cleans raw data → processed CSVs
│   ├── run_analysis.py  # (analysis: merges processed data, computes metrics)
│   └── visualize_results.py # (visualizations: generates and saves plots)
├── requirements.txt
├── README.md
└── final_report.pdf  # final written report
