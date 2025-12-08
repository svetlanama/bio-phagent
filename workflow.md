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
