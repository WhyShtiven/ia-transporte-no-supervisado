"""
modelo_arbol_decision.py
------------------------
Aprendizaje supervisado (clasificación) con árboles de decisión para predecir
el nivel de ocupación (bajo/medio/alto) de una estación de transporte masivo.

Pasos:
  1. Carga y exploración del dataset
  2. Limpieza y codificación de variables
  3. División entrenamiento/prueba (estratificada)
  4. Entrenamiento de un árbol con poda (max_depth) y búsqueda de hiperparámetros
  5. Evaluación: exactitud, matriz de confusión, reporte por clase, validación cruzada
  6. Reglas de decisión legibles (Cap. 17, Palma Méndez) e importancia de variables
  7. Comparación con un modelo base (clase mayoritaria)
  8. Guardado de resultados y modelo

Uso:
    python modelo_arbol_decision.py
"""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, ConfusionMatrixDisplay)

BASE = Path(__file__).parent
RUTA_DATOS = BASE / "datos" / "ocupacion_transporte.csv"
RUTA_RES = BASE / "resultados"
RUTA_RES.mkdir(exist_ok=True)
SEMILLA = 42

# ---------------------------------------------------------------- 1. Carga
df = pd.read_csv(RUTA_DATOS)
print("Dimensiones:", df.shape)
print("\nValores nulos por columna:\n", df.isna().sum())
print("\nDistribución de la clase objetivo:\n",
      df["nivel_ocupacion"].value_counts(normalize=True).round(3))

# ---------------------------------------------------------------- 2. Limpieza
# Imputamos temperatura con la mediana (pocos faltantes)
df["temperatura_c"] = df["temperatura_c"].fillna(df["temperatura_c"].median())

# 'ocupacion_pct' define directamente la clase: se EXCLUYE para evitar fuga de datos
X = df.drop(columns=["nivel_ocupacion", "ocupacion_pct"])
y = df["nivel_ocupacion"]

# Codificación one-hot de variables categóricas
X = pd.get_dummies(X, columns=["estacion", "linea", "zona"], drop_first=False)

# ---------------------------------------------------------------- 3. Partición
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=SEMILLA, stratify=y
)
print(f"\nEntrenamiento: {X_train.shape[0]} | Prueba: {X_test.shape[0]}")

# ---------------------------------------------------------------- 4. Entrenamiento
rejilla = {
    "max_depth": [3, 4, 5, 6, 8, 10, None],
    "min_samples_leaf": [1, 5, 10, 20],
    "criterion": ["gini", "entropy"],
}
busqueda = GridSearchCV(
    DecisionTreeClassifier(random_state=SEMILLA),
    rejilla, cv=5, scoring="accuracy", n_jobs=-1,
)
busqueda.fit(X_train, y_train)
modelo = busqueda.best_estimator_
print("\nMejores hiperparámetros:", busqueda.best_params_)
print(f"Exactitud CV (mejor combinación): {busqueda.best_score_:.3f}")

# ---------------------------------------------------------------- 5. Evaluación
y_pred = modelo.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nExactitud en prueba: {acc:.3f}")
orden = ["bajo", "medio", "alto"]
print("\nReporte de clasificación:\n",
      classification_report(y_test, y_pred, labels=orden, digits=3))

cv_scores = cross_val_score(modelo, X, y, cv=5, scoring="accuracy")
print(f"Validación cruzada 5-fold: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")

# Modelo base
base = DummyClassifier(strategy="most_frequent").fit(X_train, y_train)
acc_base = accuracy_score(y_test, base.predict(X_test))
print(f"Exactitud modelo base (clase mayoritaria): {acc_base:.3f}")

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred, labels=orden)
fig, ax = plt.subplots(figsize=(5, 4))
ConfusionMatrixDisplay(cm, display_labels=orden).plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title("Matriz de confusión (conjunto de prueba)")
fig.tight_layout()
fig.savefig(RUTA_RES / "matriz_confusion.png", dpi=150)
plt.close(fig)

# ---------------------------------------------------------------- 6. Interpretación
importancias = (pd.Series(modelo.feature_importances_, index=X.columns)
                .sort_values(ascending=False))
print("\nTop 10 variables más importantes:\n", importancias.head(10).round(3))

fig, ax = plt.subplots(figsize=(7, 4.5))
importancias.head(10)[::-1].plot.barh(ax=ax, color="#2a6f97")
ax.set_title("Importancia de variables (top 10)")
ax.set_xlabel("Importancia")
fig.tight_layout()
fig.savefig(RUTA_RES / "importancia_variables.png", dpi=150)
plt.close(fig)

# Reglas de decisión en texto (limitamos profundidad para que sea legible)
reglas = export_text(modelo, feature_names=list(X.columns), max_depth=4)
(RUTA_RES / "reglas_decision.txt").write_text(reglas, encoding="utf-8")

# Gráfico del árbol (primeros niveles)
fig, ax = plt.subplots(figsize=(18, 8))
plot_tree(modelo, feature_names=list(X.columns), class_names=list(modelo.classes_),
          filled=True, rounded=True, max_depth=3, fontsize=7, ax=ax)
fig.tight_layout()
fig.savefig(RUTA_RES / "arbol_decision.png", dpi=130)
plt.close(fig)

# ---------------------------------------------------------------- 7. Guardado
joblib.dump({"modelo": modelo, "columnas": list(X.columns)}, RUTA_RES / "modelo_arbol.joblib")

metricas = {
    "mejores_hiperparametros": busqueda.best_params_,
    "exactitud_cv_gridsearch": round(float(busqueda.best_score_), 4),
    "exactitud_prueba": round(float(acc), 4),
    "exactitud_modelo_base": round(float(acc_base), 4),
    "cv5_media": round(float(cv_scores.mean()), 4),
    "cv5_desv": round(float(cv_scores.std()), 4),
    "profundidad_arbol": int(modelo.get_depth()),
    "numero_hojas": int(modelo.get_n_leaves()),
}
(RUTA_RES / "metricas.json").write_text(json.dumps(metricas, indent=2, ensure_ascii=False),
                                        encoding="utf-8")

# ---------------------------------------------------------------- 8. Ejemplo de uso
ejemplo = pd.DataFrame([{c: 0 for c in X.columns}])
ejemplo["hora"] = 7
ejemplo["dia_semana"] = 1
ejemplo["llueve"] = 1
ejemplo["temperatura_c"] = 14.0
ejemplo["buses_por_hora"] = 12
ejemplo["estacion_Portal Norte"] = 1
ejemplo["linea_B1"] = 1
ejemplo["zona_portal"] = 1
print("\nEjemplo: Portal Norte, martes 7:00 a. m., lloviendo, 12 buses/h ->",
      modelo.predict(ejemplo)[0])
print("\nResultados guardados en:", RUTA_RES)
