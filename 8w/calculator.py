import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.current_num = '0'
        self.first_num = 0
        self.operator = ''
        self.is_ready_for_new_num = False
        self.init_ui()

    def init_ui(self):
        # 메인 윈도우 설정
        self.setWindowTitle('iPhone Calculator')
        self.setFixedSize(320, 500)
        self.setStyleSheet('background-color: black;')

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 20, 10, 20)

        # 상단 출력창
        self.label = QLabel('0')
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.label.setStyleSheet('color: white; padding-right: 10px;')
        self.label.setFont(QFont('Arial', 50))
        main_layout.addWidget(self.label)

        # 버튼 그리드 설정
        grid = QGridLayout()
        grid.setSpacing(10)

        # 버튼 데이터: (텍스트, 행, 열, 열 확장, 배경색)
        btns = [
            ('AC', 0, 0, 1, '#A5A5A5'), ('+/-', 0, 1, 1, '#A5A5A5'),
            ('%', 0, 2, 1, '#A5A5A5'), ('÷', 0, 3, 1, '#FF9F0A'),
            ('7', 1, 0, 1, '#333333'), ('8', 1, 1, 1, '#333333'),
            ('9', 1, 2, 1, '#333333'), ('×', 1, 3, 1, '#FF9F0A'),
            ('4', 2, 0, 1, '#333333'), ('5', 2, 1, 1, '#333333'),
            ('6', 2, 2, 1, '#333333'), ('-', 2, 3, 1, '#FF9F0A'),
            ('1', 3, 0, 1, '#333333'), ('2', 3, 1, 1, '#333333'),
            ('3', 3, 2, 1, '#333333'), ('+', 3, 3, 1, '#FF9F0A'),
            ('0', 4, 0, 2, '#333333'), ('.', 4, 2, 1, '#333333'),
            ('=', 4, 3, 1, '#FF9F0A')
        ]

        for text, r, c, span, color in btns:
            button = QPushButton(text)
            # 0번 버튼은 가로로 길게 설정
            width = 140 if span == 2 else 65
            button.setFixedSize(width, 65)
            
            # 스타일 설정 (PEP 8에 따라 문자열은 ' ' 사용)
            txt_color = 'black' if color == '#A5A5A5' else 'white'
            button.setStyleSheet(f'background-color: {color}; '
                                 f'color: {txt_color}; '
                                 f'border-radius: 32px; '
                                 f'font-size: 20px; '
                                 f'border: none;')
            
            button.clicked.connect(self.handle_button)
            grid.addWidget(button, r, c, 1, span)

        main_layout.addLayout(grid)
        self.setLayout(main_layout)

    def handle_button(self):
        clicked_btn = self.sender().text()

        # 숫자 및 소수점 입력
        if clicked_btn.isdigit() or clicked_btn == '.':
            if self.current_num == '0' or self.is_ready_for_new_num:
                self.current_num = clicked_btn
                self.is_ready_for_new_num = False
            else:
                self.current_num += clicked_btn

        # 초기화
        elif clicked_btn == 'AC':
            self.current_num = '0'
            self.first_num = 0
            self.operator = ''

        # 사칙연산 기호 클릭
        elif clicked_btn in ['+', '-', '×', '÷']:
            self.first_num = float(self.current_num)
            self.operator = clicked_btn
            self.is_ready_for_new_num = True

        # 결과 계산
        elif clicked_btn == '=':
            if self.operator:
                second_num = float(self.current_num)
                if self.operator == '+':
                    result = self.first_num + second_num
                elif self.operator == '-':
                    result = self.first_num - second_num
                elif self.operator == '×':
                    result = self.first_num * second_num
                elif self.operator == '÷':
                    result = self.first_num / second_num if second_num != 0 else 0
                
                # 결과값 처리 (정수면 .0 제거)
                if result == int(result):
                    self.current_num = str(int(result))
                else:
                    self.current_num = str(result)
                self.operator = ''

        self.update_screen()

    def update_screen(self):
        # 세 자리마다 콤마 추가 로직
        try:
            val = self.current_num
            if '.' in val:
                pre, post = val.split('.')
                self.label.setText(f'{int(pre):,}.{post}')
            else:
                self.label.setText(f'{int(val):,}')
        except ValueError:
            self.label.setText(self.current_num)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc_window = Calculator()
    calc_window.show()
    sys.exit(app.exec())