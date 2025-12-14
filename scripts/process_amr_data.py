#!/usr/bin/env python3
"""
Process antimicrobial resistance (AMR) data from metagenomics analysis.
Creates aggregated AMR data merged with farm metadata for visualization.

Output: output/amr_by_sample.csv
"""

import pandas as pd
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
EXPORT_DIR = BASE_DIR / "export"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)


def load_barcode_mapping():
    """Load barcode to farm metadata mapping."""
    mapping_file = OUTPUT_DIR / "barcode_farm_mapping.csv"
    return pd.read_csv(mapping_file)


def load_all_amr_data():
    """Load AMR data from all barcode files."""
    amr_dir = EXPORT_DIR / "antimicrobial_resistance"

    all_data = []

    for i in range(1, 25):
        barcode = f"barcode{i:02d}"
        amr_file = amr_dir / f"amr_{barcode}.csv"

        if amr_file.exists():
            df = pd.read_csv(amr_file)
            if len(df) > 0:
                df['barcode'] = barcode
                all_data.append(df)
            else:
                print(f"  {barcode}: empty file")
        else:
            print(f"  {barcode}: file not found")

    if all_data:
        combined = pd.concat(all_data, ignore_index=True)
        print(f"\nLoaded {len(combined):,} AMR records from {len(all_data)} files")
        return combined
    return pd.DataFrame()


def parse_resistance_classes(amr_df):
    """Parse multi-drug resistance (semicolon-separated) into individual classes."""
    # Expand resistance column (semicolon-separated values)
    expanded_rows = []

    for _, row in amr_df.iterrows():
        resistance = row['Resistance']
        if pd.isna(resistance) or resistance == '':
            resistance_classes = ['Unknown']
        else:
            resistance_classes = [r.strip() for r in str(resistance).split(';')]

        for res_class in resistance_classes:
            new_row = row.copy()
            new_row['resistance_class'] = res_class
            expanded_rows.append(new_row)

    return pd.DataFrame(expanded_rows)


def create_amr_summary(amr_df, mapping):
    """Create summary statistics per sample."""
    # Merge with farm metadata
    merged = amr_df.merge(
        mapping[['barcode', 'farm_type', 'farm_id', 'sample_type', 'oblast']],
        on='barcode',
        how='left'
    )

    # Gene counts per sample
    gene_counts = merged.groupby(['barcode', 'farm_type', 'farm_id', 'sample_type', 'oblast']).agg({
        'Gene': 'count',
        'ReadID': 'nunique'
    }).reset_index()
    gene_counts.columns = ['barcode', 'farm_type', 'farm_id', 'sample_type', 'oblast',
                           'total_gene_detections', 'unique_reads']

    # Unique genes per sample
    unique_genes = merged.groupby('barcode')['Gene'].nunique().reset_index()
    unique_genes.columns = ['barcode', 'unique_genes']

    # Unique resistance classes per sample
    unique_classes = merged.groupby('barcode')['resistance_class'].nunique().reset_index()
    unique_classes.columns = ['barcode', 'unique_resistance_classes']

    # Merge all summaries
    summary = gene_counts.merge(unique_genes, on='barcode', how='left')
    summary = summary.merge(unique_classes, on='barcode', how='left')

    return summary, merged


def create_gene_by_sample_matrix(merged_df):
    """Create gene × sample count matrix."""
    pivot = merged_df.pivot_table(
        index='Gene',
        columns='barcode',
        values='ReadID',
        aggfunc='count',
        fill_value=0
    )
    return pivot


def create_resistance_class_by_sample(merged_df):
    """Create resistance class × sample count matrix."""
    pivot = merged_df.pivot_table(
        index='resistance_class',
        columns='barcode',
        values='ReadID',
        aggfunc='count',
        fill_value=0
    )
    return pivot


def main():
    print("Processing AMR data...")
    print("=" * 50)

    # Load mapping
    mapping = load_barcode_mapping()
    print(f"Loaded metadata for {len(mapping)} barcodes")

    # Load all AMR data
    print("\nLoading AMR files:")
    amr_df = load_all_amr_data()

    if amr_df.empty:
        print("No AMR data found!")
        return

    # Parse multi-drug resistance
    print("\nParsing resistance classes...")
    amr_expanded = parse_resistance_classes(amr_df)
    print(f"Expanded to {len(amr_expanded):,} records (multi-drug parsed)")

    # Create summary
    print("\nCreating sample summaries...")
    summary, merged = create_amr_summary(amr_expanded, mapping)

    # Save outputs
    # 1. Sample summary
    summary_file = OUTPUT_DIR / "amr_by_sample.csv"
    summary.to_csv(summary_file, index=False)
    print(f"\nCreated: {summary_file}")

    # 2. Full merged data (for detailed analysis)
    full_file = OUTPUT_DIR / "amr_full_data.csv"
    merged.to_csv(full_file, index=False)
    print(f"Created: {full_file}")

    # 3. Gene × sample matrix
    gene_matrix = create_gene_by_sample_matrix(merged)
    gene_matrix_file = OUTPUT_DIR / "amr_gene_matrix.csv"
    gene_matrix.to_csv(gene_matrix_file)
    print(f"Created: {gene_matrix_file}")

    # 4. Resistance class × sample matrix
    class_matrix = create_resistance_class_by_sample(merged)
    class_matrix_file = OUTPUT_DIR / "amr_resistance_class_matrix.csv"
    class_matrix.to_csv(class_matrix_file)
    print(f"Created: {class_matrix_file}")

    # Print summary statistics
    print("\n" + "=" * 50)
    print("AMR DATA SUMMARY")
    print("=" * 50)
    print(f"\nTotal gene detections: {len(amr_df):,}")
    print(f"Unique resistance genes: {amr_df['Gene'].nunique()}")
    print(f"Unique resistance classes: {amr_expanded['resistance_class'].nunique()}")

    print("\nSamples with AMR data:")
    print(f"  Total: {summary['barcode'].nunique()} / 24")

    print("\nBy farm type:")
    farm_summary = summary.groupby('farm_type').agg({
        'barcode': 'count',
        'total_gene_detections': 'sum',
        'unique_genes': 'mean'
    }).round(1)
    farm_summary.columns = ['samples', 'total_detections', 'avg_unique_genes']
    print(farm_summary)

    print("\nTop 10 resistance genes:")
    top_genes = amr_df['Gene'].value_counts().head(10)
    for gene, count in top_genes.items():
        print(f"  {gene}: {count:,}")

    print("\nResistance classes:")
    class_counts = amr_expanded['resistance_class'].value_counts()
    for res_class, count in class_counts.items():
        print(f"  {res_class}: {count:,}")

    print("\n" + "=" * 50)
    print("Done!")


if __name__ == "__main__":
    main()
