#!/usr/bin/env python3
"""Merge AMRFinderPlus results with MOB-suite plasmid classification and farm metadata.

Produces per-barcode and combined annotated AMR tables with priority/ESBL/plasmid flags.

Inputs:
    - PHAGENT_AMR/TSV/barcode{XX}_amr.tsv  (AMRFinderPlus output)
    - PHAGENT_AMR/mob_results/barcode{XX}/contig_report.txt  (MOB-suite output)
    - output/basic/barcode_farm_mapping.csv  (farm metadata)

Outputs:
    - PHAGENT_AMR/results/merged/barcode{XX}_amr_annotated.tsv  (per-barcode)
    - PHAGENT_AMR/results/merged/all_samples_amr_annotated.tsv  (combined)
"""

from pathlib import Path

import pandas as pd

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent  # PHAGENT_AMR/
PROJECT_ROOT = BASE_DIR.parent  # bio-phagent/

AMR_TSV_DIR = BASE_DIR / "TSV"
MOB_RESULTS_DIR = BASE_DIR / "mob_results"
METADATA_FILE = PROJECT_ROOT / "output" / "basic" / "barcode_farm_mapping.csv"
MERGED_DIR = BASE_DIR / "results" / "merged"

# --- Constants ---
HIGH_PRIORITY_CLASSES = {"BETA-LACTAM", "CARBAPENEM", "COLISTIN", "QUINOLONE"}
ESBL_PREFIX = "bla"


def load_amr_results(amr_dir: Path) -> pd.DataFrame:
    """Load all AMRFinderPlus TSV files, adding a barcode column."""
    frames = []
    for tsv_file in sorted(amr_dir.glob("barcode*_amr.tsv")):
        barcode = tsv_file.stem.replace("_amr", "")
        df = pd.read_csv(tsv_file, sep="\t")
        if df.empty:
            continue
        df["barcode"] = barcode
        frames.append(df)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def load_mob_results(mob_dir: Path) -> pd.DataFrame:
    """Load all MOB-suite contig_report.txt files, extracting barcode from sample_id."""
    frames = []
    for report_file in sorted(mob_dir.glob("barcode*/contig_report.txt")):
        df = pd.read_csv(report_file, sep="\t")
        if df.empty:
            continue
        # Extract barcode from sample_id (e.g. "barcode07_assembly" -> "barcode07")
        df["barcode"] = df["sample_id"].str.replace("_assembly", "", regex=False)
        frames.append(df)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def load_metadata(metadata_file: Path) -> pd.DataFrame:
    """Load barcode-to-farm metadata mapping."""
    return pd.read_csv(metadata_file)


def merge_all(amr_df: pd.DataFrame, mob_df: pd.DataFrame, meta_df: pd.DataFrame) -> pd.DataFrame:
    """Merge AMR results with MOB-suite plasmid data and farm metadata."""
    if amr_df.empty:
        print("  No AMR genes detected across any sample.")
        return pd.DataFrame()

    # Select relevant MOB columns for the merge
    mob_cols = [
        "barcode", "contig_id", "molecule_type", "primary_cluster_id",
        "secondary_cluster_id", "rep_type(s)", "relaxase_type(s)",
        "mpf_type", "predicted_mobility", "mash_nearest_neighbor",
        "mash_neighbor_distance", "mash_neighbor_identification",
    ]
    mob_subset = mob_df[mob_cols].copy() if not mob_df.empty else pd.DataFrame(columns=mob_cols)

    # Merge AMR with MOB on barcode + contig ID
    merged = amr_df.merge(
        mob_subset,
        left_on=["barcode", "Contig id"],
        right_on=["barcode", "contig_id"],
        how="left",
    )

    # Merge with farm metadata on barcode
    merged = merged.merge(meta_df, on="barcode", how="left")

    # Add derived flag columns
    merged["is_priority"] = merged["Class"].isin(HIGH_PRIORITY_CLASSES)
    merged["is_esbl"] = merged["Element symbol"].str.startswith(ESBL_PREFIX, na=False)
    merged["is_plasmid_borne"] = merged["molecule_type"].str.lower().eq("plasmid")

    # Drop redundant contig_id column from MOB (already have "Contig id" from AMR)
    merged.drop(columns=["contig_id"], errors="ignore", inplace=True)

    return merged


def main():
    MERGED_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading AMR results...")
    amr_df = load_amr_results(AMR_TSV_DIR)
    print(f"  {len(amr_df)} AMR gene detections from {amr_df['barcode'].nunique() if not amr_df.empty else 0} barcodes")

    print("Loading MOB-suite results...")
    mob_df = load_mob_results(MOB_RESULTS_DIR)
    print(f"  {len(mob_df)} contig classifications from {mob_df['barcode'].nunique() if not mob_df.empty else 0} barcodes")

    print("Loading farm metadata...")
    meta_df = load_metadata(METADATA_FILE)
    print(f"  {len(meta_df)} barcode-to-farm mappings")

    print("Merging datasets...")
    merged = merge_all(amr_df, mob_df, meta_df)

    if merged.empty:
        print("No AMR data to write.")
        return

    # Write combined table
    combined_path = MERGED_DIR / "all_samples_amr_annotated.tsv"
    merged.to_csv(combined_path, sep="\t", index=False)
    print(f"  Combined table: {combined_path} ({len(merged)} rows)")

    # Write per-barcode tables
    for barcode, group in merged.groupby("barcode"):
        barcode_path = MERGED_DIR / f"{barcode}_amr_annotated.tsv"
        group.to_csv(barcode_path, sep="\t", index=False)
        print(f"  {barcode}: {len(group)} genes -> {barcode_path.name}")

    # Summary
    priority_count = merged["is_priority"].sum()
    esbl_count = merged["is_esbl"].sum()
    plasmid_count = merged["is_plasmid_borne"].sum()
    print(f"\nMerge complete: {len(merged)} total AMR genes, "
          f"{priority_count} priority, {esbl_count} ESBL, {plasmid_count} plasmid-borne")


if __name__ == "__main__":
    main()
