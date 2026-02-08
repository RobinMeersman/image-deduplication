import os
from abc import ABC, abstractmethod

class _BasePipeline(ABC):
    def __init__(self, input_dir: str, output_file: str):
        self.input_dir = input_dir
        self.output_file = output_file

    @staticmethod
    def is_img(file: str) -> bool:
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
        ext = os.path.splitext(file)[1].lower()

        res = os.path.isfile(file) and ext in image_extensions
        return res

    @abstractmethod
    def run(self):
        pass
