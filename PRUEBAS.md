# Pruebas realizadas al componente

Actividad 3 – Aprendizaje supervisado · Inteligencia Artificial

Las pruebas se ejecutan con:

```bash
python generar_dataset.py
python modelo_arbol_decision.py
python -m unittest pruebas_modelo -v
```

Archivo de pruebas: `pruebas_modelo.py`. La salida completa de la última ejecución está en `resultados/salida_pruebas.txt`.

**Resultado: 16 pruebas ejecutadas, 16 aprobadas.**

## 1. Pruebas sobre los datos

| # | Prueba | Qué verifica | Resultado |
|---|---|---|---|
| 01 | Columnas esperadas | El CSV tiene exactamente las 13 columnas del diccionario | OK |
| 02 | Tamaño mínimo | Al menos 1 000 filas (hay 5 000) | OK |
| 03 | Estaciones y líneas | Solo aparecen las 9 estaciones y 5 líneas del proyecto | OK |
| 04 | Rangos válidos | Hora 0–23, día 0–6, ocupación 0–150, binarias solo 0/1 | OK |
| 05 | Clases y balance | Existen las 3 clases y ninguna tiene menos del 15 % | OK |
| 06 | Etiqueta coherente | Todo "bajo" tiene ocupación < 55 y todo "alto" ≥ 85 | OK |
| 07 | Faltantes controlados | Solo `temperatura_c` tiene vacíos y son menos del 5 % | OK |

## 2. Pruebas sobre el modelo

| # | Prueba | Qué verifica | Resultado |
|---|---|---|---|
| 08 | Supera al modelo base | Exactitud en prueba > base + 0,30 (0,834 vs 0,344) | OK |
| 09 | Exactitud mínima | Exactitud en prueba ≥ 0,75 | OK |
| 10 | Sin sobreajuste grave | Diferencia entre validación cruzada y prueba < 0,05 (0,008) | OK |
| 11 | Predicción válida | Para una entrada cualquiera devuelve bajo, medio o alto | OK |
| 12 | Caso de hora pico | Portal Norte, martes 7:00, lluvia, 10 buses/h → **alto** | OK |
| 13 | Caso de baja demanda | Usaquén, domingo 22:00, 30 buses/h → **bajo** | OK |
| 14 | Coherencia de oferta | Con lo demás igual, 40 buses/h no da mayor ocupación que 8 buses/h | OK |
| 15 | Variable dominante | `hora` es la variable más importante del árbol | OK |
| 16 | Reproducibilidad | Con la misma semilla, el generador produce un CSV idéntico | OK |

## 3. Métricas del modelo (conjunto de prueba, 1 250 registros)

Modelo: `DecisionTreeClassifier` con criterio `entropy`, `max_depth=10`, `min_samples_leaf=1`, elegido por búsqueda en rejilla con validación cruzada de 5 particiones (profundidad final 10, 228 hojas).

| Métrica | Valor |
|---|---|
| Exactitud en prueba | **0,834** |
| Exactitud validación cruzada 5-fold | 0,834 ± 0,008 |
| Exactitud de la rejilla (mejor combinación) | 0,826 |
| Exactitud del modelo base (clase mayoritaria) | 0,344 |

| Clase | Precisión | Sensibilidad | F1 | Soporte |
|---|---|---|---|---|
| bajo | 0,855 | 0,863 | 0,859 | 410 |
| medio | 0,728 | 0,798 | 0,761 | 410 |
| alto | 0,933 | 0,840 | 0,884 | 430 |

**Matriz de confusión** (`resultados/matriz_confusion.png`):

| Real \ Predicho | bajo | medio | alto |
|---|---|---|---|
| bajo | 354 | 55 | 1 |
| medio | 58 | 327 | 25 |
| alto | 2 | 67 | 361 |

## 4. Análisis de resultados

- El modelo duplica con creces la exactitud del modelo base, así que aprende patrones reales del dataset.
- **Los errores ocurren casi siempre entre clases vecinas.** Solo 3 de 840 registros bajo/alto se confunden entre sí (1 + 2); la mayoría de los fallos están en la frontera bajo↔medio y medio↔alto. Esto es esperable porque las clases salen de cortar una ocupación continua con ruido.
- La clase **medio** es la más difícil (F1 0,761) por ser la intermedia.
- Variables más importantes: `hora` (0,445), `buses_por_hora` (0,132), `es_fin_de_semana` (0,086), `llueve` (0,071) y `evento_especial` (0,068). Coincide con las reglas con que se construyó el dataset, lo que valida el pipeline.
- Las reglas legibles del árbol están en `resultados/reglas_decision.txt` y su gráfico en `resultados/arbol_decision.png` (primeros 3 niveles).

## 5. Limitaciones de las pruebas

- Los datos son sintéticos, por lo que estas métricas **no se pueden extrapolar** a la operación real.
- Un árbol de profundidad 10 con 228 hojas es poco interpretable en su totalidad; para explicarlo se usan los primeros niveles y la importancia de variables.
- Como mejora futura se podría comparar con Random Forest o Gradient Boosting y evaluar con datos reales por fecha (partición temporal).
