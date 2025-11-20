# N-Gram Query Analyser

A powerful, production-ready Streamlit application for analysing search query data to discover high-impact keyword patterns and identify cost-inefficient n-grams. Built with best practices including modular architecture, comprehensive testing, type hints, and advanced visualizations.

![Platform81 Brand](https://img.shields.io/badge/Brand-Platform81-47d495)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-FF4B4B)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-80%25+-success)

## ✨ Features

### Core Analysis
- **Multi-size N-gram Extraction**: Analyse 1-grams, 2-grams, 3-grams, and 4-grams
- **Automatic Metric Aggregation**: Sum clicks, cost, conversions across all queries containing each n-gram
- **Calculated Metrics**: CTR, CVR, and CPA automatically computed
- **Flexible Sorting**: Sort by any metric (cost, clicks, conversions, CPA, CVR)
- **Cached Analysis**: Lightning-fast re-analysis with Streamlit caching
- **Vectorized Operations**: Optimized for large datasets (10k+ queries)

### Advanced Features
- **Money Waster Detection**: Automatically identifies high-cost, low-conversion n-grams using configurable percentile thresholds
- **Negative Keyword Generator**: Auto-generate negative keyword suggestions with waste score filtering
- **Stop Word Filtering**: Pre-populated stop word list with custom additions
- **Advanced Filtering**: Filter by min cost, min clicks, max CPA, min CVR
- **Query Tracking**: See which queries contain each n-gram
- **Save/Load Analyses**: Save and reload previous analyses

### Data Handling
- **Flexible Input**: Paste CSV data, upload files, or use example data
- **Smart Column Mapping**: Automatically recognises common column name variations
- **Missing Data Handling**: Gracefully handles missing impressions column
- **Data Validation**: Clear error messages for missing required columns
- **Data Quality Metrics**: Automatic quality validation and statistics

### Visualizations
- **Interactive Charts**: Plotly-powered interactive visualizations
- **Cost vs CVR Scatter**: Identify performance clusters
- **Top Performers Bar Charts**: Visualize top n-grams by any metric
- **Cost Distribution**: Understand spend patterns
- **CVR vs CPA Efficiency**: Identify sweet spots

### Export Options
- **Summary Exports**: Download aggregated n-gram metrics
- **Detailed Exports**: Include full query lists for each n-gram
- **Negative Keywords Export**: Download suggested negative keywords
- **Separate Downloads**: Export each n-gram size independently

### Code Quality
- **Type Hints**: Full type annotations throughout codebase
- **Comprehensive Tests**: 80%+ test coverage with pytest
- **Modular Architecture**: Clean separation of concerns
- **Logging**: Built-in logging for debugging and monitoring
- **Error Handling**: Robust error handling and recovery

## 📋 Required Data Format

Your data must include these columns (case-insensitive):

| Column | Variations Accepted | Required |
|--------|-------------------|----------|
| Query | keyword, search term, search_term | ✅ Yes |
| Clicks | clicks, interactions | ✅ Yes |
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

## 🚀 Installation

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
streamlit run app.py
```

### Running Tests

Run the full test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=. --cov-report=html
```

### Code Quality

Format code:
```bash
black .
```

Check linting:
```bash
flake8 .
```

Type checking:
```bash
mypy core/ data/ ui/
```

### Streamlit Cloud Deployment

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `app.py` as the main file
5. Deploy!

## 📁 Project Structure

```
ngram/
├── app.py                 # Main Streamlit application
├── config.py              # Configuration and constants
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── example_data.csv       # Example dataset
├── .gitignore            # Git ignore rules
│
├── core/                  # Core analysis logic
│   ├── __init__.py
│   ├── analyzer.py        # N-gram analysis functions
│   ├── cleaner.py         # Text cleaning and n-gram extraction
│   └── money_wasters.py   # Money waster detection
│
├── data/                  # Data handling
│   ├── __init__.py
│   ├── validator.py       # Column mapping and validation
│   └── loader.py          # Data loading utilities
│
├── ui/                    # User interface components
│   ├── __init__.py
│   ├── styles.py          # Custom CSS styling
│   ├── sidebar.py         # Sidebar components
│   ├── results.py         # Results display
│   └── visualizations.py  # Plotly charts
│
├── tests/                 # Unit tests
│   ├── __init__.py
│   ├── test_cleaner.py
│   ├── test_analyzer.py
│   ├── test_validator.py
│   └── test_money_wasters.py
│
├── logs/                  # Application logs (auto-created)
└── saved_analyses/        # Saved analysis files (auto-created)
```

## 📖 Usage Guide

### Step 1: Prepare Your Data
Export search query data from Google Ads, Microsoft Ads, or your analytics platform. Ensure it includes the required columns.

### Step 2: Input Data
Choose your input method in the sidebar:
- **Paste Data**: Copy and paste CSV data directly
- **Upload File**: Upload a CSV file
- **Use Example Data**: Load pre-populated example data

### Step 3: Configure Settings

**N-gram Sizes**: Select which n-gram sizes to analyse (1-4)

**Minimum Occurrences**: Set how many queries must contain an n-gram for it to be included (reduces noise)

**Sort Metric**: Choose which metric to sort results by

**Stop Words**: Enable to filter out common words like "the", "and", "for". Customise the list as needed.

**Money Waster Detection**:
- Enable to identify expensive, low-converting n-grams
- Adjust cost threshold (default: 75th percentile)
- Adjust CVR threshold (default: 25th percentile)

**Advanced Filters**:
- Min Cost: Filter n-grams by minimum total cost
- Min Clicks: Filter by minimum clicks
- Max CPA: Filter by maximum CPA
- Min CVR: Filter by minimum conversion rate

### Step 4: Analyse
Click the "🚀 Analyse N-Grams" button to process your data.

### Step 5: Review Results

Each n-gram size has its own tab showing:
- Summary metrics (unique n-grams, average CPA, average CVR)
- Money wasters table (if enabled)
- Negative keyword suggestions
- Full results table with all n-grams
- Download options

**Enable Visualizations**: Check "📊 Show Visualizations" to see:
- Cost vs CVR scatter plots
- Top performers bar charts
- Cost distribution histograms
- CVR vs CPA efficiency charts

### Step 6: Export & Save

**Export Options**:
- Download summary CSV files
- Download detailed files with query lists
- Download negative keywords as text file

**Save Analysis**:
- Click "💾 Save" to save your current analysis
- Load previous analyses from the sidebar
- Perfect for comparing different time periods

## 💡 Use Cases

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

## 🔧 Technical Details

### Architecture

**Modular Design**: The application follows a clean modular architecture:
- `core/`: Business logic and analysis algorithms
- `data/`: Data validation, loading, and transformation
- `ui/`: Presentation layer and user interface
- `tests/`: Comprehensive unit test suite

**Type Safety**: Full type hints throughout the codebase using Python's typing module

**Caching**: Streamlit's `@st.cache_data` decorator for performance optimization

**Logging**: Built-in logging to `logs/` directory for debugging

### N-gram Extraction Algorithm

The tool uses a sliding window approach:
1. Cleans queries (lowercases, removes special characters)
2. Optionally filters stop words
3. Extracts sequential word combinations of length n
4. Aggregates metrics across all queries containing each n-gram

**Two implementations available**:
- `analyze_ngrams()`: Standard implementation using defaultdict
- `analyze_ngrams_vectorized()`: Optimized for large datasets using pandas vectorization

### Money Waster Scoring

Money wasters are identified using:
- **Cost threshold**: N-grams above specified percentile (default: 75th)
- **CVR threshold**: N-grams below specified percentile (default: 25th)
- **Waste score**: Calculated as `(normalised_cost) * (1 - cvr/100)`

Formula:
```
waste_score = (cost / max_cost) × (1 - cvr/100)
```

Higher waste scores indicate n-grams that should be reviewed for potential negative keyword additions or bid reductions.

### Performance

**Optimizations**:
- Vectorized pandas operations for large datasets
- Streamlit caching for instant re-analysis
- Efficient defaultdict aggregation
- Lazy loading of visualizations

**Tested with**:
- ✅ Up to 50,000 queries
- ✅ Up to 10MB CSV files
- ✅ Multiple concurrent users (when deployed)

## 🧪 Testing

The project includes comprehensive unit tests with 80%+ coverage.

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_analyzer.py -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test
pytest tests/test_cleaner.py::TestCleanQuery::test_basic_cleaning -v
```

### Test Structure

- `test_cleaner.py`: Tests for text cleaning and n-gram extraction
- `test_analyzer.py`: Tests for n-gram analysis and aggregation
- `test_validator.py`: Tests for data validation and column mapping
- `test_money_wasters.py`: Tests for money waster detection

## 🎨 Brand Colours

This application uses Platform81 brand colours:
- **Night** (Primary): #111111
- **Emerald** (Accent): #47d495
- **Powder Blue**: #98c1d9
- **Burnt Sienna**: #ee6c4d
- **Slate Blue**: #6f58c9

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest tests/`)
5. Format code (`black .`)
6. Check linting (`flake8 .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

## 📞 Support

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with detailed information
3. Include sample data (anonymised) if reporting a bug

## 📄 Licence

MIT Licence - feel free to use and modify for your own projects.

## 🙏 Acknowledgements

Built for performance marketers who want to squeeze every penny of value from their paid search campaigns.

---

**Built with ❤️ for performance marketers | Platform81**
