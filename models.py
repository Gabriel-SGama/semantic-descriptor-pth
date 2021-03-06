from cProfile import label
import torch
import torchvision
import torch.nn as nn
import numpy as np
import torchvision.transforms as transforms


class wideResNet50(nn.Module):
    def __init__(self, pretrained=True):
        super().__init__()

        wr50v2 = torch.hub.load("pytorch/vision:v0.10.0", "wide_resnet50_2", pretrained=True)
        for param in wr50v2.parameters():
            param.requires_grad = True

        self.new_model = nn.Sequential(*list(wr50v2.children())[:-2])
        # in_features = wr50v2.fc.in_features
        self.upconvs = nn.Sequential(
            nn.ConvTranspose2d(2048, 1024, kernel_size=(3, 3), stride=(2, 2), padding=1, output_padding=1, bias=False),
            nn.BatchNorm2d(1024),
            nn.ReLU(),
            nn.ConvTranspose2d(1024, 512, kernel_size=(3, 3), stride=(2, 2), padding=1, output_padding=1, bias=False),
            nn.BatchNorm2d(512),
            nn.ReLU(),
            nn.ConvTranspose2d(512, 256, kernel_size=(3, 3), stride=(2, 2), padding=1, output_padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(),
            nn.ConvTranspose2d(256, 128, kernel_size=(3, 3), stride=(2, 2), padding=1, output_padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.ConvTranspose2d(128, 64, kernel_size=(3, 3), stride=(2, 2), padding=1, output_padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 19, kernel_size=(1, 1), stride=(1, 1)),
            nn.Softmax(dim=1),
        )

        for m in self.upconvs:
            if isinstance(m, nn.ConvTranspose2d) or isinstance(m, nn.Conv2d):
                torch.nn.init.xavier_normal_(m.weight, gain=1)

    def freezeTrunk(self):
        for param in self.new_model.parameters():
            param.requires_grad = False

    def unfreezeTrunk(self):
        for param in self.new_model.parameters():
            param.requires_grad = True

    def delete_features(self):
        del self.features

    def forward(self, input_imgs):
        trunk = self.new_model(input_imgs)
        output = self.upconvs(trunk)

        return trunk.detach(), output
