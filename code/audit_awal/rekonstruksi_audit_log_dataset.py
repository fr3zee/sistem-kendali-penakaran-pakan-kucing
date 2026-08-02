import os
import re
import pandas as pd
import numpy as np
from pathlib import Path

# CONFIG
REPO_ROOT = Path(__file__).resolve().parents[2]
LOGS_DIR = REPO_ROOT / "data" / "pengujian_final" / "log_160_trial"
MASTER_CSV = REPO_ROOT / "data" / "pengujian_final" / "master_dataset_160.csv"
OUTPUT_DIR = REPO_ROOT / "hasil" / "audit_awal"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TOLERANCES = {
    "FinalMass_g": 0.01,
    "FinalError_g": 0.01,
    "AbsError_pct": 0.01,
    "Duration_s": 0.01,
    "MaxOvershoot_pct": 0.01,
    "RiseTime_10_90_s": 0.01,
    "SettlingTime_s": 0.01,
}

# Mapping folder to Scenario
SCENARIO_MAP = {
    "manual_cepat": "Manual Cepat",
    "manual_presisi": "Manual Presisi",
    "fixed_pid": "Fixed PID",
    "gs_pid": "GS PID"
}

def parse_log(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Parse SUMMARY
    summary = {}
    summary_start = content.find('=== SUMMARY TRIAL ===')
    if summary_start != -1:
        summary_text = content[summary_start:content.find('=== TRIAL END ===')]
        for line in summary_text.split('\n'):
            if ':' in line and not line.startswith('==='):
                k, v = line.split(':', 1)
                summary[k.strip()] = v.strip()

    # Parse DATA
    data_start = content.find('=== DATA START ===')
    data_end = content.find('=== DATA END ===')
    if data_end == -1:
        data_end = content.find('--------------------------------------------', data_start)
    
    data_lines = []
    if data_start != -1 and data_end != -1:
        raw_data = content[data_start:data_end].split('\n')
        for line in raw_data:
            if line.startswith('DATA,'):
                data_lines.append(line.split(','))
                
    df_data = None
    if data_lines:
        # Some headers have Zone, I, D, Bridging etc. We rely on index or standard columns
        # DataFormat is in the header, usually: DATA,ms,mass_g,error_g,error_pct,output,servo_deg,...
        # We will parse columns dynamically if possible, or just fallback to fixed indices
        
        # Look for DataFormat line
        format_line = next((l for l in content.split('\n') if l.startswith('DataFormat:')), None)
        if format_line:
            cols = format_line.split(':')[1].strip().split(',')
            # Pad or truncate data_lines to match cols length
            clean_lines = []
            for row in data_lines:
                if len(row) > len(cols):
                    # Maybe I,D, zone have extra commas? No, just truncate or ignore
                    row = row[:len(cols)]
                elif len(row) < len(cols):
                    row += [''] * (len(cols) - len(row))
                clean_lines.append(row)
            df_data = pd.DataFrame(clean_lines, columns=cols)
        else:
            # Fallback
            df_data = pd.DataFrame(data_lines)
            
        # Convert ms and mass_g to numeric
        if df_data is not None:
            # Usually ms is col 1, mass_g is col 2
            try:
                if 'ms' in df_data.columns:
                    df_data['ms'] = pd.to_numeric(df_data['ms'], errors='coerce')
                else:
                    df_data[1] = pd.to_numeric(df_data[1], errors='coerce')
                    df_data.rename(columns={1: 'ms'}, inplace=True)
                    
                if 'mass_g' in df_data.columns:
                    df_data['mass_g'] = pd.to_numeric(df_data['mass_g'], errors='coerce')
                else:
                    df_data[2] = pd.to_numeric(df_data[2], errors='coerce')
                    df_data.rename(columns={2: 'mass_g'}, inplace=True)
                    
            except Exception as e:
                print(f"Error parsing data in {file_path.name}: {e}")

    return summary, df_data

def reconstruct_metrics(summary, df_data, file_path):
    # Extract identity
    parts = file_path.parts
    scenario_folder = parts[-3]
    scenario = SCENARIO_MAP.get(scenario_folder, scenario_folder)
    
    sp_str = parts[-2] # e.g. SP15
    setpoint = float(sp_str.replace('SP', ''))
    
    filename = parts[-1]
    trial_match = re.search(r'trial(\d+)', filename.lower())
    trial_no = int(trial_match.group(1)) if trial_match else 1
    
    # 1. FinalMass_g from SUMMARY
    final_mass = float(summary.get('FinalMass_g', np.nan))
    if pd.isna(final_mass) and df_data is not None and not df_data.empty:
        final_mass = float(df_data['mass_g'].iloc[-1])
        
    # 2. FinalError_g
    final_error = final_mass - setpoint
    
    # 3. AbsError_pct
    abs_error_pct = abs(final_error) / setpoint * 100.0
    
    # 4. Duration_s
    duration_s = np.nan
    if 'Duration_ms' in summary:
        duration_s = float(summary['Duration_ms']) / 1000.0
    elif df_data is not None and not df_data.empty:
        duration_s = float(df_data['ms'].iloc[-1]) / 1000.0
        
    # 5. StopReason
    stop_reason = summary.get('StopReason', 'TARGET')
    
    # 6. MaxOvershoot_pct
    max_overshoot_pct = 0.0
    if df_data is not None and not df_data.empty:
        max_mass = df_data['mass_g'].max()
        if max_mass > setpoint:
            max_overshoot_pct = (max_mass - setpoint) / setpoint * 100.0
            
    # 7. RiseTime_10_90_s
    risetime_s = np.nan
    if df_data is not None and not df_data.empty:
        t = df_data['ms'].values
        y = df_data['mass_g'].values
        
        target_10 = 0.1 * setpoint
        target_90 = 0.9 * setpoint
        
        idx_10 = np.where(y >= target_10)[0]
        idx_90 = np.where(y >= target_90)[0]
        
        if len(idx_10) > 0 and len(idx_90) > 0:
            t10 = t[idx_10[0]]
            t90 = t[idx_90[0]]
            risetime_s = (t90 - t10) / 1000.0

    # 8. SettlingTime_s
    settling_s = np.nan
    if df_data is not None and not df_data.empty:
        t = df_data['ms'].values
        y = df_data['mass_g'].values
        
        band_u = 1.05 * setpoint
        band_l = 0.95 * setpoint
        out_idx = np.where((y > band_u) | (y < band_l))[0]
        
        if len(out_idx) > 0:
            last_out = out_idx[-1]
            if last_out < len(t) - 1:
                settling_s = t[last_out + 1] / 1000.0
            else:
                settling_s = np.nan # Never settled
        else:
            settling_s = t[0] / 1000.0

    # 9. BridgingCount
    bridging = 0
    if 'BridgingCount' in summary:
        bridging = int(summary['BridgingCount'])
    elif 'Bridging' in summary:
        val = summary['Bridging'].lower().replace('x', '').strip()
        if val.isdigit():
            bridging = int(val)
            
    # 10. WithinTolerance
    within_tol = abs(abs_error_pct) <= 5.0
    
    return {
        'Scenario': scenario,
        'Setpoint_g': setpoint,
        'TrialNo': trial_no,
        'FinalMass_g': final_mass,
        'FinalError_g': final_error,
        'AbsError_pct': abs_error_pct,
        'MaxOvershoot_pct': max_overshoot_pct,
        'Duration_s': duration_s,
        'RiseTime_10_90_s': risetime_s,
        'SettlingTime_s': settling_s,
        'BridgingCount': bridging,
        'WithinTolerance': within_tol,
        'StopReason': stop_reason,
        'LogPath': str(file_path.relative_to(REPO_ROOT).as_posix())
    }

def main():
    print("Membaca log mentah...")
    log_files = list(LOGS_DIR.rglob('*.txt'))
    if not log_files:
        print("Log mentah tidak ditemukan.")
        return
        
    reconstructed = []
    for f in log_files:
        summary, data = parse_log(f)
        metrics = reconstruct_metrics(summary, data, f)
        reconstructed.append(metrics)
        
    df_recon = pd.DataFrame(reconstructed)
    df_master = pd.read_csv(MASTER_CSV)
    
    # Audit process
    audit_rows = []
    match_count = 0
    mismatch_count = 0
    
    cols_to_check = [
        'FinalMass_g', 'FinalError_g', 'AbsError_pct', 'MaxOvershoot_pct',
        'Duration_s', 'RiseTime_10_90_s', 'SettlingTime_s', 'BridgingCount',
        'WithinTolerance', 'StopReason'
    ]
    
    for _, recon_row in df_recon.iterrows():
        # Find matching row in master
        mask = (
            (df_master['Scenario'] == recon_row['Scenario']) &
            (df_master['Setpoint_g'] == recon_row['Setpoint_g']) &
            (df_master['TrialNo'] == recon_row['TrialNo'])
        )
        master_matches = df_master[mask]
        
        if master_matches.empty:
            audit_rows.append({
                'Scenario': recon_row['Scenario'],
                'Setpoint_g': recon_row['Setpoint_g'],
                'TrialNo': recon_row['TrialNo'],
                'LogPath': recon_row['LogPath'],
                'Column': 'ALL',
                'LogValue': '',
                'DatasetValue': '',
                'AbsoluteDifference': '',
                'Tolerance': '',
                'Status': 'NOT_VERIFIABLE',
                'Notes': 'Row not found in master dataset'
            })
            mismatch_count += 1
            continue
            
        master_row = master_matches.iloc[0]
        
        for col in cols_to_check:
            log_val = recon_row[col]
            dataset_val = master_row[col]
            
            # Numeric comparison
            if col in TOLERANCES:
                tol = TOLERANCES[col]
                # Handle NaN
                if pd.isna(log_val) and pd.isna(dataset_val):
                    status = 'MATCH'
                    diff = 0.0
                    note = 'Both NaN'
                elif pd.isna(log_val) or pd.isna(dataset_val):
                    status = 'MISMATCH'
                    diff = np.nan
                    note = 'One is NaN'
                else:
                    diff = abs(log_val - dataset_val)
                    if diff <= tol:
                        status = 'MATCH'
                        note = 'Within tolerance'
                    else:
                        status = 'MISMATCH'
                        note = 'Outside tolerance'
                
                audit_rows.append({
                    'Scenario': recon_row['Scenario'],
                    'Setpoint_g': recon_row['Setpoint_g'],
                    'TrialNo': recon_row['TrialNo'],
                    'LogPath': recon_row['LogPath'],
                    'Column': col,
                    'LogValue': log_val,
                    'DatasetValue': dataset_val,
                    'AbsoluteDifference': diff,
                    'Tolerance': tol,
                    'Status': status,
                    'Notes': note
                })
                
                if status == 'MATCH': match_count += 1
                else: mismatch_count += 1
                
            else:
                # Exact comparison (bool, string, int)
                # Handle boolean matching strictly or converting
                if isinstance(dataset_val, bool) or isinstance(dataset_val, np.bool_):
                    log_val = bool(log_val)
                elif isinstance(dataset_val, str):
                    log_val = str(log_val)
                
                diff = ''
                if log_val == dataset_val:
                    status = 'MATCH'
                    note = 'Exact match'
                else:
                    status = 'MISMATCH'
                    note = 'Different values'
                    
                audit_rows.append({
                    'Scenario': recon_row['Scenario'],
                    'Setpoint_g': recon_row['Setpoint_g'],
                    'TrialNo': recon_row['TrialNo'],
                    'LogPath': recon_row['LogPath'],
                    'Column': col,
                    'LogValue': log_val,
                    'DatasetValue': dataset_val,
                    'AbsoluteDifference': diff,
                    'Tolerance': 'EXACT',
                    'Status': status,
                    'Notes': note
                })
                
                if status == 'MATCH': match_count += 1
                else: mismatch_count += 1

    df_audit = pd.DataFrame(audit_rows)
    
    # Save outputs
    df_recon.to_csv(OUTPUT_DIR / 'dataset_rekonstruksi_dari_log.csv', index=False)
    df_audit.to_csv(OUTPUT_DIR / 'audit_160_log_vs_dataset.csv', index=False)
    
    total = match_count + mismatch_count
    
    report = [
        "# Ringkasan Audit Log Mentah vs Dataset",
        "",
        f"Total baris diperiksa: {total}",
        f"- MATCH: {match_count}",
        f"- MISMATCH: {mismatch_count}",
        ""
    ]
    
    if mismatch_count > 0:
        report.append("## Daftar MISMATCH")
        mismatches = df_audit[df_audit['Status'] != 'MATCH']
        # Group by column to see where problems are
        report.append("Berdasarkan metrik:")
        for k, v in mismatches.groupby('Column').size().items():
            report.append(f"- {k}: {v} errors")
            
    with open(OUTPUT_DIR / 'ringkasan_audit_log_dataset.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
        
    print(f"Audit selesai. MATCH: {match_count}, MISMATCH: {mismatch_count}")

if __name__ == '__main__':
    main()
