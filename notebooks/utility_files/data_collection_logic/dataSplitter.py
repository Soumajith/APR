from ultralytics import YOLO
import os
import random
import shutil
from itertools import islice

output_path = 'dataset/split'
input_path = 'dataset/data/all'
splitRatio = {
    'train' : 0.7,
    'val': 0.2,
    'test': 0.1
}

try:
    shutil.rmtree(output_path)
    print("Directory is removed")
except OSError as e:
    os.mkdir(output_path)

os.makedirs(f'{output_path}/train/images',exist_ok=True)
os.makedirs(f'{output_path}/train/labels',exist_ok=True)

os.makedirs(f'{output_path}/val/images',exist_ok=True)
os.makedirs(f'{output_path}/val/labels',exist_ok=True)

os.makedirs(f'{output_path}/test/images',exist_ok=True)
os.makedirs(f'{output_path}/test/labels',exist_ok=True)

listnames = os.listdir(input_path)
uniqueNames = []
for name in listnames:
    uniqueNames.append(name.split('.')[0])
uniqueNames = set(uniqueNames)
uniqueNames = list(uniqueNames)

#shuffling the data
random.shuffle(uniqueNames)

lenData = len(uniqueNames)
lenTrain = int(lenData*splitRatio['train'])
lenVal = int(lenData*splitRatio['val'])
lenTest = int(lenData*splitRatio['test'])

if lenData != lenTrain + lenVal + lenTest:
    rem = lenData - (lenTrain + lenVal + lenTest)
    lenTrain += rem

lenToSplit = [lenTrain,lenVal,lenTest]
inp = iter(uniqueNames)
out = [list(islice(inp,el)) for el in lenToSplit]  # output is 3 lists having train, test , val data

seq = ['train','val','test']
for ind,direc in enumerate(out):
    for filename in direc:
        shutil.copy(f'{input_path}/{filename}.jpg', f'{output_path}/{seq[ind]}/images/{filename}.jpg')
        shutil.copy(f'{input_path}/{filename}.txt', f'{output_path}/{seq[ind]}/labels/{filename}.txt')

# creating Data yaml file
'''yaml_content = f"""
train: {os.path.abspath(output_path)}/train/images
val: {os.path.abspath(output_path)}/val/images
test: {os.path.abspath(output_path)}/test/images

nc: 2
names: ['real', 'fake']
"""

with open('dataset/data.yaml', 'w') as f:
    f.write(yaml_content)

print("data.yaml file created successfully!")'''
