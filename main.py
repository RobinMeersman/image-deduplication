import argparse as ap
from PIL import Image
import imagehash
import os
from tqdm import tqdm


def arg_parser() -> ap.Namespace:
    parser = ap.ArgumentParser(description='Image deduplication tool')
    parser.add_argument('--input_dir', '-i', type=str, help='Input directory')
    parser.add_argument('--output_file', '-o', type=str, default='./duplicates.txt', help='Output file')
    return parser.parse_args()

def compute_hashes(input_dir: str) -> dict:
    hashes = dict()

    print(f'Computing hashes for {input_dir}')
    for f in tqdm(os.listdir(input_dir)):
        image_path = os.path.join(input_dir, f)
        if os.path.isfile(image_path) and os.path.splitext(image_path)[1].lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
            hashes[f] = imagehash.average_hash(Image.open(image_path))

    return hashes


def compute_duplicates(hashes: dict[str, imagehash.ImageHash]) -> list[tuple[str, str]]:
    keys = list(hashes.keys())
    duplicates: list[tuple[str, str]] = list()
    boundary = 5

    print(f'Computing duplicates for {len(keys)} images')
    for i in tqdm(range(len(keys))):
        for j in range(i + 1, len(keys)):
            h1 = hashes[keys[i]]
            h2 = hashes[keys[j]]

            # skip if images are not of the same size --> likely not similar
            if h1.hash.size != h2.hash.size:
                continue

            distance = h1 - h2

            # similarity boundary at 90% equal
            if distance <= boundary:
                duplicates.append((keys[i], keys[j]))

    return duplicates


if __name__ == '__main__':
    args = arg_parser()

    image_hashes = compute_hashes(args.input_dir)

    duplicates = compute_duplicates(image_hashes)

    with open(args.output_file, 'w') as f:
        for f1, f2 in duplicates:
            f.write(f'{f1},{f2}\n')
