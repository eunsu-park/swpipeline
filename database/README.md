# 우주환경 파이프라인 DB 모듈

## 실행법

```
python /path/to/scan_multi.py --cfg /path/to/multi_cfg.json
```

```
python scan_multi.py --cfg ../config/multi_cfg.json
```

`multi_cfg_.json`
```json
{
    "cfg_db": "/path/to/cfg_db.json",
    "cfg_storage": "/path/to/cfg_storage.json",
    "cfg_metadata": [
        "/path/to/cfg_metadata_1.json",
        "/path/to/cfg_metadata_2.json"
    ],
    "global_scan_flag": null
}
```

### 참고사항
- 위의 명령어를 최초 실행시 데이터베이스에 `data`, `hardware`, `metadata` schema를 생성함

- Metadata 설정파일의 이름을 기초로 프로세스 이름을 생성하고, pid 목록을 pid_list.txt파일로 저장함 (`top`로 확인 가능)
```
INFO:Process 'cfg_noaa_goes' started with PID: 4000438
INFO:Process 'cfg_ghn' started with PID: 4000439
```

- 설정파일 경로
    - 절대경로
    - 상대경로일 경우, `multi_cfg.json`이 들어 있는 폴더 기준으로 다른 config 파일의 상대경로를 입력해야 한다.
    예를 들어, `/path/to/config/multi_cfg.json`이고 `/path/to/config/metadata_table_config/cfg_ghn.json`일때, 
    `multi_cfg.json`에 대한 `cfg_ghn.json`의 상대경로는 `metadata_table_config/cfg_ghn.json`이다.

- 현재 폴더 구조에서는 database폴더가 있는 폴더에 etc/pid_list.txt가 생성되고 logs/log.log.%Y%m%d 가 생성됨

- 이름이 중복될 경우 아래와 같이 출력함
```
INFO:Process 'cfg_noaa_goes' already exists with PID: 4000438
INFO:Process 'cfg_ghn' already exists with PID: 4000439
```

- `global_scan_flag`
    - `null` : 각 테이블 설정파일에 있는 scan_flag대로 시작하도록 함
    - `true` : 각 테이블 설정파일에 있는 scan_flag를 무시하고, 모두 true로 시작
    - `false` : 각 테이블 설정파일에 있는 scan_flag를 무시하고, 모두 false로 시작

- 위 flag는 `single_scan.py`의 설정 키워드를 사용함
    - `--enable_scan` : 각 테이블 설정파일에 있는 scan_flag를 무시하고, 모두 true로 시작
    - `--disable_scan` : 각 테이블 설정파일에 있는 scan_flag를 무시하고, 모두 false로 시작
    - 위 2 키워드가 주어지지 않았을 때 : 각 테이블 설정파일에 있는 scan_flag대로 시작

- pid_list.txt를 활용한 기본적인 모니터링 프로그램이 존재함 (`python monitor_proc.py`)
```
python monitor_proc.py
Process with PID 4000438 exists. Status: sleeping. Name:cfg_noaa_goes.
Process with PID 4000439 exists. Status: sleeping. Name:cfg_ghn.
```

모든 프로세스를 죽일 때도 사용가능함
```
python monitor_proc.py -kill
```

- 아나콘다 가상환경 생성 및 활성화
```
conda env create -f db11.yaml
conda activate db11
```

- scan_single.py
    - 일반 실행
    ```
    python scan_single.py --db_cfg <DB 설정파일 경로> --sto_cfg <Storage 설정파일 경로> --tbl_cfg <메타데이터 설정파일 경로>
    ```

    - 백그라운드 실행 (`nohup`)
    ```
    nohup [명령어] 1> /dev/null 2>&1 &
    ```

    - 예시
    ```
    python scan_single.py --db_cfg ../config/cfg_db.json --sto_cfg ../config/cfg_storage.json --tbl_cfg ../config/metadata_table_config/cfg_noaa_goes.json
    ```

    ```
    nohup python scan_single.py --db_cfg ../config/cfg_db.json --sto_cfg ../config/cfg_storage.json --tbl_cfg ../config/metadata_table_config/cfg_noaa_goes.json 1> /dev/null 2>&1 &
    ```


## DB 설정파일

`cfg_db.json`
```json
{
    "database": {
        "url": {
            "drivername": "postgresql+psycopg2",
            "username": "<사용자명>",
            "password": "<비밀번호>",
            "host": "<호스트명>",
            "port": "<포트 번호>",
            "database": "<데이터베이스명>"
        },
        "engine": {
            "echo": false
        }
    }
}
```

- 설정파일에 들어가는 파라미터와 PostgreSQL의 [psql](https://www.postgresql.org/docs/current/app-psql.html)의 DB 접속 명령어에 사용되는 파라미터 사이의 관계는 아래와 같다.

```
> psql -U <사용자명> -h <호스트명> -p <포트 번호> -d <데이터베이스명>
Password for user <사용자명>: <비밀번호> 입력
```
- `engine`의 `echo`의 경우 log파일에 sqlalchemy의 상세한 DB 관련 로그를 보고 싶을때 `True`로 하면 되나, 관련 로그양이 굉장히 많아서 log파일 용량이 매우 빠르게 늘어나기 때문에 주의가 필요하다. 


## Storage 설정파일 (하드웨어 정보)

- `hardware` schema 아래에 `hardware_storage`라는 이름의 테이블을 만든다.

`cfg_storage.json`
```json
{
    "storage_info": [
        {
            "storage_id": "<스토리지 아이디>",
            "storage_name": "<스토리지 이름>",
            "volume_name": "<볼륨 이름>",
            "ip": "<스토리지 IP>",
            "hostname": "<스토리지 hostname>",
            "comment": "<설명>"
        },
        {
            "storage_id": "<스토리지 아이디>",
            "storage_name": "<스토리지 이름>",
            "volume_name": "<볼륨 이름>",
            "ip": "<스토리지 IP>",
            "hostname": "<스토리지 hostname>",
            "comment": "<설명>"
        }
    ]
}
```

- `storage_info` 파라미터의 array에 있는 dictionary 하나가 `hardware.hardware_storage` 테이블의 레코드(행) 하나가 되고, `storage_id`가 Primary Key가 된다.

## Metadata 설정파일 (데이터 저장경로)

- `metadata` schema 아래에 `table_name` 파라미터에 지정된 이름을 가진 테이블 1개를 만든다.
- `data` schema 아래에서는 `data_info`, `data_master`, `data_status` 3개의 테이블에 영향을 끼친다.
    - `data_info` 파라미터의 array에 있는 있는 dictionary 하나가 `data.data_info` 테이블의 레코드(행) 하나가 되고, `data_id`가 Primary Key가 된다.
    - `data.data_master`테이블에는 `data_id`를 Primary Key로 가지고 `data_group`을 값으로 가지는 레코드(행)들을 만든다.
    - `data.data_status`테이블에는 `data_status_id`=`data_id`_`storage_id`를 Primary Key로 가지고, 해당 데이터의 가장 오래된 시간 (start_time) 부터 가장 최근 시간 (end_time)까지의 정보를 기록한다.

- `scan_flag` 
최초 DB 생성시 `true`로 설정, `data_info` 리스트에 지정된 모든 `data_path` 아래에 있는 모든 파일을 스캔하면서 지정된 `file_format`과 맞는 파일정보를 DB에 업데이트함. `false`로 설정할 경우 해당과정을 하지 않고, DB에 있는 파일 정보를 이용하여

1. 저장된 file_path에 파일이 없다면 DB에 관련 행 삭제 
2. DB에 저장되어 있는 값이 file_format과 다르다면 삭제 
3. DB에 저장되어 있는 가장 나중의 modification time보다 더 나중에 만들어진/수정된 파일이 있으면 DB에 반영되는 작업만 함. 
 
17만개 파일 기준으로 `true`면 대략 8분, `false`면 대략 30초의 초기 실행시간(프로세스가 running에서 sleeping으로 상태가 바뀔때까지의 시간)이 걸림.

- `observer_flag`
지정된 `data_path`를 계속 지켜보면서 수정사항이 발생했을 시 DB에 반영하고 싶으면 `true`로 설정. 이럴경우 프로세스가 `sleeping`상태로 background에 존재하게 됨. 해당 `data_path`에 저장된 파일들이 전혀 업데이트 되고 있지 않아 background process가 필요없다면 `false`로 설정 

- `check_change_flag`
`scan_flag`가 `false`더라도, DB 테이블의 값들을 이용해서 수정/삭제된 파일들을 스캔하는 작업을 초기에 시행함. 만약 데이터가 지속적으로 업데이트 된다면 이것을 `true`로 설정하면, 전체 스캔보다는 빠르게 프로그램을 시작할 수 있음. 하지만 데이터가 더이상 업데이트 되지 않는 것이 확실할 때, 이 flag를 `false`로 설정하면 그 작업을 실행하지 않게됨.

- `scan_flag`, `observer_flag`, `check_change_flag`가 모두 false일 경우 파일 스캔 작업은 하지 않고 DB에 저장된 테이블의 값을 주어진 설정파일을 이용해서 update만 함.

- 데이터가 더이상 업데이트 되지 않는 경우 `observer_flag`, `check_change_flag`를 모두 `false`로 놓고 `scan_flag`만 `true`로 해서 스캔작업을 한 다음, 다음번에 실행할때는 `scan_flag`까지 `false`로 놓으면 스캔작업 없이 DB 테이블 정보 (파장, 기관 등)만 업데이트 가능함

- 데이터가 업데이트 되는 경우 초기 스캔시에는 반드시 `scan_flag`를 `true`로 해서 스캔작업을 한 다음, 다음번에 실행할때는 `scan_flag`를 `false`로 놓고 `check_change_flag`를 `true`로 놓아야 변경사항을 감지해낼 수 있음. 프로세스를 백그라운드에 띄워서 감시하게 하고 싶은 경우 `observer_flag`를 `true`로 놓으면 된다.

 `cfg_metadata_1.json`
```json
{
    "table_info": {
        "scan_flag": true,
        "observer_flag": true,
        "check_change_flag": true,
        "table_name": "<테이블 이름>",
        "data_info": [
            {
                "data_path": "<데이터가 저장되어 있는 폴더 경로>",
                "data_group": "<해당 폴더에 대응되는 데이터 그룹명>",
                "member_info": [
                    {
                        "data_id": "<데이터 아이디>",
                        "storage_id": "<스토리지 아이디>",
                        "file_format": [
                            "<DB에 정보를 업로드할 파일이름형식>",
                            "example_%Y%m%d.jpg",
                            "example_%Y%m%d_%H%M%S.fits"
                        ],
                        "institute": "<기관명>",
                        "observatory": "<관측기명>",
                        "satellite": "<위성명>",
                        "model": "<모델명>",
                        "telescope": "<관측기명>",
                        "wavelength": "",
                        "channel": "",
                        "instrument": "",
                        "file_server": 0
                    }
                ]
            },
            {
                "data_path": "/path/to/data",
                "data_group": "<데이터 그룹 이름>",
                "member_info": [
                    {
                        "data_id": "<데이터 아이디>",
                        "storage_id": "<스토리지 아이디>",
                        "file_format": [
                            "%Y%m%d_%H%M%S.jpg",
                            "%Y%m%d_%H%M%S.fits"
                        ],
                        "institute": "",
                        "observatory": "",
                        "satellite": "",
                        "model": "",
                        "telescope": "",
                        "wavelength": "",
                        "channel": "",
                        "instrument": "",
                        "file_server": 0
                    },
                    {
                        "data_id": "<데이터 아이디>",
                        "storage_id": "<스토리지 아이디>",
                        "file_format": [
                            "%Y%m%d_%H%M%S.jpg",
                            "%Y%m%d_%H%M%S.fits"
                        ],
                        "institute": "",
                        "observatory": "",
                        "satellite": "",
                        "model": "",
                        "telescope": "",
                        "wavelength": "",
                        "channel": "",
                        "instrument": "",
                        "file_server": 0
                    }
                ]
            }
        ]
    }
}
```

- 날짜와 시간관련 형식은 "Python `strftime()` and `strptime()` Format Codes" 를 따라 작성하면 된다.

`YYYYMMDD_hhmmss = %Y%m%d_%H%M%S`

|Directive|Meaning|Example|
|---|---|---|
|`%Y`|Year with century as a decimal number.|0001, 0002, …, 2013, 2014, …, 9998, 9999|
|`%m`|Month as a zero-padded decimal number.|01, 02, …, 12|
|`%d`|Day of the month as a zero-padded decimal number.|01, 02, …, 31|
|`%H`|Hour (24-hour clock) as a zero-padded decimal number.|00, 01, …, 23|
|`%M`|Minute as a zero-padded decimal number.|00, 01, …, 59|
|`%S`|Second as a zero-padded decimal number.|00, 01, …, 59|

더 자세한 사항은 아래 링크 참조.
https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes