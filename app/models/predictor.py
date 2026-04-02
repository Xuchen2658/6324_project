import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from app.config.settings import MODEL_WEIGHTS
from app.models.labels import CATEGORY_NAMES, ATTRIBUTE_NAMES
from app.models.network import MultiTaskResNet
from app.services.clothes_service import infer_extra_tags, infer_main_category
from app.utils.constants import TOP_K_ATTRIBUTES

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MultiTaskResNet().to(device)

if MODEL_WEIGHTS.exists():
    checkpoint = torch.load(MODEL_WEIGHTS, map_location=device)
    state_dict = checkpoint["model"] if isinstance(checkpoint, dict) and "model" in checkpoint else checkpoint
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    print(f"✅ 成功加载权重: {MODEL_WEIGHTS} (使用设备: {device})")
else:
    print(f"⚠️ 未找到权重文件: {MODEL_WEIGHTS}")


def get_transform():
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225])
    ])


def extract_prediction_and_feature(image_path):
    transform = get_transform()
    img = Image.open(image_path).convert("RGB")
    input_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        cat_logits, attr_logits, feat = model(input_tensor)

        cat_probs = torch.softmax(cat_logits, dim=1).squeeze()
        cat_idx = torch.argmax(cat_probs).item()

        attr_probs = torch.sigmoid(attr_logits).squeeze()
        topk = torch.topk(attr_probs, k=min(TOP_K_ATTRIBUTES, attr_probs.shape[0]))
        attr_indices = topk.indices.tolist()

    feature = feat.cpu().numpy().reshape(-1).astype(np.float32)
    category_name = CATEGORY_NAMES[cat_idx] if cat_idx < len(CATEGORY_NAMES) else "Unknown"
    category_conf = f"{cat_probs[cat_idx].item():.2%}"
    attribute_names = [ATTRIBUTE_NAMES[i] for i in attr_indices if i < len(ATTRIBUTE_NAMES)]

    tags = infer_extra_tags(category_name, attribute_names)
    main_category = infer_main_category(category_name, attribute_names)

    return {
        "category_name": category_name,
        "category_conf": category_conf,
        "attribute_names": attribute_names,
        "main_category": main_category,
        "season": tags["season"],
        "thickness": tags["thickness"],
        "feature": feature
    }