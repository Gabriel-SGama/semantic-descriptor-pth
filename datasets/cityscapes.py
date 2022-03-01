from random import random

import cv2
import torch
from torch.nn import functional as F

from datasets.dataloader import baseDataloader


class Cityscapes(baseDataloader):
    # TODO: Leitura e dataAugmentation está todo implementado em OpenCV, não está fazendo o uso de transforms
    def __getitem__(self, index):

        imgPath = self.images[index]
        labelPath = self.labels[index]
        # print(imgPath)
        # print(labelPath)
        image = cv2.imread(imgPath, cv2.IMREAD_COLOR)
        label = cv2.imread(labelPath, cv2.IMREAD_GRAYSCALE)

        self.shape = image.shape
        image = image[:, :, ::-1]  # BGR to RGB

        # If training, apply data augmentation
        if not self.eval:
            image, label = self.augmentData(image, label)
        else:
            original_size = (self.img_width, self.img_height)
            image = cv2.resize(image, original_size, interpolation=cv2.INTER_AREA)
            label = cv2.resize(label, original_size, interpolation=cv2.INTER_NEAREST)

        # Label remapping
        label = self.convertLabel(label)

        # Normalize image
        # TODO: Usar função self.normAndTranspImg(image)
        image = self.normAndTranspImg(image)  # FIXME: @gama disse que estava dando um problema com pytorch na hora de transformar para tensor?

        # Transform to tensors
        image = torch.from_numpy(image)
        label = torch.from_numpy(label)
        label = label.long()  # label.to(torch.int64)

        label = F.one_hot(label, num_classes=20)
        label = label.permute((2, 0, 1))  # TODO: Porque o label possui três canais, não deveria ser 1?
        
        return image, label


class attCityscapes(baseDataloader):
    def __getitem__(self, index):

        imgPath = self.images[index]
        labelPath = self.labels[index]

        image = cv2.imread(imgPath, cv2.IMREAD_COLOR)
        label = cv2.imread(labelPath, cv2.IMREAD_GRAYSCALE)

        self.shape = image.shape
        image = image[:, :, ::-1]

        if not self.eval and random() < 0.5:
            image = self.color(image)

        if image.shape[0] != self.img_height or image.shape[1] != self.img_width:
            imageH = cv2.resize(image, (self.img_width, self.img_height), interpolation=cv2.INTER_AREA)
            label = cv2.resize(label, (self.img_width, self.img_height), interpolation=cv2.INTER_NEAREST)
        else:
            imageH = image.copy()

        imageL = cv2.resize(image, (int(self.img_width / 2), int(self.img_height / 2)), interpolation=cv2.INTER_AREA)

        label = self.convertLabel(label)

        # Normalize images
        imageL = self.normAndTranspImg(imageL)
        imageH = self.normAndTranspImg(imageH)

        imageL = torch.from_numpy(imageL)
        imageH = torch.from_numpy(imageH)

        label = torch.from_numpy(label)
        label = label.long()

        label = F.one_hot(label, num_classes=20)
        label = label.permute((2, 0, 1))

        return imageL, imageH, label
