import numpy as np
import torch
from ..utils.load_model import load_model
from ..utils.device_utils import get_device


class AppearanceExtractor:
    def __init__(self, model_path, device=None):
        if device is None:
            device = get_device()
        kwargs = {
            "module_name": "AppearanceFeatureExtractor",
        }
        self.model, self.model_type = load_model(model_path, device=device, **kwargs)
        self.device = device

    def __call__(self, image):
        """
        image: np.ndarray, shape (1, 3, 256, 256), float32, range [0, 1]
        """
        if self.model_type == "onnx":
            pred = self.model.run(None, {"image": image})[0]
        elif self.model_type == "tensorrt":
            self.model.setup({"image": image})
            self.model.infer()
            pred = self.model.buffer["pred"][0].copy()
        elif self.model_type == 'pytorch':
            # Disable autocast for MPS to avoid hangs
            with torch.no_grad():
                pred = self.model(torch.from_numpy(image).to(self.device)).float().cpu().numpy()
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        return pred
