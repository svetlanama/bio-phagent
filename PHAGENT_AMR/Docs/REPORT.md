# PHAGENT_AMR: Assembly-Based AMR Profiling Report

**Project:** Bio-phagent — Metagenomics Analysis of Ukrainian Farm Wastewater
**Subproject:** PHAGENT_AMR — Contig-Backed AMR Detection with Plasmid Context
**Date:** March 2026
**Samples:** 4 of 24 barcodes (barcode07, barcode08, barcode09, barcode18)
**Data source:** Nanopore long-read sequencing (WW_FarmUAA_RLB_20250219)

---

## Executive Summary

Assembly-based AMR profiling was performed on 4 farm wastewater samples using a Flye → Medaka → AMRFinderPlus + MOB-suite pipeline. **Three quinolone resistance genes (qnrD/qnrD1) were detected**, all located on **small Col3M-type plasmids** closely related to *Proteus mirabilis* plasmids. The findings span 3 farms (1 poultry, 2 pig) across 2 oblasts. No ESBL, colistin resistance, or carbapenemase genes were detected in the analyzed samples.

This approach complements the main pipeline's read-level ResFinder analysis by providing **contig-backed evidence** with plasmid context — enabling higher confidence in individual AMR gene calls and their genomic location.

---

## 1. Samples Analyzed

| Barcode | Sample ID | Farm | Farm Type | Sample Type | Oblast |
|---------|-----------|------|-----------|-------------|--------|
| barcode07 | 4. | poultry #3 | Poultry | Native | Kyiv Oblast |
| barcode08 | 4. н | poultry #3 | Poultry | Enriched | Kyiv Oblast |
| barcode09 | 5.1. | pig #2 | Pig | Native | Kyiv Oblast |
| barcode18 | 8. н | pig #5 | Pig | Enriched | Chernivtsi Oblast |

**Note:** These 4 barcodes are a subset of the full 24-sample dataset. The remaining 20 barcodes have not yet been processed through the assembly pipeline. Some barcodes (barcode03, barcode11, barcode23, barcode24) are known to produce empty assemblies due to low read counts.

---

## 2. Assembly Results

### 2.1 Metagenome Assembly (metaFlye)

| Barcode | Contigs | Total Size (bp) | Notes |
|---------|---------|-----------------|-------|
| barcode07 | 2 | 5,697 | Small assembly — 2 contigs |
| barcode08 | 5 | 13,594 | Moderate — 5 contigs |
| barcode09 | 10 | 36,064 | Largest contig count |
| barcode18 | 29 | 108,311 | Largest assembly by size |

All assemblies were generated with `flye --nano-raw --meta`. Assembly sizes are small relative to full metagenomes, consistent with low-biomass wastewater samples processed with nanopore sequencing.

### 2.2 Consensus Polishing (Medaka)

| Barcode | Polished Contigs | Polished Size (bp) | Size Change |
|---------|-----------------|--------------------|----|
| barcode07 | 2 | 5,599 | -1.7% |
| barcode08 | 5 | 13,371 | -1.6% |
| barcode09 | 10 | 35,440 | -1.7% |
| barcode18 | 29 | 106,421 | -1.7% |

Polishing with Medaka (model `r1041_e82_400bps_sup_v5.2.0`) reduced assembly size by ~1.7% across all samples, consistent with correction of homopolymer-related insertion errors typical of nanopore data.

---

## 3. AMR Gene Detections

### 3.1 Summary

| Metric | Value |
|--------|-------|
| Samples analyzed | 4 |
| Samples with AMR genes | 3 |
| Total AMR genes detected | 3 |
| Unique gene symbols | 2 (qnrD1, qnrD) |
| Resistance classes | 1 (QUINOLONE) |
| Priority findings | 3 (all QUINOLONE) |
| ESBL genes | 0 |
| Colistin resistance genes | 0 |
| Carbapenemase genes | 0 |
| Plasmid-borne genes | 3 (100%) |

### 3.2 Detailed Findings

| Barcode | Farm | Gene | Contig | Method | Coverage | Identity | Reference |
|---------|------|------|--------|--------|----------|----------|-----------|
| barcode07 | poultry #3 | **qnrD1** | contig_2 | ALLELEX | 100.00% | 100.00% | WP_012634451.1 |
| barcode08 | poultry #3 | — | — | — | — | — | No AMR genes detected |
| barcode09 | pig #2 | **qnrD** | contig_4 | PARTIALX | 83.64% | 100.00% | WP_012634451.1 |
| barcode18 | pig #5 | **qnrD1** | contig_20 | ALLELEX | 100.00% | 100.00% | WP_012634451.1 |

**Detection methods:**
- **ALLELEX** — Exact allele match (highest confidence). Used for barcode07 and barcode18.
- **PARTIALX** — Partial match with 100% identity but incomplete coverage (83.64%). The barcode09 qnrD gene is truncated or located at a contig boundary.

### 3.3 Cross-Sample Distribution

| Gene | Class | Samples | Farms | Always Plasmid-Borne |
|------|-------|---------|-------|---------------------|
| qnrD1 | QUINOLONE | 2 (barcode07, barcode18) | 2 (poultry #3, pig #5) | Yes |
| qnrD | QUINOLONE | 1 (barcode09) | 1 (pig #2) | Yes |

The qnrD/qnrD1 genes were found across **3 different farms** in **2 oblasts** (Kyiv, Chernivtsi), spanning both pig and poultry operations. This suggests widespread distribution of quinolone resistance in the sampled farm environments.

---

## 4. Plasmid Context

### 4.1 MOB-suite Classification

| Barcode | Total Contigs | Chromosome | Plasmid | Plasmid Clusters |
|---------|--------------|------------|---------|-----------------|
| barcode07 | 2 | 1 | 1 | AB434 |
| barcode08 | 4 | 4 | 0 | — |
| barcode09 | 10 | 8 | 2 | AB434, AD087 |
| barcode18 | 29 | 28 | 1 | AB434 |

### 4.2 AMR–Plasmid Association

All 3 detected AMR genes are located on **plasmid contigs**, specifically within the **AB434 cluster**:

| Barcode | Gene | Contig | Plasmid Cluster | Replicon Type | Nearest Neighbor | Mash Distance |
|---------|------|--------|----------------|---------------|------------------|---------------|
| barcode07 | qnrD1 | contig_2 | AB434 / AK211 | Col3M | *Proteus mirabilis* (JQ776508) | 0.00266 |
| barcode09 | qnrD | contig_4 | AB434 / AK211 | Col3M | *Proteus mirabilis* (JQ776508) | 0.00379 |
| barcode18 | qnrD1 | contig_20 | AB434 / AK211 | Col3M | *Proteus mirabilis* (JQ776508) | 0.00142 |

**Key observations:**
- All qnrD/qnrD1 genes reside on **Col3M-type ColE1-family plasmids** — small, high-copy-number plasmids commonly found in Enterobacteriaceae
- The nearest known plasmid neighbor in all 3 cases is ***Proteus mirabilis*** plasmid JQ776508
- Very low Mash distances (0.0014–0.0038) indicate these plasmids are closely related across all 3 samples, suggesting a **common plasmid lineage** circulating across farms
- barcode09 also carries a second plasmid (cluster AD087, MOBP relaxase) with closest match to *Salmonella enterica* (CP039608) — this plasmid does not carry detected AMR genes

### 4.3 Interpretation

The co-occurrence of qnrD/qnrD1 on nearly identical Col3M plasmids across pig and poultry farms in different oblasts points to **horizontal gene transfer** as a likely dissemination mechanism. Col3M plasmids are mobilizable and can transfer between species within the gut microbiome, enabling quinolone resistance spread through farm wastewater environments.

---

## 5. Farm-Level Summary

| Farm | Type | Oblast | Samples Analyzed | AMR Genes | Priority Genes | Plasmid-Borne |
|------|------|--------|-----------------|-----------|----------------|---------------|
| poultry #3 | Poultry | Kyiv Oblast | 2 | 1 | 1 | 1 |
| pig #2 | Pig | Kyiv Oblast | 1 | 1 | 1 | 1 |
| pig #5 | Pig | Chernivtsi Oblast | 1 | 1 | 1 | 1 |

**Poultry #3** has 2 samples (Native and Enriched), but AMR was only detected in the Native sample (barcode07). The absence of qnrD1 in the Enriched sample (barcode08) may reflect:
- Stochastic assembly differences in low-biomass samples
- Enrichment conditions that did not select for quinolone-resistant organisms
- Insufficient sequencing depth in the enriched sample

---

## 6. Priority Findings

### 6.1 High-Priority AMR Categories

| Category | Status | Details |
|----------|--------|---------|
| **ESBL genes** | **Not detected** | No bla-prefix genes found in any sample |
| **Colistin resistance** | **Not detected** | No mcr or other colistin resistance genes |
| **Carbapenemases** | **Not detected** | No carbapenemase genes (KPC, NDM, OXA-48, VIM, IMP) |
| **Quinolone resistance** | **Detected** | qnrD/qnrD1 in 3 of 4 samples, all plasmid-borne |

### 6.2 Quinolone Resistance — qnrD/qnrD1

**Clinical significance:** qnrD genes encode pentapeptide repeat proteins that protect DNA gyrase and topoisomerase IV from quinolone antibiotics (ciprofloxacin, levofloxacin, norfloxacin). While qnrD alone confers low-level resistance, it can:
- Facilitate selection of higher-level resistance mutations
- Act synergistically with other resistance mechanisms
- Spread horizontally via plasmid transfer between species

**Public health relevance:** Quinolones are critically important antimicrobials (WHO classification) used widely in both human medicine and veterinary practice. Detection of plasmid-mediated quinolone resistance in farm wastewater indicates a reservoir for resistance dissemination into the environment.

---

## 7. Comparison with Read-Level AMR Analysis

The main bio-phagent pipeline detected AMR using ResFinder on raw reads (EPI2ME wf-metagenomics). Here is a comparison for the same 4 barcodes:

| Aspect | Read-Level (ResFinder) | Contig-Level (AMRFinderPlus) |
|--------|----------------------|------------------------------|
| **Approach** | Screen individual reads against ResFinder DB | Annotate assembled contigs |
| **Evidence strength** | Single-read support | Contig-backed, multi-read consensus |
| **Plasmid context** | Not available | MOB-suite classification per contig |
| **Sensitivity** | Higher — detects genes from unassembled reads | Lower — requires successful assembly |
| **Specificity** | Lower — individual reads may be chimeric | Higher — contigs represent validated sequences |
| **Gene count** | Many (broad screening) | Few (high-confidence only) |

**Complementary use:** The read-level approach provides broad AMR screening across all samples, while the assembly-based approach provides high-confidence, evidence-backed findings with genomic context. Both approaches are valuable and should be interpreted together.

---

## 8. Limitations and Caveats

1. **Partial sample coverage:** Only 4 of 24 barcodes have been analyzed. Findings cannot be generalized to all farms without processing the remaining 20 samples.

2. **Small assembly sizes:** Assemblies range from 5.6–108 KB, far smaller than typical metagenomes. This reflects the low-biomass nature of the samples and means many organisms and AMR genes present in the community may not have assembled.

3. **Assembly bias:** Metagenome assembly from nanopore data favors high-abundance organisms. Rare AMR-carrying organisms may be missed entirely.

4. **Single detection method:** AMRFinderPlus was used in nucleotide mode only (`-n`). Running in protein mode (`-p`) on translated ORFs could detect additional divergent AMR genes not captured by nucleotide search.

5. **No PlasmidFinder:** PlasmidFinder was not run as an additional replicon detection tool. MOB-suite's built-in replicon database was used instead, which covers most known replicon types but may miss novel ones.

6. **Partial gene in barcode09:** The qnrD detection in barcode09 shows only 83.64% coverage, indicating the gene may be truncated at a contig boundary. This could represent a fragmented assembly rather than a truly partial gene.

7. **Temporal snapshot:** All samples were collected in JAN-FEB 2025. AMR profiles may vary seasonally.

---

## 9. Recommendations

### Immediate Next Steps

1. **Process remaining 20 barcodes** through the full assembly pipeline to enable farm-level and region-level comparisons.
2. **Run AMRFinderPlus in protein mode** (`-p` on predicted ORFs) to capture divergent AMR genes missed by nucleotide search.
3. **Cross-reference with read-level results** — compare qnrD/qnrD1 detections from AMRFinderPlus against ResFinder results for the same barcodes to assess concordance.

### Scientific Follow-Up

4. **Investigate the Col3M plasmid lineage** — the near-identical AB434 plasmids across farms warrant further characterization (full plasmid alignment, phylogenetics).
5. **Assess co-resistance potential** — check whether qnrD-carrying contigs or neighboring contigs carry additional resistance determinants.
6. **Compare Native vs Enriched samples** across all farms — the absence of qnrD1 in barcode08 (Enriched) vs presence in barcode07 (Native) is notable and warrants investigation at larger sample size.

### Pipeline Improvements

7. **Add assembly quality metrics** — integrate contig N50, total length, and coverage statistics into the reporting pipeline.
8. **Add PlasmidFinder** as a supplementary replicon detection tool.
9. **Create visualization notebook** — AMR heatmaps, plasmid association plots, and farm comparison charts for the full 24-sample dataset.

---

## 10. Methods Summary

### Pipeline

```
Raw FASTQ (Nanopore) → metaFlye (--meta) → Medaka (r1041_e82_400bps_sup_v5.2.0)
    → AMRFinderPlus (-n, nucleotide mode)
    → MOB-suite (mob_recon)
    → Merge (AMR + MOB + farm metadata)
    → Report (priority findings, sample/farm summaries)
```

### Tools and Versions

| Tool | Version | Database |
|------|---------|----------|
| Flye | >= 2.9 | N/A (de novo assembly) |
| Medaka | latest | Model: r1041_e82_400bps_sup_v5.2.0 |
| AMRFinderPlus | latest | NCBI AMRFinder DB (auto-updated) |
| MOB-suite | 3.1.9 | NCBI plasmid DB, MOB/MPF/oriT databases |

### Priority Classification

AMR genes were flagged as priority if their resistance class matched: **BETA-LACTAM**, **CARBAPENEM**, **COLISTIN**, or **QUINOLONE**. ESBL genes were additionally flagged by the `bla` prefix in the gene symbol. Plasmid association was determined by MOB-suite molecule_type classification.

---

## Appendix: Output Files

| File | Description |
|------|-------------|
| `results/merged/all_samples_amr_annotated.tsv` | Combined annotated AMR table (3 rows) |
| `results/merged/barcode{XX}_amr_annotated.tsv` | Per-barcode annotated tables |
| `results/reports/amr_summary_by_sample.csv` | Per-sample AMR summary (4 rows) |
| `results/reports/priority_findings.csv` | Priority AMR findings (3 rows) |
| `results/reports/cross_sample_summary.csv` | Gene-centric cross-sample view (2 rows) |
| `results/reports/farm_level_summary.csv` | Farm-level aggregation (3 rows) |
| `TSV/barcode{XX}_amr.tsv` | Raw AMRFinderPlus output per barcode |
| `mob_results.zip` | MOB-suite contig classification per barcode |

---
