# 필요한 라이브러리와 모듈 내용 불러오기
import tkinter as tk
from tkinter import filedialog
from api.ace_dataset import *
from api.magnetometer_dataset import *
from api.ecallisto_dataset import *
from api.jbs_dataset import *
from api.dscovr_dataset import *
from api.dst_dataset import *
from api.gye_dataset import *
from api.swpc_dataset import *
from api.bbso_dataset import *

# 각 데이터 아이디와 데이터 셋 클래스를 매칭하는 딕셔너리 정의 
dataset_dict = {
    'noaa_ace_mag' : AceMagDataset,
    'noaa_ace_sis' : AceSisDataset,
    'noaa_ace_swepam' : AceSwepamDataset,
    'kasi_boh_mag_min' : MagnetometerBOHminDataset,
    'kasi_boh_mag_min_sec5' : MagnetometerBOHsec5Dataset,
    'kasi_boh_mag_kindex' : MagnetometerKindexDataset,
    'kasi_boh_mag_mi_ms_txt' : MagnetometerBOHmilDataset,
    'kasi_boh_mag_spectrum_x' : MagnetometerMISpectrumXDataset,
    'kasi_boh_mag_spectrum_y' : MagnetometerMISpectrumYDataset,
    'kasi_boh_mag_spectrum_z' : MagnetometerMISpectrumZDataset,
    'kasi_boh_mag_min_average' : MagnetometerMinAverageDataset,
    'kasi_boh_mag_pi2_list' : MagnetometerPi2listDataset,
    'kasi_boh_mag_pi2_power' : MagnetometerPi2powerDataset,
    'kasi_hq_ecallisto_position_lptcs' : EcallistoLPTCSLogDataset,
    'kasi_hq_ecallisto_position_lptcs' : EcallistoLPTCSTxtDataset,
    'kasi_hq_ecallisto_spectrum' : EcallistoSpFitDataset,
    'kopri_jbs_scint_iono' : JbsIonoDataset,
    'kopri_jbs_scint_navsol' : JbsNavsolDataset,
    'kopri_jbs_scint_scint' : JbsScintDataset,
    'kopri_jbs_scint_txinfo' : JbsTxinfoDataset,
    'noaa_dscovr_mag' : DscovrMagDataset,
    'noaa_dscovr_plasma' : DscovrPlasmaDataset,
    'wdc_dst_obs' : DSTDataset,
    'kasi_gye_scint_channel' : GyeChannelDataset,
    'kasi_gye_scint_iono' : GyeIonoDataset,
    'kasi_gye_scint_navsol' : GyeNavsolDataset,
    'kasi_gye_scint_scint' : GyeScintDataset,
    'kasi_gye_scint_txinfo' : GyeTxinfoDataset,
    'noaa_swpc_dayobs' : SWPCDayobsDataset,
    'noaa_swpc_daypre' : SWPCDaypreDataset,
    'noaa_swpc_dsd' : SWPCDSDDataset,
    'noaa_swpc_hpi_aurora_power' : SWPCAuroraPowerDataset,
    'noaa_swpc_rsga' : SWPCRSGADataset,
    'noaa_swpc_sgas' : SWPCSGASDataset,
    'noaa_swpc_srs' : SWPCSRSDataset,
    'ghn_bbso_fts' : BBSOFtsDataset,
    'ghn_bbso_logs' : BBSOTxtDataset,
    'ghn_oact_fts_gz' : BBSOFtsGzDataset
}

# 하위 데이터 아이디 정보를 가지고 있는 데이터 아이디 리스트(테이블) 정의
noaa_ace_list = ['noaa_ace_mag', 'noaa_ace_sis', 'noaa_ace_swepam']
kasi_boh_mag_list = ['kasi_boh_mag_mi_ms_txt', 'kasi_boh_mag_min', 'kasi_boh_mag_min_average', 'kasi_boh_mag_pi2_list', 'kasi_boh_mag_pi2_power', 'kasi_boh_mag_mi_spectrum_x', 'kasi_boh_mag_mi_spectrum_y', 'kasi_boh_mag_mi_spectrum_z', 'kasi_boh_mag_sec5', 'kasi_boh_mag_kindex']
kasi_hq_ecallisto_list = ['kasi_hq_ecallisto_position_lptcs_log', 'kasi_hq_ecallisto_position_lptcs_txt', 'kasi_hq_ecallisto_spectrum']
kopri_jbs_scint_list = ['kopri_jbs_scint_iono', 'kopri_jbs_scint_navsol', 'kopri_jbs_scint_scint', 'kopri_jbs_scint_txinfo']
noaa_dscovr_list = ['noaa_dscovr_mag', 'noaa_dscovr_plasma']
wdc_dst_list = ['wdc_dst_obs']
kasi_gye_scint_list = ['kasi_gye_scint_channel', 'kasi_gye_scint_iono', 'kasi_gye_scint_navsol', 'kasi_gye_scint_scint', 'kasi_gye_scint_txinfo']
noaa_swpc_list = ['noaa_swpc_dayobs', 'noaa_swpc_daypre', 'noaa_swpc_dsd', 'noaa_swpc_hpi_aurora_power', 'noaa_swpc_rsga', 'noaa_swpc_sgas', 'noaa_swpc_srs']
ghn_list = ['ghn_bbso_fts', 'ghn_bbso_logs', 'ghn_oact_fts_gz']

# 데이터 아이디 리스트(테이블) 정보를 가지고 있는 테이블 리스트, 테이블 이름 리스트 정의
table_list = [noaa_ace_list, kasi_boh_mag_list, kasi_hq_ecallisto_list, kopri_jbs_scint_list, noaa_dscovr_list, wdc_dst_list, kasi_gye_scint_list, noaa_swpc_list, ghn_list]
table_name_list = ['noaa_ace', 'kasi_boh_mag', 'kasi_hq_ecallisto', 'kopri_jbs_scint', 'noaa_dscovr', 'wdc_dst', 'kasi_gye_scint', 'noaa_swpc', 'ghn']

def file_explorer():
    """
    파일 탐색 함수
    - 실행 시 탐색기 창을 통해 파일 선택
    - 선택된 파일 경로 반환
    """
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    if file_path:
        print("Selected file:", file_path)
    else:
        print("No file selected.")
    root.destroy()

    return file_path

def data_id_explorer():
    """
    데이터 아이디 검색 함수
    - 테이블 이름 리스트의 내용을 번호와 함께 출력
    - 입력받은 번호에 해당하는 테이블의 이름을 테이블 리스트에서 검색
    - 해당 테이블에 존재하는 데이터 아이디를 번호와 함께 출력
    - 입력받은 번호에 해당하는 데이터 아이디를 반환
    """
    print("-----Table List-----")
    for i, table_name in enumerate(table_name_list):
        print(str(i + 1) + '. '+ table_name)
    table_num = int(input("Enter the table number: "))
    table = table_list[table_num - 1]
    print("-----Data ID-----")
    for i, data_id in enumerate(table):
        print(str(i + 1) + '. ' + data_id)
    data_id_num = int(input("Enter the data id number: "))

    return table[data_id_num - 1]

def search(file_name, data_id, info_num):
    """
    데이터 조회 함수
    - 파일 이름, 데이터 아이디, 정보의 종류를 입력받아 조회 데이터 출력
    - 1. 헤더 / 2. 데이터 / 3. 헤더+데이터 / 4. 시각화 / 5. 1~4 모두 출력
    - 해당 데이터 셋 반환
    """
    dataset = dataset_dict[data_id](file_name)
    dataset.parsing()
    if info_num == 1:
        print(dataset.header)
    elif info_num == 2:
        print(dataset.data)
    elif info_num == 3:
        print(dataset.all)
    elif info_num == 4:
        dataset.plot()
    elif info_num == 5:
        print(dataset.header)
        print(dataset.data)
        print(dataset.all)
        dataset.plot()
    else:
        exit()
    
    return dataset