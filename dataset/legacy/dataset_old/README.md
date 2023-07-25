# Dataset

## 조사

### Python Name Convention

- Document: <https://www.python.org/dev/peps/pep-0008/>
- layout

  - 들여쓰기 공백: 4칸
  - 코드 한줄: 최대 79칸
  - comment, doc string 한줄: 최대 72칸

- 함수, 변수
  - 일반 함수, 변수: lower case + underbar
  - 상수: upper case + underbar
  - 기본 keyword와의 충돌 방지: var + undervar (ex: list_)

- class
  - 클래스명: CamelCase
  - 내부적으로 사용되는 변수: underbar + var (ex:_test)

- 비교 연산자
  - None: is, is not만 사용
  - boolean: '=='으로 비교하지 말 것

- try, except
  - try: 필요한 것만 최소화
  - except: 예외 명시

### Python Codetags

- Document: <https://www.python.org/dev/peps/pep-0350/>

### 날짜 데이터 정의 (numpy, pandas python std)

- 참고: <https://ellun.tistory.com/320>
- datetime64 (numpy)
  - `np.timedelta`를 이용하여 날짜 계산 가능
  - 날짜 중 일부 검사 가능

    ``` python
    >> np.datetime64('2005') == np.datetime64('2005-01-01')
    True
    ```

- Numpy Structued array
  - formats(type)을 *object*로 설정하여 데이터 값으로 `datetime.datetime` 사용 가능
