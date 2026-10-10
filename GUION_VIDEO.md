# Guion del video (máx. 10 minutos)

Deben intervenir **los tres integrantes**. Sugerencia de reparto con tiempos; ajusten los nombres como prefieran. Graben la pantalla con el código y los resultados abiertos (VS Code o terminal + carpeta `resultados/`).

| Min | Quién | Contenido | Qué mostrar en pantalla |
|---|---|---|---|
| 0:00–1:00 | Integrante 1 | Saludo, nombres, curso y objetivo: predecir el nivel de ocupación (bajo/medio/alto) de una estación del sistema de transporte de la Actividad 2 con aprendizaje supervisado | Portada / README |
| 1:00–2:30 | Integrante 1 | Problema y datos: por qué clasificación, fuentes reales (Datos Abiertos Bogotá, IDEAM, festivos) y por qué usamos una muestra sintética | `DESCRIPCION_DATOS.md`, tabla de fuentes |
| 2:30–4:00 | Integrante 2 | Cómo se generó el dataset y su diccionario: variables, reglas, ruido, clases | `generar_dataset.py` y las primeras filas del CSV |
| 4:00–6:30 | Integrante 2 | Código del modelo paso a paso: limpieza, one-hot, **exclusión de `ocupacion_pct` para evitar fuga de datos**, partición 75/25 estratificada, árbol con GridSearchCV | `modelo_arbol_decision.py`, ejecutar el script |
| 6:30–8:30 | Integrante 3 | Resultados: exactitud 83,4 % vs 34,4 % del modelo base, matriz de confusión (errores entre clases vecinas), importancia de variables, reglas del árbol | `resultados/*.png`, `reglas_decision.txt`, `metricas.json` |
| 8:30–9:15 | Integrante 3 | Pruebas: ejecutar `python -m unittest pruebas_modelo -v` y mostrar 16/16 en OK | Terminal |
| 9:15–10:00 | Todos (una frase cada uno) | Conclusiones, limitaciones (datos sintéticos) y trabajo futuro (datos reales, Random Forest, integrar con la ruta A* de la Actividad 2) | Cierre |

## Ideas clave para explicar

- **Aprendizaje supervisado:** hay una etiqueta conocida (`nivel_ocupacion`) y el modelo aprende la relación entrada → etiqueta a partir de ejemplos.
- **Árbol de decisión (Palma Méndez, cap. 17):** divide los datos con preguntas del tipo "¿hora ≤ 8,5?" y cada camino raíz-hoja es una regla SI–ENTONCES, igual de legible que las reglas de la Actividad 2.
- **Fuga de datos:** si el modelo viera `ocupacion_pct`, acertaría casi el 100 % sin aprender nada útil.
- **Sobreajuste:** se controla con validación cruzada y comparando entrenamiento/prueba.
- **Lectura honesta de resultados:** los datos son sintéticos, así que el 83 % demuestra que el pipeline funciona, no que se predice bien la realidad.

## Antes de subir el video

- [ ] Se escucha y se ve bien el código (aumentar el tamaño de letra).
- [ ] Participan los tres integrantes.
- [ ] Dura 10 minutos o menos.
- [ ] El enlace es accesible para el tutor (YouTube "no listado" o Drive con acceso por enlace).
