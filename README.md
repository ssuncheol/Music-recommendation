# Music-recommendation

**The architecture was inspired by [Neural Collaborative Filtering](https://arxiv.org/abs/1708.05031)[![GitHub stars](https://img.shields.io/github/stars/hexiangnan/neural_collaborative_filtering.svg?logo=github&label=Stars)]**

---

## Overview

### Dataset
**Dataset : [Melon playlist](https://arena.kakao.com/c/8) is used** 

  - [x] **Users : 105141** 
  - [x] **Songs : 35919**  

### Model 

<img width='768' src='https://user-images.githubusercontent.com/52492949/98676852-7edb3700-239f-11eb-91e3-e6f40c2ece45.png'>

### Metric 

- [x] **NDCG**
- [x] **HR** 

---

## How to use 

### Languages 

<p align="left">
  <a href="#">
    <img src="https://github.com/MikeCodesDotNET/ColoredBadges/blob/master/svg/dev/languages/python.svg" alt="python" style="vertical-align:top; margin:6px 4px">
  </a> 

</p>

### Tools

<p align="left">
  <a href="#">
    <img src="https://github.com/MikeCodesDotNET/ColoredBadges/blob/master/svg/dev/tools/docker.svg" alt="docker" style="vertical-align:top; margin:6px 4px">
  </a> 

  <a href="#">
    <img src="https://github.com/MikeCodesDotNET/ColoredBadges/blob/master/svg/dev/tools/bash.svg" alt="bash" style="vertical-align:top; margin:6px 4px">
  </a> 

  <a href="#">
    <img src="https://github.com/MikeCodesDotNET/ColoredBadges/blob/master/svg/dev/tools/visualstudio_code.svg" alt="visualstudio_code" style="vertical-align:top; margin:6px 4px">
  </a> 

</p>

---

## Experiment 

### Hyperparameter

- [x] **Num of Neg : 1,5,10**<br> 
>
- [x] **Num Factor : 8,16,32**<br> 
>
- [x] **Num Layer : 1,2,3**<br>
>

### Results

<details><summary><b>Click me:heavy_exclamation_mark:<b></summary>
<p>

| HR@10 | NDCG@10 | Num of Neg | Num Factor | Num Layer |
|:-----:|:-------:|:----------:|:----------:|:---------:|
| 0.7912|   0.5140|      1     |      8     |     1     |
| 0.8013|   0.5444|      5     |      8     |     1     |
| 0.7469|   0.5026|      10    |      8     |     1     |
| 0.8224|   0.5610|      1     |      16    |     1     |
| 0.8270|   0.5853|      5     |      16    |     1     |
| -     |  -      |      10    |      16    |     1     |
| -     |  -      |      1     |      32    |     1     |
| -     |  -      |      5     |      32    |     1     |
| -     |  -      |      10    |      32    |     1     |
| 0.8030|   0.5412|      1     |      8     |     3     |
| 0.8026|   0.5524|      5     |      8     |     3     |
| 0.7696|   0.5324|      10    |      8     |     3     |
| 0.8155|   0.5590|      1     |      16    |     3     |
| 0.8152|   0.5732|      5     |      16    |     3     |
| 0.7860|   0.5465|      10    |      16    |     3     |
| -     |  -      |      1     |      32    |     3     |
| -     |  -      |      5     |      32    |     3     |
| -     |  -      |      10    |      32    |     3     |

<p>
</details>

---

### Run Example 
```sh
python3 main.py --optim=adam --lr=1e-3 --epochs=20 --batch_size=1024 --latent_dim_mf=8 --num_layers=3 --num_neg=5 --l2=0.0 --gpu=2,3
``` 