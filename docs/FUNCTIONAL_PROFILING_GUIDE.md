# Functional Profiling Guide: MetaPhlAn & HUMAnN

This guide documents how to add metabolic pathway and functional gene analysis to the bio-phagent project using MetaPhlAn and HUMAnN.

**Note:** This requires access to raw FASTQ sequencing files, which are not currently in this repository.

---

## Why Functional Profiling?

### Current Analysis (Taxonomic)
- **What organisms are present?** (Species identification)
- **How abundant are they?** (Read counts)
- **What AMR genes do they carry?** (Resistance detection)

### Functional Profiling Adds
- **What metabolic pathways are active?** (Pathway abundances)
- **What functions are present?** (Gene families)
- **What is the community doing?** (Functional potential)

---

## Overview of Tools

### MetaPhlAn 4
- **Purpose:** Taxonomic profiling using clade-specific marker genes
- **Advantages over Kraken2:**
  - Strain-level resolution
  - Lower false positive rate
  - Standardized relative abundances
  - More accurate for low-abundance taxa

### HUMAnN 3
- **Purpose:** Functional profiling of metagenomes
- **Outputs:**
  - Gene family abundances (UniRef90)
  - MetaCyc pathway abundances
  - Pathway coverage statistics
- **Database:** ChocoPhlAn (nucleotide) + UniRef90 (protein)

---

## Installation

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Create conda environment (recommended)
conda create -n humann3 python=3.8
conda activate humann3
```

### Install MetaPhlAn 4
```bash
# Install via pip
pip install metaphlan

# Download database (~15GB)
metaphlan --install --bowtie2db /path/to/metaphlan_db
```

### Install HUMAnN 3
```bash
# Install via pip
pip install humann

# Download databases (~30GB total)
humann_databases --download chocophlan full /path/to/humann_db
humann_databases --download uniref uniref90_diamond /path/to/humann_db

# Configure database paths
humann_config --update database_folders nucleotide /path/to/humann_db/chocophlan
humann_config --update database_folders protein /path/to/humann_db/uniref
```

---

## Pipeline for Nanopore Data

### Step 1: Quality Control (if not already done)
```bash
# Filter reads by quality (optional, wf-metagenomics may have done this)
NanoFilt -q 7 -l 200 < sample.fastq > sample_filtered.fastq
```

### Step 2: Run MetaPhlAn
```bash
# Single sample
metaphlan sample.fastq.gz \
    --input_type fastq \
    --nproc 8 \
    --bowtie2db /path/to/metaphlan_db \
    -o sample_metaphlan.txt

# Output: Taxonomic profile with relative abundances
# Format: clade_name | relative_abundance | coverage
```

### Step 3: Run HUMAnN
```bash
# Single sample
humann \
    --input sample.fastq.gz \
    --output humann_output/ \
    --threads 8 \
    --metaphlan-options "--bowtie2db /path/to/metaphlan_db"

# Outputs:
# - sample_genefamilies.tsv
# - sample_pathabundance.tsv
# - sample_pathcoverage.tsv
```

### Step 4: Batch Processing (All 24 Samples)
```bash
#!/bin/bash
# process_all_samples.sh

SAMPLES_DIR="/path/to/fastq_files"
OUTPUT_DIR="/path/to/humann_output"

for FASTQ in ${SAMPLES_DIR}/*.fastq.gz; do
    SAMPLE=$(basename ${FASTQ} .fastq.gz)
    echo "Processing ${SAMPLE}..."

    humann \
        --input ${FASTQ} \
        --output ${OUTPUT_DIR}/${SAMPLE} \
        --threads 8

done
```

### Step 5: Merge Sample Tables
```bash
# Merge gene families across all samples
humann_join_tables \
    --input humann_output/ \
    --output merged_genefamilies.tsv \
    --file_name genefamilies

# Merge pathway abundances
humann_join_tables \
    --input humann_output/ \
    --output merged_pathabundance.tsv \
    --file_name pathabundance

# Normalize to relative abundance
humann_renorm_table \
    --input merged_pathabundance.tsv \
    --output merged_pathabundance_relab.tsv \
    --units relab
```

---

## Expected Outputs

### Gene Family Abundances (`genefamilies.tsv`)
```
# Gene Family                        barcode01   barcode02   ...
UniRef90_A0A0H3M1R2: DNA gyrase     0.0045      0.0032      ...
UniRef90_P0A8A4: Elongation factor  0.0032      0.0028      ...
UNMAPPED                            0.15        0.18        ...
UNGROUPED                           0.05        0.06        ...
```

### Pathway Abundances (`pathabundance.tsv`)
```
# Pathway                                    barcode01   barcode02   ...
PWY-5973: cis-vaccenate biosynthesis        0.0023      0.0018      ...
PWY-6122: 5-aminoimidazole ribonucleotide   0.0015      0.0012      ...
UNMAPPED                                    0.20        0.22        ...
UNINTEGRATED                                0.10        0.12        ...
```

### Pathway Coverage (`pathcoverage.tsv`)
```
# Pathway                                    barcode01   barcode02   ...
PWY-5973: cis-vaccenate biosynthesis        0.85        0.78        ...
PWY-6122: 5-aminoimidazole ribonucleotide   0.72        0.65        ...
```

---

## Integration with Existing Analysis

### Directory Structure (Proposed)
```
bio-phagent/
├── export/
│   ├── abundances/           # Existing taxonomic data
│   ├── antimicrobial_resistance/  # Existing AMR data
│   └── functional/           # NEW: HUMAnN outputs
│       ├── genefamilies/
│       ├── pathabundance/
│       └── pathcoverage/
├── output/
│   ├── taxonomy_*.csv        # Existing
│   ├── amr_*.csv             # Existing
│   ├── pathway_abundances.csv       # NEW
│   ├── gene_family_matrix.csv       # NEW
│   └── functional_visualization.ipynb  # NEW
```

### Processing Script (Example)
```python
# scripts/process_pathway_data.py
import pandas as pd
from pathlib import Path

def load_pathway_abundances():
    """Load and process HUMAnN pathway abundance data."""
    pathway_file = Path("export/functional/merged_pathabundance.tsv")
    df = pd.read_table(pathway_file, index_col=0)

    # Remove UNMAPPED and UNINTEGRATED rows
    df = df[~df.index.str.startswith(('UNMAPPED', 'UNINTEGRATED'))]

    # Split pathway ID and name
    df['pathway_id'] = df.index.str.split(':').str[0]
    df['pathway_name'] = df.index.str.split(':').str[1]

    return df

def create_pathway_by_sample_matrix():
    """Create pathway × sample abundance matrix."""
    df = load_pathway_abundances()
    # ... processing logic
```

### Visualization Ideas
1. **Top pathways by farm type** - Bar chart comparing Pig vs Poultry
2. **Pathway heatmap** - Clustered heatmap of pathway abundances
3. **Functional diversity** - Number of unique pathways per sample
4. **Pathway differential abundance** - Log2 fold change between groups
5. **MetaCyc category analysis** - Group pathways by metabolic category

---

## Resource Requirements

### Computational Resources
| Step | CPU | RAM | Time (per sample) |
|------|-----|-----|-------------------|
| MetaPhlAn | 8 cores | 16GB | 30-60 min |
| HUMAnN | 8 cores | 32GB | 2-6 hours |
| Diamond (protein) | 8 cores | 64GB | 1-2 hours |

### Storage Requirements
| Database | Size |
|----------|------|
| MetaPhlAn DB | ~15GB |
| ChocoPhlAn | ~15GB |
| UniRef90 | ~30GB |
| **Total** | **~60GB** |

### For 24 Samples
- Estimated total runtime: 48-144 hours (with 8 cores)
- Output storage: ~5-10GB

---

## Alternative Tools

### If HUMAnN is too resource-intensive:

1. **MicrobeAnnotator** - Lighter weight functional annotation
2. **eggNOG-mapper** - COG/KEGG annotation from protein sequences
3. **MinPath** - Minimal pathway reconstruction
4. **MEGAN6** - GUI-based functional analysis

### For Nanopore-specific tools:
1. **Kraken2 + Bracken** - Already in use (taxonomic only)
2. **Centrifuge** - Alternative classifier
3. **NanoPath** - Nanopore-specific pathogen detection

---

## References

- MetaPhlAn: https://github.com/biobakery/MetaPhlAn
- HUMAnN 3: https://github.com/biobakery/humann
- bioBakery workflows: https://github.com/biobakery/biobakery_workflows
- Tutorial: https://huttenhower.sph.harvard.edu/humann

---

*This guide is provided for future implementation when raw FASTQ files become available.*

*Last updated: December 2024*
