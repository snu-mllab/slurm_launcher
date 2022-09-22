import os
import sys

import argparse
import torch
use_cuda = torch.cuda.is_available()

import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR

from tensorboard import SummaryWriterManager

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output

def test(model, device, dataloader):
    model.eval()
    test_loss = 0
    test_acc = 0
    with torch.no_grad():
        for data, target in dataloader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            test_acc += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(dataloader.dataset)
    test_acc /= len(dataloader.dataset)

    model.train()

    return test_loss, test_acc

def main():
    # Training settings
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument('--lr', type=float, default=1.0, help='learning rate (default: 1.0)')
    parser.add_argument('--seed', type=int, default=0, help='random seed')
    parser.add_argument('--boarddir', type=str, default='./board', help='tensorboard directory')
    args = parser.parse_args()

    USER = os.environ['USER']
    JOB_NAME  = os.environ['SLURM_JOB_NAME']
    JOB_ID  = os.environ['SLURM_JOB_ID']

    PROJ_DIR = f"/home/{USER}/packages/slurm_launcher/mnist_example"
    OUT_FILE_PATH = os.path.join(PROJ_DIR, "slurm", JOB_NAME, JOB_ID + ".out")

    LINK_DIR = os.path.join("link", JOB_NAME, str(args.lr))
    LINK_PATH = os.path.join(LINK_DIR, str(args.seed) + ".link")

    os.makedirs(LINK_DIR, exist_ok=True)
    print(f"Link {LINK_PATH} to {OUT_FILE_PATH}")
    os.system(f"ln -s {OUT_FILE_PATH} {LINK_PATH}")

    torch.random.manual_seed(args.seed)
    transform=transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])

    DATADIR = "/data_large/readonly/"
    trainset = datasets.MNIST(DATADIR, train=True, download=False, transform=transform)
    testset = datasets.MNIST(DATADIR, train=False, download=False, transform=transform)

    train_loader = torch.utils.data.DataLoader(trainset, batch_size=64, shuffle=True, num_workers=4)
    test_loader = torch.utils.data.DataLoader(testset, batch_size=100, shuffle=False, num_workers=4)

    device = torch.device("cuda" if use_cuda else "cpu")
    model = Net().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=args.lr)

    scheduler = StepLR(optimizer, step_size=1, gamma=0.7)

    ################################################
    boardsubdir = args.boarddir+'/lr{}/'.format(args.lr)
    tensorboardwrite = SummaryWriterManager(boardsubdir)
    ################################################

    for epoch in range(1, 15):
        model.train()
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = F.nll_loss(output, target)
            loss.backward()
            optimizer.step()

        test_loss, test_acc = test(model, device, test_loader)
        train_loss, train_acc = test(model, device, train_loader)

        print("Test")
        print('Loss: {:.4f}, Accuracy : {:.4f}'.format(test_loss, test_acc))
        print("Train")
        print('Loss: {:.4f}, Accuracy : {:.4f}'.format(train_loss, train_acc))

        ################################################
        write_content = {
                'val_acc' : test_acc,
                'val_loss' : test_loss,
                'train_acc' : train_acc,
                'train_loss' : train_loss}
        tensorboardwrite.add_summaries(write_content, global_step=epoch)
        ################################################
        scheduler.step()

if __name__ == '__main__':
    main()
