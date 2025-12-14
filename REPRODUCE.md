# How to Reproduce the Data Pipeline

This document provides step-by-step instructions to reproduce all data in this project from scratch.

---

## Prerequisites

### Check Python Version

```bash
python --version  # Requires 3.9+
```

### Create Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
```

### Install Python Packages

```bash
pip install pandas openpyxl plotly scipy matplotlib seaborn jupyter
```

### Required Files

Ensure you have the following source files:
- `input/wf-metagenomics-report_metagenomics-farms-ukr.html` - Main HTML report from wf-metagenomics pipeline
- `input/wrapper.html` - Export tool for abundance tables and AMR data
- `wip/[WIP] UA_FARM_WW_CLEAN_METADATA.xlsx` - Sample metadata

---

## Step 1: Export Data from HTML Report

The HTML report contains embedded data tables that must be exported to CSV files.

### 1.1 Start Local HTTP Server

```bash
cd /path/to/bio-phagent
python3 -m http.server 8000
```

Keep this server running in the background.

### 1.2 Export Abundance Tables

1. Open browser to: `http://localhost:8000/input/wrapper.html`

2. The wrapper loads the main HTML report in an iframe

3. Navigate to each abundance table section and click **"Export CSV"** buttons

4. Save exported files to `/export/abundances/table/`:
   - `abundance_phylum_table.csv`
   - `abundance_class_table.csv`
   - `abundance_order_table.csv`
   - `abundance_family_table.csv`
   - `abundance_genus_table.csv`
   - `abundance_species_table.csv`

5. Navigate to rarefied abundance sections and export to `/export/abundances/rarefied/`:
   - `rarefied_abundance_phylum_table.csv`
   - `rarefied_abundance_class_table.csv` (contains diversity indices)
   - `rarefied_abundance_order_table.csv`
   - `rarefied_abundance_family_table.csv`
   - `rarefied_abundance_genus_table.csv`
   - `rarefied_abundance_species_table.csv`

### 1.3 Export Antimicrobial Resistance (AMR) Data

1. This wrapper automatically:
   - Expands all AMR accordion sections
   - Adds per-barcode export buttons (e.g., "Export CSV (barcode01)")

2. Click each barcode's export button to download AMR data

3. Save files to `/export/antimicrobial_resistance/`:
   - `amr_barcode01.csv`
   - `amr_barcode02.csv`
   - ... (through `amr_barcode24.csv`)

### 1.4 Export Additional Data (Optional)

Export any other tables as needed:
- `/export/alpha_diversity/alpha_diversity_table.csv`
- `/export/number_of_reads/number_of_reads_table.csv`

### Verify Step 1

```bash
# Check abundance files
ls -la export/abundances/table/
# Expected: 6 files (abundance_*.csv)

ls -la export/abundances/rarefied/
# Expected: 6 files (rarefied_abundance_*.csv)

# Check AMR files
ls export/antimicrobial_resistance/ | wc -l
# Expected: 24 files

# Validate CSV format
head -3 export/abundances/table/abundance_species_table.csv
```

### Expected `/export` Directory Structure

```
export/
    abundances/
        table/
            abundance_phylum_table.csv
            abundance_class_table.csv
            abundance_order_table.csv
            abundance_family_table.csv
            abundance_genus_table.csv
            abundance_species_table.csv
        rarefied/
            rarefied_abundance_phylum_table.csv
            rarefied_abundance_class_table.csv
            rarefied_abundance_order_table.csv
            rarefied_abundance_family_table.csv
            rarefied_abundance_genus_table.csv
            rarefied_abundance_species_table.csv
    antimicrobial_resistance/
        amr_barcode01.csv
        amr_barcode02.csv
        ... (amr_barcode01.csv through amr_barcode24.csv)
    alpha_diversity/
        alpha_diversity_table.csv
    number_of_reads/
        number_of_reads_table.csv
```

---

## Step 2: Run Python Processing Scripts

### 2.1 Create Output Mappings (Run First)

**Script:** `scripts/create_output_mappings.py`

Creates foundational data mappings from raw exports. **Must run first** - other scripts depend on this.

#### Command

```bash
python scripts/create_output_mappings.py
```

#### Arguments

| Arg | Type | Required | Description |
|-----|------|----------|-------------|
| *(none)* | - | - | No command-line arguments |

#### Input Files

| File | Description |
|------|-------------|
| `wip/[WIP] UA_FARM_WW_CLEAN_METADATA.xlsx` | Farm metadata |
| `export/abundances/table/abundance_*.csv` | 6 taxonomy level files |
| `export/abundances/rarefied/rarefied_abundance_class_table.csv` | Diversity indices |

#### Outputs

| File | Records | Description |
|------|---------|-------------|
| `output/basic/barcode_farm_mapping.csv` | 24 | Barcode to farm metadata |
| `output/basic/taxonomy_barcode_bacteria.csv` | 6,442 | Long-format taxonomy |
| `output/basic/diversity_indices.csv` | 24 | Diversity metrics |

#### Output Schema: barcode_farm_mapping.csv

```csv
barcode,sample_id,farm_type,farm_id,sample_type,oblast,collection_period
barcode01,1.1.,Poultry,poultry #1,Native,Zaporizhzhia Oblast,JAN-FEB 2025
```

#### Verify

```bash
# Check files created
ls -la output/basic/

# Verify record counts
wc -l output/basic/barcode_farm_mapping.csv
# Expected: 25 (24 records + header)

wc -l output/basic/taxonomy_barcode_bacteria.csv
# Expected: ~6443 (6442 records + header)

# Preview data
head -5 output/basic/barcode_farm_mapping.csv
```

#### Expected Console Output

```
Creating output mappings...
==================================================
Loaded metadata for 24 barcodes
Created: output/basic/barcode_farm_mapping.csv
Created: output/basic/taxonomy_barcode_bacteria.csv
Total records: 6442
Created: output/basic/diversity_indices.csv
Diversity records: 24
==================================================
Done!
```

---

### 2.2 Process AMR Data (Requires Step 2.1)

**Script:** `scripts/process_amr_data.py`

Processes antimicrobial resistance data from all barcodes.

#### Command

```bash
python scripts/process_amr_data.py
```

#### Arguments

| Arg | Type | Required | Description |
|-----|------|----------|-------------|
| *(none)* | - | - | No command-line arguments |

#### Input Files

| File | Description |
|------|-------------|
| `output/basic/barcode_farm_mapping.csv` | From Step 2.1 |
| `export/antimicrobial_resistance/amr_barcode*.csv` | 24 AMR files |

#### Outputs

| File | Records | Description |
|------|---------|-------------|
| `output/amr/amr_by_sample.csv` | 22 | Sample-level summary |
| `output/amr/amr_full_data.csv` | 51,451 | Complete detailed data |
| `output/amr/amr_gene_matrix.csv` | 198 x 24 | Gene by sample matrix |
| `output/amr/amr_resistance_class_matrix.csv` | 47 x 24 | Class by sample matrix |

#### Output Schema: amr_by_sample.csv

```csv
barcode,farm_type,farm_id,sample_type,oblast,total_gene_detections,unique_reads,unique_genes,unique_resistance_classes
barcode01,Poultry,poultry #1,Native,Zaporizhzhia Oblast,247,211,13,27
```

#### Verify

```bash
# Check files created
ls -la output/amr/

# Verify record counts
wc -l output/amr/amr_by_sample.csv
# Expected: 23 (22 records + header)

wc -l output/amr/amr_full_data.csv
# Expected: ~51452 (51451 records + header)

# Preview gene matrix dimensions
head -1 output/amr/amr_gene_matrix.csv | tr ',' '\n' | wc -l
# Expected: 25 (24 barcodes + 1 index column)
```

#### Expected Console Output

```
Processing AMR data...
==================================================
Loaded metadata for 24 barcodes

Loading AMR files:
  barcode12: empty file
  barcode14: empty file
  barcode16: empty file
  barcode17: empty file

Loaded 449,XXX AMR records from 20 files

Parsing resistance classes...
Expanded to 51,451 records (multi-drug parsed)

Creating sample summaries...

Created: output/amr/amr_by_sample.csv
Created: output/amr/amr_full_data.csv
Created: output/amr/amr_gene_matrix.csv
Created: output/amr/amr_resistance_class_matrix.csv
...
Done!
```

---

## Step 3: Run Jupyter Notebooks

### 3.1 Taxonomy Visualization

```bash
jupyter notebook output/basic/taxonomy_visualization.ipynb
```

Or run all cells programmatically:
```bash
jupyter nbconvert --to notebook --execute output/basic/taxonomy_visualization.ipynb
```

**Visualizations generated:**
- Phylum composition stacked bar charts
- Top 20 genera heatmap (log-transformed)
- Interactive sunburst taxonomy hierarchy
- Farm type comparisons (Pig vs Poultry)
- Differential abundance analysis (log2 fold change)
- Native vs Enriched comparison
- Regional (Oblast) analysis
- Diversity analysis (Shannon, Simpson, richness)
- Mann-Whitney U statistical tests

### 3.2 AMR Visualization

```bash
jupyter notebook output/amr/amr_visualization.ipynb
```

Or run all cells programmatically:
```bash
jupyter nbconvert --to notebook --execute output/amr/amr_visualization.ipynb
```

**Visualizations generated:**
- AMR gene counts by farm type
- Top 15 resistance genes per farm type
- Resistance class distribution per sample
- AMR gene heatmap
- Differential AMR gene analysis
- Multi-drug resistance analysis
- Regional AMR patterns
- Statistical comparisons (Mann-Whitney U)

---

## Step 4: Extract Species by Barcode

**Script:** `scripts/extract_species_by_barcode.py`

Add species data sheets to the Excel metadata file.

#### Command

```bash
# Extract all 24 barcodes
python scripts/extract_species_by_barcode.py --all

# Or extract specific barcodes
python scripts/extract_species_by_barcode.py BC01 BC02 BC03
```

#### Arguments

| Arg | Type | Required | Description |
|-----|------|----------|-------------|
| `barcodes` | positional | No | Space-separated barcode IDs (BC01-BC24) |
| `--all` | flag | No | Process all 24 barcodes |

#### Input Files

| File | Description |
|------|-------------|
| `export/abundances/table/abundance_species_table.csv` | Species abundance |
| `output/basic/barcode_farm_mapping.csv` | Barcode metadata |
| `output/xlsx/[WIP] UA_FARM_WW_CLEAN_METADATA.xlsx` | Target Excel file |

#### Output

- Adds new sheets to `output/xlsx/[WIP] UA_FARM_WW_CLEAN_METADATA.xlsx`
- Each sheet named `{barcode}_Species` (e.g., `BC01_Species`)
- Contains: Rank, Species, Read Count, Relative Abundance (%), Genus, Family, Order, Class, Phylum

#### Output Sheet Schema

| Column | Description |
|--------|-------------|
| Rank | Species ranking by read count |
| Species | Scientific name |
| Read Count | Number of reads |
| Relative Abundance (%) | Percentage of total reads |
| Genus | Genus name |
| Family | Family name |
| Order | Order name |
| Class | Class name |
| Phylum | Phylum name |

#### Verify

```bash
# Check Excel file was updated
ls -la output/xlsx/

# Use Python to check sheet names
python -c "
from openpyxl import load_workbook
wb = load_workbook('output/xlsx/[WIP] UA_FARM_WW_CLEAN_METADATA.xlsx')
print('Sheets:', [s for s in wb.sheetnames if 'Species' in s])
"
```

#### Expected Console Output

```
Extracting species data for: BC01, BC02, ..., BC24
==================================================
Loaded 1267 species from abundance table

Processing BC01...
  Total reads: 45,XXX
  Unique species: XXX
  Top 5 species:
     1. Escherichia coli: X,XXX (XX.X%)
     2. ...

Added 24 sheets to: output/xlsx/[WIP] UA_FARM_WW_CLEAN_METADATA.xlsx
Done!
```

---

## Complete Pipeline Script

Save this as `run_pipeline.sh` and run with `bash run_pipeline.sh`:

```bash
#!/bin/bash
# run_pipeline.sh - Complete bio-phagent data pipeline
# Usage: bash run_pipeline.sh

set -e  # Exit on error

echo "========================================"
echo "Bio-Phagent Data Pipeline"
echo "========================================"

# Check prerequisites
echo ""
echo "Checking prerequisites..."
python --version || { echo "ERROR: Python not found"; exit 1; }

# Verify export directory exists
if [ ! -d "export/abundances" ]; then
    echo "ERROR: export/abundances not found"
    echo "Please complete Step 1 (HTML export) first"
    exit 1
fi

# Step 2.1: Create output mappings
echo ""
echo "[Step 2.1] Creating output mappings..."
python scripts/create_output_mappings.py

# Verify Step 2.1
if [ ! -f "output/basic/barcode_farm_mapping.csv" ]; then
    echo "ERROR: barcode_farm_mapping.csv not created"
    exit 1
fi
echo "Verified: barcode_farm_mapping.csv exists"

# Step 2.2: Process AMR data
echo ""
echo "[Step 2.2] Processing AMR data..."
python scripts/process_amr_data.py

# Verify Step 2.2
if [ ! -f "output/amr/amr_by_sample.csv" ]; then
    echo "ERROR: amr_by_sample.csv not created"
    exit 1
fi
echo "Verified: amr_by_sample.csv exists"

# Step 4: Extract species by barcode
echo ""
echo "[Step 4] Extracting species data..."
python scripts/extract_species_by_barcode.py --all

# Summary
echo ""
echo "========================================"
echo "Pipeline Complete!"
echo "========================================"
echo ""
echo "Output files:"
ls -la output/basic/
echo ""
ls -la output/amr/
echo ""
ls -la output/xlsx/
echo ""
echo "Next steps:"
echo "  jupyter notebook output/basic/taxonomy_visualization.ipynb"
echo "  jupyter notebook output/amr/amr_visualization.ipynb"
```

---

## Final Output Directory

```
output/
    basic/
        barcode_farm_mapping.csv         # Barcode to farm metadata (24 records)
        taxonomy_barcode_bacteria.csv    # Long-format taxonomy (6,442 records)
        diversity_indices.csv            # Rarefied diversity metrics (24 records)
        taxonomy_visualization.ipynb     # Taxonomy analysis notebook
        TAXONOMY_BUILD.md                # Taxonomy build documentation
    amr/
        amr_by_sample.csv                # AMR summary per sample (22 records)
        amr_full_data.csv                # Complete AMR data (51,451 records)
        amr_gene_matrix.csv              # Gene x sample matrix (198 x 24)
        amr_resistance_class_matrix.csv  # Resistance class x sample (47 x 24)
        amr_visualization.ipynb          # AMR analysis notebook
    xlsx/
        [WIP] UA_FARM_WW_CLEAN_METADATA.xlsx  # Excel with species sheets
```

---

## Troubleshooting

### Prerequisites Check

```bash
# Check Python version
python --version  # Should be 3.9+

# Check required packages
python -c "import pandas; import openpyxl; print('OK')"
```

### Browser Export Issues

- Ensure local HTTP server is running (`python3 -m http.server 8000`)
- Use Chrome or Firefox for best compatibility
- Check browser console (F12) for JavaScript errors
- Clear browser cache if tables don't load

### Script Errors

| Error | Solution |
|-------|----------|
| `FileNotFoundError: barcode_farm_mapping.csv` | Run `create_output_mappings.py` first |
| `FileNotFoundError: amr_barcode*.csv` | Complete Step 1 (HTML export) |
| `ModuleNotFoundError: pandas` | Run `pip install pandas openpyxl` |
| `KeyError: 'Barcode'` | Check metadata Excel file format |

### Missing Data

- Some barcodes may have empty AMR files (BC12, BC14, BC16, BC17) - this is expected
- Verify abundance files have correct column format (barcodes as columns)
- Check that metadata file exists in `/wip`

### Verification Commands

```bash
# Check all expected files exist
ls output/basic/barcode_farm_mapping.csv && echo "OK: mapping"
ls output/basic/taxonomy_barcode_bacteria.csv && echo "OK: taxonomy"
ls output/amr/amr_by_sample.csv && echo "OK: amr summary"
ls output/amr/amr_full_data.csv && echo "OK: amr full"

# Count records in key files
echo "Mapping records: $(wc -l < output/basic/barcode_farm_mapping.csv)"
echo "Taxonomy records: $(wc -l < output/basic/taxonomy_barcode_bacteria.csv)"
echo "AMR records: $(wc -l < output/amr/amr_full_data.csv)"
```

---

*Last updated: December 2024*
