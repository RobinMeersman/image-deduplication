import os

import numpy as np
from skimage import io
from skimage.feature import ORB, match_descriptors
from skimage.measure import ransac
from skimage.transform import ProjectiveTransform

from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from itertools import combinations

from ._BasePipeline import _BasePipeline


class ORBPipeline(_BasePipeline):
    def __init__(self, input_dir: str, output_file: str):
        super().__init__(input_dir, output_file)

    @staticmethod
    def _compute_descriptor(img: np.ndarray):
        orb = ORB(n_keypoints=1000)
        orb.detect_and_extract(img)
        return orb.keypoints, orb.descriptors

    @staticmethod
    def _compare_images(images: tuple[str, str]) -> tuple[str, str, int] | None:
        img1, img2 = images

        try:
            k1, d1 = ORBPipeline._compute_descriptor(io.imread(img1, as_gray=True))
            k2, d2 = ORBPipeline._compute_descriptor(io.imread(img2, as_gray=True))

            matches = match_descriptors(k1, k2, cross_check=True)

            # RANSAC needs at least 4 matches
            if len(matches) < 4:
                return None

            src = k1[matches[:, 0]][:, ::-1]
            dst = k2[matches[:, 1]][:, ::-1]

            model, inliers = ransac(
                (src, dst),
                ProjectiveTransform,
                min_samples=4,
                residual_threshold=2,
                max_trials=1000
            )

            s = inliers.sum()

            if inliers is not None and s > 8:
                return img1, img2, s

        except Exception as e:
            print(f'Error comparing {img1} and {img2}: {e}')
            return None



    def run(self) -> list[tuple[str, str, int]]:
        duplicates: list[tuple[str, str, int]] = list()
        files = os.listdir(self.input_dir)

        if len(files) == 0:
            return duplicates

        files = list(
            filter(self.is_img, map(lambda file: os.path.join(self.input_dir, file), files))
        )
        print("file count:", len(list(files)))

        files = list(combinations(files, 2))
        print("combination count:", len(files))

        # with ThreadPoolExecutor() as executor:
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._compare_images, images) for images in files]

            for future in tqdm(as_completed(futures), total=len(futures)):
                result = future.result()
                if result is not None:
                    duplicates.append(result)

        return duplicates
