# 우주환경 파이프라인 DB 모듈

## 실행법

```
> python /path/to/scan_multi.py --cfg /path/to/multi_cfg.json
```

`multi_cfg_.json`
```json
{
    "cfg_db": "/path/to/cfg_db.json",
    "cfg_storage": "/path/to/cfg_storage.json",
    "cfg_metadata": [
        "/path/to/cfg_metadata_1.json",
        "/path/to/cfg_metadata_2.json"
    ]
}
```

### 참고사항
- 위의 명령어를 최초 실행시 데이터베이스에 `data`, `hardware`, `metadata` schema를 생성함

- Metadata 설정파일의 이름을 기초로 프로세스 이름을 생성하고, pid 목록을 pid_list.txt파일로 저장함 (`top`로 확인 가능)
```
INFO:Process 'cfg_noaa_goes' started with PID: 4000438
INFO:Process 'cfg_ghn' started with PID: 4000439
```

- 모든 로그는 기본적으로 log.log 파일에 저장함

- 위의 pid_list.txt와 log.log는 python을 실행시킨 터미널이 위치한 디렉토리 (pwd)에 생성됨 

- 이름이 중복될 경우 아래와 같이 출력함
```
INFO:Process 'cfg_noaa_goes' already exists with PID: 4000438
INFO:Process 'cfg_ghn' already exists with PID: 4000439
```

- pid_list.txt를 활요한 기본적인 모니터링 프로그램이 존재함 (`python monitor_proc.py`)
```
> python monitor_proc.py
Process with PID 4000438 exists. Status: sleeping. Name:cfg_noaa_goes.
Process with PID 4000439 exists. Status: sleeping. Name:cfg_ghn.
```

모든 프로세스를 죽일 때도 사용가능함
```
> python monitor_proc.py -kill True
```

- 아나콘다 가상환경 생성 및 활성화
```
> conda env create -f db11.yaml
> conda activate db11
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

 `cfg_metadata_1.json`
```json
{
    "table_info": {
        "scan_flag": true,
        "observer_flag": true,
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