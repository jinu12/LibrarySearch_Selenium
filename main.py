import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from geopy.geocoders import Nominatim
from selenium import webdriver
import time
import math


class LibrarySearchApp(QWidget):
    def __init__(self):
        super().__init__()

        self.result_text = QTextEdit()
        self.search_button = QPushButton("검색")
        self.location_input = QLineEdit()
        self.location_label = QLabel("일반 도서:")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(self.location_label)

        layout.addWidget(self.location_input)

        layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.search_libraries)

        layout.addWidget(self.result_text)

        self.setLayout(layout)
        self.setWindowTitle("도서관 일반 검색 프로그램")
        self.show()

    def search_libraries(self):
        location = self.location_input.text()
        geolocator = Nominatim(user_agent="library_search_app")
        current_location = geolocator.geocode(location)

        # Selenium을 사용하여 웹 스크레이핑을 수행하는 부분
        try:
            # 여기에 자신의 크롬 드라이버 경로를 입력하세요.
            driver = webdriver.Chrome('./driver/chromedriver')
            # 여기에 도서관 검색 웹사이트 주소를 입력하세요.
            driver.get("https://www.nl.go.kr/kolisnet/index.do")

            search_box = driver.find_element_by_xpath(
                "//*[@id='simpleKeyword1']")
            search_box.clear()

            search_keyword = self.location_input.text()  # 검색창에 입력된 텍스트를 검색어로 사용
            search_box.send_keys(search_keyword)

            # 검색 버튼의 XPath로 변경하세요.
            search_button = driver.find_element_by_xpath(
                "//*[@id='simpleSearchBtn']")
            search_button.click()
            time.sleep(1)  # 검색 결과 로딩 대기 (필요한 경우 대기 시간을 늘리세요)

            # # 검색 결과를 가져와 출력합니다. 결과 요소의 XPath를 변경하세요.
            # search_results = driver.find_elements_by_xpath("//*[@id='contents']/div/div/div[1]/section[1]")

            # 모두 보기 버튼이 있는지 확인하고 클릭합니다.
            view_all_buttons = driver.find_elements_by_xpath(
                '//*[@id="contents"]/div/div/div[1]/section[1]/a')
            if len(view_all_buttons) > 0:
                view_all_buttons[0].click()
                time.sleep(1)  # 모든 결과 로딩 대기 (필요한 경우 대기 시간을 늘리세요)
                # search_results = driver.find_elements_by_xpath("//*[@id='contents']/div/div/div[2]/section")

            result_list = []

            current_page = 1
            real_page = 1
            while True:

                search_results = driver.find_elements_by_xpath(
                    "//*[@id='contents']/div/div/div[2]/section")  # 모두 보기 페이지에서의 XPath를 사용하세요.

                for result in search_results:
                    result_list.append(result.text + "\n")
                    result_list.append("페이지 번호 : " + str(real_page) + "\n")
                    result_list.append(
                        "===========================================\n")

                # # 다음 페이지 번호를 계산하고, 다음 페이지 버튼을 찾습니다
                next_page_number = current_page + 1
                print(next_page_number)
                total_elements = driver.find_elements_by_xpath(
                    "//*[@id='contents']/div/div/div[2]/section/div/p/span/span")
                if len(total_elements) > 0:
                    total_text = total_elements[0].text
                    total = int(total_text)
                else:
                    total = 0

                if current_page % 10 == 0:  # 페이지 번호가 10의 배수인 경우
                    next_page_buttons = driver.find_elements_by_xpath(
                        "//*[@id='contents']/div/div/div[2]/div/p/a[12]/img")  # '다음' 버튼의 XPath를 사용하세요.
                    if math.ceil(total / 15) != real_page:
                        print("total" + str(total / 15))
                        print("real" + str(real_page))
                        print(math.ceil(15))
                        next_page_number = 1
                else:
                    next_page_buttons = driver.find_elements_by_xpath(
                        f"//*[@id='contents']/div/div/div[2]/div/p/a[{next_page_number+1}]")

                    # 다음 페이지 버튼이 있으면 클릭하고, 없으면 종료합니다.
                if len(next_page_buttons) > 0:
                    # 다음 페이지 번호를 계산하고, 다음 페이지 버튼을 찾습니다
                    next_page_buttons[0].click()
                    time.sleep(1)  # 다음 페이지 로딩 대기 (필요한 경우 대기 시간을 늘리세요)
                    current_page = next_page_number

                else:
                    break
                # 현재 페이지에서 검색 결과를 가져와 출력합니다. 결과 요소의 XPath를 변경하세요.
                real_page += 1

            # 마지막 두 개의 요소를 제거합니다.
            if len(result_list) > 1:
                for i in range(0, 6):
                    result_list.pop()
                    print(i)
            print(len(result_list))

            result_text = "".join(result_list)
            self.result_text.setPlainText(result_text)
            driver.quit()

        except Exception as e:
            self.result_text.setPlainText("검색 도중 오류가 발생했습니다.\n" + str(e))
            if 'driver' in locals():
                driver.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    library_search_app = LibrarySearchApp()
    sys.exit(app.exec_())
