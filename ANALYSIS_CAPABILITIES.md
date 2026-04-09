# Analysis Capabilities

This document describes what analysis capabilities exist in this project and what additional analyses could be added with raw sequencing data.

---

## Current Capabilities

### 1. Taxonomic Profiling (Complete)

**Tool used:** Kraken2 (k-mer based classification)

**Taxonomic levels available:**
| Level | Unique Taxa | Example |
|-------|-------------|---------|
| Phylum | ~31 | Pseudomonadota, Bacteroidota, Bacillota |
| Class | ~53 | Gammaproteobacteria, Bacteroidia |
| Order | ~103 | Enterobacterales, Bacteroidales |
| Family | ~213 | Enterobacteriaceae, Bacteroidaceae |
| Genus | ~472 | Escherichia, Klebsiella, Bacteroides |
| Species | ~1,267 | Escherichia coli, Klebsiella pneumoniae |

**Data files:**
- `export/abundances/table/` - Raw read counts per taxon
- `export/abundances/rarefied/` - Normalized for diversity analysis
- `output/taxonomy_barcode_bacteria.csv` - 6,443 records (long format)

**Top 10 most abundant genera:**
1. Escherichia (549,335 reads)
2. Klebsiella (96,764 reads)
3. Proteus (70,573 reads)
4. Acinetobacter (62,803 reads)
5. Bacteroides (52,892 reads)
6. Morganella (51,126 reads)
7. Citrobacter (46,300 reads)
8. Comamonas (45,338 reads)
9. Pseudomonas (40,646 reads)
10. Shigella (27,814 reads)

---

### 2. Diversity Analysis (Complete)

**Alpha diversity indices available:**
| Index | Description | Interpretation |
|-------|-------------|----------------|
| Shannon diversity | Diversity + evenness | Higher = more diverse (0-5+) |
| Simpson's index | Dominance probability | 0-1, higher = less diverse |
| Inverse Simpson | Effective species count | Higher = more diverse |
| Richness | Total unique taxa | Raw count of taxa |
| Pielou's evenness | Distribution uniformity | 0-1, 1 = perfectly even |
| Fisher's alpha | Robust diversity metric | Higher = more diverse |
| Berger-Parker | Most abundant taxon dominance | 0-1, higher = dominated |
| Effective species | True species equivalent | Accounts for evenness |

**Data files:**
- `export/abundances/rarefied/rarefied_abundance_class_table.csv` - Source data
- `output/diversity_indices.csv` - 24 samples with all indices

---

### 3. Antimicrobial Resistance (AMR) Detection (Complete)

**Tools used:**
- ABRicate (gene detection)
- ResFinder database (resistance gene reference)

**Coverage:**
| Metric | Value |
|--------|-------|
| Total AMR gene detections | ~450,000+ |
| Unique resistance genes | 198 |
| Antibiotic resistance classes | 47 |
| Samples with AMR data | 20/24 (4 samples empty) |

**Resistance classes detected:**
- Beta-lactam resistance (bla genes)
- Aminoglycoside resistance
- Tetracycline resistance
- Quinolone resistance
- Macrolide resistance
- Sulfonamide resistance
- Trimethoprim resistance
- And 40+ more classes

**Data files:**
- `export/antimicrobial_resistance/amr_barcode*.csv` - Per-sample AMR data
- `output/amr_full_data.csv` - 51,451 records (merged + parsed)
- `output/amr_gene_matrix.csv` - Gene × sample matrix
- `output/amr_resistance_class_matrix.csv` - Class × sample matrix

---

### 4. Comparative Analyses (Complete)

**Comparisons available:**

| Comparison | Groups | Statistical Test |
|------------|--------|------------------|
| Farm type | Pig (20) vs Poultry (4) | Mann-Whitney U |
| Sample type | Native (12) vs Enriched (12) | Mann-Whitney U |
| Region | 6 Ukrainian oblasts | Visual comparison |

**Visualizations in notebooks:**
- Differential abundance (log2 fold change)
- Box plots with individual samples
- Stacked bar charts
- Heatmaps (log-transformed)
- Interactive sunburst (Plotly)

---

## What's MISSING

### 1. MetaPhlAn Taxonomic Profiling

**What it provides:**
- Marker gene-based species identification
- Strain-level profiling
- Higher precision than Kraken2 for some taxa
- Standardized relative abundance

**Why not available:** Requires raw FASTQ files (not in repository)

---

### 2. HUMAnN Functional Profiling

**What it provides:**
- **MetaCyc pathway abundances** - Metabolic pathway activity levels
- **Gene family abundances** - Functional gene counts (UniRef90)
- **Pathway coverage** - Completeness of metabolic pathways
- **Functional diversity** - Gene functional categories

**Example outputs:**
```
# Pathway abundances (pathabundance.tsv)
PATHWAY: PWY-5973 (cis-vaccenate biosynthesis)  barcode01: 0.0023
PATHWAY: PWY-6122 (5-aminoimidazole ribonucleotide biosynthesis)  barcode01: 0.0015

# Gene families (genefamilies.tsv)
UniRef90_A0A0H3M1R2: DNA gyrase subunit A  barcode01: 0.0045
UniRef90_P0A8A4: Elongation factor Tu  barcode01: 0.0032
```

**Why not available:** Requires raw FASTQ files (not in repository)

---

### 3. KEGG Pathway Analysis

**What it provides:**
- Mapping to KEGG orthology (KO) terms
- KEGG pathway modules
- BRITE hierarchical classifications
- Metabolic pathway maps

**Why not available:** Requires functional annotation pipeline on raw reads

---

### 4. Gene Ontology (GO) Analysis

**What it provides:**
- Biological process annotations
- Molecular function annotations
- Cellular component annotations

**Why not available:** Requires functional gene annotation

---

## How to Add Functional Profiling

To add MetaPhlAn/HUMAnN functional profiling, you need:

### Prerequisites
1. **Raw FASTQ files** from the original sequencing run
2. **HUMAnN 3** installed (`pip install humann`)
3. **MetaPhlAn 4** installed (`pip install metaphlan`)
4. **Databases** (~30GB total):
   - ChocoPhlAn (nucleotide database)
   - UniRef90 (protein database)

### Pipeline Commands
```bash
# 1. Run MetaPhlAn for taxonomic profiling
metaphlan sample.fastq.gz \
    --input_type fastq \
    --nproc 8 \
    -o sample_metaphlan.txt

# 2. Run HUMAnN for functional profiling
humann \
    --input sample.fastq.gz \
    --output humann_output/ \
    --threads 8

# Outputs:
# - sample_genefamilies.tsv (gene family abundances)
# - sample_pathabundance.tsv (pathway abundances)
# - sample_pathcoverage.tsv (pathway coverage)
```

### Integration with Existing Analysis
After running HUMAnN, create processing scripts similar to existing ones:
- `process_pathway_data.py` - Merge and aggregate pathway data
- `pathway_visualization.ipynb` - Visualize functional profiles

See `docs/FUNCTIONAL_PROFILING_GUIDE.md` for detailed instructions.

---

## Summary Comparison

| Capability | Status | Data Source | Tool |
|------------|--------|-------------|------|
| Species identification |  Available | HTML report | Kraken2 |
| Alpha diversity |  Available | HTML report | wf-metagenomics |
| Beta diversity |   Can calculate | Existing abundance data | scikit-bio |
| AMR gene detection |  Available | HTML report | ABRicate/ResFinder |
| AMR mechanisms |   Can derive | Existing AMR data | Custom mapping |
| Metabolic pathways | L Missing | Requires FASTQ | HUMAnN |
| Gene functions | L Missing | Requires FASTQ | HUMAnN |
| KEGG pathways | L Missing | Requires FASTQ | HUMAnN/eggNOG |
| Strain-level | L Missing | Requires FASTQ | MetaPhlAn |

---

## Current Visualization Notebooks

### `output/taxonomy_visualization.ipynb`
- Phylum composition stacked bars
- Top genera heatmaps
- Interactive taxonomy sunburst
- Farm type comparisons
- Diversity analysis (Shannon, Simpson, Richness)
- Regional (Oblast) analysis

### `output/amr_visualization.ipynb`
- AMR gene counts by farm type
- Top resistance genes
- Resistance class distribution
- Differential AMR analysis
- Multi-drug resistance patterns

---

*Last updated: December 2024*
