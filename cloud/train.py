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
plt.ion()   # interactive mode

def rotate90(x):
    from scipy.ndimage.interpolation import rotate
    rotated = rotate(x, 90.0, reshape=False,axes=(0, 1))
    return rotated

def flip(x):
    flipped = np.flip(np.flip(x.copy(), axis=0), axis=1)
    return flipped

def add_noise(x):
    added = x.copy()
    added[:, :, :] += np.random.randint(0, 5, [x.shape[0],x.shape[1],x.shape[2]],dtype='uint8') *5
    return added

def rgb2gray(rgb):
    grey = np.dot(rgb[...,:3], [0.299, 0.587, 0.144])
    grey = np.expand_dims(grey, axis =2)
    return grey

def aug(img, rnd):
    if rnd ==1:
        aug_img = rotate90(img)
    elif rnd ==2:
        aug_img = flip(img)
    else:
        aug_img = add_noise(img)
    return aug_img

class CustomDataset(Dataset):
    def __init__(self, root, concat=5, transform=None):
        categories = [cat for cat in os.listdir(root) if not cat.startswith('.')]
        imgs_dirs = [os.path.join(root,cat) for cat in os.listdir(root) if not cat.startswith('.')]
        imgs = []
        for imgs_dir in imgs_dirs:
            imgs_single = [os.path.join(imgs_dir,img) for img in os.listdir(imgs_dir) if not img.startswith('.')]
            imgs_single = sorted(imgs_single, key=lambda x: int(x.split('.')[-2].split('/')[-1]))
            imgs.append(imgs_single)
        imgs = sum(imgs,[])
        imgs_num = int(len(imgs)/concat)
        self.imgs_num = imgs_num
        self.categories = categories
        self.imgs = imgs
        self.transform = transform
        self.concat = concat
    def __getitem__(self, idx):
        idx_real = idx * self.concat
        category = str(self.imgs[idx_real].split('/')[-2].split('/')[-1])
        label = self.categories.index(category)
        img_path = self.imgs[idx_real]
        image = mpimg.imread(img_path)
        is_transform = np.random.randint(0,2)
        if(is_transform == 1):
            rnd = np.random.randint(1,4)
            samples = self.transform(image, rnd)
            samples = rgb2gray(samples)
            for i in range(1,self.concat):
                img_path = self.imgs[idx_real+i]
                image = mpimg.imread(img_path)
                sample = self.transform(image,rnd)
                sample = rgb2gray(sample)
                samples = np.concatenate((samples, sample),axis=2)
            samples = samples.transpose((2, 0, 1))
        else:
            samples = image
            samples = rgb2gray(samples)
            for i in range(1,self.concat): 
                img_path = self.imgs[idx_real+i]
                sample = mpimg.imread(img_path)
                sample = rgb2gray(sample)
                samples = np.concatenate((samples, sample),axis=2)
            samples = samples.transpose((2, 0, 1))
        return (samples, label)
    def __len__(self):
        return self.imgs_num
    
def train_model(model, criterion, optimizer, scheduler, is_trained=False, num_epochs=25, save_path = 'models/densenet121_multi'):
    since = time.time()
    
#     best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    if is_trained:
        model = torch.load(save_path)
    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)

        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                
                model.train()  # Set model to training mode
            else:
                model.eval()   # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0
            y_score = []
            y = []
            # Iterate over data.
            confusion_matrix = torch.zeros(7, 7)
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device,dtype=torch.float)
                labels = labels.to(device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                # track history if only in train
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    loss = criterion(outputs, labels)
                    _, preds = torch.max(outputs, 1)

                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                        scheduler.step()

                # statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
#                 print(preds)
#                 print(labels.data)
                if phase == 'val':
                    for t, p in zip(labels.view(-1), preds.view(-1)):
                        confusion_matrix[t.long(), p.long()] += 1

            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))
            print(confusion_matrix)

            # deep copy the model
#             if phase == 'val':
#                 if epoch_acc > best_acc:
#                     best_acc = epoch_acc
#                     best_model_wts = copy.deepcopy(model.state_dict())
            if phase == 'val':
                if (epoch+1)%1 == 0:
                    md = save_path + '_epoch' + str(epoch)
                    torch.save(model, md)

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))

    # load best model weights
#     model.load_state_dict(best_model_wts)
    torch.save(model,save_path)
    return model

if __name__ == "__main__":
    
    """
    usage: python train.py --epoch <num>  --save <PATH_TO_SAVE_MODEL> --rand <randomseed>
    
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--epoch', default=25, type=int,
                        dest='num_epochs',
                        help='number of epochs')
    parser.add_argument('--trained', default=0, type=int,
                        dest='is_trained',
                        help='if to use trained model (0 no, 1 yes)')
    parser.add_argument('--save', default='models/alexnet_try', type=str,
                        dest='save_path',
                        help='path to save the model')
    parser.add_argument('--rand', default=5, type=int,
                        dest='rand',
                        help='random seed')
    args = parser.parse_args()
    num_epochs = args.num_epochs
    save_path = args.save_path
    if (args.is_trained == 0):
        is_trained = False
    else:
        is_trained = True
    rand = args.rand
    
    # load data
    PATH = "./uploads/train"
    dataset_train = CustomDataset(PATH,transform=aug)
    batch_size = 14
    validation_split = 0.20
    shuffle_dataset = True
    random_seed= rand

    # Creating data indices for training and validation splits:
    dataset_size = len(dataset_train)
    indices = list(range(dataset_size))
    split = int(np.floor(validation_split * dataset_size))
    if shuffle_dataset :
        np.random.seed(random_seed)
        np.random.shuffle(indices)
    train_indices, val_indices = indices[split:], indices[:split]
    # Creating subset samplers and corresponding loaders:
    train_sampler = SubsetRandomSampler(train_indices)
    valid_sampler = SubsetRandomSampler(val_indices)
    train_loader = torch.utils.data.DataLoader(dataset_train, batch_size=batch_size, 
                                               sampler=train_sampler)
    validation_loader = torch.utils.data.DataLoader(dataset_train, batch_size=batch_size, 
                                               sampler=valid_sampler)
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    dataloaders={'train':train_loader, 'val':validation_loader}
    dataset_sizes={'train':len(train_sampler), 'val':len(valid_sampler)}
    
    #densenet121
    model_ft = models.resnet18(pretrained=True)
    model_ft.conv1 = nn.Conv2d(5, 64, kernel_size=(7,7), stride=(2,2), padding=(3,3))
    model_ft.fc = nn.Linear(512, 7)
#     model_ft.features._modules['0'] = nn.Conv2d(5, 64, kernel_size=11, stride=4, padding=2)
#     model_ft.classifier._modules['6'] = nn.Linear(4096, 7)

    model_ft = model_ft.to(device)

    criterion = nn.CrossEntropyLoss()

    # Observe that all parameters are being optimized
    optimizer_ft = optim.Adam(model_ft.parameters(), lr=0.0005)

    # Decay LR by a factor of 0.1 every 7 epochs
    exp_lr_scheduler = lr_scheduler.StepLR(optimizer_ft, step_size=7, gamma=0.1)
    print(model_ft)
    model_ft = train_model(model_ft, criterion, optimizer_ft, exp_lr_scheduler, is_trained=is_trained, num_epochs=num_epochs, save_path=save_path) 
    print("Train ends!")