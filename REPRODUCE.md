# How to Reproduce the Data Pipeline

This document provides step-by-step instructions to reproduce all data in this project from scratch.

---

## Prerequisites

### Python Packages

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

```bash
python scripts/create_output_mappings.py
```

**Outputs:**
- `output/basic/barcode_farm_mapping.csv` (24 records)
- `output/basic/taxonomy_barcode_bacteria.csv` (6,443 records)
- `output/basic/diversity_indices.csv` (24 records)

**Expected output:**
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

### 2.2 Process AMR Data (Requires Step 2.1)

```bash
python scripts/process_amr_data.py
```

**Outputs:**
- `output/amr/amr_by_sample.csv` (22 records)
- `output/amr/amr_full_data.csv` (51,451 records)
- `output/amr/amr_gene_matrix.csv` (198 genes x 24 samples)
- `output/amr/amr_resistance_class_matrix.csv` (47 classes x 24 samples)

**Expected output:**
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

Add species data sheets to the Excel metadata file:

### Extract All Barcodes

```bash
python scripts/extract_species_by_barcode.py --all
```

### Or Extract Specific Barcodes

```bash
python scripts/extract_species_by_barcode.py BC01 BC02 BC03
```

**Output:**
- Adds new sheets to `output/xlsx/[WIP] UA_FARM_WW_CLEAN_METADATA _v1.xlsx`
- Each sheet named `{barcode}_Species` (e.g., `BC01_Species`)
- Contains: Rank, Species, Read Count, Relative Abundance (%), Genus, Family, Order, Class, Phylum

**Expected output:**
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

Added 24 sheets to: output/xlsx/[WIP] UA_FARM_WW_CLEAN_METADATA _v1.xlsx
Done!
```

---

## Complete Execution Summary

```bash
# Step 1: Export data from HTML (manual, browser-based)
python3 -m http.server 8000
# Open http://localhost:8000/input/wrapper.html (for abundance tables)
# Open http://localhost:8000/input/w2.html (for AMR data)
# Export all tables to /export directory

# Step 2: Run processing scripts
python scripts/create_output_mappings.py
python scripts/process_amr_data.py

# Step 3: Run visualization notebooks
jupyter notebook output/basic/taxonomy_visualization.ipynb
jupyter notebook output/amr/amr_visualization.ipynb

# Step 4: Extract species data
python scripts/extract_species_by_barcode.py --all
```

---

## Final Output Directory

```
output/
    basic/
        barcode_farm_mapping.csv         # Barcode to farm metadata
        taxonomy_barcode_bacteria.csv    # Long-format taxonomy (6,443 records)
        diversity_indices.csv            # Rarefied diversity metrics (24 samples)
        taxonomy_visualization.ipynb     # Taxonomy analysis notebook
        TAXONOMY_BUILD.md                # Taxonomy build documentation
    amr/
        amr_by_sample.csv                # AMR summary per sample
        amr_full_data.csv                # Complete AMR data (51,451 records)
        amr_gene_matrix.csv              # Gene x sample matrix
        amr_resistance_class_matrix.csv  # Resistance class x sample matrix
        amr_visualization.ipynb          # AMR analysis notebook
    xlsx/
        [WIP] UA_FARM_WW_CLEAN_METADATA _v1.xlsx  # Excel with species sheets
```

---

## Troubleshooting

### Browser Export Issues
- Ensure local HTTP server is running (`python3 -m http.server 8000`)
- Use Chrome or Firefox for best compatibility
- Check browser console for JavaScript errors

### Script Errors
- Run `create_output_mappings.py` before `process_amr_data.py` (dependency)
- Ensure all export files exist in `/export` before running scripts
- Check that metadata file exists in `/wip`

### Missing Data
- Some barcodes may have empty AMR files (BC12, BC14, BC16, BC17) - this is expected
- Verify abundance files have correct column format (barcodes as columns)

---

*Last updated: December 2024*
