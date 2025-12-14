# wf-metagenomics Workflow Documentation

## Overview

This document describes the wf-metagenomics pipeline from Oxford Nanopore Technologies used to analyze metagenomic samples from Ukrainian farm wastewater.

**Pipeline version:** v2.12.1
**Analysis date:** 2025-03-19
**Samples:** 24 barcoded samples (barcode01-barcode24)

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SAMPLE COLLECTION                                   │
│                    (Farm wastewater samples, Ukraine)                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DNA EXTRACTION                                      │
│                 Total DNA isolation from samples                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      LIBRARY PREPARATION                                    │
│         • Sample barcoding (barcode01-24)                                   │
│         • Nanopore adapter ligation                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SEQUENCING                                          │
│              Oxford Nanopore (MinION/GridION/PromethION)                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    wf-metagenomics PIPELINE                                 │
│                         (Nextflow)                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. QUALITY CONTROL                                                         │
│     • Read length filtering                                                 │
│     • Quality score filtering                                               │
│     • Host depletion                                                        │
│                              │                                              │
│                              ▼                                              │
│  2. TAXONOMIC CLASSIFICATION                                                │
│     ┌─────────────────┐    ┌─────────────────┐                              │
│     │    Kraken2      │ OR │    Minimap2     │                              │
│     │  (k-mer based)  │    │  (alignment)    │                              │
│     └─────────────────┘    └─────────────────┘                              │
│                              │                                              │
│                              ▼                                              │
│  3. ABUNDANCE ESTIMATION                                                    │
│     • Read counts per taxon                                                 │
│     • Normalization                                                         │
│     • Rarefaction                                                           │
│                              │                                              │
│                              ▼                                              │
│  4. DIVERSITY ANALYSIS                                                      │
│     • Alpha diversity indices                                               │
│     • Species richness curves                                               │
│                              │                                              │
│                              ▼                                              │
│  5. AMR DETECTION                                                           │
│     ┌─────────────────┐    ┌─────────────────┐                              │
│     │    ABRicate     │ ─► │   ResFinder DB   │                              │
│     └─────────────────┘    └─────────────────┘                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         HTML REPORT                                         │
│            wf-metagenomics-report_metagenomics-farms-ukr.html               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Pipeline Steps

### 1. Quality Control (QC)

Filters raw sequencing reads based on:
- **Read length**: Minimum and maximum length thresholds
- **Quality score (Q-score)**: Minimum average quality per read
- **Host depletion**: Removal of host DNA (if applicable)

**Output metrics:**
- Number of reads per sample
- Read quality distribution (mean, median)
- Read length distribution
- Base yield above read length

### 2. Taxonomic Classification

Two approaches available:

| Approach | Method | Description |
|----------|--------|-------------|
| **Kraken2** | k-mer based | Fast classification using exact k-mer matches |
| **Minimap2** | Alignment | Maps reads to reference genomes |

**Taxonomic ranks analyzed:**
- Domain (Superkingdom)
- Kingdom
- Phylum
- Class
- Order
- Family
- Genus
- Species

### 3. Abundance Estimation

Calculates the number of reads assigned to each taxon at different taxonomic levels.

**Output tables:**
- Abundance table (raw read counts)
- Rarefied abundance table (normalized for sequencing depth)
- Relative abundance (percentages)

### 4. Diversity Analysis

#### Alpha Diversity Indices

| Index | Description | Interpretation |
|-------|-------------|----------------|
| **Richness** | Number of unique taxa | Higher = more taxa |
| **Shannon diversity** | Diversity + evenness | 0-5+; higher = more diverse |
| **Simpson's index** | Probability two reads are same species | 0-1; higher = less diverse |
| **Inverse Simpson's** | 1/Simpson | Higher = more diverse |
| **Pielou's evenness** | Distribution uniformity | 0-1; 1 = all taxa equally abundant |
| **Fisher's alpha** | Diversity for large datasets | Higher = more diverse |
| **Berger-Parker** | Dominance of most abundant taxon | 0-1; higher = one taxon dominates |
| **Effective number of species** | "True" species count | Accounts for evenness |

#### Species Richness Curves (Rarefaction)

Shows how the number of detected taxa increases with sequencing depth.
- **Plateau reached**: Sufficient sequencing depth
- **Still increasing**: More taxa to discover with deeper sequencing

### 5. Antimicrobial Resistance (AMR) Detection

**Tool:** ABRicate
**Database:** ResFinder

Identifies acquired antimicrobial resistance genes in the samples.

**Output fields:**
| Field | Description |
|-------|-------------|
| Gene name | AMR gene identifier |
| ReadID | Sequencing read containing the gene |
| Coverage % | Percentage of gene covered by reads |
| Identity % | Sequence similarity to reference |
| Resistance | Antibiotics the gene confers resistance to |

**Limitations:**
- SNP-mediated AMR cannot be detected
- Only detects known genes in the database

## Tools and Databases

| Component | Tool/Database | Purpose |
|-----------|---------------|---------|
| Pipeline framework | Nextflow | Workflow orchestration |
| Classification | Kraken2 / Minimap2 | Taxonomic assignment |
| Taxonomy database | NCBI / GTDB | Reference genomes |
| AMR detection | ABRicate | Gene identification |
| AMR database | ResFinder | Resistance gene reference |
| Visualization | ezCharts | Report generation |

## Output Report Sections

| Section | Content |
|---------|---------|
| **Read summary** | QC statistics, read quality and length distributions |
| **Taxonomy** | Barplots of taxa at different ranks (phylum, class, etc.) |
| **Abundances** | Tables with read counts per taxon per sample |
| **Alpha Diversity** | Diversity indices, rarefaction curves, abundance distributions |
| **Antimicrobial resistance** | Detected AMR genes per sample |

## References

- wf-metagenomics: https://github.com/epi2me-labs/wf-metagenomics
- Kraken2: https://ccb.jhu.edu/software/kraken2/
- Minimap2: https://github.com/lh3/minimap2
- ABRicate: https://github.com/tseemann/abricate
- ResFinder: https://cge.food.dtu.dk/services/ResFinder/

---

# Post-Pipeline Processing: `/output` Directory Workflow

This section documents the custom Python scripts that transform raw Nextflow pipeline outputs into analysis-ready datasets in the `/output` directory.

---

## Post-Processing Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              wf-metagenomics Nextflow Pipeline                  │
│                      (documented above)                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        /export Directory                         │
│  ├── abundances/table/        (raw abundance CSVs)              │
│  ├── abundances/rarefied/     (normalized + diversity indices)  │
│  ├── antimicrobial_resistance/ (24 AMR barcode files)           │
│  ├── alpha_diversity/         (diversity metrics)               │
│  └── number_of_reads/         (QC statistics)                   │
└─────────────────────────────────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐    ┌───────────────────┐    ┌───────────────────┐
│  Script #1    │    │    Script #2      │    │    Script #3      │
│ create_output │    │  process_amr_data │    │ extract_species_  │
│ _mappings.py  │    │      .py          │    │ by_barcode.py     │
└───────────────┘    └───────────────────┘    └───────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                       /output Directory                          │
│  ├── barcode_farm_mapping.csv     (24 records)                  │
│  ├── taxonomy_barcode_bacteria.csv (6,443 records)              │
│  ├── diversity_indices.csv         (24 records)                 │
│  ├── amr_by_sample.csv             (22 records)                 │
│  ├── amr_full_data.csv             (51,451 records)             │
│  ├── amr_gene_matrix.csv           (198 genes × 24 samples)     │
│  ├── amr_resistance_class_matrix.csv (47 classes × 24 samples)  │
│  ├── [WIP] UA_FARM_WW_CLEAN_METADATA _v1.xlsx (+ species sheets)│
│  ├── taxonomy_visualization.ipynb                               │
│  ├── amr_visualization.ipynb                                    │
│  └── TAXONOMY_BUILD.md                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Input Data Sources

### 1. Raw Metadata (`/wip/`)
- **File**: `[WIP] UA_FARM_WW_CLEAN_METADATA.xlsx`
- **Content**: Sample metadata for 24 barcoded samples
- **Columns**: Barcode, Sample ID, Farm Type, Farm ID, Sample Type, Oblast, Collection Period

### 2. Abundance Data (`/export/abundances/`)

#### Raw Abundance Tables (`/export/abundances/table/`)
| File | Description |
|------|-------------|
| `abundance_phylum_table.csv` | ~30 phyla |
| `abundance_class_table.csv` | ~50 classes |
| `abundance_order_table.csv` | ~100 orders |
| `abundance_family_table.csv` | ~250 families |
| `abundance_genus_table.csv` | ~500 genera |
| `abundance_species_table.csv` | ~1,500 species |

**Format**: Wide CSV with barcodes as columns, read counts as values
```csv
genus,barcode01,barcode02,...,barcode24,total,superkingdom,...,tax
Escherichia,2932,15234,...,1205,525402,Bacteria,...,Bacteria;...;Escherichia
```

#### Rarefied Abundance Tables (`/export/abundances/rarefied/`)
Same structure as raw, but normalized via rarefaction for diversity analysis. The class table contains diversity indices:
- Shannon diversity index
- Simpson's index
- Berger-Parker index
- Pielou's evenness
- Fisher's alpha
- Richness
- Effective number of species

### 3. AMR Data (`/export/antimicrobial_resistance/`)
- **Files**: 24 CSV files (`amr_barcode01.csv` through `amr_barcode24.csv`)
- **Content**: Detected AMR genes with coverage, identity, resistance class
- **Format**: Gene, ReadID, Coverage %, Identity %, Resistance (semicolon-separated for multi-drug)

---

## Processing Scripts

### Script 1: `scripts/create_output_mappings.py`

**Purpose**: Create core mapping files for taxonomy and metadata

**Functions**:

1. **`load_metadata()`**
   - Reads Excel metadata file
   - Normalizes barcode format: `BC01` → `barcode01`
   - Renames columns to snake_case

2. **`create_barcode_farm_mapping()`**
   - Outputs: `output/barcode_farm_mapping.csv`
   - 24 records mapping barcodes to farm info

3. **`create_taxonomy_barcode_bacteria()`**
   - Reads all 6 abundance CSVs from `/export/abundances/table/`
   - Transforms wide format to long format (melt)
   - Filters to non-zero abundances only
   - Merges with farm metadata
   - Outputs: `output/taxonomy_barcode_bacteria.csv` (6,443 records)

4. **`create_diversity_indices_csv()`**
   - Reads `rarefied_abundance_class_table.csv`
   - Transposes: index rows become columns
   - Renames to snake_case
   - Merges with farm metadata
   - Outputs: `output/diversity_indices.csv` (24 records)

**Execution**:
```bash
python scripts/create_output_mappings.py
```

---

### Script 2: `scripts/process_amr_data.py`

**Purpose**: Aggregate and process AMR data from all barcode files

**Functions**:

1. **`load_all_amr_data()`**
   - Reads all 24 AMR CSV files
   - Adds barcode identifier column
   - Concatenates into single DataFrame

2. **`parse_resistance_classes()`**
   - Expands multi-drug resistance (semicolon-separated)
   - Creates one row per resistance class

3. **`create_amr_summary()`**
   - Merges with farm metadata
   - Calculates per-sample statistics:
     - Total gene detections
     - Unique reads
     - Unique genes
     - Unique resistance classes

4. **`create_gene_by_sample_matrix()`**
   - Pivot table: genes as rows, samples as columns

5. **`create_resistance_class_by_sample()`**
   - Pivot table: resistance classes as rows, samples as columns

**Outputs**:
- `output/amr_by_sample.csv` - Summary per sample (22 records)
- `output/amr_full_data.csv` - Complete merged data (51,451 records)
- `output/amr_gene_matrix.csv` - Gene × sample matrix (198 genes)
- `output/amr_resistance_class_matrix.csv` - Resistance class × sample (47 classes)

**Execution**:
```bash
python scripts/process_amr_data.py
```

**Dependencies**: Requires `barcode_farm_mapping.csv` (run Script 1 first)

---

### Script 3: `scripts/extract_species_by_barcode.py`

**Purpose**: Extract dominant bacterial species per barcode and add to Excel metadata

**Usage**:
```bash
python scripts/extract_species_by_barcode.py BC01           # Single barcode
python scripts/extract_species_by_barcode.py BC01 BC02 BC03 # Multiple barcodes
python scripts/extract_species_by_barcode.py --all          # All 24 barcodes
```

**Key Functions**:

1. **`extract_species()`**
   - Filters species with read count > 0
   - Calculates relative abundance (%)
   - Ranks by read count
   - Returns formatted DataFrame

2. **`add_to_excel()`**
   - Creates new sheet named `{barcode}_Species`
   - Adds header with sample metadata
   - Adds species table with columns:
     - Rank, Species, Read Count, Relative Abundance (%)
     - Genus, Family, Order, Class, Phylum

**Output**: New sheets added to `output/[WIP] UA_FARM_WW_CLEAN_METADATA _v1.xlsx`

---

## Output Files Summary

| File | Records | Description |
|------|---------|-------------|
| `barcode_farm_mapping.csv` | 24 | Barcode to farm metadata mapping |
| `taxonomy_barcode_bacteria.csv` | 6,443 | Long-format taxonomy with abundance |
| `diversity_indices.csv` | 24 | Rarefied diversity metrics per sample |
| `amr_by_sample.csv` | 22 | AMR summary statistics per sample |
| `amr_full_data.csv` | 51,451 | Complete AMR data with metadata |
| `amr_gene_matrix.csv` | 198 | AMR gene counts by sample |
| `amr_resistance_class_matrix.csv` | 47 | Resistance class counts by sample |
| `[WIP] UA_FARM_WW...xlsx` | varies | Metadata Excel with species sheets |

---

## Visualization Notebooks

### `taxonomy_visualization.ipynb`
- Phylum composition stacked bar charts
- Top 20 genera heatmap (log-transformed)
- Interactive sunburst taxonomy hierarchy
- Farm type comparisons (Pig vs Poultry)
- Differential abundance analysis (log2 fold change)
- Native vs Enriched comparison
- Regional (Oblast) analysis
- **Diversity Analysis**:
  - Shannon/Simpson by farm type (box plots)
  - Mann-Whitney U statistical tests
  - Diversity indices heatmap

### `amr_visualization.ipynb`
- AMR gene counts by farm type
- Top 15 resistance genes per farm type
- Resistance class distribution per sample
- AMR gene heatmap
- Differential AMR gene analysis
- Multi-drug resistance analysis
- Regional AMR patterns
- Statistical comparisons (Mann-Whitney U)

---

## Execution Order

```bash
# Step 1: Create core mappings (REQUIRED FIRST)
python scripts/create_output_mappings.py

# Step 2: Process AMR data (requires Step 1)
python scripts/process_amr_data.py

# Step 3: Extract species to Excel (optional, requires Step 1)
python scripts/extract_species_by_barcode.py --all

# Step 4: Run Jupyter notebooks for visualization (optional)
jupyter notebook output/taxonomy_visualization.ipynb
jupyter notebook output/amr_visualization.ipynb
```

---

## Sample Distribution

| Attribute | Values |
|-----------|--------|
| Total samples | 24 barcodes (BC01-BC24) |
| Farm types | Poultry (4), Pig (20) |
| Sample types | Native, Enriched (50/50 split) |
| Regions | 6 oblasts (Zaporizhzhia, Zhytomyr, Kyiv, Chernivtsi, Vinnytsia, Mykolaiv) |
| Collection period | JAN-FEB 2025 |

---

## Dependencies

```bash
pip install pandas openpyxl
# For notebooks:
pip install plotly scipy matplotlib seaborn
```

---

## Key Data Transformations

1. **Wide → Long format**: Abundance tables transformed from barcodes-as-columns to one-row-per-observation
2. **Barcode normalization**: `BC01` → `barcode01` for consistency
3. **Multi-drug resistance expansion**: Semicolon-separated resistance classes split into individual rows
4. **Metadata enrichment**: All output files include farm metadata (farm_type, farm_id, sample_type, oblast)
5. **Diversity extraction**: Transposed from indices-as-rows to indices-as-columns

---

## Complete File Structure

```
bio-phagent/
├── export/                              # Nextflow pipeline outputs
│   ├── abundances/
│   │   ├── table/                       # Raw abundance CSVs
│   │   │   ├── abundance_phylum_table.csv
│   │   │   ├── abundance_class_table.csv
│   │   │   ├── abundance_order_table.csv
│   │   │   ├── abundance_family_table.csv
│   │   │   ├── abundance_genus_table.csv
│   │   │   └── abundance_species_table.csv
│   │   └── rarefied/                    # Normalized + diversity indices
│   │       ├── rarefied_abundance_class_table.csv  # Contains diversity indices
│   │       └── ...
│   ├── antimicrobial_resistance/        # 24 AMR barcode files
│   │   ├── amr_barcode01.csv
│   │   └── ...
│   ├── alpha_diversity/
│   └── number_of_reads/
├── wip/
│   └── [WIP] UA_FARM_WW_CLEAN_METADATA.xlsx  # Source metadata
├── scripts/
│   ├── create_output_mappings.py        # Script 1
│   ├── process_amr_data.py              # Script 2
│   └── extract_species_by_barcode.py    # Script 3
└── output/                              # Generated outputs
    ├── barcode_farm_mapping.csv
    ├── taxonomy_barcode_bacteria.csv
    ├── diversity_indices.csv
    ├── amr_by_sample.csv
    ├── amr_full_data.csv
    ├── amr_gene_matrix.csv
    ├── amr_resistance_class_matrix.csv
    ├── [WIP] UA_FARM_WW_CLEAN_METADATA _v1.xlsx
    ├── taxonomy_visualization.ipynb
    ├── amr_visualization.ipynb
    └── TAXONOMY_BUILD.md
```

---

*Generated: December 2024*
