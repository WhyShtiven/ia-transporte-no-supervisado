"""
pruebas_modelo.py
-----------------
Pruebas automatizadas del componente de aprendizaje supervisado.
Ejecutar DESPUÉS de generar_dataset.py y modelo_arbol_decision.py:

    python -m unittest pruebas_modelo -v
"""
import json
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

BASE = Path(__file__).parent
CSV = BASE / "datos" / "ocupacion_transporte.csv"
RES = BASE / "resultados"

ESTACIONES_VALIDAS = {
    "Portal Norte", "Calle 127", "Usaquen", "Calle 100", "Calle 72",
    "Calle 45", "Centro", "Av. Jimenez", "Portal Sur",
}
LINEAS_VALIDAS = {"B1", "B2", "C1", "D1", "E1"}
CLASES = {"bajo", "medio", "alto"}


def _fila_modelo(columnas, **valores):
    """Construye una fila con todas las columnas del modelo en 0 y aplica valores."""
    fila = {c: 0 for c in columnas}
    fila.update(valores)
    return pd.DataFrame([fila])[columnas]


class PruebasDataset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = pd.read_csv(CSV)

    def test_01_tiene_columnas_esperadas(self):
        esperadas = {"estacion", "linea", "zona", "hora", "dia_semana",
                     "es_fin_de_semana", "es_festivo", "llueve", "temperatura_c",
                     "evento_especial", "buses_por_hora", "ocupacion_pct",
                     "nivel_ocupacion"}
        self.assertEqual(set(self.df.columns), esperadas)

    def test_02_tamano_minimo(self):
        self.assertGreaterEqual(len(self.df), 1000)

    def test_03_estaciones_y_lineas_del_proyecto(self):
        self.assertTrue(set(self.df["estacion"]) <= ESTACIONES_VALIDAS)
        self.assertTrue(set(self.df["linea"]) <= LINEAS_VALIDAS)

    def test_04_rangos_validos(self):
        self.assertTrue(self.df["hora"].between(0, 23).all())
        self.assertTrue(self.df["dia_semana"].between(0, 6).all())
        self.assertTrue(self.df["ocupacion_pct"].between(0, 150).all())
        for col in ["es_fin_de_semana", "es_festivo", "llueve", "evento_especial"]:
            self.assertTrue(set(self.df[col].unique()) <= {0, 1}, col)

    def test_05_clases_validas_y_balance_razonable(self):
        self.assertEqual(set(self.df["nivel_ocupacion"]), CLASES)
        proporciones = self.df["nivel_ocupacion"].value_counts(normalize=True)
        self.assertGreater(proporciones.min(), 0.15, "una clase está casi vacía")

    def test_06_etiqueta_consistente_con_ocupacion(self):
        bajo = self.df[self.df.nivel_ocupacion == "bajo"]["ocupacion_pct"]
        alto = self.df[self.df.nivel_ocupacion == "alto"]["ocupacion_pct"]
        self.assertTrue((bajo < 55).all())
        self.assertTrue((alto >= 85).all())

    def test_07_faltantes_controlados(self):
        self.assertLess(self.df["temperatura_c"].isna().mean(), 0.05)
        self.assertEqual(self.df.drop(columns="temperatura_c").isna().sum().sum(), 0)


class PruebasModelo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        paquete = joblib.load(RES / "modelo_arbol.joblib")
        cls.modelo = paquete["modelo"]
        cls.columnas = paquete["columnas"]
        cls.metricas = json.loads((RES / "metricas.json").read_text(encoding="utf-8"))

    def test_08_exactitud_supera_al_modelo_base(self):
        self.assertGreater(self.metricas["exactitud_prueba"],
                           self.metricas["exactitud_modelo_base"] + 0.30)

    def test_09_exactitud_minima_aceptable(self):
        self.assertGreaterEqual(self.metricas["exactitud_prueba"], 0.75)

    def test_10_sin_sobreajuste_grave(self):
        brecha = abs(self.metricas["exactitud_cv_gridsearch"]
                     - self.metricas["exactitud_prueba"])
        self.assertLess(brecha, 0.05)

    def test_11_prediccion_devuelve_clase_valida(self):
        fila = _fila_modelo(self.columnas, hora=12, buses_por_hora=20,
                            temperatura_c=17.0)
        self.assertIn(self.modelo.predict(fila)[0], CLASES)

    def test_12_hora_pico_manana_en_portal_es_alta(self):
        fila = _fila_modelo(self.columnas, hora=7, dia_semana=1, llueve=1,
                            temperatura_c=14.0, buses_por_hora=10,
                            **{"estacion_Portal Norte": 1, "linea_B1": 1,
                               "zona_portal": 1})
        self.assertEqual(self.modelo.predict(fila)[0], "alto")

    def test_13_domingo_en_la_noche_es_bajo(self):
        fila = _fila_modelo(self.columnas, hora=22, dia_semana=6,
                            es_fin_de_semana=1, temperatura_c=15.0,
                            buses_por_hora=30,
                            **{"estacion_Usaquen": 1, "linea_D1": 1,
                               "zona_norte": 1})
        self.assertEqual(self.modelo.predict(fila)[0], "bajo")

    def test_14_mas_buses_no_aumenta_la_ocupacion(self):
        """Con todo lo demás igual, más oferta de buses no debe empeorar el nivel."""
        orden = {"bajo": 0, "medio": 1, "alto": 2}
        base = dict(hora=8, dia_semana=2, temperatura_c=16.0,
                    **{"estacion_Calle 72": 1, "linea_B1": 1, "zona_centro": 1})
        poca = self.modelo.predict(_fila_modelo(self.columnas, buses_por_hora=8, **base))[0]
        mucha = self.modelo.predict(_fila_modelo(self.columnas, buses_por_hora=40, **base))[0]
        self.assertLessEqual(orden[mucha], orden[poca])

    def test_15_hora_es_la_variable_mas_importante(self):
        imp = pd.Series(self.modelo.feature_importances_, index=self.columnas)
        self.assertEqual(imp.idxmax(), "hora")

    def test_16_reproducibilidad_del_dataset(self):
        """Con la misma semilla el generador produce el mismo conjunto de datos."""
        import subprocess, sys, tempfile, shutil
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copy(BASE / "generar_dataset.py", tmp)
            subprocess.run([sys.executable, str(Path(tmp) / "generar_dataset.py")],
                           check=True, capture_output=True)
            nuevo = pd.read_csv(Path(tmp) / "datos" / "ocupacion_transporte.csv")
        original = pd.read_csv(CSV)
        pd.testing.assert_frame_equal(nuevo, original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
