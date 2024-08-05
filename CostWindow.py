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

       
        main_layout = QVBoxLayout()

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

        self.sea_button.clicked.connect(self.display_sea_costs)
        self.air_button.clicked.connect(self.display_air_costs)
        self.start_date.dateChanged.connect(self.update_graphs)
        self.end_date.dateChanged.connect(self.update_graphs)

        self.display_sea_costs()

    def plot_graph(self, canvas, file_path, title, yLabel):
       
        data = pd.read_csv(file_path, encoding='utf-8')

        # 기간 필터링함
        start_period = self.start_date.date().toString("yyyy-MM")
        end_period = self.end_date.date().toString("yyyy-MM")
        filtered_data = data[(data['기간'] >= start_period) & (data['기간'] <= end_period)]

        # 데이터 시각화
        canvas.figure.clf()
        ax = canvas.figure.add_subplot(111)
        for column in filtered_data.columns[1:]:
            ax.plot(filtered_data['기간'], filtered_data[column], label=column)

        ax.set_title(title)
        ax.set_xlabel('기간')
        ax.set_ylabel(yLabel)
        ax.legend()
        ax.tick_params(axis='x', rotation=90, labelsize=8)  
        canvas.draw()

#해상
    def display_sea_costs(self):
        self.canvas1.show()
        self.canvas2.show()
        self.air_canvas.hide()
        self.label.hide()
        self.plot_graph(self.canvas1, "outcost_ship.csv", "해상 수출 운송비용", "비용(천 원/2TEU)")
        self.plot_graph(self.canvas2, "incost_ship.csv", "해상 수입 운송비용", "비용(천 원/2TEU)")

#항공
    def display_air_costs(self):
        self.canvas1.hide()
        self.canvas2.hide()
        self.air_canvas.show()
        self.label.hide()
        self.plot_graph(self.air_canvas, "cost_air.csv", "항공 운송비용", "비용(원/KG)")

    def update_graphs(self):
        if self.canvas1.isVisible():
            self.display_sea_costs()
        elif self.air_canvas.isVisible():
            self.display_air_costs()
