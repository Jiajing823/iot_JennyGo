import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim import lr_scheduler
import numpy as np
import torchvision
import argparse
from torchvision import datasets, models, transforms
import matplotlib.pyplot as plt
import time
import os
import copy
import pandas as pd
from torch.utils.data.dataset import Dataset
from torch.utils.data.sampler import SubsetRandomSampler
import matplotlib.image as mpimg

def test(imgs):
    res_list = ['tree', 'stop', 'turn', 'over', 'play', 'go', 'stone']
    data = imgs.transpose((2, 0, 1))
    data = np.expand_dims(data, axis=0)
    data = torch.from_numpy(data)
    MODEL_PATH = "models/"
    model_ft = torch.load(MODEL_PATH + 'resnet18_1212_best')
    model_ft.eval()
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        data = data.to(device,dtype=torch.float)
        outputs = model_ft(data)
        print(outputs.data)
        _, pred = torch.max(outputs.data, 1)
    result = res_list[pred.cpu()]
    return result