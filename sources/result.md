# Metagenomics Analysis Results Report

## Bio-phagent Project - Ukrainian Farm Wastewater Study

**Analysis Date:** January-February 2025
**Report Generated:** December 2025
**Project Focus:** Phage research and metagenomics analysis from Ukrainian farm samples

---

## 1. Project Overview

### 1.1 Research Objectives

This project analyzes metagenomics data from Ukrainian farm wastewater samples to:
- Identify microbial communities in farm wastewater
- Characterize taxonomic composition across different farm types
- Support phage research for agricultural applications
- Compare native vs. enriched sample microbiomes

### 1.2 Sample Collection Context

- **Collection Period:** January-February 2025
- **Sample Source:** Farm wastewater
- **Geographic Coverage:** 6 Ukrainian oblasts
- **Farm Types:** Poultry and Pig farms
- **Sample Preparation:** Native and Enriched conditions

---

## 2. Data Workflow Documentation

### 2.1 Input Data

| File | Location | Size | Description |
|------|----------|------|-------------|
| `UA_FARM_WW_CLEAN_METADATA.xlsx` | `input/` | 7.4 KB | Original sample metadata spreadsheet |
| `wf-metagenomics-report_metagenomics-farms-ukr.html` | `input/` | 25 MB | Metagenomics workflow pipeline output report |

### 2.2 Data Processing Pipeline

```
┌─────────────────────────────────────┐
│     INPUT DATA                      │
├─────────────────────────────────────┤
│ UA_FARM_WW_CLEAN_METADATA.xlsx      │
│ wf-metagenomics-report.html         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     STEP 1: Metadata Extraction     │
├─────────────────────────────────────┤
│ - Parse Excel metadata              │
│ - Clean and standardize fields      │
│ - Map barcodes to sample info       │
│ Output: metadata.csv                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     STEP 2: Taxonomy Extraction     │
├─────────────────────────────────────┤
│ - Parse HTML workflow report        │
│ - Extract hierarchical taxonomy     │
│ - Build nested JSON structure       │
│ Output: taxonomy_data.json          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     STEP 3: Species Ranking         │
├─────────────────────────────────────┤
│ - Extract top 10 species per sample │
│ - Calculate relative abundances     │
│ - Rank by read count                │
│ Output: top_species_by_barcode.csv  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     STEP 4: Data Merging            │
├─────────────────────────────────────┤
│ - Join species data with metadata   │
│ - Add total reads per sample        │
│ - Create unified analysis dataset   │
│ Output: species_with_metadata.csv   │
└─────────────────────────────────────┘
```

### 2.3 Output Files Summary

| File | Location | Size | Lines | Description |
|------|----------|------|-------|-------------|
| `metadata.csv` | `sources/` | 1.4 KB | 25 | Sample metadata mapping |
| `taxonomy_data.json` | `sources/` | 1.3 MB | 35,082 | Hierarchical taxonomy data |
| `top_species_by_barcode.csv` | `sources/` | 8.7 KB | 205 | Top 10 species per sample |
| `species_with_metadata.csv` | `sources/` | 17 KB | 205 | Species data + metadata merged |

---

## 3. Sample Overview

### 3.1 Sample Distribution

**Total Samples:** 24 (12 paired: Native + Enriched)

| Farm Type | Native Samples | Enriched Samples | Total |
|-----------|----------------|------------------|-------|
| Poultry | 4 | 4 | 8 |
| Pig | 8 | 8 | 16 |
| **Total** | **12** | **12** | **24** |

### 3.2 Geographic Distribution

| Oblast | Samples | Farm Types |
|--------|---------|------------|
| Kyiv Oblast | 8 | Poultry, Pig |
| Zhytomyr Oblast | 4 | Pig |
| Chernivtsi Oblast | 4 | Pig |
| Zaporizhzhia Oblast | 2 | Poultry |
| Vinnytsia Oblast | 2 | Pig |
| Mykolaiv Oblast | 2 | Pig |
| Unknown | 2 | Pig |

### 3.3 Barcode-Sample Mapping

| Barcode | Sample ID | Farm Type | Farm ID | Sample Type | Oblast |
|---------|-----------|-----------|---------|-------------|--------|
| BC01 | 1.1. | Poultry | poultry #1 | Native | Zaporizhzhia |
| BC02 | 1.1. н | Poultry | poultry #1 | Enriched | Zaporizhzhia |
| BC03 | 2. | Pig | pig #1 | Native | Zhytomyr |
| BC04 | 2. н | Pig | pig #1 | Enriched | Zhytomyr |
| BC05 | 3. | Poultry | poultry #2 | Native | Kyiv |
| BC06 | 3. н | Poultry | poultry #2 | Enriched | Kyiv |
| BC07 | 4. | Poultry | poultry #3 | Native | Kyiv |
| BC08 | 4. н | Poultry | poultry #3 | Enriched | Kyiv |
| BC09 | 5.1. | Pig | pig #2 | Native | Kyiv |
| BC10 | 5.1. н | Pig | pig #2 | Enriched | Kyiv |
| BC11 | 5.2. | Pig | pig #2 B2 | Native | - |
| BC12 | 5.2.н | Pig | pig #2 B2 | Enriched | - |
| BC13 | 6. | Pig | pig #3 | Native | Kyiv |
| BC14 | 6. н | Pig | pig #3 | Enriched | Kyiv |
| BC15 | 7. | Pig | pig #4 | Native | Chernivtsi |
| BC16 | 7. н | Pig | pig #4 | Enriched | Chernivtsi |
| BC17 | 8. | Pig | pig #5 | Native | Chernivtsi |
| BC18 | 8. н | Pig | pig #5 | Enriched | Chernivtsi |
| BC19 | 9. | Pig | pig #6 | Native | Vinnytsia |
| BC20 | 9. н | Pig | pig #6 | Enriched | Vinnytsia |
| BC21 | 10. | Pig | pig #7 | Native | Zhytomyr |
| BC22 | 10. н | Pig | pig #7 | Enriched | Zhytomyr |
| BC23 | 11. | Pig | pig #8 | Native | Mykolaiv |
| BC24 | 11 н | Pig | pig #8 | Enriched | - |

---

## 4. Sequencing Statistics

### 4.1 Read Count Distribution

| Metric | Value |
|--------|-------|
| **Total Reads (all samples)** | ~1.78 million |
| **Minimum Reads** | 50 (BC12) |
| **Maximum Reads** | 455,616 (BC23) |
| **Median Reads** | ~40,000 |

### 4.2 Per-Sample Read Counts

| Barcode | Total Reads | Sample Type | Notes |
|---------|-------------|-------------|-------|
| BC07 | 421,827 | Native | Highest non-anomalous |
| BC23 | 455,616 | Native | Highest overall |
| BC08 | 378,812 | Enriched | High yield enriched |
| BC18 | 161,011 | Enriched | Good enrichment |
| BC11 | 142,878 | Native | Good coverage |
| BC24 | 118,190 | Enriched | Good coverage |
| BC02 | 110,524 | Enriched | Good coverage |
| BC03 | 80,746 | Native | Standard yield |
| BC05 | 64,778 | Native | Standard yield |
| BC12 | 50 | Enriched | **Very low - potential issue** |
| BC14 | 415 | Enriched | **Very low - potential issue** |
| BC17 | 594 | Native | **Very low - potential issue** |

**Low-yield samples requiring attention:** BC12, BC14, BC16, BC17

---

## 5. Taxonomic Analysis

### 5.1 Taxonomic Hierarchy

The analysis follows standard biological taxonomy:

```
Superkingdom → Phylum → Class → Order → Family → Genus → Species
```

### 5.2 Dominant Taxa Summary

| Level | Dominant Taxa | Description |
|-------|---------------|-------------|
| **Superkingdom** | Bacteria | Primary domain detected |
| **Phylum** | Pseudomonadota | Formerly Proteobacteria |
| **Class** | Gammaproteobacteria | Key bacterial class |
| **Order** | Enterobacterales | Dominant order |
| **Family** | Enterobacteriaceae | Primary family |
| **Genus** | Escherichia, Klebsiella | Top genera |
| **Species** | Escherichia coli | Most abundant species |

### 5.3 Hierarchical Taxonomy Example (BC01)

```
Bacteria (12,465 reads)
└── Pseudomonadota (12,214 reads)
    └── Gammaproteobacteria (11,187 reads)
        └── Enterobacterales (10,675 reads)
            └── Enterobacteriaceae (8,272 reads)
                ├── Klebsiella (3,782 reads)
                │   ├── K. grimontii (1,277)
                │   ├── K. aerogenes (1,136)
                │   ├── K. pneumoniae (684)
                │   └── K. michiganensis (423)
                ├── Escherichia (2,932 reads)
                │   └── E. coli (2,829)
                └── Citrobacter (1,129 reads)
                    ├── C. freundii (379)
                    └── C. portucalensis (349)
```

---

## 6. Species-Level Findings

### 6.1 Most Abundant Species Across All Samples

| Rank | Species | Occurrence | Significance |
|------|---------|------------|--------------|
| 1 | **Escherichia coli** | 23/24 samples | Dominant gut bacterium |
| 2 | **Unknown** | 24/24 samples | Unclassified sequences |
| 3 | **Morganella morganii** | 8/24 samples | Opportunistic pathogen |
| 4 | **Klebsiella pneumoniae** | 12/24 samples | Clinical significance |
| 5 | **Salmonella enterica** | 8/24 samples | Foodborne pathogen |
| 6 | **Proteus mirabilis** | 5/24 samples | Environmental bacterium |
| 7 | **Comamonas kerstersii** | 4/24 samples | Water bacterium |

### 6.2 High E. coli Samples

| Barcode | E. coli Reads | Relative Abundance | Farm Type |
|---------|---------------|-------------------|-----------|
| BC07 | 208,631 | 49.46% | Poultry |
| BC03 | 56,352 | 69.79% | Pig |
| BC24 | 62,311 | 52.72% | Pig |
| BC08 | 48,527 | 12.81% | Poultry |
| BC11 | 38,390 | 26.87% | Pig |
| BC18 | 36,722 | 22.81% | Pig |
| BC05 | 33,578 | 51.84% | Poultry |

### 6.3 Pathogenic Species Detected

| Species | Samples | Clinical Relevance |
|---------|---------|-------------------|
| *Escherichia coli* | 23 | Potential STEC/EHEC strains |
| *Salmonella enterica* | 8 | Foodborne illness |
| *Klebsiella pneumoniae* | 12 | Nosocomial infections, AMR |
| *Shigella flexneri* | 7 | Dysentery |
| *Shigella dysenteriae* | 1 | Severe dysentery |
| *Pseudomonas aeruginosa* | 6 | Opportunistic pathogen |
| *Acinetobacter baumannii* | 1 | Hospital-acquired infections |

### 6.4 Unclassified ("Unknown") Sequences

Several samples show high proportions of unclassified sequences:

| Barcode | Unknown % | Possible Explanation |
|---------|-----------|---------------------|
| BC12 | 100% | Very low read count (50 total) |
| BC14 | 100% | Very low read count (415 total) |
| BC16 | 100% | Low coverage enrichment |
| BC17 | 100% | Low coverage sample |
| BC04 | 91.06% | Novel organisms or technical issues |
| BC23 | 90.55% | Despite high reads (455K) |
| BC19 | 81.68% | High unknown proportion |
| BC10 | 81.61% | Enriched sample effect |

**Note:** High unknown percentages may indicate novel organisms, sequencing artifacts, or database limitations.

### 6.5 Phage Detection

Bacteriophages were detected in enriched sample BC20:

| Phage | Read Count | Host |
|-------|------------|------|
| Escherichia phage GeorgBuechner | 232 | E. coli |
| Escherichia phage vB_EcoS_Sponge | 66 | E. coli |
| Escherichia phage BF9 | 62 | E. coli |
| Escherichia phage TheodorHerzl | 58 | E. coli |
| Escherichia phage vb_EcoS_bov22_1 | 48 | E. coli |

Also detected:
- **Goslarvirus goslar** (BC13): 2,125 reads
- **Asteriusvirus PBECO4** (BC22): 35 reads

### 6.6 Methanogenic Archaea

Methanogens detected indicate anaerobic conditions:

| Species | Samples | Read Count |
|---------|---------|------------|
| *Methanoculleus chikugoensis* | BC04, BC23 | 167, 2,010 |
| *Methanoculleus bourgensis* | BC23 | 1,541 |
| *Methanocorpusculum labreanum* | BC04 | 179 |

---

## 7. Comparative Analysis

### 7.1 Native vs. Enriched Samples

| Metric | Native | Enriched |
|--------|--------|----------|
| **Average Reads** | ~116,000 | ~73,000 |
| **E. coli Dominance** | More consistent | Variable |
| **Unknown %** | Lower average | Higher average |
| **Species Diversity** | Higher | Lower |

### 7.2 Poultry vs. Pig Farms

| Metric | Poultry | Pig |
|--------|---------|-----|
| **Samples** | 8 | 16 |
| **Dominant Species** | E. coli | E. coli/Unknown |
| **Average Reads** | ~187,000 | ~83,000 |
| **Pathogen Diversity** | Moderate | Higher |

---

## 8. Technical Appendix

### 8.1 File Format Specifications

#### metadata.csv

```csv
Columns: Barcode, Sample ID, Farm Type, Farm ID, Sample Type, Oblast, Collection Period
Data types: string, string, string, string, string, string, string
Rows: 24 (+ header)
Encoding: UTF-8
```

#### top_species_by_barcode.csv

```csv
Columns: barcode, rank, species, read_count, relative_abundance_pct
Data types: string, integer (1-10), string, integer, float
Rows: ~205 (+ header)
Note: barcode format is "barcodeXX" (lowercase, zero-padded)
```

#### species_with_metadata.csv

```csv
Columns: Barcode, Sample ID, Farm Type, Farm ID, Sample Type, Oblast,
         rank, species, read_count, relative_abundance_pct, total_reads
Data types: string, string, string, string, string, string,
            integer, string, integer, float, integer
Rows: 205 (+ header)
Note: Barcode format is "BCXX" (uppercase)
```

#### taxonomy_data.json

```json
{
  "barcodeXX": {
    "TaxonName": {
      "rank": "superkingdom|phylum|class|order|family|genus|species",
      "count": integer,
      "children": { /* nested taxa */ }
    }
  }
}
```

### 8.2 Data Dictionary

| Field | Description | Values/Range |
|-------|-------------|--------------|
| `Barcode` | Sample barcode ID | BC01-BC24 |
| `barcode` | Lowercase barcode | barcode01-barcode24 |
| `Sample ID` | Original sample identifier | e.g., "1.1.", "2. н" |
| `Farm Type` | Type of farm | "Poultry", "Pig" |
| `Farm ID` | Farm identifier | e.g., "poultry #1", "pig #3" |
| `Sample Type` | Sample preparation | "Native", "Enriched" |
| `Oblast` | Ukrainian administrative region | See Section 3.2 |
| `Collection Period` | When samples collected | "JAN-FEB 2025" |
| `rank` | Species ranking (1=most abundant) | 1-10 |
| `species` | Species name | Scientific names |
| `read_count` | Number of reads classified | 0 - 412,561 |
| `relative_abundance_pct` | Percentage of sample | 0.0 - 100.0 |
| `total_reads` | Total reads in sample | 50 - 455,616 |

### 8.3 Barcode ID Mapping

| CSV Format | JSON Format | Sample |
|------------|-------------|--------|
| BC01 | barcode01 | 1.1. Native |
| BC02 | barcode02 | 1.1. н Enriched |
| ... | ... | ... |
| BC24 | barcode24 | 11 н Enriched |

---

## 9. Quality Notes and Recommendations

### 9.1 Data Quality Issues

1. **Low-yield samples:** BC12, BC14, BC16, BC17 have insufficient reads for reliable analysis
2. **High unknown percentages:** Several samples (BC04, BC23, BC19, BC10) show >80% unclassified reads
3. **Missing Oblast data:** BC11, BC12, BC24 lack geographic information

### 9.2 Recommendations

1. **Re-sequence low-yield samples** if material is available
2. **Investigate high-unknown samples** with alternative databases or assembly approaches
3. **Update metadata** to fill missing Oblast information
4. **Consider deeper sequencing** for enriched samples with low diversity

---

## 10. Summary

This metagenomics analysis of 24 Ukrainian farm wastewater samples revealed:

- **Dominant microbiome:** Enterobacteriaceae family, particularly *E. coli*
- **Farm-type differences:** Poultry samples showed higher sequencing depth
- **Pathogen presence:** Multiple clinically relevant species detected including *Salmonella*, *Klebsiella*, and *Shigella*
- **Phage discovery:** Multiple *Escherichia* phages identified in enriched sample BC20
- **Data coverage:** Variable sequencing depth (50 - 455,616 reads per sample)

The processed data files provide a foundation for downstream analyses including:
- Antimicrobial resistance gene profiling
- Phage-host interaction studies
- Comparative microbiome analysis across farm types and regions

---

*Report generated as part of the bio-phagent project*
*Data processing: 1st iteration - initial analyses*
