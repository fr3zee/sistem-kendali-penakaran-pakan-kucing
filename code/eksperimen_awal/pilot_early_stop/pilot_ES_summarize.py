#!/usr/bin/env python3
"""
Pilot Early Stop Statistical Summary Script
Generates aggregate statistics from master CSV.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple


# Configuration
INPUT_CSV = Path(r"D:\SKRIPSI\draft\3. dok trial hasil\02_PILOT_EARLY_STOP\pilot_ES_master.csv")
OUTPUT_ALL_VALID = Path(r"D:\SKRIPSI\draft\3. dok trial hasil\02_PILOT_EARLY_STOP\pilot_ES_summary_all_valid.csv")
OUTPUT_BALANCED = Path(r"D:\SKRIPSI\draft\3. dok trial hasil\02_PILOT_EARLY_STOP\pilot_ES_summary_balanced_3trial.csv")


def load_and_filter_data(csv_path: Path) -> pd.DataFrame:
    """Load master CSV and filter to valid trials only."""
    df = pd.read_csv(csv_path)
    
    # Filter to successfully parsed trials with Valid=TRUE (handle both string and boolean)
    df_valid = df[(df['ParseStatus'] == 'SUCCESS') & 
                  (df['Valid'].astype(str).str.upper() == 'TRUE')].copy()
    
    print(f"Loaded {len(df)} total rows")
    print(f"Filtered to {len(df_valid)} valid trials (Valid=TRUE)")
    
    return df_valid


def create_balanced_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create balanced dataset with max 3 trials per (Controller × ES × SP).
    Selects first 3 trials by filename alphabetical order.
    """
    balanced_rows = []
    
    groups = df.groupby(['Controller', 'EarlyStop_g', 'Setpoint_g'])
    
    for name, group in groups:
        # Sort by filename to get consistent ordering (trial01, trial02, trial03)
        sorted_group = group.sort_values('FileName')
        
        # Take first 3
        first_3 = sorted_group.head(3)
        balanced_rows.append(first_3)
    
    df_balanced = pd.concat(balanced_rows, ignore_index=True)
    
    print(f"Balanced dataset: {len(df_balanced)} trials (max 3 per combination)")
    
    return df_balanced


def compute_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute aggregate statistics per (Controller × EarlyStop × Setpoint).
    
    Returns:
        DataFrame with one row per combination and aggregate columns
    """
    aggregates = []
    
    groups = df.groupby(['Controller', 'EarlyStop_g', 'Setpoint_g'])
    
    for (controller, es, sp), group in groups:
        # Count valid trials
        n_valid = len(group)
        
        # Error metrics
        mean_final_error = group['FinalError_g'].mean()
        mean_abs_error = group['FinalError_g'].abs().mean()
        mae_pct = (group['FinalError_g'].abs() / group['Setpoint_g'] * 100).mean()
        sd_error = group['FinalError_g'].std()
        
        # Overshoot metrics
        mean_overshoot_g = group['MaxOvershoot_g'].mean()
        max_overshoot_g = group['MaxOvershoot_g'].max()
        mean_overshoot_pct = group['MaxOvershoot_pct'].mean()
        
        # Time metrics
        mean_duration_s = group['Duration_s'].mean()
        mean_timeto90_ms = group['TimeTo90_ms'].mean()
        mean_settling_time_ms = group['SettlingTime_ms'].mean()
        
        # Bridging
        mean_bridging = group['BridgingCount'].mean()
        
        # Status counts
        count_akurat = (group['Status'] == 'AKURAT').sum()
        count_overshoot = (group['Status'] == 'OVERSHOOT').sum()
        
        # Compile row
        agg_row = {
            'Controller': controller,
            'EarlyStop_g': es,
            'Setpoint_g': sp,
            'n_valid': n_valid,
            'mean_FinalError_g': mean_final_error,
            'mean_AbsError_g': mean_abs_error,
            'MAE_pct': mae_pct,
            'SD_error_g': sd_error,
            'mean_Overshoot_g': mean_overshoot_g,
            'max_Overshoot_g': max_overshoot_g,
            'mean_Overshoot_pct': mean_overshoot_pct,
            'mean_Duration_s': mean_duration_s,
            'mean_TimeTo90_ms': mean_timeto90_ms,
            'mean_SettlingTime_ms': mean_settling_time_ms,
            'mean_BridgingCount': mean_bridging,
            'count_AKURAT': count_akurat,
            'count_OVERSHOOT': count_overshoot,
            'count_invalid': 0
        }
        
        aggregates.append(agg_row)
    
    df_agg = pd.DataFrame(aggregates)
    
    # Sort by controller, early stop, setpoint
    df_agg = df_agg.sort_values(['Controller', 'EarlyStop_g', 'Setpoint_g'])
    
    return df_agg


def write_summary_csv(df_agg: pd.DataFrame, output_path: Path, description: str):
    """Write aggregate summary to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_agg.to_csv(output_path, index=False, float_format='%.3f')
    print(f"{description} written to: {output_path}")
    print(f"  Rows: {len(df_agg)}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Pilot Early Stop Statistical Summary")
    print("=" * 60)
    print(f"Input CSV: {INPUT_CSV}")
    print(f"Output (all valid): {OUTPUT_ALL_VALID}")
    print(f"Output (balanced): {OUTPUT_BALANCED}")
    print()
    
    if not INPUT_CSV.exists():
        print(f"ERROR: Input CSV not found: {INPUT_CSV}")
        return
    
    # Load valid data
    print("Loading and filtering data...")
    df_valid = load_and_filter_data(INPUT_CSV)
    print()
    
    # Generate summary using all valid trials
    print("Computing aggregates for ALL VALID trials...")
    df_agg_all = compute_aggregates(df_valid)
    write_summary_csv(df_agg_all, OUTPUT_ALL_VALID, "Summary (all valid)")
    print()
    
    # Create balanced dataset
    print("Creating balanced dataset (max 3 trials per combination)...")
    df_balanced = create_balanced_dataset(df_valid)
    print()
    
    # Generate summary using balanced dataset
    print("Computing aggregates for BALANCED 3-TRIAL dataset...")
    df_agg_balanced = compute_aggregates(df_balanced)
    write_summary_csv(df_agg_balanced, OUTPUT_BALANCED, "Summary (balanced 3-trial)")
    print()
    
    print("=" * 60)
    print("Summary generation complete!")
    print("=" * 60)
    
    # Quick stats
    print("\nQuick Statistics:")
    print(f"  Total valid trials: {len(df_valid)}")
    print(f"  Balanced trials: {len(df_balanced)}")
    print(f"  Combinations: {len(df_agg_all)}")
    print(f"  Controllers: {df_valid['Controller'].nunique()}")
    print(f"  Early Stop values: {sorted(df_valid['EarlyStop_g'].unique())}")
    print(f"  Setpoints: {sorted(df_valid['Setpoint_g'].unique())}")


if __name__ == '__main__':
    main()
