import sys
import datetime as dt
from tqdm import tqdm
from data_fetcher import DataFetcher
from data_analyzer import DataAnalyzer
from utils import calculate_values_count, calculate_page_count, get_area_name
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

class AnalyzerThread(QThread):
    analysis_done = pyqtSignal(object)  # 분석 완료 시그널, 분석기 객체 전달
    
    def __init__(self, text_browsers):
        super().__init__()
        self.text_browsers = text_browsers
        self.analyzer = None

    def run(self):
        total_area = [
            "0011", "0012", "0013", "0021", "0022", "0023",
            "0031", "0032", "0033", "0041", "0042", "0043",
            "0051", "0052", "0053", "0061", "0062", "0063",
            "0071", "0072", "0073", "0081", "0082", "0083",
            "0091", "0092", "0093", "0101", "0102", "0103",
            "0111", "0112", "0113", "0121", "0122", "0123",
            "0131", "0132", "0133", "0141", "0142", "0143",
            "0151", "0152", "0153", "0161", "0162", "0163",
            "0171", "0172", "0173", "0181", "0182", "0183",
            "0191", "0192", "0193", "0201", "0202", "0203",
            "0211", "0212", "0213", "0221", "0222", "0223",
            "0231", "0232", "0233", "0241", "0242", "0243",
            "0251", "0252", "0253", "0261", "0262", "0263",
            "0271", "0272", "0273", "0281", "0282", "0283",
            "0291", "0292", "0293", "0301", "0302", "0303",
            "0311", "0312", "0313", "0321", "0322", "0323",
            "0331", "0332", "0333", "0341", "0342", "0343",
            "0351", "0352", "0353", "0361", "0362", "0363",
            "0371", "0372", "0373", "0381", "0382", "0383",
            "0391", "0392", "0393", "0401", "0402", "0403",
            "0411", "0412", "0413", "0421", "0422", "0423",
            "0431", "0432", "0433", "0441", "0442", "0443",
            "0451", "0452", "0453"
        ]

        values_cnt = calculate_values_count()  
        page_count = calculate_page_count()
        start = dt.datetime.now().strftime('%Y-%m-%d')
        end = dt.datetime.now().strftime('%Y-%m-%d')

        self.analyzer = DataAnalyzer(self.text_browsers)
        self.analyzer.set_values_count(values_cnt)
        
        for area in tqdm(total_area):
            area_name = get_area_name(area)
            data = DataFetcher.fetch_data_for_area(area, start, end, page_count)
            self.analyzer.analyze_data(data, area_name)
        
        self.analysis_done.emit(self.analyzer)

def display_results(analyzer):
    print("--완료--")
    print("과거 자료 없는 관측지점 : ", analyzer.final_count_data_zero)
    print("현재시간 데이터수 : ", analyzer.values_cnt)  
    print("현재시간 데이터수보다 -10 적은 데이터값")
    print(analyzer.final_count_data_name)
    print("제로값을 확인하세요 : ", analyzer.final_zero_state)
    print("통합센서에 문제 : ", analyzer.final_weather_state)
    print("휘발성유기화합물 값이 더 큽니다. ")
    print(analyzer.final_under_date)

def start_analysis(window):
    text_browsers = [window.textBrowser_1, window.textBrowser_2, window.textBrowser_3, window.textBrowser_4, window.textBrowser_5]
    analyzer_thread = AnalyzerThread(text_browsers)
    analyzer_thread.analysis_done.connect(display_results)
    analyzer_thread.start()
    return analyzer_thread

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = uic.loadUi("main.ui")
    window.show()

    analyzer_thread = start_analysis(window)  # 분석 스레드 시작

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
