"""
Application to find establishment unit numbers based on address comparison.

This application:
1. Gets data from a source table
2. Extracts enterprise numbers from rows
3. Filters KBO table based on enterprise numbers
4. Performs dice coefficient comparison between addresses
5. Returns the row with the highest comparison match
6. Returns the establishment unit number from that row
"""

import pandas as pd
import re
from typing import List, Tuple, Optional, Dict, Any
from difflib import SequenceMatcher


class AddressComparator:
    """Class to handle address comparison using dice coefficient."""
    
    @staticmethod
    def clean_address(address: str) -> str:
        """Clean and normalize address string for comparison."""
        if pd.isna(address) or address is None:
            return ""
        
        # Convert to lowercase and remove extra spaces
        address = str(address).lower().strip()
        
        # Remove common punctuation and normalize spaces
        address = re.sub(r'[,.\-_]', ' ', address)
        address = re.sub(r'\s+', ' ', address)
        
        return address
    
    @staticmethod
    def get_bigrams(text: str) -> set:
        """Get set of bigrams from text for dice coefficient calculation."""
        text = AddressComparator.clean_address(text)
        if len(text) < 2:
            return set()
        
        bigrams = set()
        for i in range(len(text) - 1):
            bigrams.add(text[i:i+2])
        
        return bigrams
    
    @staticmethod
    def dice_coefficient(text1: str, text2: str) -> float:
        """
        Calculate dice coefficient between two strings.
        
        Dice coefficient = 2 * |intersection| / (|set1| + |set2|)
        Returns value between 0 and 1, where 1 is perfect match.
        """
        bigrams1 = AddressComparator.get_bigrams(text1)
        bigrams2 = AddressComparator.get_bigrams(text2)
        
        if not bigrams1 and not bigrams2:
            return 1.0  # Both empty strings
        
        if not bigrams1 or not bigrams2:
            return 0.0  # One empty string
        
        intersection = bigrams1.intersection(bigrams2)
        return 2.0 * len(intersection) / (len(bigrams1) + len(bigrams2))


class EstablishmentUnitFinder:
    """Main class to find establishment unit numbers."""
    
    def __init__(self):
        self.address_comparator = AddressComparator()
    
    def extract_enterprise_number(self, row: pd.Series, enterprise_column: str = 'enterprise_number') -> Optional[str]:
        """
        Extract enterprise number from a data row.
        
        Args:
            row: Pandas series representing a data row
            enterprise_column: Name of the column containing enterprise number
            
        Returns:
            Enterprise number as string or None if not found
        """
        try:
            enterprise_num = row.get(enterprise_column)
            if pd.isna(enterprise_num):
                return None
            return str(enterprise_num).strip()
        except Exception as e:
            print(f"Error extracting enterprise number: {e}")
            return None
    
    def filter_kbo_data(self, kbo_df: pd.DataFrame, enterprise_number: str, 
                       enterprise_column: str = 'enterprise_number') -> pd.DataFrame:
        """
        Filter KBO table based on enterprise number.
        
        Args:
            kbo_df: KBO DataFrame
            enterprise_number: Enterprise number to filter by
            enterprise_column: Name of the column containing enterprise numbers
            
        Returns:
            Filtered DataFrame
        """
        try:
            if enterprise_number is None:
                return pd.DataFrame()
            
            # Convert enterprise number column to string for comparison
            kbo_df[enterprise_column] = kbo_df[enterprise_column].astype(str)
            enterprise_number = str(enterprise_number)
            
            filtered_df = kbo_df[kbo_df[enterprise_column] == enterprise_number].copy()
            
            return filtered_df
        except Exception as e:
            print(f"Error filtering KBO data: {e}")
            return pd.DataFrame()
    
    def find_best_address_match(self, source_address: str, kbo_filtered_df: pd.DataFrame, 
                               address_columns: List[str]) -> Tuple[Optional[pd.Series], float, str]:
        """
        Find the row with the best address match using dice coefficient across multiple address columns.
        
        Args:
            source_address: Address from the source data row
            kbo_filtered_df: Filtered KBO DataFrame
            address_columns: List of address column names to check
            
        Returns:
            Tuple of (best matching row, dice coefficient score, best matching address)
        """
        if kbo_filtered_df.empty:
            return None, 0.0, ""
        
        best_match = None
        best_score = 0.0
        best_address = ""
        
        for idx, row in kbo_filtered_df.iterrows():
            # Check all address columns for this row
            for address_col in address_columns:
                if address_col in row:
                    kbo_address = row.get(address_col, "")
                    score = self.address_comparator.dice_coefficient(source_address, kbo_address)
                    
                    if score > best_score:
                        best_score = score
                        best_match = row
                        best_address = kbo_address
        
        return best_match, best_score, best_address
    
    def process_single_row(self, source_row: pd.Series, kbo_df: pd.DataFrame,
                          enterprise_column: str = 'enterprise_number',
                          kbo_enterprise_column: str = None,
                          address_column: str = 'address',
                          address_columns: List[str] = None,
                          establishment_unit_column: str = 'establishment_unit_number',
                          source_columns_to_copy: List[str] = None) -> Dict[str, Any]:
        """
        Process a single source data row to find establishment unit number.
        
        Args:
            source_row: Source data row
            kbo_df: KBO DataFrame
            enterprise_column: Name of enterprise number column in source data
            kbo_enterprise_column: Name of enterprise number column in KBO data (defaults to enterprise_column)
            address_column: Name of source address column
            address_columns: List of KBO address columns to check
            establishment_unit_column: Name of establishment unit number column
            source_columns_to_copy: List of source columns to copy to output
            
        Returns:
            Dictionary with results
        """
        if address_columns is None:
            address_columns = ['address']
        
        if kbo_enterprise_column is None:
            kbo_enterprise_column = enterprise_column
        
        result = {
            'enterprise_number': None,
            'source_address': None,
            'best_match_address': None,
            'best_match_address_column': None,
            'dice_score': 0.0,
            'establishment_unit_number': None,
            'success': False,
            'error': None
        }
        
        # Copy source data columns if specified
        if source_columns_to_copy:
            for col in source_columns_to_copy:
                if col in source_row:
                    result[f'source_{col}'] = source_row[col]
        else:
            # Copy all source columns
            for col in source_row.index:
                result[f'source_{col}'] = source_row[col]
        
        try:
            # Step 1: Extract enterprise number
            enterprise_number = self.extract_enterprise_number(source_row, enterprise_column)
            result['enterprise_number'] = enterprise_number
            
            if enterprise_number is None:
                result['error'] = "No enterprise number found in source row"
                return result
            
            # Step 2: Get source address
            source_address = source_row.get(address_column, "")
            result['source_address'] = source_address
            
            # Step 3: Filter KBO data using the KBO enterprise column
            filtered_kbo = self.filter_kbo_data(kbo_df, enterprise_number, kbo_enterprise_column)
            
            if filtered_kbo.empty:
                result['error'] = f"No KBO data found for enterprise number: {enterprise_number}"
                return result
            
            # Step 4: Find best address match across multiple address columns
            best_match, dice_score, best_address = self.find_best_address_match(
                source_address, filtered_kbo, address_columns
            )
            
            result['dice_score'] = dice_score
            
            if best_match is not None:
                result['best_match_address'] = best_address
                # Find which column had the best match
                for addr_col in address_columns:
                    if addr_col in best_match and str(best_match[addr_col]) == str(best_address):
                        result['best_match_address_column'] = addr_col
                        break
                result['establishment_unit_number'] = best_match.get(establishment_unit_column)
                result['success'] = True
            else:
                result['error'] = "No matching address found"
            
        except Exception as e:
            result['error'] = f"Error processing row: {str(e)}"
        
        return result
    
    def process_data(self, source_df: pd.DataFrame, kbo_df: pd.DataFrame,
                    enterprise_column: str = 'enterprise_number',
                    kbo_enterprise_column: str = None,
                    address_column: str = 'address',
                    address_columns: List[str] = None,
                    establishment_unit_column: str = 'establishment_unit_number',
                    source_columns_to_copy: List[str] = None) -> pd.DataFrame:
        """
        Process all rows in source data to find establishment unit numbers.
        
        Args:
            source_df: Source DataFrame
            kbo_df: KBO DataFrame
            enterprise_column: Name of enterprise number column in source data
            kbo_enterprise_column: Name of enterprise number column in KBO data
            address_column: Name of source address column
            address_columns: List of KBO address columns to check
            establishment_unit_column: Name of establishment unit number column
            source_columns_to_copy: List of source columns to copy to output
            
        Returns:
            DataFrame with results
        """
        if address_columns is None:
            address_columns = ['address']
            
        results = []
        
        for idx, row in source_df.iterrows():
            print(f"Processing row {idx + 1} of {len(source_df)}")
            
            result = self.process_single_row(
                row, kbo_df, enterprise_column, kbo_enterprise_column, address_column, 
                address_columns, establishment_unit_column, source_columns_to_copy
            )
            
            # Add original row index
            result['source_row_index'] = idx
            results.append(result)
        
        return pd.DataFrame(results)


def load_sample_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Create sample data for testing purposes.
    Replace this function with actual data loading logic.
    """
    # Sample source data with extra columns
    source_data = {
        'Enterprise Number': ['123456789', '987654321', '111222333'],
        'address': [
            'Rue de la Paix 123, 1000 Brussels',
            'Avenue Louise 456, 1050 Ixelles',
            'Chaussee de Wavre 789, 1040 Etterbeek'
        ],
        'company_name': ['Company A', 'Company B', 'Company C'],
        'contact_person': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'phone': ['+32 2 123 4567', '+32 2 987 6543', '+32 2 555 0123'],
        'email': ['contact@companya.be', 'info@companyb.be', 'hello@companyc.be']
    }
    source_df = pd.DataFrame(source_data)
    
    # Sample KBO data with multiple address columns
    kbo_data = {
        'EnterpriseNumber': ['123456789', '123456789', '987654321', '987654321', '111222333'],
        'EntityNumber': ['EST001', 'EST002', 'EST003', 'EST004', 'EST005'],
        'Address NL': [
            'Vredestraat 123, 1000 Brussel',  # Dutch version
            'Oorlogstraat 456, 1000 Brussel',  # Different address, same enterprise
            'Louizalaan 456, 1050 Elsene',  # Dutch version
            'Anspachlaan 789, 1000 Brussel',  # Different address, same enterprise
            'Waversesteenweg 789, 1040 Etterbeek'  # Dutch version
        ],
        'Address FR': [
            'Rue de la Paix 123, 1000 Bruxelles',  # French version - close match
            'Rue de la Guerre 456, 1000 Bruxelles',  # Different address, same enterprise
            'Avenue Louise 456, 1050 Ixelles',  # French version - close match
            'Boulevard Anspach 789, 1000 Bruxelles',  # Different address, same enterprise
            'Chaussée de Wavre 789, 1040 Etterbeek'  # French version - close match
        ]
    }
    kbo_df = pd.DataFrame(kbo_data)
    
    return source_df, kbo_df


def main():
    """Main function to demonstrate the application."""
    print("Establishment Unit Number Finder")
    print("=" * 40)
    
    # Initialize the finder
    finder = EstablishmentUnitFinder()
    
    # Load data (replace with actual data loading)
    print("Loading data...")
    source_df, kbo_df = load_sample_data()
    
    print(f"Source data: {len(source_df)} rows")
    print(f"KBO data: {len(kbo_df)} rows")
    print()
    
    # Process data
    print("Processing data...")
    results_df = finder.process_data(
        source_df, 
        kbo_df,
        enterprise_column='Enterprise Number',  # Source data column
        kbo_enterprise_column='EnterpriseNumber',  # KBO data column
        address_column='address',
        address_columns=['Address NL', 'Address FR'],
        establishment_unit_column='EntityNumber'
    )
    
    # Display results
    print("Results:")
    print("-" * 40)
    
    for idx, result in results_df.iterrows():
        print(f"Row {result['source_row_index'] + 1}:")
        print(f"  Enterprise Number: {result['enterprise_number']}")
        print(f"  Source Address: {result['source_address']}")
        print(f"  Best Match Address: {result['best_match_address']}")
        print(f"  Best Match Column: {result['best_match_address_column']}")
        print(f"  Dice Score: {result['dice_score']:.3f}")
        print(f"  Establishment Unit Number: {result['establishment_unit_number']}")
        print(f"  Success: {result['success']}")
        if result['error']:
            print(f"  Error: {result['error']}")
        print()
    
    # Save results
    output_file = "establishment_unit_results.csv"
    results_df.to_csv(output_file, index=False, sep=';')
    print(f"Results saved to: {output_file}")
    
    # Save to Excel with multiple sheets
    excel_file = "establishment_unit_results.xlsx"
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Results sheet
        results_df.to_excel(writer, sheet_name='Results', index=False)
        
        # Source data sheet
        source_df.to_excel(writer, sheet_name='Source_Data', index=False)
        
        # KBO data sheet  
        kbo_df.to_excel(writer, sheet_name='KBO_Data', index=False)
        
        # Summary statistics sheet
        summary_stats = pd.DataFrame({
            'Metric': [
                'Total Rows Processed',
                'Successful Matches', 
                'Success Rate (%)',
                'Average Dice Score'
            ],
            'Value': [
                len(results_df),
                len(results_df[results_df['success']]),
                f"{len(results_df[results_df['success']])/len(results_df)*100:.1f}",
                f"{results_df[results_df['success']]['dice_score'].mean():.3f}" if len(results_df[results_df['success']]) > 0 else "N/A"
            ]
        })
        summary_stats.to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"Excel file saved to: {excel_file}")


if __name__ == "__main__":
    main()
