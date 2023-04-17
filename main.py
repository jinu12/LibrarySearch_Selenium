from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium import webdriver
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys
import pandas as pd
import time
import math


# 도서관 검색 프로그램의 메인 클래스
class SearchWorker(QObject):
    result_ready = pyqtSignal(str, pd.DataFrame)

    def __init__(self, search_keyword):
        super().__init__()
        self.search_keyword = search_keyword
        self.stop_search = False

    def quit_driver(self):
        if 'driver' in locals():
            self.driver.quit()

    def search_libraries(self):
        chrome_options = Options()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        try:
            self.driver.get("https://www.nl.go.kr/kolisnet/index.do")

            search_box = self.driver.find_element(by=By.XPATH, value="//*[@id='simpleKeyword1']")
            search_box.clear()

            search_box.send_keys(self.search_keyword) # 검색창에 입력된 텍스트를 검색어로 사용

            search_button = self.driver.find_element(by=By.XPATH, value="//*[@id='simpleSearchBtn']")
            search_button.click()
            time.sleep(1)

            view_all_buttons = self.driver.find_elements(
                by=By.XPATH, value='//*[@id="contents"]/div/div/div[1]/section[1]/a')

            total = self.driver.find_element(
                by=By.CSS_SELECTOR, value="section:nth-child(1) > div > p > span > span").text

            # 화폐 단위를 단위를 정수로 변경
            total = int(total.replace(',', ''))

            total_pages = math.ceil(total / 15)

            if len(view_all_buttons) > 0:
                view_all_buttons[0].click()
                time.sleep(1)

            result_list = []
            result_data = []

            # 현재 페이지
            real_page = 1

            # child_number 10보다 작으면 링크 넘버가 1 크면 링크 넘버가 3
            if total_pages > 10:
                child_number = 3
            else:
                child_number = 1

            while True:
                search_results = self.driver.find_elements(
                    by=By.XPATH, value="//*[@id='contents']/div/div/div[2]/section")
                for i in range(1, 16):
                    for result in search_results:
                        try:
                            title = result.find_element(
                                by=By.CSS_SELECTOR, value=f"li:nth-child({i}) > div > p > a").text
                            author_and_year = result.find_element(
                                by=By.CSS_SELECTOR, value=f"li:nth-child({i}) > span").text
                            library_info = result.find_element(
                                by=By.CSS_SELECTOR, value=f"li:nth-child({i}) > div > div.bookInfoList > p.own").text

                            result_list.append(title + "\n" + author_and_year + "\n" + library_info + "\n")
                            result_list.append("페이지 번호 : " + str(real_page) + "\n")
                            result_list.append("===========================================\n")

                            result_data.append({"Title": title, "Author and Publication": author_and_year,
                                                "Library Info": library_info, "Page Number": real_page})
                        except NoSuchElementException:
                            pass
                total = 0

                child_number += 1
                if real_page % 10 == 0:
                    next_page_buttons = self.driver.find_elements(
                        by=By.XPATH, value="//*[@id='contents']/div/div/div[2]/div/p/a[12]/img")
                    child_number = 3
                    # 웹 스크레이핑 작업을 중지하는지 확인
                    if self.stop_search:
                        break
                else:
                    next_page_buttons = self.driver.find_elements(
                        by=By.CSS_SELECTOR, value=f"div > p > a:nth-child({child_number})")

                # 웹 스크레이핑 작업을 중지하는지 확인
                if self.stop_search:
                    break

                # 페이지 끝나면 종료되는 부분
                # 현재 페이지하고 전체페이지가 같지 않을 경우에만 다음 화면 이동
                if total_pages != real_page:
                    if len(next_page_buttons) > 0:
                        next_page_buttons[0].click()
                        time.sleep(1)
                        real_page += 1
                    else:
                        break
                else:
                    break

            result_text = "".join(result_list)

            df = pd.DataFrame(result_data)

            self.result_ready.emit(result_text, df)

            self.quit_driver()

        except Exception as e:
            self.result_ready.emit("검색 도중 오류가 발생했습니다.\n" + str(e), pd.DataFrame())
        self.quit_driver()


# 도서관 검색 프로그램의 크롤링 기능을 하는 클래스
class LibrarySearchApp(QWidget):

    def __init__(self):
        super().__init__()
        self.search_worker = None
        self.search_thread = None
        self.stop_search = False
        self.timer = None
        self.driver = None
        self.result_text = QTextEdit()
        self.search_button = QPushButton("검색")
        self.stop_button = QPushButton("중지")
        self.quit_button = QPushButton("종료")
        self.location_input = QLineEdit()
        self.location_label = QLabel("일반 도서:")
        self.initUI()

    def initUI(self):  # UI설정
        layout = QVBoxLayout()

        layout.addWidget(self.location_label)

        layout.addWidget(self.location_input)

        layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.start_search)

        layout.addWidget(self.stop_button)
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_searching)

        layout.addWidget(self.quit_button)
        self.quit_button.clicked.connect(self.quit_app)

        layout.addWidget(self.result_text)

        self.setLayout(layout)
        self.setWindowTitle("도서관 일반 검색 프로그램")
        self.show()

    def start_search(self):  # 쓰레드 시작 함수
        search_keyword = self.location_input.text()
        self.search_worker = SearchWorker(search_keyword)

        self.search_thread = QThread()
        self.search_worker.moveToThread(self.search_thread)

        self.search_thread.started.connect(self.search_worker.search_libraries)
        self.search_worker.result_ready.connect(self.update_results)
        self.search_thread.finished.connect(self.search_worker.deleteLater)
        self.search_thread.finished.connect(self.search_thread.deleteLater)

        self.search_thread.start()

        self.search_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_search_and_cleanup(self):  # 중지 버튼 쓰레드 종료 함수
        self.search_worker.stop_search = True
        self.search_thread.quit()
        self.search_thread.wait()

    def stop_searching(self):  # 중지 버튼 클릭 이벤트 처리 함수
        self.stop_search_and_cleanup()
        self.search_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def quit_app(self): # 종료 버튼 클릭 이벤트 처리 함수
        if self.search_thread is not None:
            self.stop_search_and_cleanup()
        time.sleep(2)
        QApplication.instance().quit()
        self.quit_driver()

    def update_results(self, result_text, result_data):  # 결과 엑셀 저장 함수
        self.result_text.setPlainText(result_text)

        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Excel Files (*.xlsx);;All Files (*)")

        if file_name:
            if not file_name.endswith(".xlsx"):
                file_name += ".xlsx"
            result_data.to_excel(file_name, index=False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    library_search_app = LibrarySearchApp()
    sys.exit(app.exec_())

