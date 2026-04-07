import torch
import torch.nn as nn
from torchvision import models


# class MultiTaskResNet(nn.Module):
#     def __init__(self):
#         super().__init__()
#         resnet = models.resnet50(weights=None)
#         self.backbone = nn.Sequential(*(list(resnet.children())[:-1]))
#         self.cat_head = nn.Linear(2048, 50)
#         self.attr_head = nn.Linear(2048, 1000)
#
#     def forward(self, x):
#         feat = self.backbone(x).view(x.size(0), -1)
#         return self.cat_head(feat), self.attr_head(feat), feat
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

    def forward(self, x, color_feat):
        vis_feat = self.backbone(x).flatten(1)
        col_feat = self.color_branch(color_feat)
        combined = torch.cat([vis_feat, col_feat], dim=1)
        return self.classifier(self.fusion(combined))