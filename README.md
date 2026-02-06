# Image Deduplication tool

This tool uses the average hash algorithm to find duplicates in a directory of images.
A boundary of 90% similarity is used to determine if two images are duplicates.
A file is created containing the duplicate images (1 per line written as `<image1>,<image2>`)

# Usage
```bash
python main.py -i <input directory> [-o <output file>]```
```

# Dependencies
- PIL
- imagehash

Uses uv to manage the dependencies: `uv install`