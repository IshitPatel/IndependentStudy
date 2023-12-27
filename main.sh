#!/bin/bash



sudo python3 federated_main.py --model=cnn --dataset=cifar --gpu=1 --num_classes=10 --local_ep=2 --local_bs=32 --num_users=2 --epochs=2 --lr=0.01



