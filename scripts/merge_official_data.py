#!/usr/bin/env python3
"""
Merge official data from multiple Argentine government sources
"""

import pandas as pd
import os
import glob
from pathlib import Path

class OfficialDataMerger:
    """Merge data from official Argentine sources"""
    
    def __init__(self, input_dir='data/official_sources', output_dir='data'):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.merged_data = None
        
    def find_csv_files(self):
        """Find all CSV files in input directory"""
        if not os.path.exists(self.input_dir):
            print(f"⚠️  Directory not found: {self.input_dir}")
            print(f"📁 Create {self.input_dir}/ and add CSV files there")
            return []
        
        csv_files = glob.glob(os.path.join(self.input_dir, '*.csv'))
        print(f"📁 Found {len(csv_files)} CSV files in {self.input_dir}")
        return csv_files
    
    def standardize_columns(self, df, source_name):
        """Standardize column names across different sources"""
        print(f"\n📋 Processing {source_name}...")
        print(f"   Original columns: {len(df.columns)}")
        print(f"   Rows: {len(df)}")
        
        # Common column mappings
        column_mappings = {
            # Company name
            'name': 'company_name',
            'empresa': 'company_name',
            'nombre': 'company_name',
            'razon_social': 'company_name',
            'company': 'company_name',
            'denominacion': 'company_name',
            
            # Industry
            'industry': 'industry',
            'industria': 'industry',
            'sector': 'industry',
            'rubro': 'industry',
            'actividad': 'industry',
            
            # Province
            'province': 'province',
            'provincia': 'province',
            'estado': 'province',
            'state': 'province',
            
            # City
            'city': 'city',
            'ciudad': 'city',
            'localidad': 'city',
            
            # Contact
            'email': 'email',
            'correo': 'email',
            'mail': 'email',
            'phone': 'phone',
            'telefono': 'phone',
            'website': 'website',
            'sitio_web': 'website',
            'web': 'website',
            'url': 'website',
            
            # Registration
            'registration_date': 'registration_date',
            'fecha_inscripcion': 'registration_date',
            'fecha_registro': 'registration_date',
        }
        
        # Rename columns (case-insensitive)
        df.columns = [col.lower().strip() for col in df.columns]
        df = df.rename(columns=column_mappings)
        
        # Add source
        df['source'] = source_name
        df['merge_date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        return df
    
    def merge_all_files(self):
        """Merge all CSV files into one dataset"""
        csv_files = self.find_csv_files()
        
        if not csv_files:
            print("\n⚠️  No CSV files found!")
            print("📁 Instructions:")
            print(f"   1. Create folder: {self.input_dir}/")
            print("   2. Download CSV files from official sources:")
            print("      - AFIP data")
            print("      - CNV listed companies")
            print("      - Other government datasets")
            print("   3. Place CSV files in that folder")
            print("   4. Run this script again")
            return None
        
        print("\n" + "=" * 60)
        print("🔄 MERGING OFFICIAL DATA")
        print("=" * 60)
        
        all_data = []
        
        for csv_file in csv_files:
            source_name = os.path.basename(csv_file).replace('.csv', '')
            
            try:
                # Read CSV
                df = pd.read_csv(csv_file, encoding='utf-8')
                
                # Standardize
                df_standardized = self.standardize_columns(df, source_name)
                
                # Add to list
                all_data.append(df_standardized)
                
                print(f"   ✅ Processed: {source_name}")
                
            except Exception as e:
                print(f"   ❌ Error processing {source_name}: {e}")
        
        if not all_data:
            print("\n❌ No valid data to merge")
            return None
        
        # Merge all dataframes
        print("\n🔗 Merging all data...")
        self.merged_data = pd.concat(all_data, ignore_index=True, sort=False)
        
        # Remove duplicates based on company name and email
        print("🔄 Removing duplicates...")
        self.merged_data = self.merged_data.drop_duplicates(
            subset=['company_name', 'email'], 
            keep='first'
        )
        
        print(f"\n✅ Final merged dataset: {len(self.merged_data)} records")
        
        return self.merged_data
    
    def save_merged_data(self, format='all'):
        """Save merged data in multiple formats"""
        if self.merged_data is None:
            print("❌ No data to save")
            return
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # CSV
        if format in ['csv', 'all']:
            output_csv = os.path.join(self.output_dir, 'argentina_companies_merged.csv')
            self.merged_data.to_csv(output_csv, index=False, encoding='utf-8')
            print(f"✅ Saved CSV: {output_csv}")
        
        # Excel
        if format in ['excel', 'all']:
            try:
                output_xlsx = os.path.join(self.output_dir, 'argentina_companies_merged.xlsx')
                self.merged_data.to_excel(output_xlsx, index=False, sheet_name='Empresas')
                print(f"✅ Saved Excel: {output_xlsx}")
            except ImportError:
                print("⚠️  openpyxl not installed. Run: pip install openpyxl")
        
        # JSON
        if format in ['json', 'all']:
            output_json = os.path.join(self.output_dir, 'argentina_companies_merged.json')
            self.merged_data.to_json(output_json, orient='records', force_ascii=False, indent=2)
            print(f"✅ Saved JSON: {output_json}")
    
    def print_statistics(self):
        """Print statistics about merged data"""
        if self.merged_data is None:
            return
        
        print("\n" + "=" * 60)
        print("📊 MERGED DATA STATISTICS")
        print("=" * 60)
        
        print(f"\nTotal records: {len(self.merged_data)}")
        
        if 'source' in self.merged_data.columns:
            print(f"\nRecords by source:")
            sources = self.merged_data['source'].value_counts()
            for source, count in sources.items():
                print(f"  - {source}: {count}")
        
        if 'industry' in self.merged_data.columns:
            print(f"\nRecords by industry (top 10):")
            industries = self.merged_data['industry'].value_counts().head(10)
            for industry, count in industries.items():
                if pd.notna(industry):
                    print(f"  - {industry}: {count}")
        
        if 'province' in self.merged_data.columns:
            print(f"\nRecords by province (top 10):")
            provinces = self.merged_data['province'].value_counts().head(10)
            for province, count in provinces.items():
                if pd.notna(province):
                    print(f"  - {province}: {count}")
        
        print(f"\nColumns in final dataset:")
        for col in self.merged_data.columns:
            non_null = self.merged_data[col].notna().sum()
            print(f"  - {col}: {non_null} non-null values")


def main():
    """Main function"""
    print("🇦🇷 OFFICIAL ARGENTINE DATA MERGER")
    print("=" * 60)
    
    merger = OfficialDataMerger()
    
    # Merge files
    merged = merger.merge_all_files()
    
    if merged is not None:
        # Save in multiple formats
        merger.save_merged_data(format='all')
        
        # Print statistics
        merger.print_statistics()
        
        print("\n" + "=" * 60)
        print("✅ MERGE COMPLETE!")
        print("=" * 60)
        print("\nFiles created:")
        print("  - data/argentina_companies_merged.csv")
        print("  - data/argentina_companies_merged.xlsx")
        print("  - data/argentina_companies_merged.json")
        print("\nNext steps:")
        print("  1. Use these files with filter scripts")
        print("  2. Export to your CRM")
        print("  3. Use for marketing campaigns")
    else:
        print("\n⚠️  No data was merged. Check your CSV files!")


if __name__ == "__main__":
    main()
