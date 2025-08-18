# FindEstablishmentUnitNumber

A Python application that finds establishment unit numbers based on address comparison using the dice coefficient algorithm.

## Overview

This application performs the following steps:
1. **Data Extraction**: Gets data from a source table
2. **Enterprise Number Extraction**: Extracts enterprise numbers from each row
3. **Data Filtering**: Filters KBO (Belgian business registry) table based on enterprise numbers
4. **Address Comparison**: Performs dice coefficient comparison between addresses
5. **Best Match Selection**: Returns the row with the highest comparison match
6. **Result Extraction**: Returns the establishment unit number from the best matching row

## Features

- **Dice Coefficient Algorithm**: Uses bigram-based dice coefficient for accurate address matching
- **Address Normalization**: Cleans and normalizes addresses for better comparison
- **Batch Processing**: Processes multiple rows efficiently
- **Configurable**: Easy to configure for different data structures
- **Comprehensive Results**: Provides detailed results including confidence scores
- **Error Handling**: Robust error handling and logging

## Installation

1. Clone this repository
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Quick Start with Sample Data

Run the application with built-in sample data:

```bash
python find_establishment_unit.py
```

### Using Your Own Data

1. **Configure Data Sources**: Edit `config.py` to specify your data file paths and column names:

```python
class Config:
    # Update these paths to your actual data files
    SOURCE_DATA_PATH = 'your_source_data.csv'
    KBO_DATA_PATH = 'your_kbo_data.csv'
    
    # Update column names to match your data structure
    SOURCE_ENTERPRISE_COLUMN = 'enterprise_number'
    SOURCE_ADDRESS_COLUMN = 'address'
    KBO_ESTABLISHMENT_UNIT_COLUMN = 'establishment_unit_number'
```

2. **Prepare Your Data**: Ensure your CSV files have the following structure:

**Source Data** (e.g., `source_data.csv`):
```csv
enterprise_number,address,company_name
123456789,"Rue de la Paix 123, 1000 Brussels",Company A
987654321,"Avenue Louise 456, 1050 Ixelles",Company B
```

**KBO Data** (e.g., `kbo_data.csv`):
```csv
enterprise_number,establishment_unit_number,address
123456789,EST001,"Rue de la Paix 123, Brussels 1000"
123456789,EST002,"Rue de la Guerre 456, Brussels 1000"
987654321,EST003,"Avenue Louise 456, Ixelles 1050"
```

3. **Run with Real Data**:

```bash
python run_with_real_data.py
```

## Algorithm Details

### Dice Coefficient

The application uses the Sørensen-Dice coefficient for address comparison:

```
Dice Coefficient = 2 * |intersection of bigrams| / (|bigrams in text1| + |bigrams in text2|)
```

- **Range**: 0.0 (no similarity) to 1.0 (identical)
- **Bigrams**: Two-character substrings used for comparison
- **Normalization**: Addresses are cleaned and normalized before comparison

### Address Normalization

Addresses are preprocessed to improve matching accuracy:
- Convert to lowercase
- Remove punctuation (commas, periods, hyphens)
- Normalize whitespace
- Preserve essential address components

## File Structure

```
FindEstablishmentUnitNumber/
│
├── find_establishment_unit.py    # Main application with sample data
├── run_with_real_data.py         # Script for processing real data files
├── config.py                     # Configuration settings
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Output

The application generates a CSV file with the following columns:

- `source_row_index`: Index of the original source row
- `enterprise_number`: Enterprise number from source data
- `source_address`: Original address from source data
- `best_match_address`: Best matching address from KBO data
- `dice_score`: Similarity score (0.0 to 1.0)
- `establishment_unit_number`: Found establishment unit number
- `success`: Whether a match was found
- `error`: Error message if processing failed

## Configuration Options

### Column Mapping

Update `config.py` to match your data structure:

```python
# Source data columns
SOURCE_ENTERPRISE_COLUMN = 'your_enterprise_column'
SOURCE_ADDRESS_COLUMN = 'your_address_column'

# KBO data columns
KBO_ENTERPRISE_COLUMN = 'your_kbo_enterprise_column'
KBO_ADDRESS_COLUMN = 'your_kbo_address_column'
KBO_ESTABLISHMENT_UNIT_COLUMN = 'your_establishment_unit_column'
```

### Quality Threshold

Set minimum dice coefficient threshold for high-confidence matches:

```python
MIN_DICE_THRESHOLD = 0.3  # Adjust based on your data quality requirements
```

## Performance Considerations

- **Large Datasets**: For very large datasets, consider processing in chunks
- **Memory Usage**: The application loads all data into memory; ensure sufficient RAM
- **Processing Time**: Dice coefficient calculation is O(n²) for each enterprise number

## Error Handling

The application handles various error scenarios:
- Missing enterprise numbers
- No matching KBO data
- Invalid addresses
- File loading errors
- Data structure mismatches

## Example Results Analysis

```
Results Analysis:
==================================================
Total rows processed: 100
Successful matches: 95 (95.0%)
High confidence matches (dice >= 0.3): 88 (88.0%)
Average dice score for successful matches: 0.742

Dice score distribution:
  Excellent (0.9-1.0): 25 matches
  Good (0.7-0.9): 35 matches
  Fair (0.5-0.7): 20 matches
  Poor (0.3-0.5): 8 matches
  Very Poor (0.0-0.3): 7 matches
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Please ensure compliance with your organization's data handling policies when processing business registry data.

## Support

For issues or questions:
1. Check the error messages in the output
2. Verify your data format matches the expected structure
3. Review the configuration settings
4. Check that all required columns are present in your data
