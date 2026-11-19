# CYCLOPS - Autonomous Phishing Detection Architecture

Plataforma empresarial de arquitectura monolitica modular para la deteccion proactiva de amenazas de ingenieria social, clasificacion inteligente de correos maliciosos y mitigacion autonoma orientada al usuario final mediante Machine Learning.

---

## 1. Resumen Ejecutivo y Alcance

**CYCLOPS** es un sistema de defensa contra el fraude cibernetico por suplantacion de identidad, phishing y vectores coercitivos transmitidos por correo electronico. 

A diferencia de las arquitecturas tradicionales que dependen de un centro de operaciones de seguridad y analistas humanos para revisar incidentes, **CYCLOPS** entrega un diagnostico autonomo e instantaneo directamente al usuario final. La arquitectura procesa el mensaje en microsegundos, aisla indicadores coercitivos y ofrece un veredicto estructurado en cuatro niveles de decision.

* **Autor:** Cristian Díaz
* **Disciplina:** Mineria de Datos y Arquitectura de Sistemas de Inteligencia Artificial
* **Base de Conocimiento Notion:** https://app.notion.com/p/CYCLOPS-3e959de529f58051b74efe5d873eea90?source=copy_link
* **Repositorio de Datasets en Google Drive:** https://drive.google.com/drive/folders/1j3hjgW__ssZssPMRjrJVJT5CMo59T3YM?usp=sharing

---

## 2. Arquitectura del Sistema - Monolito Modular Limpio

El proyecto esta construido bajo principios de Clean Architecture y Monolito Modular, garantizando bajo acoplamiento, alta cohesion y reproducibilidad tanto a nivel academico como corporativo.

```text
CYCLOPS/
├── data/
│   ├── raw/                        # Datasets originales heterogeneos
│   └── processed/                  # Dataset unificado y limpio - 91,992 registros
├── docs/                           # Documentacion formal corporativa
│   ├── Plan_de_Auditoria_CYCLOPS_APA7.docx  # Documento formal bajo norma APA 7
│   ├── audit_plan.md               # Especificacion del plan de auditoria
│   ├── architecture.md             # Diagramas y decisiones de diseno
│   ├── prd.md                      # Product Requirements Document
│   └── user_stories.md             # Historias de usuario y criterios de aceptacion
├── models/                         # Modelos entrenados y serializados
│   ├── decision_tree_model.joblib  # Clasificador supervisado principal
│   ├── robust_scaler.joblib        # Escalador entrenado para valores atipicos
│   └── kmeans_model.joblib         # Modelo de segmentacion no supervisada K=3
├── notebooks/                      # Cuadernos de experimentacion y validacion
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_supervised_learning_benchmark.ipynb
│   └── 03_unsupervised_clustering.ipynb
├── src/                            # Codigo fuente modular
│   ├── data_pipeline/              # Ingesta, limpieza y feature engineering
│   ├── domain/                     # Modelos y entidades de negocio puras
│   ├── engine/                     # Motor central de inferencia y escalado
│   └── infrastructure/             # Conexiones de base de datos y persistencia
├── static/                         # Frontend estatico de alto desempeno
│   ├── css/style.css               # Diseno visual moderno sin dependencias pesadas
│   └── js/app.js                   # Logica reactiva e integracion asincrona
├── templates/
│   └── index.html                  # Interfaz grafica centrada en el usuario final
├── app.py                          # Servidor web y endpoints REST API
├── cyclops_engine.py               # Motor de inferencia y clasificacion en produccion
├── verify_no_parens.py             # Script de aseguramiento de calidad de codigo
└── requirements.txt                # Dependencias enterprise verificadas
```

---

## 3. Pipeline de Datos y Preprocesamiento

El pipeline unifica tres fuentes heterogeneas de datos de ciberseguridad, consolidando un universo de **91,992 muestras** balanceadas entre correos legitimos y amenazas reales.

* **Extraccion de Metricas Cuantitativas:** Longitud de caracteres, conteo de palabras, presencia y conteo de hipervinculos, presencia de direcciones IP y puntuacion ponderada de urgencia coercitiva.
* **Ingenieria de Densidades:** Calculo de densidad de enlaces y densidad de urgencia normalizadas por longitud textual.
* **Escalado Robusto con RobustScaler:** Se selecciono RobustScaler frente a StandardScaler y MinMaxScaler debido a la presencia extrema de valores atipicos y distribuciones con asimetria positiva severa en el trafico malicioso. RobustScaler sustrae la mediana y escala segun el rango intercuartil IQR, impidiendo que ataques con textos desproporcionadamente extensos distorsionen el modelo.
* **Particion Estratificada:** Division estricta 80% entrenamiento y 20% evaluacion sin fuga de datos.

---

## 4. Benchmark de Algoritmos Supervisados

Se realizo una comparativa cuantitativa rigurosa entre tres familias de algoritmos sobre el conjunto de prueba independiente de 18,399 muestras.

| Algoritmo | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Latencia por Muestra |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Arbol de Decision** | **73.71%** | **70.24%** | **74.19%** | **72.16%** | **74.22%** | **0.0001 ms** |
| K-Nearest Neighbors - KNN | 73.61% | 68.95% | 77.16% | 72.82% | 76.54% | 0.0093 ms |
| Gaussian Naive Bayes | 51.27% | 52.48% | 1.00% | 1.98% | 63.85% | 0.0002 ms |

### Conclusiones Tecnicas del Benchmark

1. **Predileccion por el Arbol de Decision:**
   * **Equilibrio Operativo:** Excelente balance entre precision, sensibilidad y F1-Score general de 72.16%.
   * **Velocidad de Inferencia en Tiempo Real:** Latencia de ejecucion inferior a 0.0001 ms por correo, garantizando respuesta instantanea.
   * **Inteligencia Artificial Explicable - XAI:** Permite auditar exactamente que variables causaron la activacion de la alerta. Las variables con mayor peso predictivo son:
     * Conteo total de caracteres: 37.9% de importancia relativa.
     * Conteo y densidad de hipervinculos: 18.1% de importancia relativa.
     * Nivel de urgencia coercitiva: 16.4% de importancia relativa.

2. **Descarte de K-Nearest Neighbors - KNN:**
   * Aunque obtuvo metricas predictivas similares, KNN requiere calcular distancias euclidianas contra mas de 73,000 vectores de entrenamiento en memoria RAM para cada clasificacion.
   * Esto provoco una latencia casi 100 veces mayor, resultando inviable para pasarelas de correo empresariales con alto volumen de transacciones por segundo.

3. **Colapso de Gaussian Naive Bayes:**
   * Naive Bayes colapso con un F1-Score de apenas 1.98% y un Recall del 1.00%, clasificando casi todo el trafico como legitimo.
   * Esto se debio a la violacion frontal de sus supuestos matematicos: las caracteristicas de ciberseguridad estan fuertemente correlacionadas y presentan distribuciones con inflacion de ceros que no siguen una campana de Gauss.

---

## 5. Segmentacion No Supervisada - K-Means Clustering

Para descubrir patrones ocultos sin intervencion de etiquetas humanas, se implemento un modelo de clustering K-Means sobre las variables normalizadas. Mediante el Metodo del Codo se determino un valor optimo de **K = 3 clusters**.

| Cluster | Descripcion del Patron | Total Muestras | Tasa de Phishing | Promedio Enlaces | Promedio Urgencia |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **Cluster 0** | Trafico Corporativo Habitual | 60,634 | 33.72% | 0.12 | 0.28 |
| **Cluster 1** | Comunicados Masivos y Boletines | 1,489 | 43.12% | 0.85 | 1.15 |
| **Cluster 2** | Vectores Dirigidos con Enlaces Maliciosos | 29,869 | **98.88%** | **2.65** | **4.82** |

El **Cluster 2** aislo de forma no supervisada el 98.88% de los correos maliciosos caracterizados por el uso simultaneo de hipervinculos y lenguaje de urgencia. Esta clasificacion alimenta el motor en produccion para robustecer el veredicto entregado al usuario.

---

## 6. Motor de Decision en Cuatro Niveles

La clasificacion de cada mensaje atraviesa cuatro etapas verificables en la interfaz grafica:

1. **Nivel 1 - Ingesta y Preprocesamiento NLP:** Conteo de longitud, palabras, extraccion de URLs y analisis de terminos coercitivos.
2. **Nivel 2 - Extraccion de Metricas y Escalado Robusto:** Transformacion de densidades mediante RobustScaler para aislar valores atipicos.
3. **Nivel 3 - Inferencia Probabilistica y Perfilamiento:** Evaluacion simultanea con el Arbol de Decision y asignacion de cluster K-Means.
4. **Nivel 4 - Diagnostico y Mitigacion Directa al Usuario:** Emision de una recomendacion clara para el usuario, clasificando el riesgo en Bajo, Medio o Critico con instrucciones accionables.

---

## 7. Instrucciones de Instalacion y Ejecucion

### Requisitos Previos
* Python 3.10 o superior instalado.

### Instalacion de Dependencias
```bash
pip install -r requirements.txt
```

### Ejecucion del Sistema Web
```bash
python app.py
```
El servidor estara disponible de forma local en:
`http://localhost:5000`

### Verificacion de Calidad de Codigo y Estilo
Para verificar la ausencia de caracteres conflictivos y validar la limpieza integral del repositorio:
```bash
python verify_no_parens.py
```

---

## 8. Documentacion Formal y Auditoria

Dentro del directorio `docs/` se encuentran disponibles los siguientes entregables institucionales:

* `Plan_de_Auditoria_CYCLOPS_APA7.docx`: Documento formal en formato Microsoft Word estructurado segun las normas APA 7ma edicion, detallando el alcance de auditoria, gestion de riesgos, protocolos de calidad y arquitectura de software.
* `audit_plan.md`: Registro tecnico detallado del plan de auditoria y verificacion de buenas practicas.
* `architecture.md`: Especificacion de diseno y decisiones arquitectonicas.
* `prd.md`: Documento de requisitos del producto y definicion del problema.
* `user_stories.md`: Historias de usuario bajo metodologia agil.

---

## 9. Sincronizacion con Proyecto Electivo Framework IA

El modulo central y los modelos serializados aqui consolidados sirven como base tecnica para el proyecto complementario ubicado en el repositorio `frameworkIa`, garantizando coherencia de datos y consistencia analitica en ambas asignaturas.
