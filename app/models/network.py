import torch.nn as nn
from torchvision import models


class MultiTaskResNet(nn.Module):
    def __init__(self):
        super().__init__()
        resnet = models.resnet50(weights=None)
        self.backbone = nn.Sequential(*(list(resnet.children())[:-1]))
        self.cat_head = nn.Linear(2048, 50)
        self.attr_head = nn.Linear(2048, 1000)

    def forward(self, x):
        feat = self.backbone(x).view(x.size(0), -1)
        return self.cat_head(feat), self.attr_head(feat), feat