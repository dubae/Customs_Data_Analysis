import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
import pandas as pd

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
    sorted_import_indices = import_value_per_weight.argsort()  # 오름차순 정렬
    
    # 정렬된 데이터 반환 (원본 데이터프레임에서 인덱스로 접근)
    sorted_export_data = filtered_data.iloc[sorted_export_indices]
    sorted_import_data = filtered_data.iloc[sorted_import_indices]
    return sorted_export_data, export_value_per_weight.iloc[sorted_export_indices], sorted_import_data, import_value_per_weight.iloc[sorted_import_indices]

class TradeTable(QMainWindow):
    def __init__(self, hs_code):
        super().__init__()
        self.setWindowTitle('무역 데이터')
        self.setGeometry(100, 100, 800, 600)
        
        # HS 코드로 정렬된 데이터 가져오기
        sorted_export_data, sorted_export_value_per_weight, sorted_import_data, sorted_import_value_per_weight = sort_by_hs_code(hs_code)
        
        # 수출 데이터 테이블 설정
        self.export_table = QTableWidget(self)
        self.export_table.setRowCount(len(sorted_export_data))
        self.export_table.setColumnCount(4)
        self.export_table.setHorizontalHeaderLabels(['국가', '수출 중량(kg)', '수출 금액($)', '수출 단가($/kg)'])
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
        self.import_table.setHorizontalHeaderLabels(['국가', '수입 중량(kg)', '수입 금액($)', '수입 단가($/kg)'])
        self.import_table.setGeometry(50, 300, 700, 200)

        for i, (index, row) in enumerate(sorted_import_data.iterrows()):
            self.import_table.setItem(i, 0, QTableWidgetItem(row['국가']))
            self.import_table.setItem(i, 1, QTableWidgetItem(f"{row['수입 중량']:.1f}"))
            self.import_table.setItem(i, 2, QTableWidgetItem(f"{row['수입 금액'] * 1000:,}"))
            self.import_table.setItem(i, 3, QTableWidgetItem(f"{sorted_import_value_per_weight[index]:.6f}"))

# PyQt5 애플리케이션 초기화 및 실행
if __name__ == '__main__':
    app = QApplication(sys.argv)
    hs_code_input = 3  # 예시로 "03" 코드를 사용
    window = TradeTable(hs_code_input)
    window.show()
    sys.exit(app.exec_())
