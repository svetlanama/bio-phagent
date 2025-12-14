# Workflow Documentation

This document provides visual documentation of the bio-phagent data pipeline.

---

## Pipeline Overview

```mermaid
flowchart TD
    subgraph EXPORT["1. DATA EXPORT"]
        direction TB
        H[/"HTML Report<br/>wf-metagenomics-report.html"/]
        W["wrapper.html"]
        H --> W
        W --> AB[/"abundances/*.csv"/]
        W --> AMR[/"antimicrobial_resistance/*.csv"/]
    end

    subgraph PROCESS["2. DATA PROCESSING"]
        direction TB
        M["create_output_mappings.py"]
        P["process_amr_data.py"]
        E["extract_species_by_barcode.py"]

        M --> P
        M --> E
    end

    subgraph OUTPUT["3. OUTPUTS"]
        direction TB
        BASIC[/"output/basic/<br/>mapping, taxonomy, diversity"/]
        AMROUT[/"output/amr/<br/>gene matrix, resistance classes"/]
        XLSX[/"output/xlsx/<br/>Excel with species sheets"/]
    end

    subgraph VIZ["4. VISUALIZATION"]
        direction TB
        NB1["taxonomy_visualization.ipynb"]
        NB2["amr_visualization.ipynb"]
    end

    EXPORT --> PROCESS
    PROCESS --> OUTPUT
    OUTPUT --> VIZ

    style EXPORT fill:#dbeafe,stroke:#3b82f6
    style PROCESS fill:#fae8ff,stroke:#a855f7
    style OUTPUT fill:#dcfce7,stroke:#22c55e
    style VIZ fill:#fef3c7,stroke:#f59e0b
```

---

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant HTML as HTML Report
    participant EXP as /export
    participant M as create_output_mappings.py
    participant P as process_amr_data.py
    participant E as extract_species_by_barcode.py
    participant OUT as /output

    Note over U,HTML: Step 1: Export Data
    U->>HTML: Open wrapper.html
    HTML->>EXP: Export abundance CSVs
    HTML->>EXP: Export AMR CSVs

    Note over U,M: Step 2: Create Mappings
    U->>M: Run script
    M->>EXP: Read abundances
    M->>OUT: Write barcode_farm_mapping.csv
    M->>OUT: Write taxonomy_barcode_bacteria.csv
    M->>OUT: Write diversity_indices.csv

    Note over U,P: Step 3: Process AMR
    U->>P: Run script
    P->>OUT: Read barcode_farm_mapping.csv
    P->>EXP: Read AMR files (barcode01-24)
    P->>OUT: Write amr_by_sample.csv
    P->>OUT: Write amr_full_data.csv
    P->>OUT: Write gene/class matrices

    Note over U,E: Step 4: Extract Species
    U->>E: Run script --all
    E->>EXP: Read species abundance
    E->>OUT: Add sheets to Excel

    Note over U,OUT: Complete!
    U-->>OUT: View results
```

---

## File Structure

```mermaid
graph TD
    ROOT["bio-phagent/"]

    ROOT --> INPUT["input/"]
    ROOT --> WIP["wip/"]
    ROOT --> EXPORT["export/"]
    ROOT --> OUTPUT["output/"]
    ROOT --> SCRIPTS["scripts/"]
    ROOT --> DOCS["*.md"]

    INPUT --> HTML["wf-metagenomics-report.html"]
    INPUT --> WRAP["wrapper.html"]

    WIP --> META["[WIP] UA_FARM_WW_CLEAN_METADATA.xlsx"]

    EXPORT --> ABD["abundances/"]
    EXPORT --> AMR["antimicrobial_resistance/"]

    ABD --> TABLE["table/ (6 files)"]
    ABD --> RARE["rarefied/ (6 files)"]
    AMR --> AMRCSV["amr_barcode01-24.csv"]

    OUTPUT --> BASIC["basic/"]
    OUTPUT --> AMRDIR["amr/"]
    OUTPUT --> XLSX["xlsx/"]

    BASIC --> BFM["barcode_farm_mapping.csv"]
    BASIC --> TBB["taxonomy_barcode_bacteria.csv"]
    BASIC --> DIV["diversity_indices.csv"]
    BASIC --> TNOTE["taxonomy_visualization.ipynb"]

    AMRDIR --> ABS["amr_by_sample.csv"]
    AMRDIR --> AFD["amr_full_data.csv"]
    AMRDIR --> AGM["amr_gene_matrix.csv"]
    AMRDIR --> ARC["amr_resistance_class_matrix.csv"]
    AMRDIR --> ANOTE["amr_visualization.ipynb"]

    XLSX --> XLSXF["[FINAL] UA_FARM_WW_CLEAN_METADATA.xlsx"]

    SCRIPTS --> S1["create_output_mappings.py"]
    SCRIPTS --> S2["process_amr_data.py"]
    SCRIPTS --> S3["extract_species_by_barcode.py"]

    style ROOT fill:#f0f9ff
    style INPUT fill:#fee2e2
    style EXPORT fill:#dbeafe
    style OUTPUT fill:#dcfce7
    style SCRIPTS fill:#fae8ff
```

---

## Script Dependencies

```mermaid
graph LR
    subgraph INPUTS["Input Sources"]
        META["Metadata Excel"]
        ABD["Abundance CSVs"]
        AMRCSV["AMR CSVs"]
    end

    subgraph SCRIPTS["Scripts"]
        S1["create_output_mappings.py"]
        S2["process_amr_data.py"]
        S3["extract_species_by_barcode.py"]
    end

    subgraph OUTPUTS["Outputs"]
        MAP["barcode_farm_mapping.csv"]
        TAX["taxonomy_barcode_bacteria.csv"]
        DIV["diversity_indices.csv"]
        AMROUT["AMR analysis files"]
        XLSXOUT["Excel with species"]
    end

    META --> S1
    ABD --> S1
    S1 --> MAP
    S1 --> TAX
    S1 --> DIV

    MAP --> S2
    AMRCSV --> S2
    S2 --> AMROUT

    MAP --> S3
    ABD --> S3
    S3 --> XLSXOUT

    style S1 fill:#a855f7,color:#fff
    style S2 fill:#3b82f6,color:#fff
    style S3 fill:#22c55e,color:#fff
```

---

## Input/Output Schemas

### Abundance Table Format

```
| species      | barcode01 | barcode02 | ... | barcode24 | phylum   | class     | ... |
|--------------|-----------|-----------|-----|-----------|----------|-----------|-----|
| E. coli      | 15234     | 12456     | ... | 8923      | Pseudo.. | Gamma..   | ... |
```

### AMR File Format

```
| Gene         | ReadID                               | Coverage % | Identity % | Resistance          |
|--------------|--------------------------------------|------------|------------|---------------------|
| aph(3'')-Ib  | b963a3b5-5373-43f2-8d97-47fbacb269fa | 98.76      | 96.56      | Streptomycin        |
| tetA         | c1d2e3f4-...                         | 95.43      | 98.21      | Tetracycline;Chlor.. |
```

### Output: barcode_farm_mapping.csv

```
| barcode   | sample_id | farm_type | farm_id     | sample_type | oblast              |
|-----------|-----------|-----------|-------------|-------------|---------------------|
| barcode01 | 1.1.      | Poultry   | poultry #1  | Native      | Zaporizhzhia Oblast |
| barcode02 | 1.1. n    | Poultry   | poultry #1  | Enriched    | Zaporizhzhia Oblast |
```

### Output: amr_by_sample.csv

```
| barcode   | farm_type | total_gene_detections | unique_reads | unique_genes | unique_resistance_classes |
|-----------|-----------|----------------------|--------------|--------------|---------------------------|
| barcode01 | Poultry   | 247                  | 211          | 13           | 27                        |
| barcode02 | Poultry   | 2727                 | 2586         | 46           | 22                        |
```

---

## Execution Order

```mermaid
graph LR
    A["1. Export from HTML"] --> B["2. create_output_mappings.py"]
    B --> C["3. process_amr_data.py"]
    B --> D["4. extract_species_by_barcode.py"]
    C --> E["5. Run Jupyter notebooks"]
    D --> E

    style A fill:#fee2e2
    style B fill:#a855f7,color:#fff
    style C fill:#3b82f6,color:#fff
    style D fill:#22c55e,color:#fff
    style E fill:#fef3c7
```

**Note:** Steps 3 and 4 can run in parallel after step 2.

---

## Sample Distribution

```mermaid
pie title Farm Type Distribution
    "Pig" : 20
    "Poultry" : 4
```

```mermaid
pie title Sample Type Distribution
    "Native" : 12
    "Enriched" : 12
```

---

*Generated for bio-phagent metagenomics pipeline - December 2024*
