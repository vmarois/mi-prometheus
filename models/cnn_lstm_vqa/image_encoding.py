#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) IBM Corporation 2018
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
image encoding.py: image encoding for VQA problem, same as in this paper
https://arxiv.org/abs/1706.01427, specifically desinged for sort of clevr.
"""
__author__ = "Younes Bouhadjar"

import torch.nn as nn
import torch.nn.functional as F


class ImageEncoding(nn.Module):
    """
    Image encoding using 4 convolutional layers with batch normalization, it
    was designed specifically for sort of clevr
    https://arxiv.org/abs/1706.01427.
    """

    def __init__(self):
        """
        Constructor of the ImageEncoding class.
        """
        super(ImageEncoding, self).__init__()

        self.conv1 = nn.Conv2d(3, 24, 3, stride=2, padding=1)
        self.batchNorm1 = nn.BatchNorm2d(24)
        self.conv2 = nn.Conv2d(24, 24, 3, stride=2, padding=1)
        self.batchNorm2 = nn.BatchNorm2d(24)
        self.conv3 = nn.Conv2d(24, 24, 3, stride=2, padding=1)
        self.batchNorm3 = nn.BatchNorm2d(24)
        self.conv4 = nn.Conv2d(24, 24, 3, stride=2, padding=1)
        self.batchNorm4 = nn.BatchNorm2d(24)

    def forward(self, img):
        """
        apply 4 convolutional layers over the image.

        :param img: input image [batch_size, num_channels, height, width]
        :returns: x: feature map [batch_size, num_channels_encoded_question, new_height, new_width]

        """
        x = self.conv1(img)
        x = F.relu(x)
        x = self.batchNorm1(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = self.batchNorm2(x)
        x = self.conv3(x)
        x = F.relu(x)
        x = self.batchNorm3(x)
        x = self.conv4(x)
        x = F.relu(x)
        x = self.batchNorm4(x)

        return x
