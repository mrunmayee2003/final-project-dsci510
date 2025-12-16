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

## Setup Instructions:
### Create virtual environment
- python3 -m venv .venv

##### Activate (Mac/Linux)
- source .venv/bin/activate

#### Activate (Windows)
- .venv\Scripts\activate

### Install dependencies
- pip install -r requirements.txt
