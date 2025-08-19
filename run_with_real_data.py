"""
Example usage of the Establishment Unit Finder with real data files.
"""

import pandas as pd
from find_establishment_unit import EstablishmentUnitFinder
from config import Config


def load_real_data():
    """
    Load real data from CSV files.
    Modify this function to match your data sources.
    """
    try:
        # Load source data - try different separators
        print(f"Loading source data from: {Config.SOURCE_DATA_PATH}")
        try:
            source_df = pd.read_csv(Config.SOURCE_DATA_PATH, sep=';')
        except Exception:
            source_df = pd.read_csv(Config.SOURCE_DATA_PATH)
        
        # Load KBO data - try different separators
        print(f"Loading KBO data from: {Config.KBO_DATA_PATH}")
        try:
            kbo_df = pd.read_csv(Config.KBO_DATA_PATH, sep=';')
        except Exception:
            kbo_df = pd.read_csv(Config.KBO_DATA_PATH)
        
        return source_df, kbo_df
    
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        print("Please ensure your data files exist and update the paths in config.py")
        return None, None
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None


def validate_data_structure(source_df, kbo_df):
    """
    Validate that the required columns exist in the data.
    """
    errors = []
    
    # Check source data columns
    required_source_cols = [Config.SOURCE_ENTERPRISE_COLUMN, Config.SOURCE_ADDRESS_COLUMN]
    missing_source_cols = [col for col in required_source_cols if col not in source_df.columns]
    
    if missing_source_cols:
        errors.append(f"Missing columns in source data: {missing_source_cols}")
    
    # Check KBO data columns
    required_kbo_cols = [Config.KBO_ENTERPRISE_COLUMN, Config.KBO_ESTABLISHMENT_UNIT_COLUMN]
    required_kbo_cols.extend(Config.KBO_ADDRESS_COLUMNS)
    missing_kbo_cols = [col for col in required_kbo_cols if col not in kbo_df.columns]
    
    if missing_kbo_cols:
        errors.append(f"Missing columns in KBO data: {missing_kbo_cols}")
    
    if errors:
        print("Data validation errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nAvailable columns in source data:", list(source_df.columns))
        print("Available columns in KBO data:", list(kbo_df.columns))
        print(f"Expected KBO address columns: {Config.KBO_ADDRESS_COLUMNS}")
        return False
    
    return True


def analyze_results(results_df):
    """
    Analyze and display statistics about the results.
    """
    print("\nResults Analysis:")
    print("=" * 50)
    
    total_rows = len(results_df)
    successful_matches = len(results_df[results_df['success']])
    high_confidence_matches = len(results_df[results_df['dice_score'] >= Config.MIN_DICE_THRESHOLD])
    
    print(f"Total rows processed: {total_rows}")
    print(f"Successful matches: {successful_matches} ({successful_matches/total_rows*100:.1f}%)")
    print(f"High confidence matches (dice >= {Config.MIN_DICE_THRESHOLD}): {high_confidence_matches} ({high_confidence_matches/total_rows*100:.1f}%)")
    
    if successful_matches > 0:
        avg_dice_score = results_df[results_df['success']]['dice_score'].mean()
        print(f"Average dice score for successful matches: {avg_dice_score:.3f}")
        
        print("\nDice score distribution:")
        score_ranges = [
            (0.9, 1.0, "Excellent (0.9-1.0)"),
            (0.7, 0.9, "Good (0.7-0.9)"),
            (0.5, 0.7, "Fair (0.5-0.7)"),
            (0.3, 0.5, "Poor (0.3-0.5)"),
            (0.0, 0.3, "Very Poor (0.0-0.3)")
        ]
        
        for min_score, max_score, label in score_ranges:
            count = len(results_df[
                (results_df['dice_score'] >= min_score) & 
                (results_df['dice_score'] < max_score)
            ])
            print(f"  {label}: {count} matches")


def main():
    """
    Main function to run the application with real data.
    """
    print("Establishment Unit Number Finder - Real Data Processing")
    print("=" * 60)
    
    # Load data
    source_df, kbo_df = load_real_data()
    
    if source_df is None or kbo_df is None:
        return
    
    print(f"Loaded {len(source_df)} source rows and {len(kbo_df)} KBO rows")
    
    # Validate data structure
    if not validate_data_structure(source_df, kbo_df):
        return
    
    print("Data validation passed!")
    
    # Initialize finder
    finder = EstablishmentUnitFinder()
    
    # Process data
    print("\nProcessing data...")
    results_df = finder.process_data(
        source_df, 
        kbo_df,
        enterprise_column=Config.SOURCE_ENTERPRISE_COLUMN,
        kbo_enterprise_column=Config.KBO_ENTERPRISE_COLUMN,
        address_column=Config.SOURCE_ADDRESS_COLUMN,
        address_columns=Config.KBO_ADDRESS_COLUMNS,
        establishment_unit_column=Config.KBO_ESTABLISHMENT_UNIT_COLUMN,
        source_columns_to_copy=Config.SOURCE_COLUMNS_TO_COPY
    )
    
    # Analyze results
    analyze_results(results_df)
    
    # Save results
    print(f"\nSaving results to: {Config.OUTPUT_PATH}")
    results_df.to_csv(Config.OUTPUT_PATH, index=False, sep=Config.OUTPUT_CSV_DELIMITER)
    
    # Save to Excel with multiple sheets
    print(f"Saving Excel file to: {Config.OUTPUT_EXCEL_PATH}")
    with pd.ExcelWriter(Config.OUTPUT_EXCEL_PATH, engine='openpyxl') as writer:
        # Results sheet
        results_df.to_excel(writer, sheet_name='Results', index=False)
        
        # Source data sheet (first 1000 rows to avoid file size issues)
        source_sample = source_df.head(1000) if len(source_df) > 1000 else source_df
        source_sample.to_excel(writer, sheet_name='Source_Data_Sample', index=False)
        
        # Summary statistics sheet
        summary_stats = pd.DataFrame({
            'Metric': [
                'Total Rows Processed',
                'Successful Matches',
                'Success Rate (%)',
                'High Confidence Matches',
                'High Confidence Rate (%)',
                'Average Dice Score',
                'Threshold Used'
            ],
            'Value': [
                len(results_df),
                len(results_df[results_df['success']]),
                f"{len(results_df[results_df['success']])/len(results_df)*100:.1f}",
                len(results_df[results_df['dice_score'] >= Config.MIN_DICE_THRESHOLD]),
                f"{len(results_df[results_df['dice_score'] >= Config.MIN_DICE_THRESHOLD])/len(results_df)*100:.1f}",
                f"{results_df[results_df['success']]['dice_score'].mean():.3f}" if len(results_df[results_df['success']]) > 0 else "N/A",
                Config.MIN_DICE_THRESHOLD
            ]
        })
        summary_stats.to_excel(writer, sheet_name='Summary', index=False)
    
    # Display sample results
    print("\nSample results (first 5 rows):")
    print("-" * 40)
    sample_results = results_df.head()
    
    for idx, result in sample_results.iterrows():
        print(f"Row {result['source_row_index'] + 1}:")
        print(f"  Enterprise: {result['enterprise_number']}")
        print(f"  Dice Score: {result['dice_score']:.3f}")
        print(f"  Best Match Column: {result.get('best_match_address_column', 'N/A')}")
        print(f"  Establishment Unit: {result['establishment_unit_number']}")
        print(f"  Success: {result['success']}")
        print()
    
    print("Processing complete!")


if __name__ == "__main__":
    main()
