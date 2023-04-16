from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog
from selenium.common.exceptions import NoSuchElementException
from PyQt5.QtCore import QCoreApplication, QThread  # 추가
from selenium import webdriver
import sys
import pandas as pd
import time
import math


class WebScraperThread(QThread):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.stop_requested = False  # 추가된 부분

    def run(self):
        self.app.search_libraries()

    def stop(self):
        self.stop_requested = True
        if self.app.driver:  # 추가된 부분
            self.app.driver.quit()
            self.app.driver = None


class LibrarySearchApp(QWidget):
    def __init__(self):
        super().__init__()
        self.web_scraper_thread = None  # 추가
        self.result_text = QTextEdit()
        self.search_button = QPushButton("검색")
        self.stop_button = QPushButton("중지")
        self.quit_button = QPushButton("종료")
        self.location_input = QLineEdit()
        self.location_label = QLabel("일반 도서:")
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        layout.addWidget(self.location_label)

        layout.addWidget(self.location_input)

        layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.start_search)

        layout.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop_search)

        layout.addWidget(self.quit_button)
        self.quit_button.clicked.connect(self.quit_app)

        layout.addWidget(self.result_text)

        self.setLayout(layout)
        self.setWindowTitle("도서관 일반 검색 프로그램")
        self.show()

    def search_libraries(self):
        # 여기에 자신의 크롬 드라이버 경로를 입력하세요.
        self.driver = webdriver.Chrome('./driver/chromedriver')
        # Selenium을 사용하여 웹 스크레이핑을 수행하는 부분

        try:
            self.driver.get("https://www.nl.go.kr/kolisnet/index.do")

            search_box = self.driver.find_element_by_xpath("//*[@id='simpleKeyword1']")
            search_box.clear()

            search_keyword = self.location_input.text()  # 검색창에 입력된 텍스트를 검색어로 사용
            search_box.send_keys(search_keyword)

            search_button = self.driver.find_element_by_xpath("//*[@id='simpleSearchBtn']")  # 검색 버튼의 XPath로 변경하세요.
            search_button.click()
            time.sleep(1)  # 검색 결과 로딩 대기 (필요한 경우 대기 시간을 늘리세요)

            view_all_buttons = self.driver.find_elements_by_xpath('//*[@id="contents"]/div/div/div[1]/section[1]/a')
            if len(view_all_buttons) > 0:
                view_all_buttons[0].click()
                time.sleep(1)

            result_list = []
            result_data = []

            current_page = 1
            real_page = 1

            while True:

                # 웹 스크레이핑 작업을 중지하는지 확인
                if self.web_scraper_thread is not None and self.web_scraper_thread.stop_requested:
                    break

                search_results = self.driver.find_elements_by_xpath(
                    "//*[@id='contents']/div/div/div[2]/section")
                for i in range(1, 16):
                    for result in search_results:
                        try:
                            title = result.find_element_by_css_selector(
                                f"li:nth-child({i}) > div > p > a").text
                            author_and_year = result.find_element_by_css_selector(
                                f"li:nth-child({i}) > span").text
                            library_info = result.find_element_by_css_selector(
                                f"li:nth-child({i}) > div > div > p.own").text

                            result_list.append(title + "\n" + author_and_year + "\n" + library_info + "\n")
                            result_list.append("페이지 번호 : " + str(real_page) + "\n")
                            result_list.append("===========================================\n")

                            # Add the result data to the result_data list
                            result_data.append({"Title": title, "Author and Publication": author_and_year,
                                                "Library Info": library_info, "Page Number": real_page})
                        except NoSuchElementException:
                            pass

                next_page_number = current_page + 1
                total_elements = self.driver.find_elements_by_xpath(
                    "//*[@id='contents']/div/div/div[2]/section/div/p/span/span")
                if len(total_elements) > 0:
                    total_text = total_elements[0].text
                    total = int(total_text)
                else:
                    total = 0
                if current_page % 10 == 0:
                    next_page_buttons = self.driver.find_elements_by_xpath(
                        "//*[@id='contents']/div/div/div[2]/div/p/a[12]/img")
                    if math.ceil(total / 15) != real_page:
                        next_page_number = 1
                else:
                    next_page_buttons = self.driver.find_elements_by_xpath(
                        f"//*[@id='contents']/div/div/div[2]/div/p/a[{next_page_number+1}]")

                # 페이지 끝나면 종료되는 부분
                if math.ceil(total / 15) != real_page:
                    next_page_buttons[0].click()
                    time.sleep(1)
                    current_page = next_page_number

                else:
                    break

                real_page += 1

            if len(result_list) > 1:
                for i in range(0, 6):
                    result_list.pop()

            result_text = "".join(result_list)
            self.result_text.setPlainText(result_text)

            df = pd.DataFrame(result_data)

            file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx);;All Files (*)")

            if file_name:
                if not file_name.endswith(".xlsx"):
                    file_name += ".xlsx"
                df.to_excel(file_name, index=False)

            if 'self.driver' in locals():
                self.driver.quit()

        except Exception as e:
            self.result_text.setPlainText("검색 도중 오류가 발생했습니다.\n" + str(e))
        if 'self.driver' in locals():
            self.driver.quit()

    def start_search(self):
        self.web_scraper_thread = WebScraperThread(self)
        self.web_scraper_thread.start()

    def quit_app(self):  # 종료 버튼 클릭 이벤트 처리 함수
        self.stop_search()
        QCoreApplication.instance().quit()

    def stop_search(self):
        if self.driver:
            self.driver.quit()
            self.driver = None
        if self.web_scraper_thread is not None:  # 추가
            self.web_scraper_thread.terminate()
            self.web_scraper_thread = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    library_search_app = LibrarySearchApp()
    sys.exit(app.exec_())