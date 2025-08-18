"""
Configuration file for the Establishment Unit Finder application.
Modify these settings according to your data structure.
"""

class Config:
    """Configuration settings for the application."""
    
    # Column names in your source data
    SOURCE_ENTERPRISE_COLUMN = 'enterprise_number'
    SOURCE_ADDRESS_COLUMN = 'address'
    
    # Column names in your KBO data
    KBO_ENTERPRISE_COLUMN = 'enterprise_number'
    KBO_ADDRESS_COLUMN = 'address'
    KBO_ESTABLISHMENT_UNIT_COLUMN = 'establishment_unit_number'
    
    # File paths (update these with your actual file paths)
    SOURCE_DATA_PATH = 'source_data.csv'
    KBO_DATA_PATH = 'kbo_data.csv'
    OUTPUT_PATH = 'establishment_unit_results.csv'
    
    # Dice coefficient threshold (0.0 to 1.0)
    # Matches below this threshold will be flagged as low confidence
    MIN_DICE_THRESHOLD = 0.3
    
    # Address cleaning settings
    REMOVE_PUNCTUATION = True
    NORMALIZE_SPACES = True
    CONVERT_TO_LOWERCASE = True
