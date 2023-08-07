'''
# 날짜 데이터 정의
- https://ellun.tistory.com/320
- numpy: datetime64
- datetime64
    - np.timedelta를 이용하여 날짜 계산 가능
    - np.datetime64('2005') == np.datetime64('2005-01-01') => True
- format을 object로 둬서 datetime.datetime 사용 가능

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


# NOTE: go to common funciton?
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

# column정보를 가지고 있는 structured array에만 사용 가능
def sort(data, standard, semi_standard = "", reversed=False):
    if(semi_standard == "" or semi_standard == None):
        data = np.sort(data, order=standard)
    else:
        data = np.sort(data, order=[standard, semi_standard])
    
    if(reversed == True):
        data = data[::-1]
    return data

# TODO: 객체의 구조를 보여줄 수 있는 함수
# TODO: datetime64를 통해 date핸들링 어느정도 할 수 있는지
class _GoesAscii():
    """
    Member variables
    ----------------
    test3
    
    Functions
    ---------
    test4()
    """
    def __init__(self, filepath, names, formats):
        #
        # init variable
        self.header = None
        self.data = None
        self.header_str = None
        self.filepath = filepath

        self._names = names
        self._formats = formats


        #
        # create header, data and header_str
        header_lines, data_lines = self._load_file(filepath)
        hd = self._parsing_header(header_lines)
        data = self._parsing_data(data_lines, names, formats)        
        header = self._add_info_to_header(hd, data)

        #
        # set basic member variable
        self.header = header
        self.data = data
        self.header_str = header_lines

    def __repr__(self):
        return "This is __repr__ test\n" + \
                "-------------------\n" + \
                "Observatory: {}\n" + \
                "Shape: {}\n" + \
                "Source: {}\n".format(self.header["Observatory"], self.columns, self.header["Source"])

    @property
    def size(self):
        return np.shape(self.data)
    
    @property
    def columns(self):
        return self.data.dtype.names

    def _add_info_to_header(self, header, data):
        """
        Parameters
        ----------
        header: dict
        
        Returns
        -------
        header: dict
        """

        """
        #
        # add info from header info
        interval = header["filename"].split(".txt")[0][-2:]
        time_itv, time_unit = int(interval[0]), interval[1]
        if(time_unit == "m"):
            time_itv *= 60
        header["time_interval"] = time_itv
        """

        #
        # goes common info
        header["Observatory"] = "Noaa"
        header["Object"] = "Sun"
        header["Src_url"] = "https://services.swpc.noaa.gov/json/goes/primary"
        header["Comment"] = ""
        header["History"] = ""
        header["Keycomments"] = {
                                "Location": "Longitude of satellite.",
                                }
        #
        # add info from data
        # NOTE: column명이 바뀌면 에러남 / 무슨 형태로 저장하지? (현재: np.datetime64)
        if("Date" in data.dtype.names):
            header["Obs_start_date"] = data["Date"][0]
            header["Obs_end_date"] = data["Date"][-1]
        return header

    # NOTE
    # - header_delimiters: goes에 맞게 하드 코딩?
    # - goes 말고도 다른 곳에서도 쓰일 가능성이 있을까?
    #    (+) header, data의 페어가 여러개라면?
    def _load_file(self, filepath):
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
            # NOTE: f.readlines(): contains "\n"
            for line in f.read().splitlines():
                if(line[0] in header_delimiters):
                    header_lines.append(line)
                    continue
                data_lines.append(line)
        return header_lines, data_lines

    # TODO: Label, Units -> dict형태로 보여주는 것이 좋은지 질문할 것
    def _parsing_header(self, header_lines):
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
        dict_delimiter = ":"
        
        header = {}

        notes = []
        labels = []
        units = []
        for i, line in enumerate(header_lines):
            # Remove header delimiters and both leading and trailing whitespace.
            if(any(dlmt == line[0] for dlmt in header_delimiters)):
                line = line[1:]
            line = line.strip()
            
            # Skip from column to end.
            if(i >= len(header_lines)-3):
                continue

            if(line == ""):
                continue

            # Put anything that is not in the key-value form in 'note'.
            if(dict_delimiter not in line):
                notes.append(line)
                continue

            key, value = line.split(dict_delimiter, 1)
            key = key.strip()
            value = value.strip()

            if(key == "Label"):
                labels.append(value)
            elif(key == "Units"):
                units.append(value)
            else:
                header[key] = value

        header["Note"] = notes
        header["Label"] = labels
        header["Units"] = units

        return header

    def _parsing_data(self, data_lines, names, formats):
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
            date = datetime(int(Y), int(m), int(d), int(H), int(M))
            # date = date_format.format(Y, m, d, H, M)


            data_tuple = (date,)
            for value in values:
                data_tuple += (value,)
            
            data.append(data_tuple)
        data = np.array(data, dtype={'names':names, 'formats':formats})

        return data
    
    '''
    # NOTE: 보류
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
    '''

    def plot(self):
        pass

class PartAscii(_GoesAscii):
    """
    Member variables
    ----------------
    test1
    
    Functions
    ---------
    test2()
    """
    def __init__(self, filepath):
        names = ("Date", "Satellite No", "P>1", "P>5", "P>10", "P>30", "P>50", "P>60", "P>100", "P>500", "E>2.0")
        # float 데이터 나타낼 수 있는게 이게 한계인가?
        formats = ("object", "i4", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8")
        # formats = ("datetime64[s]", "i4", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8")

        
        super().__init__(filepath, names, formats)