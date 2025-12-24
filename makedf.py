import os # list file in a directory
import pandas as pd
import hashlib
from PIL import Image # use to open image file
from sklearn.model_selection import train_test_split

# Absolute path to BOSSBase images folder
DATASET_DIR= r"C:\Users\hami 4\Desktop\project\BOSSbase_1.01"
all_images = os.listdir(DATASET_DIR)

sizes = []
decode_errors = 0

for filename in os.listdir(DATASET_DIR):
    file_path = os.path.join(DATASET_DIR, filename)

    try:
        # Attempt to open image
        img = Image.open(file_path)

        # Store (width, height)
        sizes.append(img.size)

    except Exception:
        # Count corrupted or unreadable images
        decode_errors += 1

print("Number of images:", len(sizes))
print("Unique sizes:", set(sizes))
print("Decode errors:", decode_errors)

# IMAGE_ID
image_id = os.path.splitext(filename)[0]
print(f"image_id[0]={image_id}")

# PATH
file_path = os.path.join(DATASET_DIR, filename)
print(f"file_path = {file_path}")

# SPLIT data with train, test and val cat.
# TRAIN and TEMP
train_files, temp_files = train_test_split(all_images, test_size=0.30, random_state=42)
val_files, test_files = train_test_split(temp_files, test_size=0.50, random_state=42)

# CREATE DATAFRAME
df = pd.DataFrame({
    "cover_stego": all_images,
    "image_id": [f.split('.')[0] for f in all_images],
    "path": [os.path.join(DATASET_DIR, f) for f in all_images],
    "split": ["train" if f in train_files else "val" if f in val_files else "test" for f in all_images]
})

#print(df.head())
#print(df['split'].value_counts())

# FORMAT
formats = []

for path in df['path']:
    try:
        img = Image.open(path)
        # check image format
        formats.append(img.format)
    except:
        formats.append("decode_error")  # if image doesnt open

# ADD to DataFrame
df['format'] = formats
print("\n",f"df format is: {df['format'].value_counts()}")

# COVER
#df['cover_stego'] = ['cover' for _ in range(len(df))] # because in BOSSbase dataset all the data are cover
#df['cover_stego'].value_counts()
def detect_cover_stego(cover_stego): #although we know that "boss" only have the "cover"
    name = cover_stego.lower()

    if "stego" in name:
        return "stego"
    elif "cover" in name:
        return "cover"
    else:
        return "unknown"
df['cover_stego'] = df['cover_stego'].apply(detect_cover_stego)
print("\n", f"df cover/stego is: {df['cover_stego'].value_counts()}")

def compute_hash(file_path): #def for hash
    sha = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            sha.update(f.read())
        return sha.hexdigest()
    except Exception:
        return None

# (w , h) + hash + decode
widths = []
heights = []
decode_ok_list = []
hashes = []
for path in df['path']:
    try:
        # Try opening image
        img = Image.open(path)
        w, h = img.size

        widths.append(w)
        heights.append(h)
        decode_ok_list.append(True)

    except Exception:
        # If image cannot be decoded
        widths.append(None)
        heights.append(None)
        decode_ok_list.append(False)

    # Hash is independent from decoding
    hashes.append(compute_hash(path))

df['w'] = widths
df['h'] = heights
df['decode_ok'] = decode_ok_list
df['hash'] = hashes
# checking outputs
print(df[['w', 'h', 'decode_ok']].head())
print(f"\nDecode OK counts:\n {df['decode_ok'].value_counts()}")
print(f"\nUnique image sizes:\n {df[['w', 'h']].drop_duplicates()}")
print(f"\nHash sample:\n{df['hash'].head()}")
print(df.head())

print("Number of duplicate rows:", len(df[df.duplicated()]))
print("Number of missing rows:", df.isnull().sum())

# ===== CREATE MANIFEST.PARQUET =====
# Define the output path for the manifest file
manifest_path = os.path.join(os.path.dirname(DATASET_DIR), "manifest.parquet")

# Save the dataframe as parquet file
df.to_parquet(manifest_path, index=False, engine='pyarrow')

print(f"\n✓ Manifest saved to: {manifest_path}")
print(f"  Total rows: {len(df)}")
print(f"  Columns: {list(df.columns)}")
df = pd.read_parquet(manifest_path, engine='pyarrow')
df.to_csv("manifest.csv", index=False)
# payload: count of hidden message in stego
# seed: number for stegano algorithm
# hash: create from file bit