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
python3 -m venv .venv
source .venv/bin/activate      # or .venv\Scripts\Activate.ps1 on Windows

#### b. Install dependencies
pip install -r requirements.txt

#### c. Data collection
python src/get_isbn_seed.py
python src/scrape_abebooks.py
python src/scrape_bookfinder_amazon.py

#### d. Data cleaning
python src/clean_data.py

#### e. Analysis
python src/run_analysis.py

#### f. Visualization
python src/visualize_results.py

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
├── data/
│   ├── raw/                # Raw API + scraped outputs
│   └── processed/          # Cleaned datasets ready for analysis
│
├── notebooks/              # Jupyter notebooks 
│   ├── get_isbn.ipynb              # Notebook version of ISBN seed generation
│   ├── scrape_abebooks.ipynb       # Notebook version of AbeBooks scraper
│   ├── scrape_amazn_data.ipynb     # Notebook version of BookFinder/Amazon scraper
│   └── analysis_and_viz.ipynb      # Exploratory analysis + plotting
│
├── results/
│   ├── figures/            # Saved visualizations
|
├── src/                    # Core Python pipeline scripts
│   ├── get_isbn_seed.py            # Builds ISBN-13 seed list using Open Library API
│   ├── scrape_abebooks.py          # Scrapes AbeBooks listings for each ISBN
│   ├── scrape_bookfinder_amazon.py # Scrapes BookFinder + extracts Amazon offers
│   ├── clean_data.py               # Cleans raw data into processed CSVs
│   ├── run_analysis.py             # Merges datasets, computes comparisons, stats
│   └── visualize_results.py        # Generates & saves all project visualizations
│
├── requirements.txt        # Python dependencies
├── README.md               #  overview + instructions 
└── final_report.pdf        #  written report 

