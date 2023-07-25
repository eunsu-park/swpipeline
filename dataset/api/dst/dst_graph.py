from dst_dataset import DSTDataset

f="201701_dst_obs.txt"

dst_dataset=DSTDataset(f)
dst_dataset.parsing()
dst_dataset.plot()

print(dst_dataset.header)
print(dst_dataset.data)
print(dst_dataset.all)
