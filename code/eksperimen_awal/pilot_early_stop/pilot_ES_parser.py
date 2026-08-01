#!/usr/bin/env python3
"""
Pilot Early Stop Data Parser
Recursively scans trial files and extracts summary data.
"""

import os
import re
import csv
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Configuration
BASE_DIR = Path(r"D:\SKRIPSI\draft\3. dok trial hasil\02_PILOT_EARLY_STOP")
OUTPUT_CSV = Path(r"D:\SKRIPSI\draft\3. dok trial hasil\02_PILOT_EARLY_STOP\pilot_ES_master.csv")

# Field definitions with expected types
FIELDS_COMMON = [
    'Controller', 'Setpoint_g', 'EarlyStop_g', 'StopTarget_g',
    'FinalMass_g', 'FinalError_g', 'FinalError_pct',
    'Duration_ms', 'Duration_s',
    'TimeTo90_ms', 'RiseTime_10_90_ms', 'TimeToTolerance_ms', 'SettlingTime_ms',
    'SettlingTol_pct', 'SettlingTol_g',
    'MaxMass_g', 'MaxOvershoot_g', 'MaxOvershoot_pct',
    'BridgingCount', 'Status', 'Valid', 'StopReason'
]

FIELDS_GS_ONLY = ['ZonaHit_Z1', 'ZonaHit_Z2', 'ZonaHit_Z3']

ALL_FIELDS = FIELDS_COMMON + FIELDS_GS_ONLY


def parse_summary_section(file_path: Path) -> Optional[Dict[str, any]]:
    """
    Parse the === SUMMARY TRIAL === section from a trial file.
    
    Args:
        file_path: Path to the trial .txt file
        
    Returns:
        Dictionary with parsed fields, or None if parsing failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the summary section
        summary_start = content.find('=== SUMMARY TRIAL ===')
        summary_end = content.find('=== TRIAL END ===')
        
        if summary_start == -1 or summary_end == -1:
            print(f"WARNING: Summary section not found in {file_path.name}")
            return None
        
        summary_section = content[summary_start:summary_end]
        lines = summary_section.split('\n')
        
        # Parse key-value pairs
        data = {}
        for line in lines:
            line = line.strip()
            if ':' in line and not line.startswith('==='):
                # Split on first colon only
                key_val = line.split(':', 1)
                if len(key_val) == 2:
                    key = key_val[0].strip()
                    value = key_val[1].strip()
                    data[key] = value
        
        # Convert to standardized field names and types
        parsed = {}
        
        # String fields
        parsed['Controller'] = data.get('Controller', '')
        parsed['Status'] = data.get('Status', '')
        parsed['Valid'] = data.get('Valid', '')
        parsed['StopReason'] = data.get('StopReason', '')
        
        # Numeric fields - convert to float
        numeric_fields = [
            'Setpoint_g', 'EarlyStop_g', 'StopTarget_g',
            'FinalMass_g', 'FinalError_g', 'FinalError_pct',
            'Duration_ms', 'Duration_s',
            'TimeTo90_ms', 'RiseTime_10_90_ms', 'TimeToTolerance_ms', 'SettlingTime_ms',
            'SettlingTol_pct', 'SettlingTol_g',
            'MaxMass_g', 'MaxOvershoot_g', 'MaxOvershoot_pct',
            'BridgingCount'
        ]
        
        for field in numeric_fields:
            if field in data:
                try:
                    parsed[field] = float(data[field])
                except ValueError:
                    parsed[field] = None
            else:
                parsed[field] = None
        
        # GS PID specific fields
        gs_fields = ['ZonaHit_Z1', 'ZonaHit_Z2', 'ZonaHit_Z3']
        for field in gs_fields:
            if field in data:
                try:
                    parsed[field] = int(data[field])
                except ValueError:
                    parsed[field] = None
            else:
                parsed[field] = None
        
        return parsed
        
    except Exception as e:
        print(f"ERROR parsing {file_path.name}: {e}")
        return None


def extract_metadata_from_path(file_path: Path) -> Dict[str, str]:
    """
    Extract controller type, setpoint, and early stop from file path.
    
    Args:
        file_path: Path to the trial file
        
    Returns:
        Dictionary with path-based metadata
    """
    parts = file_path.parts
    
    metadata = {
        'FilePath': str(file_path),
        'FileName': file_path.name,
        'ControllerFolder': '',
        'SetpointFolder': '',
        'EarlyStopFolder': ''
    }
    
    # Find controller folder (Fixed_PID or Gain_Scheduling_PID)
    for part in parts:
        if 'Fixed_PID' in part:
            metadata['ControllerFolder'] = 'Fixed_PID'
        elif 'Gain_Scheduling_PID' in part:
            metadata['ControllerFolder'] = 'Gain_Scheduling_PID'
    
    # Find setpoint folder (e.g., "15 gram")
    for part in parts:
        if 'gram' in part:
            metadata['SetpointFolder'] = part
    
    # Find early stop folder (e.g., "ES_0_2")
    for part in parts:
        if part.startswith('ES_'):
            metadata['EarlyStopFolder'] = part
    
    return metadata


def validate_filename_consistency(file_path: Path, parsed_data: Dict) -> List[str]:
    """
    Check if filename matches parsed data content.
    
    Args:
        file_path: Path to the file
        parsed_data: Parsed summary data
        
    Returns:
        List of validation warnings (empty if all OK)
    """
    warnings = []
    filename = file_path.name
    
    # Extract info from filename
    # Fixed PID: Fixed_0.2_SP15_trial01.txt
    # GS PID: GS_ES0.3_SP20_trial01.txt
    
    # Check controller type
    if 'Fixed' in filename and parsed_data.get('Controller') != 'Fixed PID':
        warnings.append(f"Controller mismatch: filename has 'Fixed' but parsed '{parsed_data.get('Controller')}'")
    elif 'GS' in filename and parsed_data.get('Controller') != 'Gain Scheduling PID':
        warnings.append(f"Controller mismatch: filename has 'GS' but parsed '{parsed_data.get('Controller')}'")
    
    # Extract setpoint from filename
    sp_match = re.search(r'SP(\d+)', filename)
    if sp_match and parsed_data.get('Setpoint_g'):
        sp_filename = float(sp_match.group(1))
        sp_parsed = parsed_data.get('Setpoint_g')
        if abs(sp_filename - sp_parsed) > 0.01:
            warnings.append(f"Setpoint mismatch: filename SP{sp_filename} vs parsed {sp_parsed}g")
    
    # Extract early stop from filename
    es_match = re.search(r'(?:Fixed_|ES)(0\.\d+)', filename)
    if es_match and parsed_data.get('EarlyStop_g'):
        es_filename = float(es_match.group(1))
        es_parsed = parsed_data.get('EarlyStop_g')
        if abs(es_filename - es_parsed) > 0.01:
            warnings.append(f"EarlyStop mismatch: filename {es_filename} vs parsed {es_parsed}g")
    
    return warnings


def scan_and_parse_all(base_dir: Path) -> List[Dict]:
    """
    Recursively scan directories and parse all trial files.
    
    Args:
        base_dir: Base directory containing Fixed_PID and Gain_Scheduling_PID folders
        
    Returns:
        List of dictionaries, one per successfully parsed trial
    """
    results = []
    txt_files = list(base_dir.rglob('*.txt'))
    
    print(f"Found {len(txt_files)} .txt files")
    print("Parsing files...")
    
    for i, file_path in enumerate(txt_files, 1):
        print(f"  [{i}/{len(txt_files)}] {file_path.name}...", end='')
        
        # Parse summary section
        parsed_data = parse_summary_section(file_path)
        
        if parsed_data is None:
            print(" FAILED")
            # Still add a row with metadata for tracking
            metadata = extract_metadata_from_path(file_path)
            row = metadata.copy()
            row['ParseStatus'] = 'FAILED'
            row['QC_Flags'] = 'Parse error'
            results.append(row)
            continue
        
        # Extract path metadata
        metadata = extract_metadata_from_path(file_path)
        
        # Validate filename consistency
        warnings = validate_filename_consistency(file_path, parsed_data)
        
        # Combine all data
        row = metadata.copy()
        row.update(parsed_data)
        row['ParseStatus'] = 'SUCCESS'
        row['QC_Flags'] = '; '.join(warnings) if warnings else ''
        
        results.append(row)
        print(" OK")
    
    print(f"\nSuccessfully parsed {sum(1 for r in results if r.get('ParseStatus') == 'SUCCESS')} / {len(txt_files)} files")
    
    return results


def write_to_csv(data: List[Dict], output_path: Path):
    """
    Write parsed data to CSV file.
    
    Args:
        data: List of dictionaries with trial data
        output_path: Path to output CSV file
    """
    if not data:
        print("No data to write!")
        return
    
    # Define column order
    metadata_cols = ['FilePath', 'FileName', 'ControllerFolder', 'SetpointFolder', 'EarlyStopFolder', 
                     'ParseStatus', 'QC_Flags']
    data_cols = ALL_FIELDS
    
    all_cols = metadata_cols + data_cols
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=all_cols, extrasaction='ignore')
        writer.writeheader()
        
        # Sort by controller, early stop, setpoint, filename
        sorted_data = sorted(data, key=lambda x: (
            x.get('ControllerFolder', ''),
            x.get('EarlyStopFolder', ''),
            x.get('SetpointFolder', ''),
            x.get('FileName', '')
        ))
        
        writer.writerows(sorted_data)
    
    print(f"\nCSV written to: {output_path}")
    print(f"Total rows: {len(data)}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("Pilot Early Stop Data Parser")
    print("=" * 60)
    print(f"Base directory: {BASE_DIR}")
    print(f"Output CSV: {OUTPUT_CSV}")
    print()
    
    if not BASE_DIR.exists():
        print(f"ERROR: Base directory not found: {BASE_DIR}")
        return
    
    # Scan and parse all files
    results = scan_and_parse_all(BASE_DIR)
    
    # Write to CSV
    write_to_csv(results, OUTPUT_CSV)
    
    print("\n" + "=" * 60)
    print("Parsing complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
