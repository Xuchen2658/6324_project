from app.config.settings import DATA_ANNO_PATH


def load_labels():
    try:
        cat_file = DATA_ANNO_PATH / "list_category_cloth.txt"
        attr_file = DATA_ANNO_PATH / "list_attr_cloth.txt"

        with open(cat_file, "r", encoding="utf-8") as f:
            cats = [line.split()[0] for line in f.readlines()[2:]]

        with open(attr_file, "r", encoding="utf-8") as f:
            attrs = [line.strip().rsplit(None, 1)[0] for line in f.readlines()[2:]]

        return cats, attrs
    except Exception as e:
        print(f"❌ 标签文件加载失败: {e}")
        return ["Unknown"] * 50, ["Unknown"] * 1000


CATEGORY_NAMES, ATTRIBUTE_NAMES = load_labels()