# PLAN DE AUDITORÍA TÉCNICA, CALIDAD DE DATOS Y SISTEMA ML

## CYCLOPS SENTINEL - SISTEMA AUTÓNOMO DE DETECCIÓN DE PHISHING PARA USUARIOS FINALES

---

### INFORMACIÓN DEL DOCUMENTO

* **Proyecto:** CYCLOPS SENTINEL
* **Versión del Plan:** 2.0 - Arquitectura Unificada Centrada en el Usuario Final
* **Autor y Responsable:** Cristian Díaz
* **Fecha de Emisión:** 15 de Noviembre de 2026
* **Tipo de Auditoría:** Técnica, Algorítmica, Calidad de Datos y Seguridad del Software
* **Estado:** Aprobado para Ejecución de Entrega Final

---

## 1. INTRODUCCIÓN Y JUSTIFICACIÓN

El presente Plan de Auditoría establece las directrices, metodologías, criterios de aceptación y pruebas formales para evaluar el sistema **CYCLOPS SENTINEL**.

Tras el ajuste arquitectónico de optimización operativa, el sistema se enfoca de manera exclusiva y autónoma en el **Usuario Final**. Su objetivo primordial es brindar un diagnóstico inmediato, preciso y comprensible sobre correos sospechosos reportados por el usuario, sin intermediación humana ni dependencia de analistas de seguridad externos.

La auditoría garantiza que el pipeline de datos, el acondicionamiento con RobustScaler, el modelo de Machine Learning y la interfaz de usuario operen bajo los más altos estándares de rigor metodológico, privacidad de información y rendimiento computacional.

---

## 2. OBJETIVOS DE LA AUDITORÍA

### 2.1 Objetivo General

Evaluar y certificar de manera integral la calidad de los datos, la robustez del modelo de aprendizaje automático, la precisión diagnóstica, la seguridad en el tratamiento de información y la usabilidad de la plataforma CYCLOPS SENTINEL orientada al usuario corporativo.

### 2.2 Objetivos Específicos

1. **Auditoría del Pipeline de Datos:** Verificar la integridad de la unificación de los tres datasets fuente, la efectividad del proceso de anonimización de identificadores personales e IPs, y la consistencia de las métricas extraídas.
2. **Auditoría del Acondicionamiento Estadístico:** Comprobar la correcta aplicación de RobustScaler, garantizando la prevención estricta de fuga de datos mediante el ajuste exclusivo sobre el conjunto de entrenamiento.
3. **Auditoría del Modelo y Diagnóstico Autónomo:** Evaluar las métricas de rendimiento del clasificador supervisado y asegurar que el veredicto entregado al usuario sea confiable, determinístico y explicable.
4. **Auditoría de Rendimiento y Experiencia de Usuario:** Medir los tiempos de respuesta de la inferencia en tiempo real y validar que la interfaz gráfica sea intuitiva, accesible y libre de fricciones operativas.
5. **Auditoría de Cumplimiento de Restricciones Técnicas:** Verificar la adhesión estricta a las reglas de estilo de código, arquitectura modular limpia y ausencia total de caracteres no permitidos según la especificación del proyecto.

---

## 3. ALCANCE DE LA AUDITORÍA

### 3.1 Componentes en Alcance

* **Módulo de Ingesta y Datos:** Archivos de datos crudos y procesados, scripts de unificación, limpieza léxica y extracción de características cuantitativas.
* **Módulo de Transformación:** Artefacto serializado de RobustScaler y validación de rangos intercuartílicos frente a valores atípicos.
* **Módulo de Inferencia:** Algoritmo clasificador de Machine Learning, cálculo de probabilidades y categorización directa de riesgo para el usuario.
* **Módulo de Explicabilidad:** Desglose secuencial de los niveles de evaluación y recomendaciones preventivas inmediatas para el usuario.
* **Aplicación Web:** Endpoints REST de análisis, interfaz gráfica interactiva del usuario y scripts de validación estática.

### 3.2 Componentes Fuera de Alcance

* Interfaces de triaje manual para terceros o consolas de analistas externos, ya que el sistema es completamente autónomo y autosuficiente para el usuario final.
* Integraciones con herramientas de orquestación complejas que requieran supervisión humana manual.

---

## 4. MARCO NORMATIVO Y ESTÁNDARES DE REFERENCIA

La auditoría se estructura considerando las directrices de los siguientes marcos de referencia reconocidos en la industria:

* **ISO/IEC 25010:** Modelo de calidad de producto de software, evaluando adecuación funcional, eficiencia de desempeño, usabilidad y fiabilidad.
* **ISO/IEC 27001 / GDPR:** Principios de confidencialidad, minimización de datos y anonimización de información de identificación personal.
* **NIST AI Risk Management Framework - NIST AI RMF 1.0:** Gobernanza, explicabilidad, precisión y mitigación de riesgos en sistemas de inteligencia artificial.
* **Principios de Ingeniería de Machine Learning - MLOps:** Prevención de data leakage, reproducibilidad del pipeline y persistencia controlada de artefactos.

---

## 5. MATRIZ DE CONTROLES, PRUEBAS Y CRITERIOS DE ACEPTACIÓN

A continuación se detalla la matriz de auditoría con los controles específicos que deben ejecutarse y superarse para la entrega final:

| Identificador        | Dominio de Control                      | Descripción de la Prueba                                                                                                                                       | Criterio de Aceptación                                                                                                    | Evidencia Requerida                                                                 |
| :------------------- | :-------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------- |
| **AUD-DAT-01** | Integridad de Datos                     | Verificar la consolidación de los tres datasets fuente: correos corporativos, correos de phishing y mensajes sms spam.                                         | Unión coherente sin registros vacíos ni etiquetas contradictorias. Balance razonable de clases.                          | Script de unificación y reporte descriptivo de distribución.                      |
| **AUD-DAT-02** | Anonimización y Privacidad             | Comprobar que los textos procesados enmascaren direcciones IP, correos electrónicos reales y datos sensibles.                                                  | Cero presencia de direcciones IP públicas reales o nombres identificables en los datasets procesados.                     | Muestreo aleatorio en `clean_dataset.csv` y expresiones regulares de validación. |
| **AUD-DAT-03** | Extracción de Métricas                | Validar que las funciones de ingeniería de características calculen correctamente: conteo de caracteres, palabras, cantidad de enlaces y puntaje de urgencia. | Consistencia matemática entre el texto crudo y el vector de características numéricas generado.                         | Pruebas unitarias de extracción con textos de longitud y formato variable.         |
| **AUD-SCL-01** | Control de Outliers con RobustScaler    | Evaluar el comportamiento del escalador ante correos con conteos extremos de caracteres o hipervínculos atípicos.                                             | Las variables escaladas deben utilizar la mediana y el rango intercuartílico sin ser distorsionadas por valores extremos. | Gráficos de distribución de variables antes y después del escalado en notebooks. |
| **AUD-SCL-02** | Prevención de Fuga de Datos            | Constatar que el ajuste de RobustScaler se realice únicamente con el 80% de datos de entrenamiento.                                                            | Cero filtración de parámetros estadísticos del conjunto de prueba en la etapa de entrenamiento.                         | Código fuente de entrenamiento con separación estricta mediante train_test_split. |
| **AUD-MOD-01** | Precisión y Desempeño del Modelo      | Medir las métricas de clasificación del modelo supervisado: Accuracy, Precision, Recall y F1-Score.                                                           | F1-Score superior al 85% en detección de phishing para minimizar falsos negativos críticos para el usuario.              | Matriz de confusión y reporte de clasificación exportado en Jupyter Notebook.     |
| **AUD-MOD-02** | Diagnóstico Autónomo Directo          | Validar que el motor determine con claridad si el mensaje es Phishing o Legítimo, entregando una probabilidad precisa.                                         | Salida binaria definitiva orientada al usuario sin derivación a revisiones intermedias ambiguas.                          | Pruebas de integración con los casos de prueba de alta, media y baja urgencia.     |
| **AUD-EXP-01** | Explicabilidad para el Usuario          | Verificar que el sistema explique con lenguaje claro por qué un mensaje fue catalogado como amenaza.                                                           | Presentación de factores detonantes: inductores de urgencia coercitiva, hipervínculos anómalos o suplantación.         | Captura de pantalla de la interfaz con el panel de diagnóstico detallado.          |
| **AUD-PRF-01** | Latencia y Rendimiento                  | Medir el tiempo total de respuesta desde la solicitud de análisis del usuario hasta la visualización del veredicto.                                           | Tiempo de ejecución total inferior a 200 milisegundos por mensaje evaluado.                                               | Logs de tiempo en milisegundos generados por el endpoint `/api/analyze`.          |
| **AUD-SEC-01** | Seguridad y Manejo de Errores           | Comprobar que entradas maliciosas, inyecciones de código o mensajes vacíos no provoquen caídas en el servidor.                                               | Validación estricta de entradas y respuestas HTTP con códigos de estado coherentes.                                      | Pruebas de caja negra con payloads inválidos y textos de gran tamaño.             |
| **AUD-COD-01** | Cumplimiento de Restricciones de Estilo | Ejecutar la auditoría estática sobre archivos web y código Python para verificar la ausencia total de signos de paréntesis.                                 | 100% de cumplimiento reportado por `verify_no_parens.py` en textos visibles, etiquetas, comentarios y literales.         | Salida de terminal limpia del script `verify_no_parens.py`.                       |

---

## 6. METODOLOGÍA Y PROCEDIMIENTO DE EJECUCIÓN

La auditoría se desarrolla en tres etapas cronológicas secuenciales:

```
┌────────────────────────────────┐
│ 1. REVISIÓN ESTÁTICA Y DE DATOS│ -> Auditoría de datasets, código fuente y notebooks
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ 2. PRUEBAS DINÁMICAS Y DE ML   │ -> Ejecución del pipeline, métricas del modelo y RobustScaler
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ 3. EVALUACIÓN DE LA INTERFAZ   │ -> Pruebas de usuario, latencia, explicabilidad y estilo
└────────────────────────────────┘
```

1. **Etapa de Inspección Estática:**

   * Revisión de la documentación arquitectónica en `mi-framework-ia/docs/`.
   * Ejecución del script `verify_no_parens.py` para asegurar cumplimiento absoluto de restricciones de formato.
   * Inspección visual de scripts de datos en búsqueda de buenas prácticas de programación.
2. **Etapa de Validación Experimental de Machine Learning:**

   * Revisión de los notebooks de análisis exploratorio (`descriptive_graphs.ipynb`, `heatmap.ipynb`, `arbol_de.ipynb`).
   * Evaluación de la correlación de características y efectividad de las densidades sintéticas.
   * Confirmación del almacenamiento y carga del transformador serializado `robust_scaler.pkl`.
3. **Etapa de Verificación de Integración y Experiencia del Usuario:**

   * Despliegue local de la aplicación interactiva.
   * Ejecución de pruebas funcionales utilizando las plantillas de prueba del usuario:
     * Caso A: Correo de extorsión y urgencia bancaria con enlaces externos.
     * Caso B: Correo de alerta de credenciales con dominio sospechoso.
     * Caso C: Convocatoria legítima de trabajo en equipo.
     * Caso D: Notificación institucional ordinaria sin riesgos.
   * Verificación del tiempo de cómputo y claridad del veredicto final desplegado en pantalla.

---

## 7. CRITERIOS DE DICTAMEN FINAL

Para considerar el sistema CYCLOPS SENTINEL **APROBADO** en la auditoría de entrega final, se deberán cumplir simultáneamente las siguientes condiciones:

* **No Conformidades Críticas:** 0 toleradas.
* **F1-Score del Modelo:** $\ge 0.85$ en la clase de amenaza de phishing.
* **Tasa de Falsos Negativos:** $\le 5\%$ en mensajes de alta urgencia con enlaces.
* **Tiempo de Respuesta Promedio:** $< 150 \text{ ms}$ en inferencia local.
* **Auditoría de Formato:** 100% de cumplimiento en la verificación estática de estilo.

---

## 8. CONCLUSIÓN Y DICTAMEN PRELIMINAR

El sistema CYCLOPS SENTINEL, bajo su modelo enfocado exclusivamente en el usuario final, demuestra un diseño arquitectónico altamente eficiente y robusto. La supresión de dependencias externas agiliza la toma de decisiones defensivas, entregando una herramienta transparente, de alta velocidad y científicamente fundamentada en técnicas estadísticas avanzadas para la mitigación del fraude digital.
