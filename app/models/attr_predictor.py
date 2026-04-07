import cv2
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from sklearn.cluster import KMeans
from torchvision import models, transforms
from ultralytics import YOLO

from app.config.settings import ATTR_LIST_PATH, ATTR_MODEL_WEIGHTS, YOLO_WEIGHTS


# ==================== 1. 关键词定义 ====================
CORE_CATEGORY_KEYWORDS = [
    "dress", "t-shirt", "shirt", "blouse", "sweater", "cardigan", "knit",
    "jacket", "coat", "pants", "jeans", "top", "skirt"
]

SINGLE_PIECE_KEYWORDS = [
    "cardigan", "dress", "coat", "sweater", "jacket", "robe", "suit",
    "overcoat", "hoodie", "pullover", "trench coat", "blazer"
]

# 这些词只当属性，不要重复混入 attribute_names 里当普通“详细属性”
INVALID_ATTRIBUTE_WORDS = {
    "dress", "skirt", "jeans", "pants", "trousers", "shorts", "legging",
    "hoodie", "jacket", "coat", "blazer", "cardigan",
    "shirt", "blouse", "t-shirt", "tee", "tank", "top", "pullover",
    "sweater", "sneaker", "shoe", "boot", "heel", "sandal",
    "hat", "cap", "beanie"
}


# ==================== 2. 颜色区间（使用你新版本） ====================
COLOR_RANGES = [
    # ==================== 红色 Red ====================
    {"name": "red", "lower": [0, 50, 35], "upper": [10, 255, 255], "priority": 1},
    {"name": "red", "lower": [170, 50, 35], "upper": [180, 255, 255], "priority": 1},

    # ==================== 粉色 Pink ====================
    {"name": "pink", "lower": [160, 20, 170], "upper": [175, 120, 255], "priority": 2},
    {"name": "pink", "lower": [0, 20, 170], "upper": [10, 120, 255], "priority": 2},

    # ==================== 橙色 Orange ====================
    {"name": "orange", "lower": [10, 70, 80], "upper": [22, 255, 255], "priority": 3},

    # ==================== 黄色 Yellow ====================
    {"name": "yellow", "lower": [22, 70, 120], "upper": [35, 255, 255], "priority": 4},

    # ==================== 黄绿色 Lime ====================
    {"name": "lime", "lower": [35, 50, 80], "upper": [48, 255, 255], "priority": 5},

    # ==================== 绿色 Green ====================
    {"name": "green", "lower": [48, 45, 45], "upper": [85, 255, 255], "priority": 6},

    # ==================== 青绿色 Cyan/Teal ====================
    {"name": "cyan", "lower": [85, 40, 50], "upper": [100, 255, 255], "priority": 7},

    # ==================== 蓝色 Blue ====================
    {"name": "blue", "lower": [100, 45, 40], "upper": [130, 255, 255], "priority": 8},

    # ==================== 靛蓝 Indigo ====================
    {"name": "indigo", "lower": [130, 40, 35], "upper": [145, 255, 255], "priority": 9},

    # ==================== 紫色 Purple ====================
    {"name": "purple", "lower": [145, 35, 40], "upper": [160, 255, 255], "priority": 10},

    # ==================== 棕色 Brown ====================
    {"name": "brown", "lower": [5, 55, 25], "upper": [20, 255, 180], "priority": 11},
    {"name": "brown", "lower": [10, 80, 20], "upper": [30, 255, 150], "priority": 11},

    # ==================== 米色 Beige ====================
    {"name": "beige", "lower": [10, 15, 150], "upper": [40, 110, 255], "priority": 12},

    # ==================== 白色 White ====================
    {"name": "white", "lower": [0, 0, 185], "upper": [180, 22, 255], "priority": 13},

    # ==================== 灰色 Gray ====================
    {"name": "gray", "lower": [0, 0, 55], "upper": [180, 25, 184], "priority": 14},

    # ==================== 黑色 Black ====================
    {"name": "black", "lower": [0, 0, 0], "upper": [180, 255, 54], "priority": 15},
]

# ==================== 3. 模型定义 ====================
class FinalClothingModel(nn.Module):
    def __init__(self, num_attr=1000):
        super().__init__()
        backbone = models.convnext_tiny(weights=None)
        self.backbone = nn.Sequential(*list(backbone.children())[:-1])
        self.color_branch = nn.Sequential(
            nn.Linear(9, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64)
        )
        self.fusion = nn.Sequential(
            nn.Linear(768 + 64, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256)
        )
        self.classifier = nn.Linear(256, num_attr)

    def forward(self, x, c):
        v = self.backbone(x).flatten(1)
        color_v = self.color_branch(c)
        fused = self.fusion(torch.cat([v, color_v], dim=1))
        logits = self.classifier(fused)
        return logits, fused


# ==================== 4. 标签加载 ====================
def load_attr_names(path):
    with open(path, "r", encoding="utf-8") as f:
        return [" ".join(line.split()[:-1]) for line in f.readlines()[2:]]


ATTRIBUTE_NAMES = load_attr_names(ATTR_LIST_PATH)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

attr_model = FinalClothingModel().to(device)
detector = YOLO(str(YOLO_WEIGHTS))

if ATTR_MODEL_WEIGHTS.exists():
    state_dict = torch.load(ATTR_MODEL_WEIGHTS, map_location=device)
    attr_model.load_state_dict(state_dict, strict=False)
    attr_model.eval()
    print(f"✅ 成功加载新属性模型权重: {ATTR_MODEL_WEIGHTS} (设备: {device})")
else:
    print(f"⚠️ 未找到新属性模型权重: {ATTR_MODEL_WEIGHTS}")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


# ==================== 5. 工具函数 ====================
def _normalize_name(name: str) -> str:
    if not name:
        return "Unknown"
    name = name.replace("_", " ").strip()
    return " ".join(word.capitalize() for word in name.split())


def _select_main_item(orig_img: Image.Image, masks, boxes):
    """
    保持你当前逻辑：优先用 YOLO 分割；没有检测到时回退 GrabCut
    """
    orig_w, orig_h = orig_img.size

    if masks is None or len(masks) == 0:
        img_cv = cv2.cvtColor(np.array(orig_img), cv2.COLOR_RGB2BGR)
        mask_grab = np.zeros(img_cv.shape[:2], np.uint8)
        bg_model = np.zeros((1, 65), np.float64)
        fg_model = np.zeros((1, 65), np.float64)
        rect = (10, 10, max(orig_w - 20, 1), max(orig_h - 20, 1))

        try:
            cv2.grabCut(img_cv, mask_grab, rect, bg_model, fg_model, 5, cv2.GC_INIT_WITH_RECT)
            bin_mask = np.where((mask_grab == 2) | (mask_grab == 0), 0, 1).astype("uint8")
            return orig_img, [0, 0, orig_w, orig_h], bin_mask, "grabcut"
        except Exception:
            return orig_img, [0, 0, orig_w, orig_h], None, "full"

    best_idx = 0
    best_area = -1
    for i in range(len(masks)):
        b = boxes[i].xyxy.cpu().numpy()[0]
        area = max(float(b[2] - b[0]), 0) * max(float(b[3] - b[1]), 0)
        if area > best_area:
            best_area = area
            best_idx = i

    b = boxes[best_idx].xyxy.cpu().numpy()[0]
    x1, y1, x2, y2 = map(int, b)
    x1, y1 = max(x1, 0), max(y1, 0)
    x2, y2 = min(x2, orig_w), min(y2, orig_h)

    mask_np = cv2.resize(masks[best_idx].data[0].cpu().numpy(), (orig_w, orig_h))
    crop = orig_img.crop((x1, y1, x2, y2))
    crop_mask = mask_np[y1:y2, x1:x2]
    return crop, [x1, y1, x2, y2], crop_mask, "yolo"


def _get_dominant_color_name(hsv_img, mask):
    active_pixels = cv2.countNonZero(mask)
    if active_pixels < 50:
        return None

    best_name = None
    max_ratio = 0

    for color in COLOR_RANGES:
        c_mask = cv2.inRange(hsv_img, np.array(color["lower"]), np.array(color["upper"]))
        inter_mask = cv2.bitwise_and(c_mask, mask)
        ratio = cv2.countNonZero(inter_mask) / max(active_pixels, 1)

        if ratio > max_ratio and ratio > 0.10:
            max_ratio = ratio
            best_name = color["name"]

    return best_name


def _get_region_color_vector(hsv_img, mask):
    pixels = hsv_img[mask > 0]
    if len(pixels) == 0:
        return None
    return np.mean(pixels, axis=0)


def _color_distance(vec1, vec2):
    if vec1 is None or vec2 is None:
        return float("inf")

    h_diff = min(abs(vec1[0] - vec2[0]), 180 - abs(vec1[0] - vec2[0]))
    s_diff = abs(vec1[1] - vec2[1])
    v_diff = abs(vec1[2] - vec2[2])
    return np.sqrt(h_diff ** 2 * 2 + s_diff ** 2 + v_diff ** 2 * 0.5)


def _are_similar_colors(name1, name2):
    if name1 == name2:
        return True

    similar_groups = [
        {"white", "gray", "beige"},
        {"pink", "red", "purple"},
        {"orange", "yellow", "brown"},
        {"lime", "green"},
        {"cyan", "blue", "indigo"},
        {"black", "gray", "brown"},
    ]

    for group in similar_groups:
        if name1 in group and name2 in group:
            return True

    return False

def _extract_kmeans_feature(img_np, clothing_mask):
    try:
        valid_pixels = (img_np / 255.0)[clothing_mask > 0]
        if len(valid_pixels) > 3:
            kmeans = KMeans(n_clusters=min(3, len(valid_pixels)), n_init="auto", random_state=42)
            kmeans.fit(valid_pixels.reshape(-1, 3))
            cluster_centers = kmeans.cluster_centers_.flatten()
            if len(cluster_centers) < 9:
                cluster_centers = np.pad(cluster_centers, (0, 9 - len(cluster_centers)), "constant")
        else:
            cluster_centers = np.array([0.9] * 9, dtype=np.float32)
    except Exception:
        cluster_centers = np.array([0.9] * 9, dtype=np.float32)

    return torch.tensor(cluster_centers, dtype=torch.float32).unsqueeze(0)


def post_process_cloth_type(pred_attrs, current_type, color_name):
    """
    保留你新版本里的单衣/上下衣修正逻辑
    """
    pred_str = " ".join(pred_attrs).lower()

    # 上下衣 -> 单衣
    if current_type == "two_piece":
        for keyword in SINGLE_PIECE_KEYWORDS:
            if keyword in pred_str:
                return "single_piece"

    # 单衣 -> 上下衣
    if current_type == "single_piece":
        bottom_keywords = ["pants", "jeans", "trousers", "skirt", "shorts", "bottom"]
        top_keywords = ["shirt", "blouse", "top", "jacket", "coat", "sweater", "cardigan"]

        has_bottom = any(kw in pred_str for kw in bottom_keywords)
        has_top = any(tw in pred_str for tw in top_keywords)

        if has_bottom and has_top:
            return "two_piece"

        if " + " in color_name:
            c1, c2 = color_name.split(" + ")
            if not _are_similar_colors(c1.strip(), c2.strip()):
                return "two_piece"

    return current_type


def extract_pure_color_and_type(pil_img, mask_np):
    """
    这一整套颜色 + 单衣/上下衣判断，按你 predict0405(2).py 的思路接入，
    但保持当前返回结构不变。
    """
    img_np = np.array(pil_img)
    h, w = img_np.shape[:2]
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

    if mask_np is not None:
        mask = cv2.resize((mask_np * 255).astype(np.uint8), (w, h))
    else:
        mask = np.ones((h, w), dtype=np.uint8) * 255

    # 皮肤过滤（沿用你新代码）
    skin1 = cv2.inRange(hsv, np.array([5, 20, 70]), np.array([20, 170, 255]))
    skin2 = cv2.inRange(hsv, np.array([170, 20, 70]), np.array([180, 170, 255]))
    skin = cv2.bitwise_or(skin1, skin2)
    clothing_mask = cv2.bitwise_and(mask, cv2.bitwise_not(skin))

    y_coords, x_coords = np.where(clothing_mask > 0)
    if len(y_coords) == 0:
        return torch.zeros((1, 9)), "unknown", "single_piece"

    y_min, y_max = np.min(y_coords), np.max(y_coords)
    x_min, x_max = np.min(x_coords), np.max(x_coords)
    mask_h = y_max - y_min
    mask_w = x_max - x_min
    aspect_ratio = mask_h / max(mask_w, 1)

    mid_y = y_min + (mask_h // 2)
    mid_region_height = max(int(mask_h * 0.1), 20)
    mid_region = clothing_mask[mid_y - mid_region_height // 2: mid_y + mid_region_height // 2, :]
    mid_fill_ratio = np.sum(mid_region > 0) / max((mid_region.shape[0] * mid_region.shape[1]), 1)

    upper_mask = clothing_mask.copy()
    upper_mask[mid_y:, :] = 0
    lower_mask = clothing_mask.copy()
    lower_mask[:mid_y, :] = 0

    upper_vec = _get_region_color_vector(hsv, upper_mask)
    lower_vec = _get_region_color_vector(hsv, lower_mask)
    color_dist = _color_distance(upper_vec, lower_vec) if upper_vec is not None and lower_vec is not None else 0

    c_up_name = _get_dominant_color_name(hsv, upper_mask) or "unknown"
    c_low_name = _get_dominant_color_name(hsv, lower_mask) or "unknown"

    is_long_shape = mask_h > (h * 0.35)
    is_tall_ratio = aspect_ratio > 0.8
    is_separated = mid_fill_ratio < 0.60
    is_color_different = color_dist > 15
    names_are_different = c_up_name != c_low_name

    should_be_separate = (
        is_long_shape and is_tall_ratio and
        (
            is_separated or
            is_color_different or
            (names_are_different and not _are_similar_colors(c_up_name, c_low_name))
        )
    )

    if should_be_separate:
        cloth_type = "two_piece"
        if not _are_similar_colors(c_up_name, c_low_name) and names_are_different:
            up_pixels = np.sum(upper_mask > 0)
            low_pixels = np.sum(lower_mask > 0)
            final_names = [c_up_name] if up_pixels >= low_pixels else [c_low_name]
        else:
            cloth_type = "single_piece"
            up_pixels = np.sum(upper_mask > 0)
            final_names = [c_up_name] if up_pixels > np.sum(lower_mask > 0) else [c_low_name]
    else:
        cloth_type = "single_piece"
        detected_color = _get_dominant_color_name(hsv, clothing_mask)
        final_names = [detected_color if detected_color else "unknown"]

    color_tensor = _extract_kmeans_feature(img_np, clothing_mask)
    display_color = " + ".join([n for n in final_names if n])

    return color_tensor, display_color, cloth_type


def _split_core_and_detail(output_probs, threshold=0.5):
    valid_attrs = []
    valid_scores = []

    for j in range(len(output_probs)):
        attr_name = ATTRIBUTE_NAMES[j]
        attr_low = attr_name.lower()

        current_t = 0.2 if any(k in attr_low for k in CORE_CATEGORY_KEYWORDS) else threshold
        if output_probs[j] > current_t:
            valid_attrs.append(attr_name)
            valid_scores.append((float(output_probs[j]), attr_name))

    valid_scores = sorted(valid_scores, key=lambda x: -x[0])

    return valid_attrs, valid_scores


def extract_attr_and_color(image_path):
    """
    对外接口保持不变：
    返回 color_name / attribute_names / raw_core_categories / attr_feature
    """
    attr_model.eval()

    results = detector(str(image_path), conf=0.25, classes=[0])
    orig_img = Image.open(image_path).convert("RGB")
    masks = results[0].masks
    boxes = results[0].boxes

    crop, _, crop_mask, _ = _select_main_item(orig_img, masks, boxes)

    color_tensor, color_name, cloth_type = extract_pure_color_and_type(crop, crop_mask)
    img_tensor = transform(crop).unsqueeze(0).to(device)

    with torch.no_grad():
        logits, fused_feat = attr_model(img_tensor, color_tensor.to(device))
        output = torch.sigmoid(logits)[0].cpu().numpy()

    valid_attrs, valid_scores = _split_core_and_detail(output, threshold=0.5)

    # 用你新版本的 cloth_type 后处理
    cloth_type = post_process_cloth_type(valid_attrs, cloth_type, color_name)

    # 如果最终判断是单衣，但颜色字符串里有两种颜色，只保留主色
    if cloth_type == "single_piece" and " + " in color_name:
        color_name = color_name.split(" + ")[0].strip()

    attributes = []
    if color_name and color_name != "unknown":
        attributes.append(f"color: {color_name}")

    # 把单衣/上下衣判断也作为属性补充进去，但不改现有逻辑
    attributes.append(f"cloth_type: {'single' if cloth_type == 'single_piece' else 'two_piece'}")

    for _, attr_name in valid_scores[:8]:
        low = attr_name.lower().strip()
        if low in INVALID_ATTRIBUTE_WORDS:
            continue

        clean_attr = _normalize_name(attr_name)
        if clean_attr not in attributes:
            attributes.append(clean_attr)

    raw_core_categories = []
    for score, name in valid_scores[:8]:
        name_low = name.lower()
        if any(k in name_low for k in CORE_CATEGORY_KEYWORDS):
            raw_core_categories.append({
                "name": _normalize_name(name),
                "score": round(float(score), 4)
            })

    return {
        "color_name": color_name,
        "attribute_names": attributes,
        "raw_core_categories": raw_core_categories[:5],
        "attr_feature": fused_feat.cpu().numpy().reshape(-1).astype(np.float32)
    }