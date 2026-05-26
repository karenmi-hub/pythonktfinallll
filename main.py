import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox
)

SUPPORTED_CURRENCIES = ["USD", "EUR", "RUB", "GBP", "JPY", "CNY"]


class CurrencyConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Конвертер валют")
        self.resize(350, 200)
        
        layout = QVBoxLayout(self)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Введите сумму")
        layout.addWidget(QLabel("Сумма:"))
        layout.addWidget(self.amount_input)
        
        self.from_currency = QComboBox()
        self.from_currency.addItems(SUPPORTED_CURRENCIES)
        self.to_currency = QComboBox()
        self.to_currency.addItems(SUPPORTED_CURRENCIES)
        self.to_currency.setCurrentText("RUB")
        
        currency_layout = QHBoxLayout()
        currency_layout.addWidget(QLabel("Из:"))
        currency_layout.addWidget(self.from_currency)
        currency_layout.addWidget(QLabel("В:"))
        currency_layout.addWidget(self.to_currency)
        layout.addLayout(currency_layout)
        
        self.convert_btn = QPushButton("Конвертировать")
        self.convert_btn.clicked.connect(self.convert)
        layout.addWidget(self.convert_btn)

        self.result = QLabel("")
        self.result.setWordWrap(True)
        layout.addWidget(self.result)
    
    def convert(self):
        try:
            amount = float(self.amount_input.text().strip())
        except ValueError:
            self.result.setText("Ошибка: введите число")
            return
        
        from_curr = self.from_currency.currentText()
        to_curr = self.to_currency.currentText()
        
        try:
            response = requests.get(
                "http://127.0.0.1:8000/convert",
                params={
                    "amount": amount,
                    "from_currency": from_curr,
                    "to_currency": to_curr
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.result.setText(
                    f"{data['amount']} {data['from_currency']} = "
                    f"{data['converted_amount']} {data['to_currency']}\n"
                    f"Курс: 1 {data['from_currency']} = {data['rate']} {data['to_currency']}"
                )
            else:
                error = response.json().get("detail", "Ошибка сервера")
                self.result.setText(f"Ошибка: {error}")
                
        except requests.exceptions.ConnectionError:
            self.result.setText("Нет связи с сервером")
        except Exception as e:
            self.result.setText(f"Ошибка: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CurrencyConverterApp()
    window.show()
    sys.exit(app.exec_())