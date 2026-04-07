import cv2
import numpy as np
import torch
from sklearn.cluster import KMeans

# 尽量与给你的预测代码一致
COLOR_RANGES = [
    {"name": "白色", "lower": [0, 0, 180], "upper": [180, 45, 255], "priority": 1},
    {"name": "黑色", "lower": [0, 0, 0], "upper": [180, 255, 55], "priority": 10},
    {"name": "灰色", "lower": [0, 0, 46], "upper": [180, 50, 179], "priority": 8},
    {"name": "红色", "lower": [0, 50, 50], "upper": [10, 255, 255], "priority": 2},
    {"name": "红色", "lower": [160, 50, 50], "upper": [180, 255, 255], "priority": 2},
    {"name": "蓝色", "lower": [100, 50, 50], "upper": [130, 255, 255], "priority": 3},
    {"name": "浅蓝色", "lower": [90, 30, 150], "upper": [115, 180, 255], "priority": 3},
    {"name": "粉色", "lower": [161, 30, 40], "upper": [175, 255, 255], "priority": 2},
    {"name": "米色/奶油色", "lower": [10, 5, 170], "upper": [35, 80, 255], "priority": 4},
    {"name": "棕色/卡其", "lower": [10, 30, 40], "upper": [25, 150, 180], "priority": 5}
]


def _extract_one_region(region_mask: np.ndarray, hsv_img: np.ndarray):
    active_pixels = cv2.countNonZero(region_mask)
    if active_pixels == 0:
        return {"names": [], "centers": None}

    hsv_filtered = cv2.bitwise_and(hsv_img, hsv_img, mask=region_mask)

    candidates = []
    for color in COLOR_RANGES:
        mask_color = cv2.inRange(
            hsv_filtered,
            np.array(color["lower"], dtype=np.uint8),
            np.array(color["upper"], dtype=np.uint8)
        )
        ratio = cv2.countNonZero(mask_color) / max(active_pixels, 1)

        threshold = 0.45 if color["name"] in ["黑色", "灰色"] else 0.18
        if color["name"] == "白色":
            threshold = 0.12

        if ratio > threshold:
            candidates.append({
                "name": color["name"],
                "ratio": ratio,
                "priority": color["priority"]
            })

    sorted_res = sorted(candidates, key=lambda x: (x["priority"], -x["ratio"]))

    img_rgb = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2RGB)
    cloth_pixels = (img_rgb / 255.0)[region_mask > 0].reshape(-1, 3)

    if len(cloth_pixels) < 3:
        centers = np.zeros((3, 3), dtype=np.float32)
    else:
        try:
            kmeans = KMeans(n_clusters=3, n_init="auto", random_state=42).fit(cloth_pixels)
            centers = kmeans.cluster_centers_.astype(np.float32)
        except Exception:
            centers = np.zeros((3, 3), dtype=np.float32)

    return {
        "names": [c["name"] for c in sorted_res],
        "centers": centers
    }


def extract_multi_region_color(pil_img, mask_np):
    """
    输出：
    - color_tensor: 给模型使用的 9 维颜色特征
    - display_str:
        单一颜色 -> "黑色"
        上下不同 -> "1:黑色  2:白色"
        无法识别 -> "未知"
    """
    img_np = np.array(pil_img)
    h, w = img_np.shape[:2]
    img_hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

    if mask_np is None:
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.rectangle(
            mask,
            (int(w * 0.1), int(h * 0.1)),
            (int(w * 0.9), int(h * 0.9)),
            255,
            -1
        )
    else:
        mask = cv2.resize(
            (mask_np * 255).astype(np.uint8),
            (w, h),
            interpolation=cv2.INTER_NEAREST
        )

    # 去皮肤色
    skin_mask = cv2.inRange(
        img_hsv,
        np.array([0, 20, 70], dtype=np.uint8),
        np.array([20, 255, 255], dtype=np.uint8)
    )
    clothing_mask = cv2.bitwise_and(mask, cv2.bitwise_not(skin_mask))

    active_coords = np.where(clothing_mask > 0)
    if len(active_coords[0]) == 0:
        return torch.zeros((1, 9), dtype=torch.float32), "未知"

    y_min, y_max = np.min(active_coords[0]), np.max(active_coords[0])
    total_height = y_max - y_min

    region_masks = []

    # 全身照判定：拆上下
    if total_height / max(h, 1) > 0.65:
        split_y = y_min + int(total_height * 0.5)

        up = np.zeros_like(clothing_mask)
        up_start = y_min + int(total_height * 0.1)
        up[up_start:split_y, :] = clothing_mask[up_start:split_y, :]
        region_masks.append(up)

        down = np.zeros_like(clothing_mask)
        down_end = y_max - int(total_height * 0.05)
        down[split_y:down_end, :] = clothing_mask[split_y:down_end, :]
        region_masks.append(down)
    else:
        region_masks.append(clothing_mask)

    final_color_names = []
    all_centers = []

    for m in region_masks:
        res = _extract_one_region(m, img_hsv)
        if res["centers"] is not None:
            all_centers.append(res["centers"])
            if res["names"]:
                main_color = res["names"][0]
                if main_color not in final_color_names:
                    final_color_names.append(main_color)

    if not final_color_names:
        display_str = "未知"
    elif len(final_color_names) == 1:
        display_str = final_color_names[0]
    else:
        display_str = "  ".join([f"{i + 1}:{name}" for i, name in enumerate(final_color_names)])

    model_centers = all_centers[0] if all_centers else np.zeros((3, 3), dtype=np.float32)
    color_tensor = torch.tensor(model_centers.flatten(), dtype=torch.float32).unsqueeze(0)

    return color_tensor, display_str