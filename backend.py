import os
import torch
import torch.nn as nn
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from torchvision import models, transforms
from PIL import Image
from pathlib import Path

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)  # 允许跨域请求

# ================= 1. 配置区 (根据你的电脑环境修改) =================
# 必须指向你存放 list_category_cloth.txt 的真实目录
BASE_DIR = Path(__file__).resolve().parent
DATA_ANNO_PATH = BASE_DIR / "dataset" / "Anno_coarse"
MODEL_WEIGHTS = str(BASE_DIR / "checkpoint_c2_full_1000.pth")
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ================= 2. 标签加载逻辑 =================
def load_labels():
    try:
        cat_file = DATA_ANNO_PATH / "list_category_cloth.txt"
        attr_file = DATA_ANNO_PATH / "list_attr_cloth.txt"

        with open(cat_file, 'r', encoding='utf-8') as f:
            cats = [line.split()[0] for line in f.readlines()[2:]]
        with open(attr_file, 'r', encoding='utf-8') as f:
            # 属性名可能带空格，使用 rsplit 分离最后的类别编号
            attrs = [line.strip().rsplit(None, 1)[0] for line in f.readlines()[2:]]
        return cats, attrs
    except Exception as e:
        print(f"❌ 标签文件加载失败: {e}")
        return ["Unknown"] * 50, ["Unknown"] * 1000


CATEGORY_NAMES, ATTRIBUTE_NAMES = load_labels()


# ================= 3. 模型架构定义 =================
class MultiTaskResNet(nn.Module):
    def __init__(self):
        super().__init__()
        resnet = models.resnet50()
        # 提取骨干网络 (去掉最后的 FC 层)
        self.backbone = nn.Sequential(*(list(resnet.children())[:-1]))
        self.cat_head = nn.Linear(2048, 50)
        self.attr_head = nn.Linear(2048, 1000)

    def forward(self, x):
        feat = self.backbone(x).view(x.size(0), -1)
        return self.cat_head(feat), self.attr_head(feat), feat


# 初始化模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = MultiTaskResNet().to(device)

# 加载训练好的权重
if os.path.exists(MODEL_WEIGHTS):
    checkpoint = torch.load(MODEL_WEIGHTS, map_location=device)
    model.load_state_dict(checkpoint['model'])
    model.eval()
    print(f"✅ 成功加载权重: {MODEL_WEIGHTS} (使用设备: {device})")
else:
    print(f"⚠️ 未找到权重文件 {MODEL_WEIGHTS}，请确保文件在当前目录下。")


# ================= 4. 路由逻辑 =================

# 渲染首页
@app.route('/')
def index():
    return render_template('index.html', result=None)
# @app.route('/')
# def index():
#     return render_template('index.html')



# 静态文件服务 (让前端能看到上传的图)
@app.route('/static/uploads/<filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_DIR, filename)


# 核心上传与识别接口
@app.route('/upload', methods=['POST'])
def upload_and_predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # 保存文件
    file_path = UPLOAD_DIR / file.filename
    file.save(file_path)

    # 图像预处理
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    try:
        img = Image.open(file_path).convert('RGB')
        input_tensor = transform(img).unsqueeze(0).to(device)

        # AI 推理
        with torch.no_grad():
            cat_logits, attr_logits, feat = model(input_tensor)

            # 计算品类概率
            cat_probs = torch.softmax(cat_logits, dim=1).squeeze()
            cat_idx = torch.argmax(cat_probs).item()

            # 计算属性概率 (Sigmoid)
            attr_probs = torch.sigmoid(attr_logits).squeeze()
            attr_indices = (attr_probs > 0.5).nonzero(as_tuple=True)[0]

        # 提取 2048 维特征并保存 (为任务二做准备)
        feat_path = UPLOAD_DIR / f"{file_path.stem}.npy"
        np.save(feat_path, feat.cpu().numpy())

        # 构建返回结果
        result = {
            "category_name": CATEGORY_NAMES[cat_idx] if cat_idx < len(CATEGORY_NAMES) else "Unknown",
            "category_conf": f"{cat_probs[cat_idx]:.2%}",
            "attribute_names": [ATTRIBUTE_NAMES[i] for i in attr_indices.tolist() if i < len(ATTRIBUTE_NAMES)],
            "image_url": f"/static/uploads/{file.filename}"
        }
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # 端口固定为 5000 配合前端
    app.run(host='0.0.0.0', port=5001, debug=True)