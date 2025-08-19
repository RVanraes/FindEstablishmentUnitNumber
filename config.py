"""
Configuration file for the Establishment Unit Finder application.
Modify these settings according to your data structure.
"""

class Config:
    """Configuration settings for the application."""
    
    # Column names in your source data
    SOURCE_ENTERPRISE_COLUMN = 'Enterprise Number'
    SOURCE_ADDRESS_COLUMN = 'address'
    
    # Column names in your KBO data
    KBO_ENTERPRISE_COLUMN = 'EnterpriseNumber'
    KBO_ADDRESS_COLUMNS = ['Address NL', 'Address FR']  # Multiple address columns to check
    KBO_ESTABLISHMENT_UNIT_COLUMN = 'EntityNumber'
    
    # File paths (update these with your actual file paths)
    SOURCE_DATA_PATH = 'source_data.csv'
    KBO_DATA_PATH = 'kbo/kbo_data.csv'
    OUTPUT_PATH = 'establishment_unit_results.csv'
    
    # Source data columns to copy to output (set to None to copy all columns)
    SOURCE_COLUMNS_TO_COPY = None  # Will copy all source columns if None
    
    # Dice coefficient threshold (0.0 to 1.0)
    # Matches below this threshold will be flagged as low confidence
    MIN_DICE_THRESHOLD = 0.3
    
    # Address cleaning settings
    REMOVE_PUNCTUATION = True
    NORMALIZE_SPACES = True
    CONVERT_TO_LOWERCASE = True
