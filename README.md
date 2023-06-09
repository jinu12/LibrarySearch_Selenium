# 도서관 일반 검색 프로그램

이 프로그램은 PyQt5와 Selenium을 사용하여 도서관 웹사이트에서 일반 도서를 검색하는 프로그램입니다.

## 필요한 라이브러리

- PyQt5
- Selenium
- Pandas
- webdriver_manger

## 사용법

1. 크롬 드라이버를 설치하고 프로그램의 'driver = webdriver.Chrome()' 부분에 경로를 입력합니다.
2. 도서관 검색 웹사이트 주소를 'driver.get()' 부분에 입력합니다.
3. 검색 버튼의 XPath를 'search_button = driver.find_element_by_xpath()' 부분에 입력합니다.
4. 프로그램을 실행하고 일반 도서를 검색하고 싶은 키워드를 입력한 후 검색 버튼을 클릭합니다.

## 주요기능
### 검색
- 검색창에 입력한 키워드로 일반도서 검색 결과를 가져옵니다.
- 검색 결과는 텍스트창에 표시됩니다.
- 검색 도중 오류가 발생하면, 텍스트창에 오류 내용이 표시됩니다.
### 검색중지
- 검색 중지 버튼을 클릭하여 검색을 중지할 수 있습니다.
### 저장
- 저장 버튼을 클릭하여 검색 결과를 엑셀 파일로 저장할 수 있습니다.
### 종료
- 검색 중지 버튼을 모든 작업을 종료 할 수 있습니다.


## 코드 구성

### 클래스

- LibrarySearchApp: 도서관 검색 프로그램의 메인 클래스입니다.

- SearchWorker : 도서관 검색 프로그램의 크롤링 기능을 하는 클래스입니다.

### 메서드

- `__init__`: 초기화 메서드로 객체 생성 시 실행됩니다.
- `initUI`: 사용자 인터페이스를 초기화하는 메서드입니다.
- `search_libraries`: 도서관 검색을 수행하는 메서드입니다.
- `stop_search`: 검색을 중지하는 메서드입니다.

## 실행 방법

프로그램을 실행하려면 다음 명령을 사용합니다.

```bash
python main.py
