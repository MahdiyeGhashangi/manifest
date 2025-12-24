import os
import pandas as pd
import hashlib
from PIL import Image
from sklearn.model_selection import train_test_split
from pathlib import Path
from typing import Dict, Optional

# Configuration
DATASET_DIR = r"C:\Users\hami 4\Desktop\project\BOSSbase_1.01"


def compute_hash(file_path: str) -> Optional[str]:
    """Compute SHA256 hash of a file."""
    sha = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Read in chunks for memory efficiency
            for chunk in iter(lambda: f.read(8192), b""):
                sha.update(chunk)
        return sha.hexdigest()
    except Exception as e:
        print(f"Hash error for {file_path}: {e}")
        return None


def extract_image_info(file_path: str) -> Dict:
    """Extract all image information in a single pass."""
    info = {
        'width': None,
        'height': None,
        'format': None,
        'decode_ok': False,
        'error_msg': None
    }

    try:
        with Image.open(file_path) as img:
            info['width'], info['height'] = img.size
            info['format'] = img.format
            info['decode_ok'] = True
    except Exception as e:
        info['error_msg'] = str(e)
        info['format'] = 'decode_error'

    return info


def detect_cover_stego(filename: str) -> str:
    """Detect if image is cover or stego based on filename."""
    name_lower = filename.lower()
    if "stego" in name_lower:
        return "stego"
    elif "cover" in name_lower:
        return "cover"
    else:
        return "unknown"  # BOSSBase = all covers


def create_image_dataframe(dataset_dir: str) -> pd.DataFrame:
    """Create comprehensive dataframe from image directory."""

    # Get all image files
    all_files = [f for f in os.listdir(dataset_dir)
                 if os.path.isfile(os.path.join(dataset_dir, f))]

    if not all_files:
        raise ValueError(f"No files found in {dataset_dir}")

    print(f"Found {len(all_files)} files")

    # Split into train/val/test sets efficiently
    train_files, temp_files = train_test_split(
        all_files, test_size=0.30, random_state=42
    )
    val_files, test_files = train_test_split(
        temp_files, test_size=0.50, random_state=42
    )

    # Create split lookup dictionary for O(1) access
    split_dict = {f: 'train' for f in train_files}
    split_dict.update({f: 'val' for f in val_files})
    split_dict.update({f: 'test' for f in test_files})

    # Process all images in a single loop
    records = []
    for filename in all_files:
        file_path = os.path.join(dataset_dir, filename)

        # Extract all info at once
        img_info = extract_image_info(file_path)

        record = {
            'filename': filename,
            'image_id': os.path.splitext(filename)[0],
            'path': file_path,
            'split': split_dict[filename],
            'cover_stego': detect_cover_stego(filename),
            'format': img_info['format'],
            'w': img_info['width'],
            'h': img_info['height'],
            'decode_ok': img_info['decode_ok'],
            'hash': compute_hash(file_path)
        }

        records.append(record)

    # Create dataframe
    df = pd.DataFrame(records)

    return df


# Main execution
if __name__ == "__main__":
    print("Creating dataframe...")
    df = create_image_dataframe(DATASET_DIR)

    # Display summary statistics
    print("\n" + "=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)

    print(f"\nTotal images: {len(df)}")

    print(f"\nSplit distribution:")
    print(df['split'].value_counts().to_string())

    print(f"\nFormat distribution:")
    print(df['format'].value_counts().to_string())

    print(f"\nCover/Stego distribution:")
    print(df['cover_stego'].value_counts().to_string())

    print(f"\nDecode success rate:")
    print(df['decode_ok'].value_counts().to_string())

    print(f"\nUnique image dimensions:")
    unique_dims = df[df['decode_ok']][['w', 'h']].drop_duplicates()
    print(unique_dims.to_string())

    print(f"\nData quality checks:")
    print(f"  - Duplicate rows: {df.duplicated().sum()}")
    print(f"  - Missing values per column:")
    print(f"{df.isnull().sum().to_string()}")
    print(f"  - Unique hashes: {df['hash'].nunique()} (should equal total images)")

    print("\n" + "=" * 60)
    print("First 5 rows:")
    print("=" * 60)
    print(df.head().to_string())

    # Optional: Save to CSV
    # output_path = "bossbase_metadata.csv"
    # df.to_csv(output_path, index=False)
    # print(f"\nDataframe saved to {output_path}")