from app.models.attr_predictor import extract_attr_and_color
from app.models.legacy_predictor import extract_legacy_prediction_and_feature
from app.services.clothes_service import infer_extra_tags


def extract_prediction_and_feature(image_path):
    """
    双模型融合，保持现有逻辑不变：
    - 旧模型：类别 / 大类 / 置信度 / feature
    - 新模型：颜色 / 详细属性
    """
    legacy_result = extract_legacy_prediction_and_feature(image_path)
    attr_result = extract_attr_and_color(image_path)

    category_name = legacy_result["category_name"]
    category_conf = legacy_result["category_conf"]
    main_category = legacy_result["main_category"]

    merged_attributes = []

    # 先放新模型属性
    for attr in attr_result.get("attribute_names", []):
        if attr not in merged_attributes:
            merged_attributes.append(attr)

    # 再补一点旧模型属性候选（兜底）
    for attr in legacy_result.get("legacy_attribute_candidates", [])[:4]:
        if attr not in merged_attributes:
            merged_attributes.append(attr)

    tags = infer_extra_tags(category_name, merged_attributes)

    return {
        "category_name": category_name,
        "category_conf": category_conf,
        "attribute_names": merged_attributes,
        "main_category": main_category,
        "season": tags["season"],
        "thickness": tags["thickness"],
        "feature": legacy_result["feature"],   # 保持现有相似检索逻辑不变
        "color_name": attr_result.get("color_name", "unknown"),
        "raw_core_categories": attr_result.get("raw_core_categories", [])
    }