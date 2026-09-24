import sys
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget

import logic


class BMIWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(Path(__file__).with_name("bmi.ui"), self)
        logic.init_db()

        self.resultLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ageResultLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.birthDateEdit.setMaximumDate(QDate.currentDate())

        self.calcButton.clicked.connect(self.on_calculate)
        self.ageButton.clicked.connect(self.on_calculate_age)

    def on_calculate(self):
        name = self.nameEdit.text().strip()
        height = self.heightEdit.text().strip()
        weight = self.weightEdit.text().strip()

        errors = logic.validate(name, height, weight)
        if errors:
            QMessageBox.warning(self, "Invalid input", "\n".join(errors))
            return

        bmi = logic.calc_bmi(int(height), float(weight))
        logic.save_record(name, int(height), float(weight), bmi)

        self.resultLabel.setText(
            f"{name}, your BMI is {bmi:.2f} ({logic.bmi_category(bmi)})"
        )

    def on_calculate_age(self):
        birth = self.birthDateEdit.date().toPyDate()
        try:
            years, months, days = logic.calculate_age(birth)
        except ValueError as e:
            QMessageBox.warning(self, "Invalid date", str(e))
            return

        logic.save_age(birth, years, months, days)

        self.ageResultLabel.setText(
            f"Your age: {years} years, {months} months, {days} days"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BMIWindow()
    window.show()
    sys.exit(app.exec())
