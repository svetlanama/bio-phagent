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
flowchart LR
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

## Script Dependencies

```mermaid
graph LR
    subgraph INPUTS["Input Sources"]
        FASTQ["Raw FASTQ<br/>barcode01-24"]
        META["barcode_farm_mapping.csv"]
    end

    subgraph SCRIPTS["Scripts"]
        S1["01_assemble.py"]
        S2["02_polish.py"]
        S3["03_amrfinder.py"]
        S4["04_mob_recon.py"]
        S5["05_merge_results.py"]
        S6["06_report.py"]
    end

    subgraph OUTPUTS["Outputs"]
        ASM["Assembly FASTA"]
        POL["Polished FASTA"]
        AMRTSV["AMR TSVs"]
        MOBRPT["MOB contig reports"]
        ANNOT["Annotated AMR tables"]
        RPT["Summary reports"]
    end

    FASTQ --> S1
    S1 --> ASM

    ASM --> S2
    FASTQ --> S2
    S2 --> POL

    POL --> S3
    S3 --> AMRTSV

    ASM --> S4
    S4 --> MOBRPT

    AMRTSV --> S5
    MOBRPT --> S5
    META --> S5
    S5 --> ANNOT

    ANNOT --> S6
    META --> S6
    S6 --> RPT

    style S1 fill:#8b5cf6,color:#fff
    style S2 fill:#a855f7,color:#fff
    style S3 fill:#f59e0b,color:#fff
    style S4 fill:#f59e0b,color:#fff
    style S5 fill:#22c55e,color:#fff
    style S6 fill:#16a34a,color:#fff
```

---

## File Structure

```mermaid
graph TD
    ROOT["PHAGENT_AMR/"]

    ROOT --> INPUT_DIR["Input/"]
    ROOT --> CODE["Code/"]
    ROOT --> SCRIPTS["scripts/"]
    ROOT --> RESULTS["results/"]
    ROOT --> DOCS["Docs/"]

    INPUT_DIR --> ZIP["WW_FarmUAA_RLB_20250219-fastqs.zip"]

    CODE --> NB1["contigs_for_barcode_v1.ipynb"]
    CODE --> NB2["contigs_for_barcode_v2.ipynb"]
    CODE --> NB3["mob_result.ipynb"]

    SCRIPTS --> SC1["01_assemble.py"]
    SCRIPTS --> SC2["02_polish.py"]
    SCRIPTS --> SC3["03_amrfinder.py"]
    SCRIPTS --> SC4["04_mob_recon.py"]
    SCRIPTS --> SC5["05_merge_results.py"]
    SCRIPTS --> SC6["06_report.py"]

    RESULTS --> ASM_DIR["assembly/"]
    RESULTS --> POL_DIR["polished/"]
    RESULTS --> AMR_DIR["amr/"]
    RESULTS --> MOB_DIR["mob/"]
    RESULTS --> MRG_DIR["merged/"]
    RESULTS --> RPT_DIR["reports/"]

    MRG_DIR --> MRG1["all_samples_amr_annotated.tsv"]
    MRG_DIR --> MRG2["barcode{XX}_amr_annotated.tsv"]

    RPT_DIR --> R1["amr_summary_by_sample.csv"]
    RPT_DIR --> R2["priority_findings.csv"]
    RPT_DIR --> R3["cross_sample_summary.csv"]
    RPT_DIR --> R4["farm_level_summary.csv"]

    DOCS --> DOC1["WORKFLOW.md"]
    DOCS --> DOC2["REPRODUCE.md"]

    style ROOT fill:#f0f9ff
    style INPUT_DIR fill:#fee2e2
    style CODE fill:#f5f5f4
    style SCRIPTS fill:#fae8ff
    style RESULTS fill:#dcfce7
    style DOCS fill:#dbeafe
```

---

## Execution Order

```mermaid
graph LR
    A["1. Prepare FASTQ"] --> B["2. 01_assemble.py"]
    B --> C["3. 02_polish.py"]
    C --> D["4a. 03_amrfinder.py"]
    C --> E["4b. 04_mob_recon.py"]
    D --> F["5. 05_merge_results.py"]
    E --> F
    F --> G["6. 06_report.py"]

    style A fill:#fee2e2
    style B fill:#8b5cf6,color:#fff
    style C fill:#a855f7,color:#fff
    style D fill:#f59e0b,color:#fff
    style E fill:#f59e0b,color:#fff
    style F fill:#22c55e,color:#fff
    style G fill:#16a34a,color:#fff
```

**Note:** Steps 4a and 4b can run in parallel after step 3.

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

```mermaid
flowchart LR
    subgraph MAIN["Main Pipeline (ResFinder / EPI2ME)"]
        direction TB
        MR["Raw reads"] -->|"read-level"| MRF["ResFinder"]
        MRF --> MOUT["51,451 AMR records<br/>198 genes, 47 classes"]
    end

    subgraph PHAGENT["PHAGENT_AMR Pipeline (Assembly-based)"]
        direction TB
        PR["Raw reads"] -->|"assembly"| PF["Flye + Medaka"]
        PF -->|"contig-level"| PAMR["AMRFinderPlus + MOB-suite"]
        PAMR --> POUT["Contig-backed AMR<br/>+ plasmid context"]
    end

    style MAIN fill:#dbeafe,stroke:#3b82f6
    style PHAGENT fill:#dcfce7,stroke:#22c55e
```

| Aspect | Main Pipeline | PHAGENT_AMR |
|--------|---------------|-------------|
| AMR source | ResFinder (read-level) | AMRFinderPlus (contig-level) |
| Evidence type | Individual reads | Assembled contigs |
| Plasmid context | None | MOB-suite classification |
| Confidence | Coverage % + Identity % | Assembly + gene coordinates |
| Scope | All 24 barcodes | Currently 4 (scalable to 24) |
| Best for | Broad screening | High-confidence, evidence-backed findings |

---
