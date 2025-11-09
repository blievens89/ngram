# N-Gram Query Analyser

A powerful Streamlit application for analysing search query data to discover high-impact keyword patterns and identify cost-inefficient n-grams.

![Platform81 Brand](https://img.shields.io/badge/Brand-Platform81-47d495)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-FF4B4B)

## Features

### Core Analysis
- **Multi-size N-gram Extraction**: Analyse 1-grams, 2-grams, 3-grams, and 4-grams
- **Automatic Metric Aggregation**: Sum clicks, cost, conversions across all queries containing each n-gram
- **Calculated Metrics**: CTR, CVR, and CPA automatically computed
- **Flexible Sorting**: Sort by any metric (cost, clicks, conversions, CPA, CVR)

### Advanced Features
- **Money Waster Detection**: Automatically identifies high-cost, low-conversion n-grams using configurable percentile thresholds
- **Stop Word Filtering**: Pre-populated stop word list with custom additions
- **Minimum Occurrence Filtering**: Set thresholds to reduce noise
- **Query Tracking**: See which queries contain each n-gram

### Data Handling
- **Flexible Input**: Paste CSV data or upload files
- **Smart Column Mapping**: Automatically recognises common column name variations
- **Missing Data Handling**: Gracefully handles missing impressions column
- **Data Validation**: Clear error messages for missing required columns

### Export Options
- **Summary Exports**: Download aggregated n-gram metrics
- **Detailed Exports**: Include full query lists for each n-gram
- **Separate Downloads**: Export each n-gram size independently

## Required Data Format

Your data must include these columns (case-insensitive):

| Column | Variations Accepted | Required |
|--------|-------------------|----------|
| Query | keyword, search term, search_term | ✅ Yes |
| Clicks | clicks | ✅ Yes |
| Cost | cost, spend, cost_gbp | ✅ Yes |
| Conversions | conversions, conv., conv | ✅ Yes |
| Impressions | impressions, impr., impr | ⚠️ Optional |

**Note**: If impressions are not provided, the tool will use clicks as a proxy for CTR calculations.

### Example CSV Format

```csv
query,clicks,cost,conversions,impressions
remortgage rates,150,245.50,12,2500
cheap remortgage,89,156.20,7,1800
best remortgage deals,234,412.80,18,3200
remortgage calculator,67,89.40,5,890
```

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ngram-query-analyser.git
cd ngram-query-analyser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run ngram_analyzer.py
```

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `ngram_analyzer.py` as the main file
5. Deploy!

## Usage Guide

### Step 1: Prepare Your Data
Export search query data from Google Ads, Microsoft Ads, or your analytics platform. Ensure it includes the required columns.

### Step 2: Input Data
Choose your input method in the sidebar:
- **Paste Data**: Copy and paste CSV data directly
- **Upload File**: Upload a CSV file

### Step 3: Configure Settings

**N-gram Sizes**: Select which n-gram sizes to analyse (1-4)

**Minimum Occurrences**: Set how many queries must contain an n-gram for it to be included (reduces noise)

**Sort Metric**: Choose which metric to sort results by

**Stop Words**: Enable to filter out common words like "the", "and", "for". Customise the list as needed.

**Money Waster Detection**: 
- Enable to identify expensive, low-converting n-grams
- Adjust cost threshold (default: 75th percentile)
- Adjust CVR threshold (default: 25th percentile)

### Step 4: Analyse
Click the "🚀 Analyse N-Grams" button to process your data.

### Step 5: Review Results

Each n-gram size has its own tab showing:
- Summary metrics (unique n-grams, average CPA, average CVR)
- Money wasters table (if enabled)
- Full results table with all n-grams
- Download options

### Step 6: Export
Download summary or detailed CSV files for each n-gram size.

## Use Cases

### 1. Identify Negative Keywords
Find n-grams with high cost but low conversions - these are candidates for negative keywords.

### 2. Discover High-Performers
Identify n-grams with strong conversion rates and reasonable CPAs to inform new campaign structures or ad copy.

### 3. Budget Optimisation
See which keyword patterns consume the most budget and whether they're delivering value.

### 4. Theme Development
Spot patterns across successful queries to develop new ad groups or content themes.

### 5. Competitive Analysis
Understand which competitor names or product comparisons appear in your queries and their performance.

## Technical Details

### N-gram Extraction
The tool:
1. Cleans queries (lowercases, removes special characters)
2. Optionally filters stop words
3. Extracts sequential word combinations of length n
4. Aggregates metrics across all queries containing each n-gram

### Money Waster Scoring
Money wasters are identified using:
- Cost threshold: N-grams above specified percentile (default: 75th)
- CVR threshold: N-grams below specified percentile (default: 25th)
- Waste score: Calculated as `(normalised_cost) * (1 - cvr)`

Higher waste scores indicate n-grams that should be reviewed for potential negative keyword additions or bid reductions.

## Brand Colours

This application uses Platform81 brand colours:
- **Night** (Primary): #111111
- **Emerald** (Accent): #47d495
- **Powder Blue**: #98c1d9
- **Burnt Sienna**: #ee6c4d
- **Slate Blue**: #6f58c9

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Include sample data (anonymised) if reporting a bug

## Licence

MIT Licence - feel free to use and modify for your own projects.

## Acknowledgements

Built for performance marketers who want to squeeze every penny of value from their paid search campaigns.

---

**Built with ❤️ for performance marketers | Platform81**
