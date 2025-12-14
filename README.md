# Bio-Phagent

> Metagenomics analysis pipeline for bacteriophage research from Ukrainian farm wastewater samples

## Quick Start

```bash
# Install dependencies
pip install pandas openpyxl plotly scipy matplotlib seaborn jupyter

# Run the full pipeline
python scripts/create_output_mappings.py
python scripts/process_amr_data.py
python scripts/extract_species_by_barcode.py --all
```

## Project Structure

```
bio-phagent/
├── input/                              # Source data
│   ├── wf-metagenomics-report_*.html   # Main workflow report
│   └── wrapper.html                    # Export tool
├── wip/                                # Source metadata
│   └── [WIP] UA_FARM_WW_CLEAN_METADATA.xlsx
├── export/                             # Exported CSV data
│   ├── abundances/
│   │   ├── table/                      # 6 taxonomy levels
│   │   └── rarefied/                   # Normalized data
│   └── antimicrobial_resistance/       # 24 barcode AMR files
├── output/                             # Processed outputs
│   ├── basic/                          # Taxonomy, mapping, diversity
│   ├── amr/                            # AMR analysis results
│   └── xlsx/                           # Excel outputs
├── scripts/                            # Processing scripts
├── REPRODUCE.md                        # Step-by-step guide
└── WORKFLOW.md                         # Pipeline diagrams
```

## Prerequisites

- Python 3.9+
- Required packages:

```bash
pip install pandas openpyxl plotly scipy matplotlib seaborn jupyter
```

## Scripts

### 1. create_output_mappings.py

Creates foundational data mappings from raw exports. **Must run first.**

```bash
python scripts/create_output_mappings.py
```

**Outputs:**
- `output/basic/barcode_farm_mapping.csv` - 24 sample metadata records
- `output/basic/taxonomy_barcode_bacteria.csv` - 6,442 taxonomy records
- `output/basic/diversity_indices.csv` - 24 diversity metrics

### 2. process_amr_data.py

Processes antimicrobial resistance data from all barcodes.

```bash
python scripts/process_amr_data.py
```

**Outputs:**
- `output/amr/amr_by_sample.csv` - Sample-level summary
- `output/amr/amr_full_data.csv` - 51,451 detailed records
- `output/amr/amr_gene_matrix.csv` - 198 genes x 24 samples
- `output/amr/amr_resistance_class_matrix.csv` - 47 classes x 24 samples

### 3. extract_species_by_barcode.py

Extracts dominant bacterial species per sample to Excel.

```bash
# All barcodes
python scripts/extract_species_by_barcode.py --all

# Specific barcodes
python scripts/extract_species_by_barcode.py BC01 BC02 BC03
```

**Output:**
- Adds `BC01_Species`, `BC02_Species`, etc. sheets to Excel file

## Jupyter Notebooks

Interactive visualizations are available in:

- `output/basic/taxonomy_visualization.ipynb` - Taxonomy analysis
- `output/amr/amr_visualization.ipynb` - AMR analysis

```bash
jupyter notebook output/basic/taxonomy_visualization.ipynb
```

## Data Summary

| Metric | Value |
|--------|-------|
| Total Samples | 24 barcodes |
| Farm Types | Pig, Poultry |
| Sample Types | Native, Enriched |
| Taxonomy Records | 6,442 |
| AMR Records | 51,451 |
| Resistance Genes | 198 |
| Resistance Classes | 47 |

## Documentation

- [REPRODUCE.md](REPRODUCE.md) - Complete reproduction guide
- [WORKFLOW.md](WORKFLOW.md) - Pipeline diagrams and data flow

## License

Research project - Kyiv School of Economics
