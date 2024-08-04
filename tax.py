import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import rc
from matplotlib import font_manager, rcParams

# 영어 폰트 설정 (matplotlib)
rc('font', family='Arial')

# 한글 폰트 설정 (윈도우의 경우)
import matplotlib.pyplot as plt
plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

# CSV 파일 읽기
file_path = 'incomeoutcome2.csv'
data = pd.read_csv(file_path)

# 특정 HS 코드에 대해 거래한 국가들을 정렬하는 함수
def sort_by_hs_code(hs_code):
    # HS 코드로 필터링하고, 수출 중량과 수입 중량이 0이 아닌 데이터만 선택
    filtered_data = data[(data['HS코드'] == hs_code) & (data['수출 중량'] > 0) & (data['수입 중량'] > 0)]
    
    # "수출 금액/수출 중량" 계산
    export_value_per_weight = filtered_data['수출 금액'] * 1000 / filtered_data['수출 중량']
    # "수입 금액/수입 중량" 계산
    import_value_per_weight = filtered_data['수입 금액'] * 1000 / filtered_data['수입 중량']
    
    # 정렬 인덱스 생성
    sorted_export_indices = export_value_per_weight.argsort()[::-1]  # 내림차순 정렬
    sorted_import_indices = import_value_per_weight.argsort()[::-1]  # 내림차순 정렬
    
    # 정렬된 데이터 반환 (원본 데이터프레임에서 인덱스로 접근)
    sorted_export_data = filtered_data.iloc[sorted_export_indices]
    sorted_import_data = filtered_data.iloc[sorted_import_indices]
    return sorted_export_data, export_value_per_weight.iloc[sorted_export_indices], sorted_import_data, import_value_per_weight.iloc[sorted_import_indices]

class TradeTable(QMainWindow):
    def __init__(self, hs_code):
        super().__init__()
        self.setWindowTitle('Trade Data')
        self.setGeometry(100, 100, 800, 1500)

        # PyQt5에서 사용할 폰트 설정
        font = QFont("Arial")
        self.setFont(font)
        
        # HS 코드로 정렬된 데이터 가져오기
        sorted_export_data, sorted_export_value_per_weight, sorted_import_data, sorted_import_value_per_weight = sort_by_hs_code(hs_code)
        
        # 수출 데이터 테이블 설정
        self.export_table = QTableWidget(self)
        self.export_table.setRowCount(len(sorted_export_data))
        self.export_table.setColumnCount(4)
        self.export_table.setHorizontalHeaderLabels(['Country', 'Export Weight (kg)', 'Export Value ($)', 'Export Unit Value ($/kg)'])
        self.export_table.setGeometry(50, 50, 700, 200)

        for i, (index, row) in enumerate(sorted_export_data.iterrows()):
            self.export_table.setItem(i, 0, QTableWidgetItem(row['국가']))
            self.export_table.setItem(i, 1, QTableWidgetItem(f"{row['수출 중량']:.1f}"))
            self.export_table.setItem(i, 2, QTableWidgetItem(f"{row['수출 금액'] * 1000:,}"))
            self.export_table.setItem(i, 3, QTableWidgetItem(f"{sorted_export_value_per_weight[index]:.6f}"))

        # 수입 데이터 테이블 설정
        self.import_table = QTableWidget(self)
        self.import_table.setRowCount(len(sorted_import_data))
        self.import_table.setColumnCount(4)
        self.import_table.setHorizontalHeaderLabels(['Country', 'Import Weight (kg)', 'Import Value ($)', 'Import Unit Value ($/kg)'])
        self.import_table.setGeometry(50, 300, 700, 200)

        for i, (index, row) in enumerate(sorted_import_data.iterrows()):
            self.import_table.setItem(i, 0, QTableWidgetItem(row['국가']))
            self.import_table.setItem(i, 1, QTableWidgetItem(f"{row['수입 중량']:.1f}"))
            self.import_table.setItem(i, 2, QTableWidgetItem(f"{row['수입 금액'] * 1000:,}"))
            self.import_table.setItem(i, 3, QTableWidgetItem(f"{sorted_import_value_per_weight[index]:.6f}"))

        # 그래프를 위한 Figure 설정
        self.figure_export = plt.figure()
        self.canvas_export = FigureCanvas(self.figure_export)
        self.canvas_export.setGeometry(50, 550, 700, 200)

        self.figure_export_pie = plt.figure()
        self.canvas_export_pie = FigureCanvas(self.figure_export_pie)
        self.canvas_export_pie.setGeometry(50, 800, 700, 200)

        self.figure_total = plt.figure()
        self.canvas_total = FigureCanvas(self.figure_total)
        self.canvas_total.setGeometry(50, 1050, 700, 200)

        # 그래프를 그릴 레이아웃 설정
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.export_table)
        self.layout.addWidget(self.import_table)
        self.layout.addWidget(self.canvas_export)
        self.layout.addWidget(self.canvas_export_pie)
        self.layout.addWidget(self.canvas_total)

        # 중심 위젯 설정
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        # 그래프 그리기
        self.plot_graphs(sorted_export_data, sorted_export_value_per_weight, sorted_import_data)

    def plot_graphs(self, sorted_export_data, sorted_export_value_per_weight, sorted_import_data):
        # 상위 10개의 데이터만 선택 (수출)
        top_10_export_data = sorted_export_data.head(10)
        top_10_export_value_per_weight = sorted_export_value_per_weight.head(10)
        
        ax_export = self.figure_export.add_subplot(111)
        ax_export.clear()
        ax_export.bar(top_10_export_data['국가'], top_10_export_value_per_weight)
        ax_export.set_title('Top 10 Countries Export Unit Value')
        ax_export.set_xlabel('Country')
        ax_export.set_ylabel('Export Unit Value ($/kg)')
        ax_export.tick_params(axis='x', rotation=90)

        # 상위 10개의 데이터 원형 그래프로 선택 (수출)
        ax_export_pie = self.figure_export_pie.add_subplot(111)
        ax_export_pie.clear()
        ax_export_pie.pie(top_10_export_value_per_weight, labels=top_10_export_data['국가'], autopct='%1.1f%%', startangle=140)
        ax_export_pie.set_title('Top 10 Countries Export Unit Value (Pie)')

        # 수출 및 수입 총액 계산
        total_export_value = sorted_export_data['수출 금액'].sum() * 1000
        total_import_value = sorted_import_data['수입 금액'].sum() * 1000

        # 수출 및 수입 총액 막대 그래프
        ax_total = self.figure_total.add_subplot(111)
        ax_total.clear()
        ax_total.bar(['Total Export Value', 'Total Import Value'], [total_export_value, total_import_value], color=['blue', 'orange'])
        ax_total.set_title('Total Export and Import Value')
        ax_total.set_ylabel('Total Value ($)')

        self.canvas_export.draw()
        self.canvas_export_pie.draw()
        self.canvas_total.draw()

# PyQt5 애플리케이션 초기화 및 실행
if __name__ == '__main__':
    app = QApplication(sys.argv)
    hs_code_input = 3  # 예시로 "03" 코드를 사용
    window = TradeTable(hs_code_input)
    window.show()
    sys.exit(app.exec_())
