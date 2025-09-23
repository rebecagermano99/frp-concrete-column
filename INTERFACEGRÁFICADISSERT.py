import sys
import math
import sympy as sp
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit
)
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QBrush
from PyQt6.QtCore import Qt

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(500)
        self.setMinimumWidth(600)
        self.n_maior = 0
        self.n_menor = 0
        self.diam_maior = 0
        self.diam_menor = 0
        self.h = 0
        self.b = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        margin = 50

        if self.h <= 0 or self.b <= 0:
            return

        escala = 10
        w = int(self.b * escala)
        h = int(self.h * escala)
        offset = 20

        # Retângulo da seção
        painter.setBrush(QBrush(QColor("lightgray")))
        painter.drawRect(margin, margin, w, h)

        # Barras superiores (A'f)
        if self.n_menor > 0:
            n = max(2, self.n_menor)
            espacamento = (w - 2*offset) / (n - 1)
            cx_list = [int(margin + offset + i * espacamento) for i in range(n)]
            for cx in cx_list:
                cy = margin + offset
                r = int(self.diam_menor * escala / 10)
                painter.setBrush(QBrush(QColor("black")))
                painter.drawEllipse(cx - r // 2, cy - r // 2, r, r)

        # Barras inferiores (Af)
        if self.n_maior > 0:
            n = max(2, self.n_maior)
            espacamento = (w - 2*offset) / (n - 1)
            cx_list = [int(margin + offset + i * espacamento) for i in range(n)]
            for cx in cx_list:
                cy = margin + h - offset
                r = int(self.diam_maior * escala / 10)
                painter.setBrush(QBrush(QColor("black")))
                painter.drawEllipse(cx - r // 2, cy - r // 2, r, r)

class PilarApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FRP Concrete Column")
        self.resize(1400, 800)

        layout = QHBoxLayout(self)
        azul_claro = QColor(173, 216, 230)
        branco = QColor(255, 255, 255)

        # Painel de inputs
        self.input_panel = QWidget()
        self.input_panel.setAutoFillBackground(True)
        p = self.input_panel.palette()
        p.setColor(QPalette.ColorRole.Window, azul_claro)
        self.input_panel.setPalette(p)
        input_layout = QVBoxLayout(self.input_panel)
        font_label = QFont("Arial Black", 10)

        self.inputs = {}
        labels = [
            ("Nd (kN):", "Nd"),
            ("b (cm):", "b"),
            ("h (cm):", "h"),
            ("fck (MPa):", "fck"),
            ("E (GPa):", "E"),
            ("c (cm):", "c"),
            ("x (cm):", "x"),
            ("e (cm):", "e"),
            ("Altura do pilar (cm):", "l0"),
        ]
        for text, key in labels:
            lbl = QLabel(text)
            lbl.setFont(font_label)
            lbl.setStyleSheet("color: black;")
            edit = QLineEdit()
            input_layout.addWidget(lbl)
            input_layout.addWidget(edit)
            self.inputs[key] = edit

        lbl_bitola = QLabel("Escolha bitola principal (mm):")
        lbl_bitola.setFont(font_label)
        lbl_bitola.setStyleSheet("color: black;")
        self.combo_bitola = QComboBox()
        self.combo_bitola.addItems(["10", "12.5", "16", "20", "25", "32"])
        input_layout.addWidget(lbl_bitola)
        input_layout.addWidget(self.combo_bitola)

        btn = QPushButton("Calcular")
        btn.clicked.connect(self.calcular)
        input_layout.addWidget(btn)

        # Janela de resultados menor
        self.result_panel = QWidget()
        self.result_panel.setAutoFillBackground(True)
        p2 = self.result_panel.palette()
        p2.setColor(QPalette.ColorRole.Window, branco)
        self.result_panel.setPalette(p2)
        result_layout = QVBoxLayout(self.result_panel)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setFont(QFont("Arial", 12))
        self.result_box.setStyleSheet("color: white; background-color: black;")
        self.result_box.setMaximumHeight(120)
        result_layout.addWidget(self.result_box)

        # Canvas maior
        self.canvas = Canvas()
        result_layout.addWidget(self.canvas)

        layout.addWidget(self.input_panel, 2)
        layout.addWidget(self.result_panel, 4)

    def calcular(self):
        try:
            Nd = float(self.inputs["Nd"].text())
            b = float(self.inputs["b"].text())
            h = float(self.inputs["h"].text())
            fck = float(self.inputs["fck"].text())
            E = float(self.inputs["E"].text())
            c = float(self.inputs["c"].text())
            x = float(self.inputs["x"].text())
            e = float(self.inputs["e"].text())
            l0 = float(self.inputs["l0"].text())
            bitola_principal = float(self.combo_bitola.currentText())

            fck1 = fck / 10
            E1 = E * 1000
            E2 = E1 * 0.1
            fcd = fck1 / 1.4

            eflinha = (h / 2) - e - c
            A_barra = (math.pi * (bitola_principal ** 2) / 4) / 100

            d = h - c - (bitola_principal / 10)
            ksi1 = x / h
            delta1 = d / h
            deltalinha1 = c / h

            episilonf = (0.002 * (ksi1 - delta1)) / (ksi1 - (3 / 7))
            episilonflinha = (0.002 * (ksi1 - deltalinha1)) / (ksi1 - (3 / 7))

            sigmaf = E2 * episilonf
            sigmaflinha = E2 * episilonflinha

            fi = 4 / (7 * (x / h) - 3)
            ksi1linha = (3 / 7) * ((24.5 - (8 * (fi ** 2))) / (21 - 4 * (fi ** 2)))
            alfa1 = 1 - ((4 / 21) * (fi ** 2))

            nid = Nd / (b * h * fcd)
            milinhad = (Nd * eflinha) / (b * (h ** 2) * fcd)

            fu = sigmaf * A_barra
            fulinha = sigmaflinha * A_barra

            w, wlinha = sp.symbols('w wlinha')
            eq1 = sp.Eq(nid, 0.85 * alfa1 + wlinha * (sigmaflinha / fulinha) + w * (sigmaf / fu))
            eq2 = sp.Eq(milinhad, 0.85 * alfa1 * (ksi1linha - deltalinha1) + w * (sigmaf / fu) * (delta1 - deltalinha1))
            solucao = sp.solve((eq1, eq2), (w, wlinha), dict=True)
            w_val = solucao[0][w]
            wlinha_val = solucao[0][wlinha]

            Af = (w_val * b * h * fcd) / fu
            Aflinha = (wlinha_val * b * h * fcd) / fulinha

            bitolas = [10, 12.5, 16, 20, 25, 32]
            area_barra = {d: (math.pi * (d ** 2) / 4) / 100 for d in bitolas}

            maior = max(Af, Aflinha)
            menor = min(Af, Aflinha)

      
            bitola_maior = bitola_principal
            n_maior = max(2, math.ceil(maior / area_barra[bitola_maior]))

        
            bitola_menor = None
            n_menor = None
            for d in sorted(bitolas):
                if d < bitola_maior:
                    barras_necessarias = max(2, math.ceil(menor / area_barra[d]))
                    if barras_necessarias * area_barra[d] >= menor:
                        bitola_menor = d
                        n_menor = barras_necessarias
                        break
            if bitola_menor is None:
                bitola_menor = min([d for d in bitolas if d < bitola_maior])
                n_menor = max(2, math.ceil(menor / area_barra[bitola_menor]))

       
            self.canvas.h = h
            self.canvas.b = b
            if Af >= Aflinha:
                self.canvas.n_maior = n_maior
                self.canvas.n_menor = n_menor
                self.canvas.diam_maior = bitola_maior
                self.canvas.diam_menor = bitola_menor
            else:
                self.canvas.n_maior = n_menor
                self.canvas.n_menor = n_maior
                self.canvas.diam_maior = bitola_menor
                self.canvas.diam_menor = bitola_maior
            self.canvas.update()

            efeito2 = "Desnecessário considerar efeitos de 2ª ordem" if l0/h <= 10 else "Necessário considerar efeitos de 2ª ordem"

            if Af >= Aflinha:
                texto = (
                    f"Af = {Af:.2f} cm² -> {n_maior} Φ{bitola_maior}\n"
                    f"A'f = {Aflinha:.2f} cm² -> {n_menor} Φ{bitola_menor}\n"
                    f"{efeito2}"
                )
            else:
                texto = (
                    f"Af = {Af:.2f} cm² -> {n_menor} Φ{bitola_menor}\n"
                    f"A'f = {Aflinha:.2f} cm² -> {n_maior} Φ{bitola_maior}\n"
                    f"{efeito2}"
                )

            self.result_box.setText(texto)

        except Exception as e:
            self.result_box.setText(f"Erro no cálculo: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PilarApp()
    win.show()
    sys.exit(app.exec())
