from api.sdo_dataset import HMIDataset

f1 = "./hmi_magnetogram.fits"
f2 = "./hmi_continuum.fits"
f3 = "./hmi_dopplergram.fits"

fs = [f1, f2, f3]

for f in fs :
    hmi_dataset = HMIDataset(f)
    hmi_dataset.parsing()
    hmi_dataset.plot()