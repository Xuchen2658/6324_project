import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms

from app.config.settings import ATTR_LIST_PATH, CATEGORY_LIST_PATH, LEGACY_MODEL_WEIGHTS
from app.services.clothes_service import infer_main_category


def load_category_names(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()[2:]
        names = []
        for line in lines:
            parts = line.split()
            if parts:
                names.append(parts[0])
        return names


def load_attr_names(path):
    with open(path, "r", encoding="utf-8") as f:
        return [" ".join(line.split()[:-1]) for line in f.readlines()[2:]]


CATEGORY_NAMES = load_category_names(CATEGORY_LIST_PATH)
ATTRIBUTE_NAMES = load_attr_names(ATTR_LIST_PATH)


class MultiTaskResNet(nn.Module):
    def __init__(self):
        super().__init__()
        resnet = models.resnet50(weights=None)
        self.backbone = nn.Sequential(*(list(resnet.children())[:-1]))
        self.cat_head = nn.Linear(2048, 50)
        self.attr_head = nn.Linear(2048, 1000)

    def forward(self, x):
        feat = self.backbone(x).view(x.size(0), -1)
        cat_logits = self.cat_head(feat)
        attr_logits = self.attr_head(feat)
        return cat_logits, attr_logits, feat


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
legacy_model = MultiTaskResNet().to(device)

if LEGACY_MODEL_WEIGHTS.exists():
    checkpoint = torch.load(LEGACY_MODEL_WEIGHTS, map_location=device)
    state_dict = checkpoint["model"] if isinstance(checkpoint, dict) and "model" in checkpoint else checkpoint
    legacy_model.load_state_dict(state_dict, strict=False)
    legacy_model.eval()
    print(f"✅ 成功加载旧模型权重: {LEGACY_MODEL_WEIGHTS} (设备: {device})")
else:
    print(f"⚠️ 未找到旧模型权重: {LEGACY_MODEL_WEIGHTS}")

legacy_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])


def _normalize_name(name: str) -> str:
    if not name:
        return "Unknown"
    name = name.replace("_", " ").strip()
    return " ".join(word.capitalize() for word in name.split())


def extract_legacy_prediction_and_feature(image_path):
    legacy_model.eval()

    img = Image.open(image_path).convert("RGB")
    input_tensor = legacy_transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        cat_logits, attr_logits, feat = legacy_model(input_tensor)

        cat_probs = torch.softmax(cat_logits, dim=1).squeeze()
        cat_idx = torch.argmax(cat_probs).item()

        attr_probs = torch.sigmoid(attr_logits).squeeze()
        top_attr = torch.topk(attr_probs, k=min(8, attr_probs.shape[0]))
        attr_indices = top_attr.indices.tolist()

    category_name = CATEGORY_NAMES[cat_idx] if cat_idx < len(CATEGORY_NAMES) else "Unknown"
    category_name = _normalize_name(category_name)
    category_conf = f"{cat_probs[cat_idx].item():.2%}"

    old_attrs = []
    for i in attr_indices:
        if i < len(ATTRIBUTE_NAMES):
            old_attrs.append(_normalize_name(ATTRIBUTE_NAMES[i]))

    main_category = infer_main_category(category_name, old_attrs)
    feature = feat.cpu().numpy().reshape(-1).astype(np.float32)

    return {
        "category_name": category_name,
        "category_conf": category_conf,
        "main_category": main_category,
        "feature": feature,
        "legacy_attribute_candidates": old_attrs
    }