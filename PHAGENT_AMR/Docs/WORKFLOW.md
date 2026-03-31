# PHAGENT_AMR Workflow Documentation

This document provides visual documentation of the assembly-based AMR profiling pipeline.

---

## Pipeline Overview

```mermaid
flowchart TD
    subgraph INPUT["1. RAW DATA"]
        direction TB
        FASTQ[/"FASTQ files<br/>barcode01-24.fastq.gz"/]
        META[/"barcode_farm_mapping.csv<br/>farm metadata"/]
    end

    subgraph ASSEMBLY["2. ASSEMBLY & POLISHING"]
        direction TB
        FLYE["metaFlye<br/>metagenome assembly"]
        MEDAKA["Medaka<br/>consensus polishing"]
        FLYE --> MEDAKA
    end

    subgraph DETECTION["3. AMR & PLASMID DETECTION"]
        direction TB
        AMR["AMRFinderPlus<br/>AMR gene annotation"]
        MOB["MOB-suite<br/>plasmid classification"]
    end

    subgraph ANALYSIS["4. MERGE & REPORTING"]
        direction TB
        MERGE["05_merge_results.py<br/>join AMR + MOB + metadata"]
        REPORT["06_report.py<br/>summary tables & priority findings"]
        MERGE --> REPORT
    end

    subgraph OUTPUT["5. OUTPUTS"]
        direction TB
        ANNOTATED[/"results/merged/<br/>annotated AMR tables"/]
        SUMMARY[/"results/reports/<br/>sample, farm, priority summaries"/]
    end

    INPUT --> ASSEMBLY
    ASSEMBLY --> DETECTION
    DETECTION --> ANALYSIS
    META --> ANALYSIS
    ANALYSIS --> OUTPUT

    style INPUT fill:#dbeafe,stroke:#3b82f6
    style ASSEMBLY fill:#fae8ff,stroke:#a855f7
    style DETECTION fill:#fef3c7,stroke:#f59e0b
    style ANALYSIS fill:#dcfce7,stroke:#22c55e
    style OUTPUT fill:#f0fdf4,stroke:#16a34a
```

---

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant FLYE as 01_assemble.py
    participant MED as 02_polish.py
    participant AMR as 03_amrfinder.py
    participant MOB as 04_mob_recon.py
    participant MERGE as 05_merge_results.py
    participant RPT as 06_report.py

    Note over U,FLYE: Step 1: Metagenome Assembly
    U->>FLYE: Run per-sample assembly
    FLYE->>FLYE: flye --nano-raw --meta
    FLYE-->>U: results/assembly/barcode{XX}_assembly.fasta

    Note over U,MED: Step 2: Consensus Polishing
    U->>MED: Run per-sample polishing
    MED->>MED: medaka_consensus
    MED-->>U: results/polished/barcode{XX}_consensus.fasta

    Note over U,MOB: Step 3: AMR & Plasmid Detection (parallel)
    par AMR detection
        U->>AMR: Run AMRFinderPlus on polished contigs
        AMR->>AMR: amrfinder -n (nucleotide mode)
        AMR-->>U: results/amr/barcode{XX}_amr.tsv
    and Plasmid classification
        U->>MOB: Run MOB-suite on assemblies
        MOB->>MOB: mob_recon
        MOB-->>U: results/mob/barcode{XX}/contig_report.txt
    end

    Note over U,MERGE: Step 4: Merge & Annotate
    U->>MERGE: Join AMR + MOB + farm metadata
    MERGE->>MERGE: Left-join on barcode + contig_id
    MERGE->>MERGE: Add priority / ESBL / plasmid flags
    MERGE-->>U: results/merged/all_samples_amr_annotated.tsv

    Note over U,RPT: Step 5: Generate Reports
    U->>RPT: Generate summaries
    RPT-->>U: results/reports/*.csv

    Note over U,RPT: Pipeline Complete
```

---

## Data Transformation Diagram

```mermaid
flowchart TD
    subgraph RAW["Raw Reads"]
        R1["barcode07.fastq.gz<br/>~thousands of reads"]
        R2["barcode08.fastq.gz"]
        R3["...24 samples"]
    end

    subgraph CONTIGS["Assembled Contigs"]
        C1["barcode07_assembly.fasta<br/>4 contigs, 5.6 KB"]
        C2["barcode08_assembly.fasta<br/>4 contigs, 13 KB"]
        C3["..."]
    end

    subgraph POLISHED["Polished Consensus"]
        P1["barcode07_consensus.fasta<br/>2 contigs, 5.5 KB"]
        P2["barcode08_consensus.fasta<br/>4 contigs, 13 KB"]
        P3["..."]
    end

    subgraph AMR_HITS["AMR Detections"]
        A1["barcode07_amr.tsv<br/>1 gene: qnrD1"]
        A2["barcode08_amr.tsv<br/>0 genes"]
        A3["..."]
    end

    subgraph MOB_CLASS["Plasmid Classification"]
        M1["contig_report.txt<br/>chromosome vs plasmid<br/>per contig"]
    end

    subgraph MERGED["Annotated AMR Table"]
        MG["all_samples_amr_annotated.tsv<br/>gene + contig + plasmid + farm"]
    end

    subgraph REPORTS["Summary Reports"]
        S1["amr_summary_by_sample.csv"]
        S2["priority_findings.csv"]
        S3["cross_sample_summary.csv"]
        S4["farm_level_summary.csv"]
    end

    RAW -->|"Flye --meta"| CONTIGS
    CONTIGS -->|"Medaka"| POLISHED
    POLISHED -->|"AMRFinderPlus -n"| AMR_HITS
    CONTIGS -->|"MOB-recon"| MOB_CLASS
    AMR_HITS --> MERGED
    MOB_CLASS --> MERGED
    MERGED --> REPORTS

    style RAW fill:#dbeafe,stroke:#3b82f6
    style CONTIGS fill:#ede9fe,stroke:#8b5cf6
    style POLISHED fill:#fae8ff,stroke:#a855f7
    style AMR_HITS fill:#fef3c7,stroke:#f59e0b
    style MOB_CLASS fill:#fef3c7,stroke:#f59e0b
    style MERGED fill:#dcfce7,stroke:#22c55e
    style REPORTS fill:#f0fdf4,stroke:#16a34a
```

---

## Evidence Model

Each AMR finding is traceable through the full chain:

```mermaid
flowchart LR
    SAMPLE["Sample<br/>(barcode)"] --> FARM["Farm<br/>(farm_id, type, oblast)"]
    SAMPLE --> CONTIG["Contig<br/>(contig_id)"]
    CONTIG --> GENE["AMR Gene<br/>(symbol, class, identity%)"]
    CONTIG --> PLASMID["Plasmid Context<br/>(molecule_type, mobility)"]
    GENE --> PRIORITY["Priority Flag<br/>(ESBL, colistin, carbapenem)"]
    PLASMID --> NEIGHBOR["Nearest Neighbor<br/>(mash identification)"]

    style SAMPLE fill:#dbeafe,stroke:#3b82f6
    style FARM fill:#dbeafe,stroke:#3b82f6
    style CONTIG fill:#fae8ff,stroke:#a855f7
    style GENE fill:#fef3c7,stroke:#f59e0b
    style PLASMID fill:#fef3c7,stroke:#f59e0b
    style PRIORITY fill:#fee2e2,stroke:#ef4444
    style NEIGHBOR fill:#f0fdf4,stroke:#16a34a
```

---

## Tool Chain Summary

| Step | Tool | Input | Output | Key Parameters |
|------|------|-------|--------|----------------|
| Assembly | metaFlye | Raw FASTQ | Contigs FASTA | `--nano-raw --meta` |
| Polishing | Medaka | FASTQ + Assembly | Consensus FASTA | `-m r1041_e82_400bps_sup_v5.2.0` |
| AMR Detection | AMRFinderPlus | Polished contigs | AMR gene TSV | `-n` (nucleotide mode) |
| Plasmid Typing | MOB-suite | Assembly contigs | Contig report | `mob_recon` |
| Merge | Python/pandas | AMR + MOB + metadata | Annotated table | Left joins on barcode + contig |
| Report | Python/pandas | Annotated table | Summary CSVs | Priority filtering, aggregation |

---

## Comparison with Main Pipeline

| Aspect | Main Pipeline | PHAGENT_AMR |
|--------|---------------|-------------|
| AMR source | ResFinder (read-level) | AMRFinderPlus (contig-level) |
| Evidence type | Individual reads | Assembled contigs |
| Plasmid context | None | MOB-suite classification |
| Confidence | Coverage % + Identity % | Assembly + gene coordinates |
| Scope | All 24 barcodes | Currently 4 (scalable to 24) |
| Best for | Broad screening | High-confidence, evidence-backed findings |

---
