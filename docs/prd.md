# Product Requirements Document - CYCLOPS

Este documento especifica la visión, el alcance, las reglas de negocio, los requerimientos funcionales y no funcionales, así como los casos de uso principales para la plataforma de ciberseguridad **CYCLOPS SENTINEL**, enfocada exclusivamente en el **Usuario Final**.

---

## 1. Visión y Alcance del Producto

### Visión
Empoderar al usuario final mediante un asistente inteligente y autónomo de ciberseguridad capaz de detectar amenazas de phishing e ingeniería social en correos electrónicos en tiempo real, proporcionando diagnósticos precisos, explicables y recomendaciones inmediatas sin requerir la intervención de analistas externos.

### Alcance
El sistema comprende la ingesta directa de correos sospechosos ingresados por el usuario, la anonimización y limpieza de texto mediante procesamiento de lenguaje natural, la transformación estadística de métricas numéricas con RobustScaler, y la clasificación inmediata por modelos de Machine Learning. El usuario recibe un veredicto definitivo, un desglose de los factores de riesgo y un historial completo de sus consultas para proteger sus activos digitales.

---

## 2. Casos de Uso Principales

### CU01: Análisis de Correo Sospechoso por Usuario Final
* **Actor Principal:** Usuario Final.
* **Precondición:** El usuario recibe un correo sospechoso y desea verificar su legitimidad.
* **Flujo Principal:**
  1. El usuario ingresa el texto del mensaje en la interfaz interactiva o utiliza plantillas de prueba.
  2. El sistema recibe el texto, extrae las características y procesa la inferencia en milisegundos.
  3. El sistema despliega el veredicto definitivo, el porcentaje de confianza, el nivel de riesgo y las recomendaciones preventivas.

### CU02: Inferencia Automatizada y Explicabilidad por Agente de IA
* **Actor Principal:** Motor de Inteligencia Artificial CYCLOPS.
* **Precondición:** Mensaje ingresado por el usuario en espera de evaluación.
* **Flujo Principal:**
  1. El motor ejecuta la limpieza léxica, enmascara identificadores personales e IPs, y cuantifica variables estructurales.
  2. Transforma el vector numérico utilizando el artefacto preentrenado de RobustScaler para aislar valores atípicos.
  3. Calcula la probabilidad matemática de amenaza mediante el clasificador de Scikit-Learn.
  4. Genera el desglose explicativo en cuatro niveles: Ingesta NLP, Escalado Robusto, Inferencia Probabilística y Recomendación al Usuario.

### CU03: Consulta de Historial y Trazabilidad por Usuario
* **Actor Principal:** Usuario Final.
* **Precondición:** Existencia de análisis previos realizados en la sesión o registrados en el sistema.
* **Flujo Principal:**
  1. El usuario accede a la pestaña de Historial de Análisis.
  2. Visualiza el registro cronológico con identificador de consulta, fecha, nivel de riesgo y recomendación asignada.
  3. Revisa la trazabilidad de sus correos evaluados para mantener control preventivo de su bandeja de entrada.

---

## 3. Requerimientos Funcionales

* **RF01 - Ingesta de Mensajes:** La API y la interfaz deben permitir la recepción de solicitudes HTTP POST con el contenido de correos sospechosos y el identificador del usuario.
* **RF02 - Preprocesamiento NLP y Anonimización:** El sistema debe normalizar el texto y enmascarar automáticamente direcciones IP y direcciones de correo electrónico para proteger la privacidad.
* **RF03 - Escalado Robusto:** Las variables numéricas de longitud, conteo de palabras, cantidad de hipervínculos y densidad de urgencia deben ser transformadas con RobustScaler para evitar distorsiones por valores extremos.
* **RF04 - Clasificación Autónoma de Riesgo:** El motor debe determinar de forma directa y probabilística si el mensaje constituye una amenaza de Phishing o es Legítimo.
* **RF05 - Explicabilidad y Recomendaciones Directas:** La interfaz debe presentar al usuario una justificación clara del diagnóstico, alertando sobre factores como inductores de urgencia coercitiva o enlaces no verificados, con directrices claras de actuación.
* **RF06 - Historial de Consultas:** El sistema debe registrar cada análisis realizado y exponerlo en una vista accesible de historial para el usuario.

---

## 4. Requerimientos No Funcionales

* **RNF01 - Rendimiento y Latencia:** La inferencia completa debe retornar el diagnóstico al usuario en menos de doscientos milisegundos.
* **RNF02 - Escalabilidad:** La arquitectura debe procesar consultas concurrentes sin degradar la precisión ni bloquear el hilo de ejecución principal.
* **RNF03 - Seguridad y Privacidad por Diseño:** No se almacenan datos personales sin anonimización previa, garantizando estricta confidencialidad bajo estándares de protección de datos.
* **RNF04 - Mantenibilidad y Clean Architecture:** El código debe estructurarse modularmente desacoplando el motor de extracción, el escalador, los clasificadores y la capa de presentación.
* **RNF05 - Usabilidad y Experiencia de Usuario:** La interfaz gráfica interactiva debe ser intuitiva, moderna, adaptativa y con información clara orientada a la toma de decisiones del usuario sin tecnicismos innecesarios.
