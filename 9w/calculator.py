import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QGridLayout, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class Calculator:
    """
    계산기 로직을 담당하는 클래스.
    UI와 분리하여 순수하게 계산 기능만 처리한다.
    """

    # 계산기가 처리할 수 있는 숫자의 최대 범위
    MAX_VALUE = 1e+99

    def __init__(self):
        self.current_num = '0'
        self.first_num = 0.0
        self.operator = ''
        self.is_ready_for_new_num = False
        self.error_message = ''

    # ──────────────────────────────────────────
    # 사칙연산 메소드
    # ──────────────────────────────────────────

    def add(self, a, b):
        """덧셈을 수행하고 결과를 반환한다."""
        result = a + b
        return self._check_overflow(result)

    def subtract(self, a, b):
        """뺄셈을 수행하고 결과를 반환한다."""
        result = a - b
        return self._check_overflow(result)

    def multiply(self, a, b):
        """곱셈을 수행하고 결과를 반환한다."""
        result = a * b
        return self._check_overflow(result)

    def divide(self, a, b):
        """
        나눗셈을 수행하고 결과를 반환한다.
        0으로 나누는 경우 None을 반환하고 에러 메시지를 설정한다.
        """
        if b == 0:
            self.error_message = '0으로 나눌 수 없습니다'
            return None
        result = a / b
        return self._check_overflow(result)

    # ──────────────────────────────────────────
    # 기능 메소드
    # ──────────────────────────────────────────

    def reset(self):
        """모든 상태를 초기값으로 되돌린다."""
        self.current_num = '0'
        self.first_num = 0.0
        self.operator = ''
        self.is_ready_for_new_num = False
        self.error_message = ''

    def negative_positive(self):
        """현재 숫자의 부호를 양수 ↔ 음수로 전환한다."""
        if self.current_num == '0' or self.current_num == 'Error':
            return
        if self.current_num.startswith('-'):
            self.current_num = self.current_num[1:]
        else:
            self.current_num = '-' + self.current_num

    def percent(self):
        """현재 숫자를 100으로 나눠 퍼센트 값으로 변환한다."""
        try:
            value = float(self.current_num) / 100
            self.current_num = self._format_result(value)
        except ValueError:
            pass

    def equal(self):
        """
        저장된 첫 번째 숫자, 연산자, 현재 숫자로 계산을 수행한다.
        결과를 current_num에 저장하고 반환한다.
        """
        if not self.operator:
            return self.current_num

        try:
            second_num = float(self.current_num)
        except ValueError:
            return self.current_num

        result = None

        if self.operator == '+':
            result = self.add(self.first_num, second_num)
        elif self.operator == '-':
            result = self.subtract(self.first_num, second_num)
        elif self.operator == '×':
            result = self.multiply(self.first_num, second_num)
        elif self.operator == '÷':
            result = self.divide(self.first_num, second_num)

        # 오류 발생 시 에러 표시
        if result is None:
            self.current_num = 'Error'
            self.operator = ''
            return self.current_num

        self.current_num = self._format_result(result)
        self.operator = ''
        return self.current_num

    # ──────────────────────────────────────────
    # 숫자 입력 메소드
    # ──────────────────────────────────────────

    def input_digit(self, digit):
        """
        숫자 키 입력을 처리한다.
        숫자를 누를 때마다 화면에 숫자가 누적된다.
        """
        if self.current_num == 'Error':
            self.current_num = digit
            return

        if self.current_num == '0' or self.is_ready_for_new_num:
            self.current_num = digit
            self.is_ready_for_new_num = False
        else:
            self.current_num += digit

    def input_dot(self):
        """
        소수점 키 입력을 처리한다.
        이미 소수점이 있으면 추가 입력되지 않는다.
        """
        if self.is_ready_for_new_num:
            self.current_num = '0.'
            self.is_ready_for_new_num = False
            return

        if '.' not in self.current_num:
            self.current_num += '.'

    def input_operator(self, op):
        """연산자 입력을 처리하고 첫 번째 숫자를 저장한다."""
        if self.current_num == 'Error':
            return
        try:
            self.first_num = float(self.current_num)
        except ValueError:
            return
        self.operator = op
        self.is_ready_for_new_num = True

    # ──────────────────────────────────────────
    # 내부 유틸리티 메소드
    # ──────────────────────────────────────────

    def _check_overflow(self, value):
        """
        결과값이 처리 가능한 범위를 초과하는지 확인한다.
        범위 초과 시 None을 반환하고 에러 메시지를 설정한다.
        """
        if abs(value) > self.MAX_VALUE:
            self.error_message = '처리할 수 있는 숫자 범위를 초과했습니다'
            return None
        return value

    def _format_result(self, value):
        """
        결과값을 화면에 표시할 문자열로 변환한다.
        - 정수이면 .0 제거
        - 소수점 6자리 이하는 반올림하여 출력 (보너스 과제)
        """
        # 정수인 경우 .0 제거
        if value == int(value) and abs(value) < 1e15:
            return str(int(value))

        # 소수점 이하 6자리로 반올림 (보너스 과제)
        rounded = round(value, 6)
        result_str = str(rounded)

        # 반올림 후 정수가 된 경우 처리
        if '.' in result_str:
            result_str = result_str.rstrip('0').rstrip('.')

        return result_str


class CalculatorWindow(QWidget):
    """
    PyQt6를 사용한 계산기 UI 클래스.
    Calculator 클래스와 연결하여 완전한 동작을 구현한다.
    """

    def __init__(self):
        super().__init__()
        self.calc = Calculator()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Calculator')
        self.setFixedSize(320, 520)
        self.setStyleSheet('background-color: black;')

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 20, 10, 10)
        main_layout.setSpacing(0)

        # 숫자 표시 라벨
        self.label = QLabel('0')
        self.label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.label.setStyleSheet('color: white; padding-right: 10px;')
        self.label.setMinimumHeight(120)
        self._adjust_font_size('0')
        main_layout.addWidget(self.label)

        # 버튼 그리드
        grid = QGridLayout()
        grid.setSpacing(10)

        # (텍스트, 행, 열, 열 확장, 배경색)
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
                f'font-size: 22px; '
                f'font-weight: bold; '
                f'border: none;'
            )
            button.clicked.connect(self.handle_button)
            grid.addWidget(button, r, c, 1, span)

        main_layout.addLayout(grid)
        self.setLayout(main_layout)

    def handle_button(self):
        """모든 버튼 클릭을 처리하고 Calculator 클래스 메소드와 연결한다."""
        clicked_btn = self.sender().text()

        # 숫자 버튼
        if clicked_btn.isdigit():
            self.calc.input_digit(clicked_btn)

        # 소수점 버튼
        elif clicked_btn == '.':
            self.calc.input_dot()

        # AC(초기화) 버튼 → reset() 메소드 연결
        elif clicked_btn == 'AC':
            self.calc.reset()

        # +/- (음수양수 전환) 버튼 → negative_positive() 메소드 연결
        elif clicked_btn == '+/-':
            self.calc.negative_positive()

        # % (퍼센트) 버튼 → percent() 메소드 연결
        elif clicked_btn == '%':
            self.calc.percent()

        # 사칙연산 버튼 → input_operator() 메소드 연결
        elif clicked_btn in ['+', '-', '×', '÷']:
            self.calc.input_operator(clicked_btn)

        # = (등호) 버튼 → equal() 메소드 연결
        elif clicked_btn == '=':
            result = self.calc.equal()
            # 오류 메시지가 있으면 라벨에 표시
            if self.calc.error_message:
                self.label.setText(self.calc.error_message)
                self.calc.error_message = ''
                self._adjust_font_size(self.label.text())
                return

        self.update_screen()

    def update_screen(self):
        """화면(라벨)을 현재 숫자로 갱신하고 폰트 크기를 자동 조절한다."""
        try:
            val = self.calc.current_num

            if val == 'Error':
                self.label.setText('Error')
                self._adjust_font_size('Error')
                return

            # 소수점 포함 숫자 → 정수 부분에만 콤마 적용
            if '.' in val:
                parts = val.split('.')
                pre = parts[0]
                post = parts[1]
                # 음수 처리
                if pre.startswith('-'):
                    formatted = f'-{abs(int(pre[1:])):,}.{post}'
                else:
                    formatted = f'{int(pre):,}.{post}'
            else:
                # 음수 처리
                if val.startswith('-'):
                    formatted = f'-{abs(int(val[1:])):,}'
                else:
                    formatted = f'{int(val):,}'

            self.label.setText(formatted)
            self._adjust_font_size(formatted)

        except ValueError:
            self.label.setText(self.calc.current_num)
            self._adjust_font_size(self.calc.current_num)

    def _adjust_font_size(self, text):
        """
        표시되는 값의 길이에 따라 폰트 크기를 자동으로 조절한다. (보너스 과제)
        전체 내용이 한 번에 출력될 수 있도록 한다.
        """
        length = len(text)

        if length <= 6:
            font_size = 60
        elif length <= 9:
            font_size = 48
        elif length <= 12:
            font_size = 38
        elif length <= 15:
            font_size = 30
        else:
            font_size = 22

        self.label.setFont(QFont('Arial', font_size, QFont.Weight.Bold))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CalculatorWindow()
    window.show()
    sys.exit(app.exec())