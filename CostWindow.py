import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDateEdit
from PyQt5.QtCore import Qt, QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class CostWindow(QDialog):
    def __init__(self, parent=None):
        super(CostWindow, self).__init__(parent)
        self.setWindowTitle('CostWindow')
        self.setGeometry(100, 100, 1000, 1000)

        # 메인 레이아웃 설정
        main_layout = QVBoxLayout()

        # 버튼 및 기간 설정 레이아웃
        control_layout = QHBoxLayout()
        self.sea_button = QPushButton('해상 요금', self)
        self.air_button = QPushButton('항공 요금', self)
        self.start_date = QDateEdit(self)
        self.end_date = QDateEdit(self)
        self.start_date.setDate(QDate(2019, 1, 1))
        self.end_date.setDate(QDate(2024, 6, 1))
        self.start_date.setCalendarPopup(True)
        self.end_date.setCalendarPopup(True)

        control_layout.addWidget(QLabel("시작 날짜(2019-01~):"))
        control_layout.addWidget(self.start_date)
        control_layout.addWidget(QLabel("종료 날짜(~2024-06):"))
        control_layout.addWidget(self.end_date)
        control_layout.addWidget(self.sea_button)
        control_layout.addWidget(self.air_button)
        main_layout.addLayout(control_layout)

        # 그래프와 텍스트 레이아웃 설정
        self.canvas1 = FigureCanvas(plt.Figure(figsize=(5, 3)))
        self.canvas2 = FigureCanvas(plt.Figure(figsize=(5, 3)))
        self.air_canvas = FigureCanvas(plt.Figure(figsize=(5, 3)))
        self.label = QLabel('항공 요금 데이터가 없습니다.', self)
        self.label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.canvas1)
        main_layout.addWidget(self.canvas2)
        main_layout.addWidget(self.air_canvas)
        main_layout.addWidget(self.label)
        self.setLayout(main_layout)

        # 버튼 클릭 이벤트 연결
        self.sea_button.clicked.connect(self.display_sea_costs)
        self.air_button.clicked.connect(self.display_air_costs)
        self.start_date.dateChanged.connect(self.update_graphs)
        self.end_date.dateChanged.connect(self.update_graphs)

        # 초기 화면: 해상 요금 그래프 표시
        self.display_sea_costs()

    def plot_graph(self, canvas, file_path, title, yLabel):
        # CSV 파일 읽기
        data = pd.read_csv(file_path, encoding='utf-8')

        # 선택한 기간에 따른 데이터 필터링
        start_period = self.start_date.date().toString("yyyy-MM")
        end_period = self.end_date.date().toString("yyyy-MM")
        filtered_data = data[(data['기간'] >= start_period) & (data['기간'] <= end_period)]

        # 데이터 시각화
        canvas.figure.clf()  # 이전 그래프 초기화
        ax = canvas.figure.add_subplot(111)
        for column in filtered_data.columns[1:]:
            ax.plot(filtered_data['기간'], filtered_data[column], label=column)

        ax.set_title(title)
        ax.set_xlabel('기간')
        ax.set_ylabel(yLabel)
        ax.legend()
        ax.tick_params(axis='x', rotation=90, labelsize=8)  # X축 레이블 90도 회전 및 폰트 크기 조정
        canvas.draw()

    def display_sea_costs(self):
        # 해상 요금 그래프 표시
        self.canvas1.show()
        self.canvas2.show()
        self.air_canvas.hide()
        self.label.hide()
        self.plot_graph(self.canvas1, "outcost_ship.csv", "해상 수출 운송비용", "비용(천 원/2TEU)")
        self.plot_graph(self.canvas2, "incost_ship.csv", "해상 수입 운송비용", "비용(천 원/2TEU)")

    def display_air_costs(self):
        # 항공 요금 그래프 표시
        self.canvas1.hide()
        self.canvas2.hide()
        self.air_canvas.show()
        self.label.hide()
        self.plot_graph(self.air_canvas, "cost_air.csv", "항공 운송비용", "비용(원/KG)")

    def update_graphs(self):
        # 선택한 기간에 따라 그래프 업데이트
        if self.canvas1.isVisible():
            self.display_sea_costs()
        elif self.air_canvas.isVisible():
            self.display_air_costs()
