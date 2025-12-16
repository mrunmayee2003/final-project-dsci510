# final-project-dsci510
Final Project by group members: 
1. Mrunmayee Khilare
- Mail ID: khilare@usc.edu
- PRN: 2849110690
2. Sathvika Priya
- Mail ID: chakka@usc.edu
- PRN: 3994472051

## 1. Project Overview
This project compares book prices across online sources by matching the same books using ISBN-13. We:
1) build a seed list of ISBNs using the Open Library API,
2) scrape price listings for those ISBNs from AbeBooks and BookFinder,
3) clean and standardize the scraped outputs into analysis-ready tables,
4) run summary analysis and generate visualizations.
The main goal is to understand how much prices vary for the same ISBN across different sources, and which source tends to offer lower prices more often.

## 2. Setup Instructions:
### Create virtual environment
- python3 -m venv .venv

##### Activate (Mac/Linux)
- source .venv/bin/activate

#### Activate (Windows)
- .venv\Scripts\activate

### Install dependencies
- pip install -r requirements.txt

## 3. How to Run the Project:

This section describes how to run the scripts for data collection, cleaning, analysis, and visualization.
(All commands below assume you are in the project root and that the virtual environment is activated.)

To fully reproduce the project:

#### a. Create and activate a virtual environment
- python3 -m venv .venv
- source .venv/bin/activate      # or .venv\Scripts\Activate.ps1 on Windows

#### b. Install dependencies
- pip install -r requirements.txt

#### c. Data collection
- python src/get_isbn_seed.py
- python src/scrape_abebooks.py
- python src/scrape_bookfinder_amazon.py

#### d. Data cleaning
- python src/clean_data.py

#### e. Analysis
- python src/run_analysis.py

#### f. Visualization
- python src/visualize_results.py

After these steps, you should have:
- Raw data under data/raw/
- Cleaned datasets under data/processed/
- Analysis outputs and plots 

### Responsible Scraping
All scraping in this project is for educational purposes only. We use:
- A custom User-Agent
- Delays between requests
- Simple retry logic
to avoid putting unnecessary load on the websites we query. If any site’s structure or terms change, the scraping scripts may need to be updated or disabled.




## 3. Repository Structure
```text
book-price-analysis/
│
├── data/
│   ├── raw/                         # Raw scraped and API-collected data
│   │   ├── abebooks_raw.csv
│   │   ├── abebooks_raw.jsonl
│   │   ├── bookfinder_data.csv
│   │   └── isbn_seed_1000.csv
│   │
│   └── processed/                   # Cleaned datasets used for analysis
│       ├── abebooks_cleaned.csv
│       └── amazon_cleaned.csv
│
├── notebook/                       # Interactive notebooks for development & EDA
│   ├── get_isbn.ipynb
│   ├── scrape_abebooks.ipynb
│   ├── scrape_bookfinder.ipynb
│   ├── clean_data.ipynb
│   └── run_analysis.ipynb
│
├── src/                             # FPython Scripts
│   ├── get_isbn_seed.py
│   ├── scrape_abebooks.py
│   ├── scrape_bookfinder_amazon.py
│   ├── clean_data.py
│   ├── run_analysis.py
│   └── visualize_results.py         
│
├── visualizations/                  # All generated plots (as PNGs)
│   ├── viz1_boxplot_price_by_source.png
│   ├── viz2_histogram_price_difference.png
│   ├── viz3_winner_bar_chart.png
│   ├── viz4_grouped_boxplot_offer_type.png
│   ├── viz5_scatter_direct_comparison.png
│   └── viz6_top10_price_gaps.png
│
├── results/
│   └── final_report.pdf             # Final submitted paper/report
│
├── requirements.txt                 # Required Python libraries
├── README.md                        # Project description & instructions
└── DSCI 510 Final Project Proposal.pdf


