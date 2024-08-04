import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QFrame
from PyQt5.QtCore import Qt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from CostWindow import CostWindow

# 한글 폰트 설정 (윈도우의 경우)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# CSV 파일 읽기
file_path = 'incomeoutcome2.csv'
data = pd.read_csv(file_path)

# 특정 HS 코드에 대해 거래한 국가들을 정렬하는 함수
def sort_by_hs_code(hs_code):
    filtered_data = data[(data['HS코드'] == hs_code) & (data['수출 중량'] > 0) & (data['수입 중량'] > 0)&(data['수입 금액'] > 0)]
    
    export_value_per_weight = filtered_data['수출 금액'] * 1000 / filtered_data['수출 중량']
    import_value_per_weight = filtered_data['수입 금액'] * 1000 / filtered_data['수입 중량']
    
    sorted_export_indices = export_value_per_weight.argsort()[::-1]
    sorted_import_indices = import_value_per_weight.argsort()
    
    sorted_export_data = filtered_data.iloc[sorted_export_indices]
    sorted_import_data = filtered_data.iloc[sorted_import_indices]
    return sorted_export_data, export_value_per_weight.iloc[sorted_export_indices], sorted_import_data, import_value_per_weight.iloc[sorted_import_indices]

class TradeTable(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('무역 데이터')
        self.setGeometry(100, 100, 1000, 600)
        
        # 중앙 위젯 및 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        
        # 상단 위젯 및 레이아웃 설정
        self.top_widget = QWidget()
        self.top_layout = QHBoxLayout(self.top_widget)
        
        # HS 코드 입력 및 버튼
        self.hscode_edit = QLineEdit(self)
        self.hscode_edit.setPlaceholderText('HS 코드 입력 (숫자만)')
        self.hscode_edit.textChanged.connect(self.update_item_name)  # 텍스트 변경 시 업데이트
        
        self.item_name_label = QLabel('', self)
        
        self.table_button = QPushButton('표', self)
        self.graph_button = QPushButton('그래프', self)
        self.cost_button = QPushButton('운송 요금',self)

        self.table_button.clicked.connect(self.show_table)
        self.graph_button.clicked.connect(self.show_graph)
        self.cost_button.clicked.connect(self.show_cost)
        
        # 버튼 레이아웃
        self.top_layout.addWidget(self.cost_button)
        self.top_layout.addWidget(self.hscode_edit)
        self.top_layout.addWidget(self.item_name_label)  # 품목명 레이블 추가
        self.top_layout.addWidget(self.table_button)
        self.top_layout.addWidget(self.graph_button)
        
        self.main_layout.addWidget(self.top_widget)
        
        # 하단 위젯 및 레이아웃 설정
        self.bottom_widget = QWidget()
        self.bottom_layout = QVBoxLayout(self.bottom_widget)
        
        # 테이블 프레임 및 레이아웃
        self.table_frame = QFrame()
        self.table_layout = QVBoxLayout(self.table_frame)
        self.export_table = QTableWidget(self)
        self.import_table = QTableWidget(self)
        self.table_layout.addWidget(self.export_table)
        self.table_layout.addWidget(self.import_table)
        
        # 그래프 프레임 및 레이아웃
        self.graph_frame = QFrame()
        self.graph_layout = QVBoxLayout(self.graph_frame)
        self.canvas_export = FigureCanvas(plt.Figure())
        self.canvas_import = FigureCanvas(plt.Figure())
        self.graph_layout.addWidget(self.canvas_export)
        self.graph_layout.addWidget(self.canvas_import)
        
        # 하단 레이아웃에 프레임 추가
        self.bottom_layout.addWidget(self.table_frame)
        self.bottom_layout.addWidget(self.graph_frame)
        
        self.main_layout.addWidget(self.bottom_widget)
        
        # 기본적으로 테이블을 표시합니다.
        self.show_table()
    
    def show_cost(self):
        self.cost_window = CostWindow(self)
        self.cost_window.show()
        
    def hide_widgets(self):
        self.table_frame.hide()
        self.graph_frame.hide()
        
    def show_table(self):
        self.table_frame.show()
        self.graph_frame.hide()
        self.update_table()
        
    def update_table(self):
        hs_code_text = self.hscode_edit.text().strip()
        if not hs_code_text.isdigit():
            self.hide_widgets()
            return
        
        hs_code_input = int(hs_code_text)
        sorted_export_data, sorted_export_value_per_weight, sorted_import_data, sorted_import_value_per_weight = sort_by_hs_code(hs_code_input)
        
        # 수출 데이터 테이블 설정
        self.export_table.setRowCount(len(sorted_export_data))
        self.export_table.setColumnCount(4)
        self.export_table.setHorizontalHeaderLabels(['국가', '수출 중량(kg)', '수출 금액($)', '수출 단가($/kg)'])

        for i, (index, row) in enumerate(sorted_export_data.iterrows()):
            self.export_table.setItem(i, 0, QTableWidgetItem(row['국가']))
            self.export_table.setItem(i, 1, QTableWidgetItem(f"{row['수출 중량']:.1f}"))
            self.export_table.setItem(i, 2, QTableWidgetItem(f"${row['수출 금액'] * 1000:,.0f}"))
            self.export_table.setItem(i, 3, QTableWidgetItem(f"${sorted_export_value_per_weight[index]:.6f}"))

        # 수입 데이터 테이블 설정
        self.import_table.setRowCount(len(sorted_import_data))
        self.import_table.setColumnCount(4)
        self.import_table.setHorizontalHeaderLabels(['국가', '수입 중량(kg)', '수입 금액($)', '수입 단가($/kg)'])

        for i, (index, row) in enumerate(sorted_import_data.iterrows()):
            self.import_table.setItem(i, 0, QTableWidgetItem(row['국가']))
            self.import_table.setItem(i, 1, QTableWidgetItem(f"{row['수입 중량']:.1f}"))
            self.import_table.setItem(i, 2, QTableWidgetItem(f"${row['수입 금액'] * 1000:,.0f}"))
            self.import_table.setItem(i, 3, QTableWidgetItem(f"${sorted_import_value_per_weight[index]:.6f}"))

    def show_graph(self):
        self.table_frame.hide()
        self.graph_frame.show()
        
        hs_code_text = self.hscode_edit.text().strip()
        if not hs_code_text.isdigit():
            return

        hs_code_input = int(hs_code_text)
        sorted_export_data, sorted_export_value_per_weight, sorted_import_data, sorted_import_value_per_weight = sort_by_hs_code(hs_code_input)

        # 그래프를 위한 Figure 설정
        self.figure_export = plt.Figure(figsize=(8, 4))  # 크기 조정
        self.figure_import = plt.Figure(figsize=(8, 4))  # 크기 조정
        self.canvas_export.figure = self.figure_export
        self.canvas_import.figure = self.figure_import
        
        # Figure를 위한 새로운 Axes 생성
        self.ax_export = self.figure_export.add_subplot(111)
        self.ax_import = self.figure_import.add_subplot(111)

        # 수출 데이터 그래프
        self.ax_export.bar(sorted_export_data['국가'], sorted_export_value_per_weight, color='blue')
        self.ax_export.set_title('수출 단가', fontsize=12)  # 글자 크기 조정
        self.ax_export.set_xlabel('국가', fontsize=10)  # 글자 크기 조정
        self.ax_export.set_ylabel('단가($/kg)', fontsize=10)  # 글자 크기 조정
        self.ax_export.tick_params(axis='x', rotation=90, labelsize=8)  # 글자 크기 조정
        self.ax_export.tick_params(axis='y', labelsize=8)  # 글자 크기 조정

        # 수입 데이터 그래프
        self.ax_import.bar(sorted_import_data['국가'], sorted_import_value_per_weight, color='green')
        self.ax_import.set_title('수입 단가', fontsize=12)  # 글자 크기 조정
        self.ax_import.set_xlabel('국가', fontsize=10)  # 글자 크기 조정
        self.ax_import.set_ylabel('단가($/kg)', fontsize=10)  # 글자 크기 조정
        self.ax_import.tick_params(axis='x', rotation=90, labelsize=8)  # 글자 크기 조정
        self.ax_import.tick_params(axis='y', labelsize=8)  # 글자 크기 조정
        
        # 그래프를 레이아웃에 추가
        self.canvas_export.draw()
        self.canvas_import.draw()
    
    def update_item_name(self):
        hs_code_text = self.hscode_edit.text().strip()
        if hs_code_text.isdigit():
            hs_code_input = int(hs_code_text)
            item_name = data.loc[data['HS코드'] == hs_code_input, '품목명']
            if not item_name.empty:
                self.item_name_label.setText(f'품목명: {item_name.values[0]}')
            else:
                self.item_name_label.setText('해당 HS 코드의 품목명이 없습니다.')
        else:
            self.item_name_label.setText('HS 코드가 유효하지 않습니다.')

# PyQt5 애플리케이션 초기화 및 실행
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TradeTable()
    window.show()  # 여기서 창을 표시합니다.
    sys.exit(app.exec_())
