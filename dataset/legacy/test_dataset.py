from astropy.io import fits
import dataset.sdo as sdo

if __name__ == "__main__" :
    file_aia = "./sample_aia.fits"
    file_aia_comp = "./sample_aia_compressed.fits"

    aia = sdo.aia_open(file_aia)
    aia_comp = sdo.aia_open(file_aia_comp)

    print(aia.header)
    print(aia_comp.header)

    print(aia.data.shape, aia.data.dtype)
    print(aia_comp.data.shape, aia_comp.data.dtype)

    aia.prep()
    aia_comp.prep()

    aia.plot()
    aia_comp.plot()

    f1 = "hmi_ic_45s_2011_01_01_00_00_00_tai_continuum.fits"
    f2 = "hmi_m_45s_2011_01_01_00_00_00_tai_magnetogram.fits"
    f3 = "hmi_v_45s_2011_01_01_00_00_00_tai_dopplergram.fits"

    h1 = sdo.hmi_open(f1)
    h2 = sdo.hmi_open(f2)
    h3 = sdo.hmi_open(f3)

    h1.prep()
    h2.prep()
    h3.prep()

    h1.plot()
    h2.plot()
    h3.plot()
ㅇ