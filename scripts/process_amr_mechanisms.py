#!/usr/bin/env python3
"""
Process AMR data to group genes by resistance mechanism.
Creates mechanism-based analysis as a proxy for "pathway" analysis.

Mechanisms are inferred from gene name prefixes based on ResFinder nomenclature.
"""

import pandas as pd
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"

# AMR Gene to Mechanism Mapping
# Based on standard AMR gene nomenclature from ResFinder database
MECHANISM_MAPPING = {
    # Beta-lactamases (Drug Inactivation - Hydrolysis)
    'bla': 'Beta-lactamase (Drug Inactivation)',

    # Aminoglycoside-modifying enzymes (Drug Inactivation - Modification)
    'aac': 'Aminoglycoside Acetyltransferase (Drug Inactivation)',
    'aad': 'Aminoglycoside Adenylyltransferase (Drug Inactivation)',
    'ant': 'Aminoglycoside Nucleotidyltransferase (Drug Inactivation)',
    'aph': 'Aminoglycoside Phosphotransferase (Drug Inactivation)',
    'armA': 'Aminoglycoside Methyltransferase (Target Modification)',
    'rmtA': 'Aminoglycoside Methyltransferase (Target Modification)',
    'rmtB': 'Aminoglycoside Methyltransferase (Target Modification)',
    'rmtC': 'Aminoglycoside Methyltransferase (Target Modification)',
    'rmtD': 'Aminoglycoside Methyltransferase (Target Modification)',

    # Efflux pumps
    'tet': 'Tetracycline Efflux/Ribosomal Protection',
    'oqx': 'RND Efflux Pump (Quinolone/Multidrug)',
    'qep': 'Quinolone Efflux Pump',
    'mef': 'Macrolide Efflux Pump',
    'msr': 'Macrolide Efflux Pump',
    'floR': 'Chloramphenicol Efflux Pump',
    'cml': 'Chloramphenicol Efflux Pump',
    'cat': 'Chloramphenicol Acetyltransferase (Drug Inactivation)',
    'qac': 'Quaternary Ammonium Compound Efflux',
    'emr': 'Multidrug Efflux Pump',
    'acr': 'RND Efflux Pump (Multidrug)',
    'mdt': 'Multidrug Efflux Pump',
    'norA': 'Quinolone Efflux Pump',
    'norB': 'Quinolone Efflux Pump',
    'norC': 'Quinolone Efflux Pump',

    # Target modification/protection
    'mcr': 'Colistin Resistance (Target Modification)',
    'erm': 'Ribosome Methylase (Target Modification)',
    'cfr': 'Ribosome Methylase (Target Modification)',
    'mph': 'Macrolide Phosphotransferase (Drug Inactivation)',
    'lin': 'Lincosamide Nucleotidyltransferase (Drug Inactivation)',
    'lnu': 'Lincosamide Nucleotidyltransferase (Drug Inactivation)',
    'vat': 'Streptogramin Acetyltransferase (Drug Inactivation)',
    'vgb': 'Streptogramin Lyase (Drug Inactivation)',

    # Quinolone resistance
    'qnr': 'Quinolone Resistance (Target Protection)',
    'gyr': 'DNA Gyrase (Target Mutation)',
    'par': 'Topoisomerase IV (Target Mutation)',

    # Folate pathway inhibitors
    'dfr': 'Dihydrofolate Reductase (Target Bypass)',
    'sul': 'Sulfonamide Resistance (Target Bypass)',

    # Glycopeptide resistance
    'van': 'Glycopeptide Resistance (Target Modification)',

    # Fosfomycin resistance
    'fos': 'Fosfomycin Resistance (Drug Inactivation/Target Modification)',

    # Rifampicin resistance
    'arr': 'Rifampicin ADP-ribosyltransferase (Drug Inactivation)',
    'rpo': 'RNA Polymerase (Target Mutation)',

    # Other
    'str': 'Streptomycin Resistance',
    'nim': 'Nitroimidazole Resistance',
    'ere': 'Erythromycin Esterase (Drug Inactivation)',
    'lsa': 'Lincosamide-Streptogramin Efflux',
    'optrA': 'ABC Transporter (Oxazolidinone/Phenicol Efflux)',
    'poxtA': 'ABC Transporter (Oxazolidinone/Phenicol Efflux)',
}

# Broader mechanism categories for summary
MECHANISM_CATEGORIES = {
    'Drug Inactivation': [
        'Beta-lactamase (Drug Inactivation)',
        'Aminoglycoside Acetyltransferase (Drug Inactivation)',
        'Aminoglycoside Adenylyltransferase (Drug Inactivation)',
        'Aminoglycoside Nucleotidyltransferase (Drug Inactivation)',
        'Aminoglycoside Phosphotransferase (Drug Inactivation)',
        'Chloramphenicol Acetyltransferase (Drug Inactivation)',
        'Macrolide Phosphotransferase (Drug Inactivation)',
        'Lincosamide Nucleotidyltransferase (Drug Inactivation)',
        'Streptogramin Acetyltransferase (Drug Inactivation)',
        'Streptogramin Lyase (Drug Inactivation)',
        'Erythromycin Esterase (Drug Inactivation)',
        'Rifampicin ADP-ribosyltransferase (Drug Inactivation)',
        'Fosfomycin Resistance (Drug Inactivation/Target Modification)',
    ],
    'Efflux Pump': [
        'Tetracycline Efflux/Ribosomal Protection',
        'RND Efflux Pump (Quinolone/Multidrug)',
        'Quinolone Efflux Pump',
        'Macrolide Efflux Pump',
        'Chloramphenicol Efflux Pump',
        'Quaternary Ammonium Compound Efflux',
        'Multidrug Efflux Pump',
        'Lincosamide-Streptogramin Efflux',
        'ABC Transporter (Oxazolidinone/Phenicol Efflux)',
    ],
    'Target Modification': [
        'Aminoglycoside Methyltransferase (Target Modification)',
        'Colistin Resistance (Target Modification)',
        'Ribosome Methylase (Target Modification)',
        'Glycopeptide Resistance (Target Modification)',
    ],
    'Target Protection': [
        'Quinolone Resistance (Target Protection)',
    ],
    'Target Bypass': [
        'Dihydrofolate Reductase (Target Bypass)',
        'Sulfonamide Resistance (Target Bypass)',
    ],
    'Target Mutation': [
        'DNA Gyrase (Target Mutation)',
        'Topoisomerase IV (Target Mutation)',
        'RNA Polymerase (Target Mutation)',
    ],
}


def get_mechanism(gene_name):
    """Determine resistance mechanism from gene name."""
    gene_lower = gene_name.lower()

    # Check exact matches first
    for prefix, mechanism in MECHANISM_MAPPING.items():
        if gene_lower.startswith(prefix.lower()):
            return mechanism

    # Fallback patterns
    if 'bla' in gene_lower:
        return 'Beta-lactamase (Drug Inactivation)'
    if gene_lower.startswith('tet'):
        return 'Tetracycline Efflux/Ribosomal Protection'
    if any(gene_lower.startswith(p) for p in ['aac', 'aad', 'ant', 'aph']):
        return 'Aminoglycoside Modifying Enzyme (Drug Inactivation)'

    return 'Other/Unknown Mechanism'


def get_mechanism_category(mechanism):
    """Get broad category for a specific mechanism."""
    for category, mechanisms in MECHANISM_CATEGORIES.items():
        if mechanism in mechanisms:
            return category
    return 'Other'


def load_amr_data():
    """Load AMR data from full data file."""
    amr_file = OUTPUT_DIR / "amr_full_data.csv"
    df = pd.read_csv(amr_file)
    return df


def add_mechanism_columns(df):
    """Add mechanism and category columns to dataframe."""
    df = df.copy()
    df['mechanism'] = df['Gene'].apply(get_mechanism)
    df['mechanism_category'] = df['mechanism'].apply(get_mechanism_category)
    return df


def create_mechanism_summary(df):
    """Create summary of mechanisms by sample."""
    # Get unique gene detections (not expanded by resistance class)
    unique_genes = df.drop_duplicates(subset=['Gene', 'ReadID', 'barcode'])

    summary = unique_genes.groupby(['barcode', 'farm_type', 'farm_id', 'sample_type', 'oblast']).agg({
        'Gene': 'count',
        'mechanism': lambda x: x.nunique(),
        'mechanism_category': lambda x: x.nunique()
    }).reset_index()

    summary.columns = ['barcode', 'farm_type', 'farm_id', 'sample_type', 'oblast',
                       'total_gene_detections', 'unique_mechanisms', 'unique_categories']

    return summary


def create_mechanism_matrix(df):
    """Create mechanism × sample count matrix."""
    # Get unique gene detections
    unique_genes = df.drop_duplicates(subset=['Gene', 'ReadID', 'barcode'])

    pivot = unique_genes.pivot_table(
        index='mechanism',
        columns='barcode',
        values='ReadID',
        aggfunc='count',
        fill_value=0
    )
    return pivot


def create_category_matrix(df):
    """Create mechanism category × sample count matrix."""
    unique_genes = df.drop_duplicates(subset=['Gene', 'ReadID', 'barcode'])

    pivot = unique_genes.pivot_table(
        index='mechanism_category',
        columns='barcode',
        values='ReadID',
        aggfunc='count',
        fill_value=0
    )
    return pivot


def create_gene_mechanism_mapping(df):
    """Create mapping of genes to their mechanisms."""
    gene_mechanisms = df[['Gene', 'mechanism', 'mechanism_category']].drop_duplicates()
    gene_mechanisms = gene_mechanisms.sort_values(['mechanism_category', 'mechanism', 'Gene'])
    return gene_mechanisms


def main():
    print("Processing AMR mechanisms...")
    print("=" * 50)

    # Load data
    df = load_amr_data()
    print(f"Loaded {len(df):,} AMR records")

    # Add mechanism columns
    print("\nClassifying genes by mechanism...")
    df_with_mechanisms = add_mechanism_columns(df)

    # Save full data with mechanisms
    full_file = OUTPUT_DIR / "amr_full_data_with_mechanisms.csv"
    df_with_mechanisms.to_csv(full_file, index=False)
    print(f"Created: {full_file}")

    # Create gene-mechanism mapping
    gene_mapping = create_gene_mechanism_mapping(df_with_mechanisms)
    gene_mapping_file = OUTPUT_DIR / "amr_gene_mechanism_mapping.csv"
    gene_mapping.to_csv(gene_mapping_file, index=False)
    print(f"Created: {gene_mapping_file}")

    # Create mechanism matrix
    mechanism_matrix = create_mechanism_matrix(df_with_mechanisms)
    mechanism_matrix_file = OUTPUT_DIR / "amr_mechanism_matrix.csv"
    mechanism_matrix.to_csv(mechanism_matrix_file)
    print(f"Created: {mechanism_matrix_file}")

    # Create category matrix
    category_matrix = create_category_matrix(df_with_mechanisms)
    category_matrix_file = OUTPUT_DIR / "amr_category_matrix.csv"
    category_matrix.to_csv(category_matrix_file)
    print(f"Created: {category_matrix_file}")

    # Create summary by sample
    summary = create_mechanism_summary(df_with_mechanisms)
    summary_file = OUTPUT_DIR / "amr_mechanism_summary.csv"
    summary.to_csv(summary_file, index=False)
    print(f"Created: {summary_file}")

    # Print statistics
    print("\n" + "=" * 50)
    print("MECHANISM STATISTICS")
    print("=" * 50)

    unique_genes = df_with_mechanisms.drop_duplicates(subset=['Gene', 'ReadID', 'barcode'])

    print(f"\nTotal unique gene detections: {len(unique_genes):,}")
    print(f"Unique resistance genes: {df_with_mechanisms['Gene'].nunique()}")
    print(f"Unique mechanisms: {df_with_mechanisms['mechanism'].nunique()}")
    print(f"Unique mechanism categories: {df_with_mechanisms['mechanism_category'].nunique()}")

    print("\nMechanism category distribution:")
    category_counts = unique_genes['mechanism_category'].value_counts()
    for cat, count in category_counts.items():
        pct = count / len(unique_genes) * 100
        print(f"  {cat}: {count:,} ({pct:.1f}%)")

    print("\nTop 10 specific mechanisms:")
    mechanism_counts = unique_genes['mechanism'].value_counts().head(10)
    for mech, count in mechanism_counts.items():
        pct = count / len(unique_genes) * 100
        print(f"  {mech}: {count:,} ({pct:.1f}%)")

    print("\n" + "=" * 50)
    print("Done!")


if __name__ == "__main__":
    main()
