# Taxonomy Data Build Documentation

This document describes how the taxonomy-barcode-bacteria mapping was constructed from the metagenomics data.

## Overview

The taxonomy data pipeline transforms raw metagenomics abundance tables into a structured format that links:
- **Barcodes** (sample identifiers) → **Taxonomy** (bacteria classification)
- **Barcodes** → **Farm metadata** (farm type, location, sample type)

**Final output**: 6,442 records mapping 24 barcodes to their detected bacteria across 6 taxonomy levels.

---

## Data Sources

### 1. Metagenomics Abundance Data

There are **two abundance data folders** with different purposes:

#### 1a. Raw Abundance Data (Used for Taxonomy Mapping)

**Location**: `export/abundances/table/`

| File | Description | Rows |
|------|-------------|------|
| `abundance_phylum_table.csv` | Phylum-level classification | ~30 |
| `abundance_class_table.csv` | Class-level classification | ~50 |
| `abundance_order_table.csv` | Order-level classification | ~100 |
| `abundance_family_table.csv` | Family-level classification | ~250 |
| `abundance_genus_table.csv` | Genus-level classification | ~500 |
| `abundance_species_table.csv` | Species-level classification | ~1500 |

**Source format** (wide format):
```
genus,barcode01,barcode02,...,barcode24,total,superkingdom,kingdom,phylum,class,order,family,tax
Escherichia,2932,15234,...,1205,525402,Bacteria,Bacteria_none,Pseudomonadota,Gammaproteobacteria,Enterobacterales,Enterobacteriaceae,Bacteria;Bacteria_none;Pseudomonadota;...
```

**Note**: Values are raw read counts (e.g., 2932, 15234). This data is used for taxonomy mapping.

#### 1b. Rarefied Abundance Data (For Diversity Analysis)

**Location**: `export/abundances/rarefied/`

| File | Description |
|------|-------------|
| `rarefied_abundance_phylum_table.csv` | Rarefied phylum data |
| `rarefied_abundance_class_table.csv` | **Contains diversity indices** |
| `rarefied_abundance_order_table.csv` | Rarefied order data |
| `rarefied_abundance_family_table.csv` | Rarefied family data |
| `rarefied_abundance_genus_table.csv` | Rarefied genus data |
| `rarefied_abundance_species_table.csv` | Rarefied species data |

**Rarefaction** is a normalization technique that subsamples reads to the same depth across all samples, enabling fair comparison of diversity metrics.

**Key difference from raw data**:
- Values are small integers (0, 1, 2) instead of large counts
- Allows valid comparison of alpha diversity across samples with different sequencing depths

**Diversity Indices** (in `rarefied_abundance_class_table.csv`):

| Index | Description |
|-------|-------------|
| Shannon diversity index | Measures species diversity (higher = more diverse) |
| Simpson's index | Probability two individuals are different species |
| Inverse Simpson's index | Effective number of equally abundant species |
| Berger Parker index | Proportional abundance of most abundant species |
| Pielou's evenness | How evenly individuals are distributed among species |
| Fisher's alpha | Diversity metric robust to sample size |
| Richness | Total number of unique taxa |
| Total counts | Total reads in sample |

**Example diversity data**:
```csv
Indices,barcode01,barcode02,...,barcode24,total
Shannon diversity index,2.79,3.12,1.58,0.61,...,2.82
Simpson's index,0.9,0.77,0.5,0.17,...,0.78
Richness,57.0,411.0,159.0,48.0,...,1267.0
```

#### Comparison: table/ vs rarefied/

| Aspect | `table/` (Raw) | `rarefied/` (Normalized) |
|--------|----------------|--------------------------|
| Values | Large counts (2932, 15234) | Small integers (0, 1, 2) |
| Purpose | Abundance analysis, taxonomy | Diversity comparison |
| Use case | "How many reads of E. coli?" | "Which sample is more diverse?" |
| Bias | Affected by sequencing depth | Normalized for fair comparison |

### 2. Farm Metadata

**Location**: `wip/[WIP] UA_FARM_WW_CLEAN_METADATA.xlsx`

| Column | Description | Example Values |
|--------|-------------|----------------|
| Barcode | Sample ID (BC01-BC24) | BC01, BC02, ... |
| Sample ID | Original sample code | 1.1., 2., 3. н |
| Farm Type | Type of farm | Poultry, Pig |
| Farm ID | Farm identifier | poultry #1, pig #3 |
| Sample Type | Processing method | Native, Enriched |
| Oblast | Ukrainian region | Kyiv Oblast, Zhytomyr Oblast |
| Collection Period | When collected | JAN-FEB 2025 |

**Sample distribution**:
- **Poultry farms**: 4 samples (2 Native, 2 Enriched)
- **Pig farms**: 20 samples (10 Native, 10 Enriched)
- **Regions**: 6 oblasts

---

## Processing Pipeline

### Script: `scripts/create_output_mappings.py`

#### Step 1: Load Metadata
```python
def load_metadata():
    # Read Excel file
    df = pd.read_excel(metadata_file)

    # Normalize barcode format: BC01 -> barcode01
    df['barcode'] = df['Barcode'].apply(lambda x: f"barcode{int(x.replace('BC', '')):02d}")

    # Rename columns to snake_case
    df = df.rename(columns={
        'Sample ID': 'sample_id',
        'Farm Type': 'farm_type',
        ...
    })
```

#### Step 2: Process Abundance Tables
```python
def create_taxonomy_barcode_bacteria(metadata):
    # For each abundance CSV file (phylum, class, order, family, genus, species):
    for csv_file in abundance_dir.glob("abundance_*.csv"):
        # Extract taxon level from filename
        taxon_level = csv_file.stem.replace("abundance_", "").replace("_table", "")
        # e.g., "abundance_genus_table.csv" -> "genus"

        # Read wide-format data
        df = pd.read_csv(csv_file)

        # Transform to long format (melt)
        for barcode in barcode_cols:
            for _, row in df.iterrows():
                if row[barcode] > 0:  # Only non-zero abundances
                    record = {
                        'barcode': barcode,
                        'taxon_level': taxon_level,
                        'taxon_name': row[taxon_col],
                        'abundance': row[barcode],
                        'full_taxonomy': row['tax']
                    }
```

#### Step 3: Merge with Metadata
```python
# Join taxonomy data with farm metadata
merged_df = taxonomy_df.merge(
    metadata[['barcode', 'farm_type', 'farm_id', 'sample_type', 'oblast']],
    on='barcode',
    how='left'
)
```

#### Step 4: Export
```python
# Sort and save
merged_df = merged_df.sort_values(['barcode', 'taxon_level', 'taxon_name'])
merged_df.to_csv('taxonomy_barcode_bacteria.csv', index=False)
```

---

## Output Files

### 1. `barcode_farm_mapping.csv`

Maps barcodes to farm metadata.

| Column | Type | Description |
|--------|------|-------------|
| barcode | string | Sample ID (barcode01-barcode24) |
| sample_id | string | Original sample code |
| farm_type | string | Poultry or Pig |
| farm_id | string | Farm identifier |
| sample_type | string | Native or Enriched |
| oblast | string | Ukrainian region |
| collection_period | string | Collection timeframe |

**Example**:
```csv
barcode,sample_id,farm_type,farm_id,sample_type,oblast,collection_period
barcode01,1.1.,Poultry,poultry #1,Native,Zaporizhzhia Oblast,JAN-FEB 2025
barcode02,1.1. н,Poultry,poultry #1,Enriched,Zaporizhzhia Oblast,JAN-FEB 2025
```

### 2. `taxonomy_barcode_bacteria.csv`

Complete taxonomy-barcode-bacteria mapping (6,442 records).

| Column | Type | Description |
|--------|------|-------------|
| barcode | string | Sample ID |
| farm_type | string | Poultry or Pig |
| farm_id | string | Farm identifier |
| sample_type | string | Native or Enriched |
| oblast | string | Ukrainian region |
| taxon_level | string | phylum, class, order, family, genus, or species |
| taxon_name | string | Taxon name (e.g., Escherichia) |
| abundance | integer | Read count |
| full_taxonomy | string | Full taxonomy path (semicolon-separated) |

**Example**:
```csv
barcode,farm_type,farm_id,sample_type,oblast,taxon_level,taxon_name,abundance,full_taxonomy
barcode01,Poultry,poultry #1,Native,Zaporizhzhia Oblast,genus,Escherichia,2932,Bacteria;Bacteria_none;Pseudomonadota;Gammaproteobacteria;Enterobacterales;Enterobacteriaceae;Escherichia
barcode01,Poultry,poultry #1,Native,Zaporizhzhia Oblast,genus,Klebsiella,3782,Bacteria;Bacteria_none;Pseudomonadota;Gammaproteobacteria;Enterobacterales;Enterobacteriaceae;Klebsiella
```

**Taxonomy hierarchy** (full_taxonomy column):
```
Superkingdom;Kingdom;Phylum;Class;Order;Family;Genus
Bacteria;Bacteria_none;Pseudomonadota;Gammaproteobacteria;Enterobacterales;Enterobacteriaceae;Escherichia
```

### 3. `diversity_indices.csv`

Diversity metrics extracted from rarefied data (24 records, one per barcode).

| Column | Type | Description |
|--------|------|-------------|
| barcode | string | Sample ID (barcode01-barcode24) |
| farm_type | string | Poultry or Pig |
| farm_id | string | Farm identifier |
| sample_type | string | Native or Enriched |
| oblast | string | Ukrainian region |
| shannon_index | float | Shannon diversity index (higher = more diverse) |
| simpson_index | float | Simpson's index (0-1, probability two are different) |
| inverse_simpson | float | Inverse Simpson's index |
| berger_parker | float | Berger Parker index (dominance) |
| pielou_evenness | float | Pielou's evenness (0-1, distribution equality) |
| fisher_alpha | float | Fisher's alpha diversity |
| richness | float | Number of unique taxa |
| total_counts | float | Total read count in sample |
| effective_species | float | Effective number of species |

**Example**:
```csv
barcode,farm_type,farm_id,sample_type,oblast,shannon_index,simpson_index,...,richness
barcode01,Poultry,poultry #1,Native,Zaporizhzhia Oblast,2.79,0.9,...,57.0
barcode02,Poultry,poultry #1,Enriched,Zaporizhzhia Oblast,3.12,0.77,...,411.0
```

**Important**: Use this file for diversity comparisons between samples/groups. Raw abundance data (`taxonomy_barcode_bacteria.csv`) should NOT be used for diversity comparisons due to sequencing depth bias.

---

## Visualization

### Notebook: `output/taxonomy_visualization.ipynb`

Interactive Jupyter notebook with visualizations:

1. **Barcode → Taxonomy** (using raw abundance data)
   - Stacked bar: Phylum composition per barcode
   - Heatmap: Top 20 genera across barcodes
   - Sunburst: Interactive taxonomy hierarchy (Plotly)

2. **Farm Type Comparison (Pig vs Poultry)**
   - Bar charts: Top 15 genera per farm type
   - Box plots: Diversity metrics (richness, Shannon index)
   - Differential abundance: Log2 fold change

3. **Additional Analysis**
   - Native vs Enriched comparison
   - Regional (Oblast) distribution

4. **Diversity Analysis (Rarefied Data)** - NEW
   - Shannon diversity by farm type (box plots with statistical tests)
   - Simpson's index comparison
   - Taxa richness by farm type and sample type
   - Shannon vs Richness scatter plot
   - Regional diversity comparison
   - Mann-Whitney U statistical tests (Pig vs Poultry)
   - Diversity indices heatmap (all metrics, normalized)

---

## How to Regenerate

### Prerequisites
```bash
pip install pandas openpyxl
```

### Run the script
```bash
cd /path/to/bio-phagent
python scripts/create_output_mappings.py
```

### Expected output
```
Creating output mappings...
==================================================
Loaded metadata for 24 barcodes
Created: output/barcode_farm_mapping.csv
Created: output/taxonomy_barcode_bacteria.csv
Total records: 6442
Created: output/diversity_indices.csv
Diversity records: 24
==================================================
Done!
```

---

## Data Statistics

| Metric | Value |
|--------|-------|
| Total barcodes | 24 |
| Total taxonomy records | 6,442 |
| Unique phyla | ~10 |
| Unique classes | ~30 |
| Unique orders | ~60 |
| Unique families | ~150 |
| Unique genera | ~350 |
| Unique species | ~800 |
| Poultry samples | 4 |
| Pig samples | 20 |
| Regions covered | 6 oblasts |

---

## File Structure

```
bio-phagent/
├── export/
│   └── abundances/
│       ├── table/                           # Raw abundance data
│       │   ├── abundance_phylum_table.csv
│       │   ├── abundance_class_table.csv
│       │   ├── abundance_order_table.csv
│       │   ├── abundance_family_table.csv
│       │   ├── abundance_genus_table.csv
│       │   └── abundance_species_table.csv
│       └── rarefied/                        # Rarefied/normalized data
│           ├── rarefied_abundance_phylum_table.csv
│           ├── rarefied_abundance_class_table.csv  # Contains diversity indices
│           ├── rarefied_abundance_order_table.csv
│           ├── rarefied_abundance_family_table.csv
│           ├── rarefied_abundance_genus_table.csv
│           └── rarefied_abundance_species_table.csv
├── wip/
│   └── [WIP] UA_FARM_WW_CLEAN_METADATA.xlsx
├── scripts/
│   └── create_output_mappings.py
└── output/
    ├── barcode_farm_mapping.csv             # Barcode → farm metadata
    ├── taxonomy_barcode_bacteria.csv        # Taxonomy mapping (6,442 records)
    ├── diversity_indices.csv                # Diversity metrics (24 records)
    ├── taxonomy_visualization.ipynb
    └── TAXONOMY_BUILD.md (this file)
```

---

*Generated: December 2024*
*Updated: December 2024 - Added diversity_indices.csv and rarefied data analysis*
