#!/usr/bin/env python3
"""Generate AMR summary reports from merged annotated data.

Inputs:
    - PHAGENT_AMR/results/merged/all_samples_amr_annotated.tsv

Outputs:
    - PHAGENT_AMR/results/reports/amr_summary_by_sample.csv
    - PHAGENT_AMR/results/reports/priority_findings.csv
    - PHAGENT_AMR/results/reports/cross_sample_summary.csv
    - PHAGENT_AMR/results/reports/farm_level_summary.csv
"""

from pathlib import Path

import pandas as pd

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent  # PHAGENT_AMR/
MERGED_DIR = BASE_DIR / "results" / "merged"
REPORTS_DIR = BASE_DIR / "results" / "reports"
METADATA_FILE = BASE_DIR.parent / "output" / "basic" / "barcode_farm_mapping.csv"

# AMR TSV dir for detecting barcodes with no AMR hits
AMR_TSV_DIR = BASE_DIR / "TSV"

# Priority interpretation map
PRIORITY_INTERPRETATION = {
    "BETA-LACTAM": "Beta-lactam resistance — may confer resistance to penicillins, cephalosporins, or carbapenems",
    "CARBAPENEM": "Carbapenem resistance — last-resort antibiotic, critical public health concern",
    "COLISTIN": "Colistin resistance — last-resort antibiotic for multidrug-resistant Gram-negatives",
    "QUINOLONE": "Quinolone resistance — widely used antibiotic class in human and veterinary medicine",
}


def load_merged_data() -> pd.DataFrame:
    """Load the combined annotated AMR table."""
    path = MERGED_DIR / "all_samples_amr_annotated.tsv"
    if not path.exists():
        raise FileNotFoundError(f"Run 05_merge_results.py first. Missing: {path}")
    return pd.read_csv(path, sep="\t")


def get_all_analyzed_barcodes() -> list[str]:
    """Get list of all barcodes that have AMR TSV files (including empty ones)."""
    return sorted(f.stem.replace("_amr", "") for f in AMR_TSV_DIR.glob("barcode*_amr.tsv"))


def generate_sample_summary(df: pd.DataFrame, all_barcodes: list[str]) -> pd.DataFrame:
    """Per-sample AMR summary with gene counts and flags."""
    meta = pd.read_csv(METADATA_FILE)

    if df.empty:
        # All barcodes have 0 genes
        summary = meta[meta["barcode"].isin(all_barcodes)].copy()
        for col in ["total_amr_genes", "unique_amr_genes", "unique_classes",
                     "priority_gene_count", "esbl_gene_count", "plasmid_borne_count"]:
            summary[col] = 0
        summary["gene_list"] = ""
        return summary

    agg = df.groupby("barcode").agg(
        total_amr_genes=("Element symbol", "size"),
        unique_amr_genes=("Element symbol", "nunique"),
        unique_classes=("Class", "nunique"),
        priority_gene_count=("is_priority", "sum"),
        esbl_gene_count=("is_esbl", "sum"),
        plasmid_borne_count=("is_plasmid_borne", "sum"),
        gene_list=("Element symbol", lambda x: ", ".join(sorted(x.unique()))),
    ).reset_index()

    # Include barcodes with 0 AMR genes
    all_bc_df = pd.DataFrame({"barcode": all_barcodes})
    agg = all_bc_df.merge(agg, on="barcode", how="left")
    for col in ["total_amr_genes", "unique_amr_genes", "unique_classes",
                 "priority_gene_count", "esbl_gene_count", "plasmid_borne_count"]:
        agg[col] = agg[col].fillna(0).astype(int)
    agg["gene_list"] = agg["gene_list"].fillna("")

    # Merge with farm metadata
    summary = agg.merge(meta, on="barcode", how="left")

    # Reorder columns: metadata first, then counts
    meta_cols = ["barcode", "sample_id", "farm_type", "farm_id", "sample_type", "oblast"]
    count_cols = ["total_amr_genes", "unique_amr_genes", "unique_classes",
                  "priority_gene_count", "esbl_gene_count", "plasmid_borne_count", "gene_list"]
    ordered = [c for c in meta_cols if c in summary.columns] + count_cols
    return summary[ordered]


def generate_priority_findings(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to priority AMR hits with interpretation."""
    if df.empty:
        return pd.DataFrame()

    priority = df[df["is_priority"]].copy()
    if priority.empty:
        return pd.DataFrame()

    priority["interpretation"] = priority["Class"].map(PRIORITY_INTERPRETATION).fillna("")
    priority = priority.sort_values(["Class", "barcode"]).reset_index(drop=True)
    return priority


def generate_cross_sample_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Gene-centric view: which genes appear in which samples and farms."""
    if df.empty:
        return pd.DataFrame()

    agg = df.groupby(["Element symbol", "Class"]).agg(
        num_samples_detected=("barcode", "nunique"),
        sample_list=("barcode", lambda x: ", ".join(sorted(x.unique()))),
        num_farms_detected=("farm_id", "nunique"),
        farm_list=("farm_id", lambda x: ", ".join(sorted(x.dropna().unique()))),
        always_plasmid_borne=("is_plasmid_borne", "all"),
    ).reset_index()

    agg.columns = ["gene_symbol", "class", "num_samples_detected", "sample_list",
                    "num_farms_detected", "farm_list", "always_plasmid_borne"]
    return agg.sort_values("num_samples_detected", ascending=False).reset_index(drop=True)


def generate_farm_summary(df: pd.DataFrame, all_barcodes: list[str]) -> pd.DataFrame:
    """Farm-centric aggregation of AMR findings."""
    meta = pd.read_csv(METADATA_FILE)
    meta = meta[meta["barcode"].isin(all_barcodes)]

    if df.empty:
        farm_agg = meta.groupby(["farm_id", "farm_type", "oblast"]).agg(
            num_samples=("barcode", "nunique"),
        ).reset_index()
        for col in ["total_amr_genes", "unique_genes", "priority_genes", "plasmid_borne_genes"]:
            farm_agg[col] = 0
        return farm_agg

    # Merge metadata onto AMR data to get farm info for each gene
    merged = df[["barcode", "Element symbol", "Class", "is_priority", "is_plasmid_borne",
                  "farm_id", "farm_type", "oblast"]].copy()

    farm_agg = merged.groupby(["farm_id", "farm_type", "oblast"]).agg(
        total_amr_genes=("Element symbol", "size"),
        unique_genes=("Element symbol", "nunique"),
        priority_genes=("is_priority", "sum"),
        plasmid_borne_genes=("is_plasmid_borne", "sum"),
    ).reset_index()

    # Add sample count from metadata
    sample_counts = meta.groupby("farm_id")["barcode"].nunique().reset_index()
    sample_counts.columns = ["farm_id", "num_samples"]
    farm_agg = farm_agg.merge(sample_counts, on="farm_id", how="left")

    # Include farms with 0 AMR genes
    all_farms = meta.groupby(["farm_id", "farm_type", "oblast"]).agg(
        num_samples=("barcode", "nunique"),
    ).reset_index()
    farm_agg = all_farms.merge(
        farm_agg.drop(columns=["farm_type", "oblast", "num_samples"]),
        on="farm_id", how="left"
    )
    for col in ["total_amr_genes", "unique_genes", "priority_genes", "plasmid_borne_genes"]:
        farm_agg[col] = farm_agg[col].fillna(0).astype(int)

    return farm_agg.sort_values("total_amr_genes", ascending=False).reset_index(drop=True)


def print_summary(df: pd.DataFrame, sample_summary: pd.DataFrame,
                  priority_df: pd.DataFrame, cross_df: pd.DataFrame):
    """Print text summary to stdout."""
    print("\n" + "=" * 60)
    print("AMR REPORT SUMMARY")
    print("=" * 60)

    total_barcodes = len(sample_summary)
    barcodes_with_amr = (sample_summary["total_amr_genes"] > 0).sum()
    total_genes = len(df) if not df.empty else 0
    priority_count = len(priority_df)
    plasmid_count = int(df["is_plasmid_borne"].sum()) if not df.empty else 0

    print(f"\nSamples analyzed:     {total_barcodes}")
    print(f"Samples with AMR:     {barcodes_with_amr}")
    print(f"Total AMR genes:      {total_genes}")
    print(f"Priority findings:    {priority_count}")
    print(f"Plasmid-borne:        {plasmid_count}")

    if not priority_df.empty:
        print(f"\nPriority AMR detections:")
        for _, row in priority_df.iterrows():
            plasmid_tag = " [PLASMID]" if row.get("is_plasmid_borne") else ""
            print(f"  - {row['Element symbol']} ({row['Class']}) in {row['barcode']} "
                  f"on {row['Contig id']}{plasmid_tag}")

    if not cross_df.empty:
        print(f"\nRecurring genes across samples:")
        for _, row in cross_df.iterrows():
            print(f"  - {row['gene_symbol']} ({row['class']}): "
                  f"{row['num_samples_detected']} samples, {row['num_farms_detected']} farms")

    print("\n" + "=" * 60)


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading merged AMR data...")
    df = load_merged_data()
    all_barcodes = get_all_analyzed_barcodes()
    print(f"  {len(df)} annotated AMR records, {len(all_barcodes)} analyzed barcodes")

    # 1. Per-sample summary
    print("Generating per-sample summary...")
    sample_summary = generate_sample_summary(df, all_barcodes)
    path = REPORTS_DIR / "amr_summary_by_sample.csv"
    sample_summary.to_csv(path, index=False)
    print(f"  -> {path.name} ({len(sample_summary)} rows)")

    # 2. Priority findings
    print("Generating priority findings...")
    priority_df = generate_priority_findings(df)
    path = REPORTS_DIR / "priority_findings.csv"
    priority_df.to_csv(path, index=False)
    print(f"  -> {path.name} ({len(priority_df)} rows)")

    # 3. Cross-sample summary
    print("Generating cross-sample summary...")
    cross_df = generate_cross_sample_summary(df)
    path = REPORTS_DIR / "cross_sample_summary.csv"
    cross_df.to_csv(path, index=False)
    print(f"  -> {path.name} ({len(cross_df)} rows)")

    # 4. Farm-level summary
    print("Generating farm-level summary...")
    farm_df = generate_farm_summary(df, all_barcodes)
    path = REPORTS_DIR / "farm_level_summary.csv"
    farm_df.to_csv(path, index=False)
    print(f"  -> {path.name} ({len(farm_df)} rows)")

    # Print text summary
    print_summary(df, sample_summary, priority_df, cross_df)


if __name__ == "__main__":
    main()
