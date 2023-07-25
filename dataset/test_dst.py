

from api.dst_dataset import DSTDataset



f = "./testdata/DST/201701_dst_obs.txt"


dataset = DSTDataset(f)

dataset.parsing()

d = dataset.data
h = dataset.header

print(d)
print(h)