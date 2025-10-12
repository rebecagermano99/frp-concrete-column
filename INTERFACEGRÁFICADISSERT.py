import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QScrollArea, QTextEdit, QFrame
)
from PyQt6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor
from PyQt6.QtCore import Qt


IMAGE_PATH = r"C:\Users\rebec\Documents\PYTHON\Dissertação\icon.jpg"

class SectionCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(600, 520)
        # valores a serem passados pelo app
        self.b = 0.0   # cm
        self.h = 0.0   # cm
        self.n_inferior = 0
        self.n_superior = 0
        self.diam_inferior = 0.0  # mm
        self.diam_superior = 0.0  # mm

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)


        painter.fillRect(self.rect(), QBrush(QColor(255, 255, 255)))

        if self.b <= 0 or self.h <= 0:
            painter.setPen(Qt.GlobalColor.black)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter,
                             "Insira os dados no painel à esquerda e clique em Calcular")
            return


        margin = 30
        avail_w = self.width() - 2 * margin
        avail_h = self.height() - 2 * margin
        escala_x = avail_w / self.b
        escala_y = avail_h / self.h
        escala = min(escala_x, escala_y)
        escala = max(min(escala, 8.0), 3.0)

        rect_w = int(self.b * escala)
        rect_h = int(self.h * escala)
        top_left_x = (self.width() - rect_w) // 2
        top_left_y = (self.height() - rect_h) // 2


        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.setPen(QColor(30, 30, 30))
        painter.drawRect(top_left_x, top_left_y, rect_w, rect_h)


        offset_px = int(1.5 * escala)


        def draw_bar_row(n_barras, diam_mm, y_px):
            if n_barras <= 0:
                return
            diam_cm = diam_mm / 10.0
            radius_px = max(2, int((diam_cm * escala) / 2))
            inner_w = rect_w - 2 * offset_px
            if n_barras == 1:
                xs = [top_left_x + offset_px + inner_w // 2]
            else:
                espac = inner_w / (n_barras - 1)
                xs = [int(top_left_x + offset_px + i * espac) for i in range(n_barras)]
            painter.setBrush(QBrush(QColor(20, 20, 20)))
            for x in xs:
                painter.drawEllipse(x - radius_px, y_px - radius_px, 2 * radius_px, 2 * radius_px)


        y_superior = top_left_y + offset_px
        draw_bar_row(self.n_superior, self.diam_superior, y_superior)

        y_inferior = top_left_y + rect_h - offset_px
        draw_bar_row(self.n_inferior, self.diam_inferior, y_inferior)


        painter.setFont(QFont("Arial", 9))
        painter.setPen(QColor(0, 0, 0))
        legenda = f"Seção: b = {self.b:.1f} cm  x  h = {self.h:.1f} cm"
        painter.drawText(10, 15, legenda)



class PilarGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FRP Concrete Column - GUI")
        self.resize(1200, 760)

        main_layout = QHBoxLayout(self)


        left_panel = QVBoxLayout()
        left_panel.setSpacing(12)


        img_label = QLabel()
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            pix = QPixmap(IMAGE_PATH)
            if not pix.isNull():
                pix = pix.scaledToWidth(220, Qt.TransformationMode.SmoothTransformation)
                img_label.setPixmap(pix)
        except Exception:
            img_label.setText("FRP CONCRETE COLUMN\n(imagem não encontrada)")
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(img_label)


        title_in = QLabel("DADOS DE ENTRADA")
        title_in.setFont(QFont("Arial Black", 12))
        title_in.setStyleSheet("background-color: #1f2b2e; color: white; padding: 8px; border-radius: 6px;")
        title_in.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_panel.addWidget(title_in)

        self.inputs = {}
        def make_labeled_edit(label_text, key, placeholder=""):
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Arial", 10))
            edit = QLineEdit()
            edit.setPlaceholderText(placeholder)
            left_panel.addWidget(lbl)
            left_panel.addWidget(edit)
            self.inputs[key] = edit

        make_labeled_edit("Força axial Nk (kN):", "Nk", "ex.: 100")
        make_labeled_edit("Excentricidade e (cm):", "e", "ex.: 2.5")
        make_labeled_edit("Largura b (cm):", "b", "ex.: 30")
        make_labeled_edit("Altura h (cm):", "h", "ex.: 30")
        make_labeled_edit("fck (MPa):", "fck", "ex.: 30")
        make_labeled_edit("Módulo E da barra FRP (GPa):", "E", "ex.: 50")
        make_labeled_edit("Cobrimento c (cm):", "c", "ex.: 2.5")
        make_labeled_edit("Resistência compressão da barra FRP ffd (kN/cm²):", "ffd", "ex.: 0.5")
        make_labeled_edit("Altura do pilar l0 (cm):", "l0", "ex.: 300")


        btn = QPushButton("Calcular")
        btn.clicked.connect(self.on_calcular)
        left_panel.addWidget(btn)
        left_panel.addStretch(1)

        scroll_content = QWidget()
        scroll_content.setLayout(left_panel)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_content)
        scroll_area.setFixedWidth(360)
        main_layout.addWidget(scroll_area)


        right_panel = QVBoxLayout()
        titulo_secao = QLabel("SEÇÃO TRANSVERSAL DO PILAR")
        titulo_secao.setFont(QFont("Arial Black", 12))
        titulo_secao.setStyleSheet("background-color: #1f2b2e; color: white; padding: 10px;")
        titulo_secao.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        right_panel.addWidget(titulo_secao)

        self.canvas = SectionCanvas()
        frame_canvas = QFrame()
        frame_canvas.setFrameShape(QFrame.Shape.StyledPanel)
        frame_canvas.setLayout(QVBoxLayout())
        frame_canvas.layout().addWidget(self.canvas)
        right_panel.addWidget(frame_canvas, stretch=6)

        resultado_title = QLabel("RESULTADOS")
        resultado_title.setFont(QFont("Arial Black", 12))
        resultado_title.setStyleSheet("background-color: #1f2b2e; color: white; padding: 10px;")
        resultado_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        right_panel.addWidget(resultado_title)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setFont(QFont("Consolas", 10))
        right_panel.addWidget(self.result_box, stretch=2)

        main_layout.addLayout(right_panel, stretch=1)


    def on_calcular(self):
        try:

            Nk = float(self.inputs["Nk"].text())
            Nd = Nk * 1.4
            e = float(self.inputs["e"].text())
            b = float(self.inputs["b"].text())
            h = float(self.inputs["h"].text())
            fck = float(self.inputs["fck"].text())
            E = float(self.inputs["E"].text())
            c = float(self.inputs["c"].text())
            ffd = float(self.inputs["ffd"].text())
            l0 = float(self.inputs["l0"].text())


            Md = Nd * e
            dlinha = c + 1.0
            eflinha = (h / 2.0) - e - dlinha
            fcd = (fck / 10.0) / 1.4
            Mlinha = Nd * eflinha
            Ef = E * 1000.0 * 0.1
            d = h - dlinha
            delta1 = d / h
            deltalinha1 = dlinha / h
            nid = Nd / (b * h * fcd)
            milinhad = (Nd * eflinha) / (b * (h ** 2) * fcd)
            V = (0.286 * h - 0.688 * dlinha) * fcd * b * h
            le = l0 + h
            I = (b * (h ** 3)) / 12.0
            Asec = b * h
            i = math.sqrt(I / Asec)
            lamb = le / i
            misdlim = 0.85 * (0.5 - deltalinha1)

            barras = [1.0, 1.25, 1.6, 2.0, 2.5, 3.2]

            def calc_barras(Areq, b, h, c):
                for phi in barras:
                    A_barra = math.pi * (phi / 2.0) ** 2
                    n_barras = max(2, math.ceil(Areq / A_barra))
                    diam_max = b / 8.0
                    if phi > diam_max:
                        continue
                    if n_barras > 1:
                        espac = (b - 2 * c - n_barras * phi) / (n_barras - 1)
                    else:
                        espac = b - 2 * c - phi
                    espac_min = max(phi, 2.0)
                    if espac >= espac_min:
                        return phi, n_barras, espac
                return None, None, None

            lines = []
            lines.append(f"{'Seção no domínio 5' if Mlinha >= V else 'Seção fora do domínio 5'}")
            lines.append(f"{'Efeitos de 2ª ordem podem ser desprezados' if lamb <= 55 else 'Considerar efeitos de 2ª ordem'}")
            lines.append("")

            if Mlinha < V:
                lines.append("Seção fora do domínio 5. Cálculo interrompido.")
                self.result_box.setPlainText("\n".join(lines))
                self.canvas.b = b
                self.canvas.h = h
                self.canvas.n_inferior = 0
                self.canvas.n_superior = 0
                self.canvas.update()
                return
            else:
                lines.append("Seção no domínio 5\n")


            if milinhad <= misdlim:
                lines.append("Usar armadura UNILATERAL")
                alfa1req = milinhad / (0.85 * (0.5 - deltalinha1))
                alfa1req = max(0.8, min(alfa1req, 0.997))
                lines.append(f"alfa1req = {alfa1req:.4f}")
                fiaa = math.sqrt((21.0 / 4.0) * (1.0 - alfa1req))
                ksi1 = (3.0 / 7.0) + (8.0 / (7.0 * math.sqrt(21.0 * (1.0 - alfa1req))))
                ksi1linhaa = (42.0 * alfa1req - 17.5) / (49.0 * alfa1req)
                episilonfdlinhaa = (0.002 * (ksi1 - deltalinha1)) / (ksi1 - (3.0 / 7.0))
                sigmafdlinhaa = Ef * episilonfdlinhaa
                if abs(sigmafdlinhaa) < 1e-9:
                    lines.append("Erro: sigmafdlinhaa ~ 0")
                    self.result_box.setPlainText("\n".join(lines))
                    return
                wa = (nid - 0.85 * alfa1req) * (ffd / sigmafdlinhaa)
                Areq = (wa * b * h * fcd) / ffd
                lines.append(f"Areq (área FRP necessária) = {Areq:.3f} cm²")
                phi_cm, n_barras, espac = calc_barras(Areq, b, h, c)
                if phi_cm:
                    lines.append(f"Inferior φ = {phi_cm*10:.1f} mm | {n_barras} barras | espaçamento ≈ {espac:.2f} cm")
                    self.canvas.n_inferior = n_barras
                    self.canvas.diam_inferior = phi_cm * 10
                    self.canvas.n_superior = 0
                    self.canvas.diam_superior = 0
                else:
                    self.canvas.n_inferior = 0
                    self.canvas.n_superior = 0


            else:
                lines.append("Usar armadura BILATERAL")
                alfa1b = 1.0
                ksi1linhab = 0.5
                episilonfdlinhab = 0.002
                sigmafdblinha = Ef * episilonfdlinhab
                if abs(sigmafdblinha) < 1e-9:
                    lines.append("Erro: sigmafdblinha ~ 0")
                    self.result_box.setPlainText("\n".join(lines))
                    return
                wb = (ffd / sigmafdblinha) * ((milinhad - 0.85 * (0.5 - deltalinha1)) / (delta1 - deltalinha1))
                Ainf = (wb * b * h * fcd) / ffd
                wlinha = (nid - 0.85 * alfa1b - wb * sigmafdblinha / ffd) * (ffd / sigmafdblinha)
                Asup = (wlinha * b * h * fcd) / ffd
                phi_inf, n_inf, espac_inf = calc_barras(Ainf, b, h, c)
                phi_sup, n_sup, espac_sup = calc_barras(Asup, b, h, c)
                if phi_inf and phi_sup:
                    lines.append(f"Área inferior= {Ainf:.2f} cm²")
                    lines.append(f"Área superior= {Asup:.2f} cm²")
                    lines.append(f"Inferior φ = {phi_inf*10:.1f} mm | {n_inf} barras | espaçamento ≈ {espac_inf:.2f} cm")
                    lines.append(f"Superior φ = {phi_sup*10:.1f} mm | {n_sup} barras | espaçamento ≈ {espac_sup:.2f} cm")
                    self.canvas.n_inferior = n_inf
                    self.canvas.diam_inferior = phi_inf * 10
                    self.canvas.n_superior = n_sup
                    self.canvas.diam_superior = phi_sup * 10
                else:
                    self.canvas.n_inferior = 0
                    self.canvas.n_superior = 0

            self.canvas.b = b
            self.canvas.h = h
            self.result_box.setPlainText("\n".join(lines))
            self.canvas.update()

        except Exception as ex:
            self.result_box.setPlainText(f"Erro no cálculo: {ex}")
            self.canvas.b = 0
            self.canvas.h = 0
            self.canvas.n_inferior = 0
            self.canvas.n_superior = 0
            self.canvas.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PilarGUI()
    win.show()
    sys.exit(app.exec())

