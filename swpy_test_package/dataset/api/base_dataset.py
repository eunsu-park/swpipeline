from abc import ABC, abstractmethod


class BaseDataset(ABC):
    """
    데이터 셋 기본 추상 클래스
    - 생성자와 필수 구현 5가지 추상 메소드 정의
    """
    def __init__(self, file_):
        self.file_ = file_
        self.data = None
        self.header = None
        self.all = None

    @abstractmethod
    def parsing(self):
        pass

    @abstractmethod
    def parsing_header(self):
        pass

    @abstractmethod
    def parsing_data(self):
        pass

    @abstractmethod
    def parsing_all(self):
        pass

    @abstractmethod
    def plot(self):
        pass