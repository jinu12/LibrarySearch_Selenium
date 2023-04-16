# 도서관 일반 검색 프로그램

이 프로그램은 PyQt5와 Selenium을 사용하여 도서관 웹사이트에서 일반 도서를 검색하는 프로그램입니다.

## 필요한 라이브러리

- PyQt5
- Selenium
- pandas

## 사용법

1. 크롬 드라이버를 설치하고 프로그램의 'driver = webdriver.Chrome()' 부분에 경로를 입력합니다.
2. 도서관 검색 웹사이트 주소를 'driver.get()' 부분에 입력합니다.
3. 검색 버튼의 XPath를 'search_button = driver.find_element_by_xpath()' 부분에 입력합니다.
4. 프로그램을 실행하고 일반 도서를 검색하고 싶은 키워드를 입력한 후 검색 버튼을 클릭합니다.

## 코드 구성

### 클래스

- LibrarySearchApp: 도서관 검색 프로그램의 메인 클래스입니다.

### 메서드

- `__init__`: 초기화 메서드로 객체 생성 시 실행됩니다.
- `initUI`: 사용자 인터페이스를 초기화하는 메서드입니다.
- `search_libraries`: 도서관 검색을 수행하는 메서드입니다.
- `stop_search`: 검색을 중지하는 메서드입니다.
- `quit_search`: 인터페이스를 종료하는 메서드입니다.

## 실행 방법

프로그램을 실행하려면 다음 명령을 사용합니다.

```bash
python main.py
