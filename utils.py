#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python version: 3.6

import copy
import torch
import os
from torchvision import datasets, transforms
from sampling import mnist_iid, mnist_noniid, mnist_noniid_unequal
from sampling import cifar_iid, cifar_noniid


def get_dataset(args):
    """ Returns train and test datasets and a user group which is a dict where
    the keys are the user index and the values are the corresponding data for
    each of those users.
    """

    if args.dataset=='office-home':
        data_dir = '/mnt/data/liuby/aaai-privacy-model-adapt/office-home/federated_learning/client'
        # data_dir = '/mnt/data/liuby/aaai-privacy-model-adapt/cifar10_50sample/client'

        user_dir=[]
        for i in [1,2,3,4,5,6,7,8,9,10,16,17,18,19,20]:
            train_dir=data_dir+str(i)+'/'
            user_dir.append(train_dir)

        # test_dir = '/mnt/data/liuby/aaai-privacy-model-adapt/office-home/domain_adaptation/Art_edge-test/'
        test_dir = '/mnt/data/liuby/aaai-privacy-model-adapt/office-home/federated_learning/test_client20/'
        # test_dir = '/mnt/data/liuby/aaai-privacy-model-adapt/cifar10png/federated_test/'
        # test_dir = '/mnt/data/liuby/aaai-privacy-model-adapt/cifar10png/test_type5/'
        # test_dir = '/mnt/data/liuby/aaai-privacy-model-adapt/office-home/federated_learning/federated_test/'


        return test_dir, user_dir



    elif args.dataset == 'cifar':
        data_dir = '../data/cifar/'
        train_dir = '../data/cifar/train/'
        test_dir = '../data/cifar/test/'
        apply_transform = transforms.Compose(
            [transforms.ToTensor(),
             transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))])

        train_dataset = datasets.CIFAR10(data_dir, train=True, download=True,
                                       transform=apply_transform)

        test_dataset = datasets.CIFAR10(data_dir, train=False, download=True,
                                      transform=apply_transform)
        
        # Classes in CIFAR-10
        classes = ('plane', 'car', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck')

        # Create directories for each class
        for cls in classes:
            os.makedirs(os.path.join(train_dir, cls), exist_ok=True)

        # Save each image in the respective class folder
        for i in range(len(train_dataset)):
            image, label = train_dataset[i]
            image_path = os.path.join(train_dir, classes[label], f'{i}.png')
            image = transforms.ToPILImage()(image)
            image.save(image_path)

        # Create directories for each class
        for cls in classes:
            os.makedirs(os.path.join(test_dir, cls), exist_ok=True)

        # Save each image in the respective class folder
        for i in range(len(test_dataset)):
            image, label = test_dataset[i]
            image_path = os.path.join(test_dir, classes[label], f'{i}.png')
            image = transforms.ToPILImage()(image)
            image.save(image_path)

        # sample training data amongst users
        if args.iid:
            # Sample IID user data from Mnist
            user_groups = cifar_iid(train_dataset, args.num_users)
            #print(user_groups)
        else:
            # Sample Non-IID user data from Mnist
            if args.unequal:
                # Chose uneuqal splits for every user
                raise NotImplementedError()
            else:
                # Chose euqal splits for every user
                user_groups = cifar_noniid(train_dataset, args.num_users)

    elif args.dataset == 'mnist' or 'fmnist':
        if args.dataset == 'mnist':
            data_dir = '../data/mnist/'
        else:
            data_dir = '../data/fmnist/'

        apply_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))])

        train_dataset = datasets.MNIST(data_dir, train=True, download=True,
                                       transform=apply_transform)

        test_dataset = datasets.MNIST(data_dir, train=False, download=True,
                                      transform=apply_transform)
        
        # sample training data amongst users
        if args.iid:
            # Sample IID user data from Mnist
            user_groups = mnist_iid(train_dataset, args.num_users)
        else:
            # Sample Non-IID user data from Mnist
            if args.unequal:
                # Chose uneuqal splits for every user
                user_groups = mnist_noniid_unequal(train_dataset, args.num_users)
            else:
                # Chose euqal splits for every user
                user_groups = mnist_noniid(train_dataset, args.num_users)

    return test_dir, train_dir, user_groups


def average_weights(w):
    """
    Returns the average of the weights.
    """
    w_avg = copy.deepcopy(w[0])
    for key in w_avg.keys():
        for i in range(1, len(w)):
            w_avg[key] += w[i][key]
        w_avg[key] = torch.div(w_avg[key], len(w))
    return w_avg


def exp_details(args):
    print('\nExperimental details:')
    print(f'    Model     : {args.model}')
    print(f'    Optimizer : {args.optimizer}')
    print(f'    Learning  : {args.lr}')
    print(f'    Global Rounds   : {args.epochs}\n')

    print('    Federated parameters:')
    if args.iid:
        print('    IID')
    else:
        print('    Non-IID')
    print(f'    Fraction of users  : {args.frac}')
    print(f'    Local Batch size   : {args.local_bs}')
    print(f'    Local Epochs       : {args.local_ep}\n')
    return
