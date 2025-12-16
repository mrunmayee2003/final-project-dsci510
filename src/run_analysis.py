## E-Commerce Book Price Comparison Analysis

import pandas as pd
import numpy as np
from scipy import stats
from typing import Tuple, Dict
import warnings

warnings.filterwarnings('ignore')


# ============================================================================
# CONFIGURATION
# ============================================================================

# Resolve project root (github_repo_structure/)
ROOT_DIR = Path(__file__).resolve().parent.parent

# File paths (relative to project root)
ABEBOOKS_PATH = ROOT_DIR / "data" / "processed" / "abebooks_cleaned.csv"
AMAZON_PATH   = ROOT_DIR / "data" / "processed" / "amazon_cleaned.csv"

# ============================================================================
# LOAD DATA
# ============================================================================

print("=" * 80)
print("LOADING DATA")
print("=" * 80)

# Load data
abebooks_df = pd.read_csv(ABEBOOKS_PATH)
amazon_df = pd.read_csv(AMAZON_PATH)

print(f"AbeBooks records: {len(abebooks_df)}")
print(f"Amazon records: {len(amazon_df)}")

# Combine datasets
df = pd.concat([abebooks_df, amazon_df], ignore_index=True)
print(f"Total combined records: {len(df)}")
print()


# ============================================================================
# Q1: HOW DO PRICES DIFFER ACROSS SOURCES?
# ============================================================================

print("=" * 80)
print("Q1: HOW DO PRICES DIFFER ACROSS SOURCES?")
print("=" * 80)

# Overall statistics by source
print("\n1.1 OVERALL PRICE STATISTICS BY SOURCE")
print("-" * 80)

overall_stats = df.groupby('source')['total_price'].agg([
    ('count', 'count'),
    ('mean', 'mean'),
    ('median', 'median'),
    ('std', 'std'),
    ('min', 'min'),
    ('max', 'max'),
    ('q1', lambda x: x.quantile(0.25)),
    ('q3', lambda x: x.quantile(0.75))
]).round(2)

# Add IQR and CV
overall_stats['iqr'] = (overall_stats['q3'] - overall_stats['q1']).round(2)
overall_stats['cv'] = (overall_stats['std'] / overall_stats['mean'] * 100).round(2)

print(overall_stats)

# Statistical significance test
print("\n1.2 STATISTICAL SIGNIFICANCE TEST (Independent t-test)")
print("-" * 80)

abebooks_prices = df[df['source'] == 'abebooks']['total_price']
amazon_prices = df[df['source'].str.contains('Amazon', case=False)]['total_price']

t_stat, p_value = stats.ttest_ind(abebooks_prices, amazon_prices)

print(f"t-statistic: {t_stat:.4f}")
print(f"p-value: {p_value:.4f}")

if p_value < 0.05:
    print("✓ RESULT: Price difference is STATISTICALLY SIGNIFICANT (p < 0.05)")
else:
    print("✗ RESULT: Price difference is NOT statistically significant (p >= 0.05)")

# Price distribution by offer type
print("\n1.3 PRICE STATISTICS BY OFFER TYPE (NEW vs USED)")
print("-" * 80)

offer_stats = df.groupby(['source', 'offer_type'])['total_price'].agg([
    ('count', 'count'),
    ('mean', 'mean'),
    ('median', 'median'),
    ('std', 'std')
]).round(2)

print(offer_stats)


# ============================================================================
# Q2: WHICH SOURCE OFFERS THE BEST VALUE MOST CONSISTENTLY?
# ============================================================================

print("\n" + "=" * 80)
print("Q2: WHICH SOURCE OFFERS THE BEST VALUE MOST CONSISTENTLY?")
print("=" * 80)

# Normalize source names
df['source_clean'] = df['source'].apply(
    lambda x: 'Amazon' if 'Amazon' in x else x
)

# Find shared ISBNs
isbn_counts = df.groupby('isbn')['source_clean'].nunique()
shared_isbns = isbn_counts[isbn_counts > 1].index.tolist()

print(f"\n2.1 SHARED ISBN STATISTICS")
print("-" * 80)
print(f"Total unique ISBNs: {df['isbn'].nunique()}")
print(f"Shared ISBNs (on both platforms): {len(shared_isbns)}")
print(f"Percentage of shared books: {len(shared_isbns) / df['isbn'].nunique() * 100:.1f}%")

# Filter to shared ISBNs
shared_df = df[df['isbn'].isin(shared_isbns)].copy()

# Get minimum price per ISBN per source
price_comparison = shared_df.groupby(['isbn', 'source_clean'])['total_price'].min().unstack(fill_value=np.nan)

# Only keep rows where both sources have data
price_comparison = price_comparison.dropna()

print(f"ISBNs with valid price data on both platforms: {len(price_comparison)}")

# Calculate price difference
price_comparison['price_diff'] = price_comparison['abebooks'] - price_comparison['Amazon']
price_comparison['abs_diff'] = price_comparison['price_diff'].abs()
price_comparison['pct_diff'] = (price_comparison['price_diff'] / price_comparison['Amazon'] * 100).round(2)

# Determine winner
def determine_winner(row):
    if abs(row['price_diff']) < 0.01:  # Within 1 cent
        return 'Tie'
    elif row['price_diff'] < 0:
        return 'AbeBooks'
    else:
        return 'Amazon'

price_comparison['winner'] = price_comparison.apply(determine_winner, axis=1)

# Winner statistics
print("\n2.2 PRICE WINNER ANALYSIS")
print("-" * 80)

winner_counts = price_comparison['winner'].value_counts()
print("\nWinner counts:")
for source, count in winner_counts.items():
    pct = count / len(price_comparison) * 100
    print(f"  {source}: {count} books ({pct:.1f}%)")

# Average savings
print("\n2.3 AVERAGE SAVINGS ANALYSIS")
print("-" * 80)

abebooks_wins = price_comparison[price_comparison['winner'] == 'AbeBooks']
amazon_wins = price_comparison[price_comparison['winner'] == 'Amazon']

if len(abebooks_wins) > 0:
    avg_savings_abebooks = abebooks_wins['price_diff'].abs().mean()
    print(f"When AbeBooks wins: Average savings = ${avg_savings_abebooks:.2f}")

if len(amazon_wins) > 0:
    avg_savings_amazon = amazon_wins['price_diff'].abs().mean()
    print(f"When Amazon wins: Average savings = ${avg_savings_amazon:.2f}")

overall_avg_diff = price_comparison['price_diff'].mean()
print(f"\nOverall average price difference (AbeBooks - Amazon): ${overall_avg_diff:.2f}")

if overall_avg_diff < 0:
    print(f"→ AbeBooks is ${abs(overall_avg_diff):.2f} cheaper on average")
else:
    print(f"→ Amazon is ${overall_avg_diff:.2f} cheaper on average")

# Top 10 largest price gaps
print("\n2.4 TOP 10 LARGEST PRICE GAPS")
print("-" * 80)

top_gaps = price_comparison.nlargest(10, 'abs_diff')[['abebooks', 'Amazon', 'price_diff', 'abs_diff', 'winner']]
print(top_gaps)


# ============================================================================
# Q3: DO PRICING PATTERNS DIFFER BETWEEN NEW AND USED BOOKS?
# ============================================================================

print("\n" + "=" * 80)
print("Q3: DO PRICING PATTERNS DIFFER BETWEEN NEW AND USED BOOKS?")
print("=" * 80)

print("\n3.1 DISTRIBUTION BY OFFER TYPE AND SOURCE")
print("-" * 80)

offer_dist = df.groupby(['source_clean', 'offer_type']).size().unstack(fill_value=0)
print(offer_dist)
print("\nPercentages:")
print((offer_dist.div(offer_dist.sum(axis=1), axis=0) * 100).round(1))

print("\n3.2 PRICE COMPARISON: NEW vs USED")
print("-" * 80)

offer_price_stats = df.groupby(['source_clean', 'offer_type'])['total_price'].agg([
    ('count', 'count'),
    ('mean', 'mean'),
    ('median', 'median'),
    ('std', 'std'),
    ('cv', lambda x: (x.std() / x.mean() * 100))
]).round(2)

print(offer_price_stats)

print("\n3.3 PRICE VARIANCE ANALYSIS")
print("-" * 80)

# Coefficient of variation comparison
cv_summary = df.groupby(['source_clean', 'offer_type'])['total_price'].apply(
    lambda x: (x.std() / x.mean() * 100)
).round(2)

print("Coefficient of Variation (CV) - measures relative price spread:")
print(cv_summary)
print("\nInterpretation: Higher CV = More price variability")

# Statistical test: new vs used
print("\n3.4 STATISTICAL TEST: NEW vs USED PRICES")
print("-" * 80)

new_prices = df[df['offer_type'] == 'new']['total_price']
used_prices = df[df['offer_type'] == 'used']['total_price']

t_stat_offer, p_value_offer = stats.ttest_ind(new_prices, used_prices)

print(f"Mean price for NEW books: ${new_prices.mean():.2f}")
print(f"Mean price for USED books: ${used_prices.mean():.2f}")
print(f"t-statistic: {t_stat_offer:.4f}")
print(f"p-value: {p_value_offer:.4f}")

if p_value_offer < 0.05:
    print("✓ RESULT: Price difference between new and used is STATISTICALLY SIGNIFICANT")
else:
    print("✗ RESULT: Price difference between new and used is NOT statistically significant")

# ============================================================================
# EXECUTIVE SUMMARY
# ============================================================================

print("\n" + "=" * 80)
print("EXECUTIVE SUMMARY")
print("=" * 80)

print("\nKEY FINDINGS:")
print("-" * 80)

# Data overview
print(f"\n1. DATA OVERVIEW")
print(f"   • Total books analyzed: {len(df)}")
print(f"   • Unique ISBNs: {df['isbn'].nunique()}")
print(f"   • Sources: {', '.join(df['source'].unique())}")

# Price comparison
abebooks_median = df[df['source'] == 'abebooks']['total_price'].median()
amazon_median = df[df['source'].str.contains('Amazon')]['total_price'].median()

print(f"\n2. PRICE COMPARISON")
print(f"   • AbeBooks median price: ${abebooks_median:.2f}")
print(f"   • Amazon median price: ${amazon_median:.2f}")

if abebooks_median < amazon_median:
    diff = amazon_median - abebooks_median
    pct = (diff / amazon_median) * 100
    print(f"   • AbeBooks is ${diff:.2f} ({pct:.1f}%) cheaper (median)")
    print(f"   ✓ RECOMMENDATION: AbeBooks offers better overall value")
else:
    diff = abebooks_median - amazon_median
    pct = (diff / abebooks_median) * 100
    print(f"   • Amazon is ${diff:.2f} ({pct:.1f}%) cheaper (median)")
    print(f"   ✓ RECOMMENDATION: Amazon offers better overall value")

# Statistical significance
print(f"   • Statistical significance: p-value = {p_value:.4f}")
if p_value < 0.05:
    print(f"   ✓ Price difference is statistically significant")

# ============================================================================
# ANALYSIS COMPLETE
# ============================================================================

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)
print("\nAll statistical analyses have been performed and displayed above.")
