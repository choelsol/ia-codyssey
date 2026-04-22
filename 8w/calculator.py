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
        self.setWindowTitle('iPhone Calculator')
        self.setFixedSize(320, 500)
        self.setStyleSheet('background-color: black;')

        main_layout = QVBoxLayout() 
        main_layout.setContentsMargins(10, 20, 10, 20)

        self.label = QLabel('0')
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.label.setStyleSheet('color: white; padding-right: 10px;')
        self.label.setFont(QFont('Arial', 50))
        main_layout.addWidget(self.label)

        grid = QGridLayout()
        grid.setSpacing(10)

        btns = [
            ('AC',  0, 0, 1, '#A5A5A5'),
            ('+/-', 0, 1, 1, '#A5A5A5'),
            ('%',   0, 2, 1, '#A5A5A5'),
            ('÷',   0, 3, 1, '#FF9F0A'),
            ('7',   1, 0, 1, '#333333'),
            ('8',   1, 1, 1, '#333333'),
            ('9',   1, 2, 1, '#333333'),
            ('×',   1, 3, 1, '#FF9F0A'),
            ('4',   2, 0, 1, '#333333'),
            ('5',   2, 1, 1, '#333333'),
            ('6',   2, 2, 1, '#333333'),
            ('-',   2, 3, 1, '#FF9F0A'),
            ('1',   3, 0, 1, '#333333'),
            ('2',   3, 1, 1, '#333333'),
            ('3',   3, 2, 1, '#333333'),
            ('+',   3, 3, 1, '#FF9F0A'),
            ('0',   4, 0, 2, '#333333'),
            ('.',   4, 2, 1, '#333333'),
            ('=',   4, 3, 1, '#FF9F0A'),
        ]

        for text, r, c, span, color in btns:
            button = QPushButton(text)
            width = 140 if span == 2 else 65
            button.setFixedSize(width, 65)
            txt_color = 'black' if color == '#A5A5A5' else 'white'
            button.setStyleSheet(
                f'background-color: {color}; '
                f'color: {txt_color}; '
                f'border-radius: 32px; '
                f'font-size: 20px; '
                f'border: none;'
            )
            button.clicked.connect(self.handle_button)
            grid.addWidget(button, r, c, 1, span)

        main_layout.addLayout(grid)
        self.setLayout(main_layout)

    def handle_button(self):
        clicked_btn = self.sender().text()

        if clicked_btn.isdigit() or clicked_btn == '.':
            if clicked_btn == '.' and '.' in self.current_num:
                return
            if self.current_num == '0' or self.is_ready_for_new_num:
                self.current_num = clicked_btn
                self.is_ready_for_new_num = False
            else:
                self.current_num += clicked_btn

        elif clicked_btn == 'AC':
            self.current_num = '0'
            self.first_num = 0
            self.operator = ''

        elif clicked_btn in ['+', '-', '×', '÷']:
            self.first_num = float(self.current_num)
            self.operator = clicked_btn
            self.is_ready_for_new_num = True

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
                    if second_num == 0:
                        self.current_num = 'Error'
                        self.operator = ''
                        self.update_screen()
                        return
                    result = self.first_num / second_num

                if result == int(result):
                    self.current_num = str(int(result))
                else:
                    self.current_num = str(result)
                self.operator = ''

        self.update_screen()

    def update_screen(self):
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