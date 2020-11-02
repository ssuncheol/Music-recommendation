import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import argparse
from collections import Counter
import time
from neucf import NeuralCF
from data import SampleGenerator
from engine import Engine
from metrics import MetronAtK
import matplotlib.pyplot as plt
import random
import warnings
import os

warnings.filterwarnings("ignore")
train = pd.read_json("/daintlab/data/music_rec/train.json")
song_meta = pd.read_json("/daintlab/data/music_rec/song_meta.json")

n_data = len(train)
train["nid"] = range(n_data) # 0부터 data 개수만큼 번호를 줌

train_song = train['songs']
song_counter = Counter([song for songs in train_song for song in songs])
song_dict = {x: song_counter[x] for x in song_counter}
song_dict = dict(filter(lambda x : x[1]>=100, song_dict.items())) # dict에서 n곡 이상만 필터링

song_id_sid = dict()
song_sid_id = dict()
for i, song_id in enumerate(song_dict): # i : 인덱스, song_id : 곡 id
  song_id_sid[song_id] = i # 각 곡에 인덱스 번호 주기
  song_sid_id[i] = song_id # 각 인덱스에 곡 id 주기
  
n_songs = len(song_dict)
song_meta["nid"] = song_meta["id"].apply(lambda x : song_id_sid.get(x))
meta = song_meta[song_meta["nid"].notnull()]
meta["nid"] = meta["nid"].astype(int)
meta["issue_date"] = meta["issue_date"].astype(str)
meta["issue_date"] = meta["issue_date"].apply(lambda x : x[:4] + x[4:6].replace("00","01") + x[6:].replace("00","01"))

# to_datetime
def to_date(x):
    try:
        y = pd.to_datetime(x, format = "%Y%m%d")
    except:
        y = None
    return y


meta["issue_date"] = meta["issue_date"].apply(lambda x : to_date(x))
meta = meta[meta["issue_date"].notnull()]

issue_date = dict(zip(meta["nid"],meta["issue_date"]))

train['itemId'] = train['songs'].map(lambda x: [song_id_sid.get(song_id) for song_id in x if song_id_sid.get(song_id) != None])
train.loc[:,'num_songs'] = train['itemId'].map(len)

user_train_1 = np.repeat(range(n_data), train['num_songs'])
song_train_1 = np.array([song for songs in train['itemId'] for song in songs])
rat_train_1 = np.repeat(1, train['num_songs'].sum())
dat_train_1 = np.array([issue_date.get(song) for songs in train['itemId'] for song in songs])
data = pd.DataFrame({"userId":user_train_1,"itemId":song_train_1,"rating":rat_train_1,"timestamp":dat_train_1})

data['rank_latest'] = data.groupby(['userId'])['timestamp'].rank(method='first', ascending=False)


parser = argparse.ArgumentParser()
parser.add_argument('--optim',
                type=str,
                default='adam',
                help='optimizer')
parser.add_argument('--lr',
                type=float,
                default=0.001,
                help='learning rate')
parser.add_argument('--epochs',
                type=int,
                default=10,
                help='learning rate')
parser.add_argument('--batch_size',
                type=int,
                default=1024,
                help='train batch size')
parser.add_argument('--latent_dim_mf',
                type=int,
                default=8,
                help='latent_dim_mf')
parser.add_argument('--num_layers',
                type=int,
                default=3,
                help='num layers')
parser.add_argument('--num_ng',
                type=int,
                default=4,
                help='negative sample')
parser.add_argument('--l2',
                type=float,
                default=0.0,
                help='l2_regularization')
parser.add_argument('--gpu',
                type=str,
                default='0',
                help='gpu number')
args = parser.parse_args()

os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu

'''
neumf_config = {'alias': 'neumf',
            'num_epoch': 20,
            'batch_size': 256,
            'optimizer': 'adam',
            'adam_lr': 1e-3,
            'num_users': n_data,
            'num_items': n_songs,
            'latent_dim_mf': 8,
            'latent_dim_mlp': 32,
            'num_negative': 10,
            'layers': [64,32,16,8],  # layers[0] is the concat of latent user vector & latent item vector
            'l2_regularization': 0.0,
            'use_cuda': True,
            'device_id': 0,
            'model_dir':'checkpoints/{}_Epoch{}_HR{:.4f}_NDCG{:.4f}.model'
            }
'''
# Reindex
print('Range of userId is [{}, {}]'.format(data["userId"].min(), data["userId"].max()))
print('Range of itemId is [{}, {}]'.format(data["itemId"].min(), data["itemId"].max()))
# DataLoader for training

print("SampleGenerator")
t1 = time.time()
sample_generator = SampleGenerator(ratings=data)
t2 = time.time()
print("SampleGenerator Time : ",t2-t1)

print("EvaluateGenerator")
t1 = time.time()
evaluate_data = sample_generator.evaluate_data
t2 = time.time()
print("EvaluateGenerator Time : ", t2 - t1)


# Specify the exact model
model = NeuralCF(n_data,n_songs,args.latent_dim_mf,args.num_layers)
model = nn.DataParallel(model).cuda()
print(model)
optimizer = torch.optim.Adam(model.parameters(),lr=args.lr,weight_decay=args.l2)
criterion = nn.BCEWithLogitsLoss()

H, N, L = [], [], []

t1 = time.time()
train_loader = sample_generator.instance_a_train_loader(args.num_ng, args.batch_size)
t2 = time.time()
print("train_loader : ", t2 - t1)

for epoch in range(args.epochs):
    print('Epoch {} starts !'.format(epoch))
    print('-' * 80)
    t1 = time.time()
    random.shuffle(train_loader.sampler.seq)
    t2 = time.time()
    print("Data Loader : ", t2 - t1)
    t1 = time.time()
    model.train()
    total_loss = 0
    count=0
    for batch_id, batch in enumerate(train_loader):
        assert isinstance(batch[0], torch.LongTensor)
        users, items, ratings = batch[0], batch[1], batch[2]
        ratings = ratings.float()
        users, items, ratings = users.cuda(), items.cuda(), ratings.cuda()
        optimizer.zero_grad()
        output = model(users, items).cuda()
        loss = criterion(output, ratings)
        loss.backward()
        optimizer.step()
        loss = loss.item()
        total_loss += loss
        count+=1
    t2 = time.time()
    print("train : ", t2 - t1) 
    t1 = time.time()   
    #loss = engine.train_an_epoch(train_loader, epoch_id=epoch)
    engine = Engine()
    hit_ratio,ndcg = engine.evaluate(model,evaluate_data, epoch_id=epoch)
    H.append(hit_ratio)
    N.append(ndcg)
    L.append(total_loss/count)
    #engine.save(config['alias'], epoch, hit_ratio, ndcg)
    t2 = time.time()
    print("Evaluate = {:.2f}".format(t2-t1))

e = range(1, args.epochs + 1)

plt.figure()

plt.plot(e, L, 'bo', label='Loss') 
plt.title('Loss') 
plt.legend()

plt.show()
plt.savefig("Loss.png")

plt.figure()

plt.plot(e, H, 'bo', label='HR') 
plt.title('HR') 
plt.legend()

plt.show()
plt.savefig("HR.png")

plt.figure()

plt.plot(e, N, 'bo', label='NDCG100') 
plt.title('NDCG') 
plt.legend()

plt.show()
plt.savefig("NDCG.png")

import ipdb; ipdb.set_trace()