"""
crear_pdf_entrega.py
Genera Entrega_Actividad_3.pdf con la portada y la lista de enlaces del entregable.
Antes de ejecutarlo, reemplacen las URL de la sección ENLACES por las reales
(o editen el PDF final) y corran:  python crear_pdf_entrega.py
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether)

# ----------------------------------------------------------------- ENLACES
REPO = "https://github.com/USUARIO/REPOSITORIO"          # <- reemplazar
VIDEO = "https://www.youtube.com/watch?v=XXXXXXXXXXX"    # <- reemplazar
RAMA = "main"

ENLACES = [
    ("1. Archivos de fuentes de datos",
     "Carpeta datos/ (ocupacion_transporte.csv)", f"{REPO}/tree/{RAMA}/datos"),
    ("2. Código fuente en Python",
     "generar_dataset.py, modelo_arbol_decision.py, pruebas_modelo.py", f"{REPO}/tree/{RAMA}"),
    ("3. Descripción de los datos",
     "DESCRIPCION_DATOS.md", f"{REPO}/blob/{RAMA}/DESCRIPCION_DATOS.md"),
    ("4. Pruebas realizadas al componente",
     "PRUEBAS.md y resultados/salida_pruebas.txt", f"{REPO}/blob/{RAMA}/PRUEBAS.md"),
    ("5. Video explicativo (máx. 10 min)",
     "Participan los tres integrantes", VIDEO),
]

# ----------------------------------------------------------------- ESTILOS
ss = getSampleStyleSheet()
base = ParagraphStyle("base", parent=ss["Normal"], fontName="Times-Roman",
                      fontSize=11.5, leading=17, alignment=4)
centro = ParagraphStyle("centro", parent=base, alignment=1)
titulo = ParagraphStyle("titulo", parent=centro, fontName="Times-Bold",
                        fontSize=22, leading=28)
sub = ParagraphStyle("sub", parent=centro, fontName="Times-Italic", fontSize=13)
h1 = ParagraphStyle("h1", parent=base, fontName="Times-Bold", fontSize=15,
                    leading=20, alignment=0, spaceBefore=14, spaceAfter=6)
celda = ParagraphStyle("celda", parent=base, fontSize=10, leading=13, alignment=0)
celda_b = ParagraphStyle("celda_b", parent=celda, fontName="Times-Bold")
enlace = ParagraphStyle("enlace", parent=celda, textColor=colors.HexColor("#1a4fa0"))


def encabezado_pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 10)
    canvas.line(2.5 * cm, 26.2 * cm, 19 * cm, 26.2 * cm)
    canvas.drawString(2.5 * cm, 25.7 * cm, "Aprendizaje supervisado")
    canvas.drawRightString(19 * cm, 25.7 * cm, "Actividad 3 - IA")
    canvas.drawCentredString(10.75 * cm, 1.5 * cm, str(doc.page))
    canvas.restoreState()


doc = SimpleDocTemplate("Entrega_Actividad_3.pdf", pagesize=letter,
                        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                        topMargin=3 * cm, bottomMargin=2.5 * cm,
                        title="Actividad 3 - Aprendizaje supervisado",
                        author="Lombana, Guayabo, Chaparro")
h = []

# ---- Portada
h += [Spacer(1, 1.5 * cm),
      Paragraph("Corporación Universitaria Iberoamericana", ParagraphStyle(
          "u", parent=centro, fontSize=18, leading=24)),
      Paragraph("Facultad de Ingeniería", ParagraphStyle(
          "f", parent=centro, fontSize=13)),
      Spacer(1, 3 * cm),
      Paragraph("Aprendizaje supervisado:<br/>árboles de decisión", titulo),
      Spacer(1, 0.4 * cm),
      Paragraph("Actividad 3 - Conceptos y aplicaciones de Inteligencia Artificial", sub),
      Spacer(1, 2.5 * cm),
      Paragraph("<b>Integrantes del equipo:</b>", centro),
      Paragraph("Freddy Anderson Lombana Cárdenas", centro),
      Paragraph("Miller Guayabo Sánchez", centro),
      Paragraph("Javier Shtiven Chaparro Hernández", centro),
      Spacer(1, 1.5 * cm),
      Paragraph("<b>Docente:</b>", centro),
      Paragraph("Sandra Bautista", centro),
      Spacer(1, 0.3 * cm),
      Paragraph("<b>Asignatura:</b>", centro),
      Paragraph("Inteligencia Artificial", centro),
      Spacer(1, 1.2 * cm),
      Paragraph("9 de octubre de 2026", centro),
      PageBreak()]

# ---- Resumen
h += [Paragraph("1. Resumen del proyecto", h1),
      Paragraph(
          "Se desarrolló un componente de aprendizaje supervisado para el sistema de "
          "transporte masivo modelado en la Actividad 2 (líneas B1, B2, C1, D1 y E1). "
          "Un árbol de decisión clasifica el nivel de ocupación de una estación "
          "(<i>bajo</i>, <i>medio</i> o <i>alto</i>) a partir de la hora, el día, la lluvia, "
          "los eventos especiales y los buses ofertados por hora. Se usó un dataset "
          "sintético de 5 000 registros con la estructura de los datos abiertos de "
          "transporte de Bogotá. El modelo alcanza una exactitud de 83,4 % en el "
          "conjunto de prueba, frente a 34,4 % del modelo base, y supera las 16 pruebas "
          "automatizadas.", base),
      Spacer(1, 0.2 * cm),
      Paragraph("Los datos son sintéticos, por lo que las métricas validan el flujo de "
                "trabajo y no el desempeño con datos reales de operación.", base)]

# ---- Enlaces
h += [Paragraph("2. Enlaces del entregable", h1),
      Paragraph("Todos los elementos están alojados en el repositorio Git. La docente "
                "fue agregada como colaboradora para revisar el código y comentar.", base),
      Spacer(1, 0.3 * cm)]

filas = [[Paragraph("Elemento", celda_b), Paragraph("Contenido", celda_b),
          Paragraph("Enlace", celda_b)]]
for el, cont, url in ENLACES:
    filas.append([Paragraph(el, celda), Paragraph(cont, celda),
                  Paragraph(f'<link href="{url}">{url}</link>', enlace)])
filas.append([Paragraph("Repositorio completo", celda_b),
              Paragraph("Código, datos, documentos y log de commits por integrante", celda),
              Paragraph(f'<link href="{REPO}">{REPO}</link>', enlace)])

t = Table(filas, colWidths=[4.3 * cm, 5.2 * cm, 6.5 * cm], repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8edf5")),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8a94a6")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
h += [t]

# ---- Resultados
titulo_res = Paragraph("3. Resultados principales", h1)
res =[["Métrica", "Valor"],
       ["Exactitud en prueba (1 250 registros)", "83,4 %"],
       ["Validación cruzada 5-fold", "83,4 % ± 0,8"],
       ["Modelo base (clase mayoritaria)", "34,4 %"],
       ["Pruebas automatizadas aprobadas", "16 de 16"],
       ["Variable más importante", "hora del día (0,445)"]]
t2 = Table(res, colWidths=[9 * cm, 5 * cm])
t2.setStyle(TableStyle([
    ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"), ("FONTSIZE", (0, 0), (-1, -1), 10.5),
    ("FONTNAME", (0, 0), (-1, 0), "Times-Bold"),
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8edf5")),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#8a94a6")),
    ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
]))
h += [KeepTogether([titulo_res, t2])]

h += [Paragraph("4. Referencia", h1),
      Paragraph("Palma Méndez, J. T. (2008). <i>Inteligencia artificial: métodos, técnicas y "
                "aplicaciones</i> (cap. 17: Aprendizaje de árboles y reglas de decisión). "
                "Madrid: McGraw-Hill España.", base)]

doc.build(h, onFirstPage=lambda c, d: None, onLaterPages=encabezado_pie)
print("Generado: Entrega_Actividad_3.pdf")
