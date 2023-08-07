'''
# 날짜 데이터 정의
- https://ellun.tistory.com/320
- numpy: datetime64

# python name convention
- https://www.python.org/dev/peps/pep-0008/
- layout
    - 들여쓰기 공백: 4칸
    - 코드 한줄: 최대 79칸
    - comment, doc string 한줄: 최대 72칸
- 함수, 변수
    - 일반 함수, 변수: lower case + underbar
    - 상수: upper case + underbar
    - 기본 keyword와의 충돌 방지: list_
- class
    - 클래스명: CamelCase
    - 내부적으로 사용되는 변수: _var
- 비교 연산자
    - None: is, is not만 사용
    - boolean: '=='으로 비교하지 말 것
- try, except
    - try: 필요한 것만 최소화
    - except: 예외 명시
'''
from dateutil.parser import parse
import numpy as np
from datetime import datetime

#NOTE: 함수를 open()라고 명명하니 parsing_file()안의 open에서 오류가 남. 덮어씌워진것같음.. 
def read(filepath):
    """
    Parameters
    ----------
    filepath: str
        filepath to read
    
    Returns
    -------
    goes: GoesAscii object
    """
    ############
    names = ("date", "no", "P>1", "P>5", "P>10", "P>30", "P>50", "P>60", "P>100", "P>500", "E>2.0")
    # float 데이터 나타낼 수 있는게 이게 한계인가?
    formats = ("datetime64[s]", "i4", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8")
    ############

    header_lines, data_lines = parsing_file(filepath)
    hd = parsing_header(header_lines)
    # dt = parsing_data(data_lines)
    data = parsing_data(data_lines, names, formats)
    
    header = add_info_to_header(hd)
    # data = create_data(dt, names, formats)

    # add obs_start_date, obs_end_date to header
    # header["obs_start_date"] = data["date"][0]
    # header["obs_end_date"] = data["date"][-1]
    hd = add_info_to_header_from_data(hd, data)

    goes = GoesAscii(header, data, header_lines, filepath)
    return goes

# NOTE
# - naming: get_lines_of_header_and_data vs parsing file...?
# - header_delimiters: goes에 맞게 하드 코딩?
# - goes 말고도 다른 곳에서도 쓰일 가능성이 있을까?
#    (+) header, data의 페어가 여러개라면?
# - f.readlines(): contains "\n"
def parsing_file(filepath):
    """
    Parameters
    ----------
    filepath: str
        filepath to read
    
    Returns
    -------
    header_lines: list
        lines of header
    data_lines: list
        lines of data
    """
    header_delimiters = ["#", ":"]
    header_lines = []
    data_lines = []

    with open(filepath, "r") as f:
        for line in f.read().splitlines():
            if(line[0] in header_delimiters):
                header_lines.append(line)
                continue
            data_lines.append(line)
    return header_lines, data_lines

# NOTE
# - columens에 대해서도 정보를 적는게 좋을까? 적을 때에는 변환한 값으로?
#   (ex- 'YR MO DA HHMM' -> 'date')
#    -> 우선 note에 넣는 걸로 -> column은 나중에 함수로 보여주면되지
# - satellite number의 약어..?
#   -> 지금은 그냥 no로 설정
# - 여기서 key 변환한 이름을 리턴하는게 좋을까?
#   (ex- 'source' -> 'instrument', 'data_list' -> 'filename' ...)
# - instrument = satellite = 'goes 16'?
# - title도 그냥 note에 넣어버릴까 / key value에 해당하지 않는 것은 모두 note에 넣을까?(columns도)
# - 완전 goes데이터 맞춤
# - 'Created' string or date 형식 변환?
def parsing_header(header_lines):
    """
    Parameters
    ----------
    header_lines: list
        lines of header
    
    Returns
    -------
    header: dict
    """
    header_delimiters=["#", ":"]
    value_delimiter = ": "
    
    header = {}

    notes = []
    labels = []
    units = []
    for i, line in enumerate(header_lines):
        # Remove header delimiters and both leading and trailing whitespace.
        if(any(dlmt == line[0] for dlmt in header_delimiters)):
            line = line[1:]
        line = line.strip()
        
        if(line.strip() == ""):
            continue

        if(value_delimiter not in line):
            notes.append(line)
            continue
        
        key, value = line.split(value_delimiter)
        if(key == "Data_list"):
            header["filename"] = value
        elif(key == "Created"):
            header["date"] = value
        elif(key == "Label"):
            labels.append(value)
        elif(key == "Units"):
            units.append(value)
        elif(key == "Source"):
            header["instrument"] = value
        elif(key == "Location"):
            header["location"] = value
        elif(key == "Missing data"):
            header["error value"] = value

    header["note"] = notes
    header["label"] = labels
    header["unit"] = units

    return header



'''
# try1: 함수에서  names, format 하드코딩
def parsing_data(data_lines):
    """
    return data(np.ndarray)
    """
    names = ("date", "no", "P>1", "P>5", "P>10", "P>30", "P>50", "P>60", "P>100", "P>500", "E>2.0")
    # float 데이터 나타낼 수 있는게 이게 한계인가?
    formats = ("datetime64[s]", "i4", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8")
    date_format = "{0}-{1}-{2}T{3}:{4}"

    data_list = []
    for line in data_lines:
        if(line == ""):
            continue
        
        values = line.split()
        Y, m, d, HM = values.pop(0), values.pop(0), values.pop(0), values.pop(0)
        H, M = HM[:2], HM[2:]
        date = date_format.format(Y, m, d, H, M)

        data_tuple = (date,)
        for value in values:
            data_tuple += (value,)
        
        data_list.append(data_tuple)

    data = np.array(data_list, dtype={'names':names, 'formats':formats})
    return data

##### run #####
header, data = parsing_file("20210316_Gp_part_5m.txt")
print(parsing_data(data))

'''


'''
# try2: names, format 설정하는 곳 함수로 분리
def parsing_data(data_lines):
    """
    Parameters
    ----------
    data_lines: list
        lines of data

    Returns
    -------
    data: list
        list of data sets in the form of tuple
    """
    data = []
    date_format = "{0}-{1}-{2}T{3}:{4}"

    for line in data_lines:
        if(line.strip == ""):
            continue
        
        values = line.split()
        Y, m, d, HM = values.pop(0), values.pop(0), values.pop(0), values.pop(0)
        H, M = HM[:2], HM[2:]
        date = date_format.format(Y, m, d, H, M)

        data_tuple = (date,)
        for value in values:
            data_tuple += (value,)
        
        data.append(data_tuple)

    return data

def create_data(data, names, formats):
    """
    Parameters
    ----------
    data: list
        list of data sets in the form of tuple
    names: tuple
        data columnes
    formats: tuple
        data type for each data column
    
    Returns
    -------
    data: np.ndarray
    """
    data = np.array(data, dtype={'names':names, 'formats':formats})
    
    return data
'''


def parsing_data(data_lines, names, formats):
    """
    Parameters
    ----------
    data_lines: list
        lines of data
    names: tuple
        data columnes
    formats: tuple
        data type for each data column

    Returns
    -------
    data: list
        data: np.ndarray
    """
    data = []
    date_format = "{0}-{1}-{2}T{3}:{4}"

    for line in data_lines:
        if(line.strip == ""):
            continue
        
        values = line.split()
        Y, m, d, HM = values.pop(0), values.pop(0), values.pop(0), values.pop(0)
        H, M = HM[:2], HM[2:]
        date = date_format.format(Y, m, d, H, M)

        data_tuple = (date,)
        for value in values:
            data_tuple += (value,)
        
        data.append(data_tuple)

    data = np.array(data, dtype={'names':names, 'formats':formats})

    return data


# NOTE
# - obs_start_date, obs_end_date -> 데이터에서 추출한 값은 여기서 추가 못해주겠는데..?
def add_info_to_header(header):
    """
    Parameters
    ----------
    header: dict
    
    Returns
    -------
    header: dict
    """
    # from header info
    header["satellite"] = header["instrument"] ##???
    
    interval = header["filename"].split(".txt")[0][-2:]
    time_itv, time_unit = int(interval[0]), interval[1]
    if(time_unit == "m"):
        time_itv *= 60
    header["time_interval"] = time_itv

    # goes common info
    header["observatory"] = "noaa"
    header["object"] = "Sun"
    header["time_std"] = "utc"
    header["src_url"] = "https://services.swpc.noaa.gov/json/goes/primary"
    header["comment"] = ""
    header["history"] = ""
    header["keycomments"] = {
                            "location": "Longitude of satellite.",
                            "time_interval": "The interval at which data is recorded. Time unit is second."
                            }
    return header


def add_info_to_header_from_data(header, data):
    """
    Parameters
    ----------
    header: dict
    data: np.ndarray
    
    Returns
    -------
    header: dict
    """
    header["obs_start_date"] = data["date"][0]
    header["obs_end_date"] = data["date"][-1]
    return header

def convert_key_letter_case(dict_obj, letter_case = "u"):
    """
    Parameters
    ----------
    dict_obj: dict object
    letter_case: str
        'u'(upper) or 'l'(lower)
    Returns
    -------
    dict_obj: dict_obj
    """
    
    import copy

    dict_obj = copy.deepcopy(dict_obj)
    # dict_obj = self.dict_obj
    if(letter_case == "u"):
        dict_obj = {k.upper(): v for k, v in dict_obj.items()}
    elif(letter_case == "l"):
        dict_obj = {k.lower(): v for k, v in dict_obj.items()}
    
    return dict_obj


class GoesAscii():
    def __init__(self, header, data, header_str, filepath):
        self.header = header
        self.data = data
        self.header_str = header_str
        self.filepath = filepath

    @property
    def size(self):
        return np.shape(self.data)
    
    @property
    def columns(self):
        return self.data.dtype.names

    def convert_object_to_datetime(self, obj):
        """
        Parameters
        ----------
        obj: np.datetime64, str
        
        Returns
        -------
        result: datetime.datetime
        """
        result = None
        if(isinstance(obj, np.datetime64)):
            ts = (obj - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's') 
            result = datetime.utcfromtimestamp(ts)
        elif(isinstance(obj, str)):
            try:
                result = datetime.strptime(obj, "%Y-%m-%d %H:%M UTC")
            except:
                try:
                    result = parse(obj)
                except:
                    result = None
        return result


    def plot(self):
        pass

class PartAscii(GoesAscii):
    def __init__(self):
        super().__init__()
        names = ("date", "no", "P>1", "P>5", "P>10", "P>30", "P>50", "P>60", "P>100", "P>500", "E>2.0")
        # float 데이터 나타낼 수 있는게 이게 한계인가?
        formats = ("datetime64[s]", "i4", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8")
