# BOSSbase dataset manifest creation
This repository contains code to create a structured DataFrame (manifest) for the BOSSbase 1.01 image dataset.
The manifest collects essential metadata for each image and prepares the dataset for steganography and steganalysis research, including future controlled stego generation.
## What is the BOSSbase dataset?
BOSSbase (Break Our Steganographic System) is a widely used benchmark dataset in the field of steganography and steganalysis.

-It contains 10,000 original (unaltered) images

-All images are cover images (no embedded messages)

-Images are stored in the spatial domain (PPM format)

-The dataset was created by Binghamton University

-It is commonly used to:

    -Evaluate steganographic algorithms

    -Generate controlled stego images

    -Train and test steganalysis models
    
## What does this code do?
This project builds a metadata DataFrame from the BOSSbase dataset and saves it as a manifest file (parquet and csv).

| Column name   | Description                                          |
| ------------- | ---------------------------------------------------- |
| `image_id`    | Numeric identifier extracted from the image filename |
| `path`        | Absolute path to the image file                      |
| `w`           | Width (pixels)                                       |
| `h`           | Height (pixels)                                      |
| `format`      | Image format (PPM)                                   |
| `decode_ok`   | Whether the image can be successfully opened         |
| `hash`        | SHA-256 hash of the image file                       |
| `split`       | Dataset split (`train`, `val`, or `test`)            |
| `cover_stego` | Image type (`cover`)                                 |
| `algo`        | Steganography algorithm used (empty for covers)      |
