import os
from typing import overload

import imagehash
import numpy as np
from PIL import Image
from tqdm import tqdm

from ._BasePipeline import _BasePipeline


class SimplePipeline(_BasePipeline):
    def __init__(self, input_dir: str, output_file: str):
        super().__init__(input_dir, output_file)

    def _compute_hashes(self, input_dir: str) -> dict[str, imagehash.ImageHash]:
        hashes = dict()

        print(f'Computing hashes for {input_dir}')
        for f in tqdm(os.listdir(input_dir)):
            image_path = os.path.join(input_dir, f)

            if not self.is_img(image_path):
                continue

            # load in image and convert instantly to grayscale
            image = Image.open(image_path)
            image = image.convert('L')

            hashes[image_path] = imagehash.dhash(image)

        return hashes

    def _pixel_comparison(self, img1: str, img2: str) -> bool:
        assert os.path.isfile(img1) and os.path.isfile(img2), "Files do not exist"

        _img1 = Image.open(img1).convert('L')
        _img2 = Image.open(img2).convert('L')

        img1_data = np.array(_img1)
        img2_data = np.array(_img2)

        mse = np.mean((img1_data - img2_data) ** 2)

        tqdm.write(f'Pixel comparison: {img1} vs {img2} -> {mse}')

        threshold = 1.0
        return mse <= threshold

    def _compute_duplicates(self, hashes: dict[str, imagehash.ImageHash]) -> list[tuple[str, str]]:
        keys = list(hashes.keys())
        duplicates: list[tuple[str, str]] = list()
        boundary = 3

        print(f'Computing duplicates for {len(keys)} images')
        for i in tqdm(range(len(keys))):
            for j in range(i + 1, len(keys)):
                img1, h1 = keys[i], hashes[keys[i]]
                img2, h2 = keys[j], hashes[keys[j]]

                # skip if images are not of the same size --> likely not similar
                if h1.hash.size != h2.hash.size:
                    continue

                distance = h1 - h2

                if distance <= boundary and self._pixel_comparison(img1, img2):
                    duplicates.append((keys[i], keys[j]))

        return duplicates

    def run(self) -> None:
        image_hashes = self._compute_hashes(self.input_dir)

        duplicates = self._compute_duplicates(image_hashes)

        with open(self.output_file, 'w') as f:
            for f1, f2 in duplicates:
                f.write(f'{f1},{f2}\n')
