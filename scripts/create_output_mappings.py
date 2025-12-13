#!/usr/bin/env python3
"""
Create output mappings for bio-phagent project:
1. barcode_farm_mapping.csv - Maps barcodes to farm metadata
2. taxonomy_barcode_bacteria.csv - Taxonomy with barcode and farm info
3. diversity_indices.csv - Diversity metrics from rarefied data with farm metadata
"""

import pandas as pd
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
EXPORT_DIR = BASE_DIR / "export"
WIP_DIR = BASE_DIR / "wip"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


def load_metadata():
    """Load and normalize metadata from Excel file."""
    metadata_file = WIP_DIR / "[WIP] UA_FARM_WW_CLEAN_METADATA.xlsx"
    df = pd.read_excel(metadata_file)

    # Normalize barcode format: BC01 -> barcode01
    df['barcode'] = df['Barcode'].str.replace('BC', 'barcode').str.zfill(9)
    df['barcode'] = df['Barcode'].apply(lambda x: f"barcode{int(x.replace('BC', '')):02d}")

    # Rename columns to snake_case
    df = df.rename(columns={
        'Sample ID': 'sample_id',
        'Farm Type': 'farm_type',
        'Farm ID': 'farm_id',
        'Sample Type': 'sample_type',
        'Oblast': 'oblast',
        'Collection Period': 'collection_period'
    })

    return df[['barcode', 'sample_id', 'farm_type', 'farm_id', 'sample_type', 'oblast', 'collection_period']]


def create_barcode_farm_mapping(metadata):
    """Create barcode to farm mapping CSV."""
    output_file = OUTPUT_DIR / "barcode_farm_mapping.csv"
    metadata.to_csv(output_file, index=False)
    print(f"Created: {output_file}")
    return metadata


def create_taxonomy_barcode_bacteria(metadata):
    """Create taxonomy-barcode-bacteria mapping from abundance data."""
    abundance_dir = EXPORT_DIR / "abundances" / "table"

    # Get barcode columns
    barcode_cols = [f"barcode{i:02d}" for i in range(1, 25)]

    all_data = []

    # Process each taxonomy level
    for csv_file in abundance_dir.glob("abundance_*.csv"):
        # Extract taxon level from filename (e.g., abundance_genus_table.csv -> genus)
        taxon_level = csv_file.stem.replace("abundance_", "").replace("_table", "")

        df = pd.read_csv(csv_file)

        # Get the first column name (taxon name column)
        taxon_col = df.columns[0]

        # Get taxonomy column if exists
        tax_col = 'tax' if 'tax' in df.columns else None

        # Melt the dataframe to long format
        for barcode in barcode_cols:
            if barcode in df.columns:
                for _, row in df.iterrows():
                    abundance = row[barcode]
                    if abundance > 0:  # Only include non-zero abundances
                        record = {
                            'barcode': barcode,
                            'taxon_level': taxon_level,
                            'taxon_name': row[taxon_col],
                            'abundance': abundance,
                            'full_taxonomy': row[tax_col] if tax_col else ''
                        }
                        all_data.append(record)

    # Create dataframe
    taxonomy_df = pd.DataFrame(all_data)

    # Merge with metadata
    merged_df = taxonomy_df.merge(
        metadata[['barcode', 'farm_type', 'farm_id', 'sample_type', 'oblast']],
        on='barcode',
        how='left'
    )

    # Reorder columns
    final_cols = ['barcode', 'farm_type', 'farm_id', 'sample_type', 'oblast',
                  'taxon_level', 'taxon_name', 'abundance', 'full_taxonomy']
    merged_df = merged_df[final_cols]

    # Sort by barcode and taxon level
    merged_df = merged_df.sort_values(['barcode', 'taxon_level', 'taxon_name'])

    output_file = OUTPUT_DIR / "taxonomy_barcode_bacteria.csv"
    merged_df.to_csv(output_file, index=False)
    print(f"Created: {output_file}")
    print(f"Total records: {len(merged_df)}")

    return merged_df


def create_diversity_indices_csv(metadata):
    """Extract diversity indices from rarefied data and merge with farm metadata."""
    rarefied_file = EXPORT_DIR / "abundances" / "rarefied" / "rarefied_abundance_class_table.csv"

    # Read rarefied data (indices as rows, barcodes as columns)
    df = pd.read_csv(rarefied_file)

    # Get barcode columns
    barcode_cols = [col for col in df.columns if col.startswith('barcode')]

    # Transpose: indices become columns, barcodes become rows
    df_transposed = df.set_index('Indices')[barcode_cols].T.reset_index()
    df_transposed = df_transposed.rename(columns={'index': 'barcode'})

    # Rename columns to snake_case
    column_mapping = {
        'Shannon diversity index': 'shannon_index',
        'Simpson\'s index': 'simpson_index',
        'Inverse Simpson\'s index': 'inverse_simpson',
        'Berger Parker index': 'berger_parker',
        'Pielou\'s evenness': 'pielou_evenness',
        'Fisher\'s alpha': 'fisher_alpha',
        'Richness': 'richness',
        'Total counts': 'total_counts',
        'Effective number of species': 'effective_species'
    }
    df_transposed = df_transposed.rename(columns=column_mapping)

    # Merge with farm metadata
    merged_df = df_transposed.merge(
        metadata[['barcode', 'farm_type', 'farm_id', 'sample_type', 'oblast']],
        on='barcode',
        how='left'
    )

    # Reorder columns: metadata first, then diversity indices
    index_cols = [col for col in column_mapping.values() if col in merged_df.columns]
    final_cols = ['barcode', 'farm_type', 'farm_id', 'sample_type', 'oblast'] + index_cols
    merged_df = merged_df[final_cols]

    # Sort by barcode
    merged_df = merged_df.sort_values('barcode')

    output_file = OUTPUT_DIR / "diversity_indices.csv"
    merged_df.to_csv(output_file, index=False)
    print(f"Created: {output_file}")
    print(f"Diversity records: {len(merged_df)}")

    return merged_df


def main():
    print("Creating output mappings...")
    print("=" * 50)

    # Load metadata
    metadata = load_metadata()
    print(f"Loaded metadata for {len(metadata)} barcodes")

    # Create barcode-farm mapping
    create_barcode_farm_mapping(metadata)

    # Create taxonomy-barcode-bacteria mapping
    create_taxonomy_barcode_bacteria(metadata)

    # Create diversity indices from rarefied data
    create_diversity_indices_csv(metadata)

    print("=" * 50)
    print("Done!")


if __name__ == "__main__":
    main()
