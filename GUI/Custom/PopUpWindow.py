from functools import partial

from PyQt5.QtWidgets import QMessageBox


def warning(text):
    pop_up = QMessageBox()
    pop_up.setWindowTitle("ATENÇÃO!")
    pop_up.setText(text)
    pop_up.setIcon(QMessageBox.Warning)
    pop_up.exec_()


selection_pop_up_key = {
    'Cancel': -1,
    'OK': 1,
    '&No': 0
}


def selection_pop_up(title, text, function):
    pop_up = QMessageBox()
    pop_up.setWindowTitle(title)
    pop_up.setText(text)
    pop_up.setIcon(QMessageBox.Question)
    pop_up.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok | QMessageBox.No)

    for button in pop_up.buttons():
        print(button.text())
        button.clicked.connect(partial(function, selection_pop_up_key[button.text()]))

    pop_up.exec_()
