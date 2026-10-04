# CYCLOPS

Plataforma modular Enterprise para la detección proactiva de amenazas de ciberseguridad, análisis de correo malicioso y respuesta automatizada ante incidentes mediante Machine Learning.

---
<br>

## Descripción del Proyecto

**CYCLOPS** es una solución avanzada diseñada para resolver la problemática del fraude por ingeniería social, phishing y vectores de ataque transmitidos por correo electrónico. El sistema procesa correos electrónicos en tiempo real, aplicando técnicas de Procesamiento de Lenguaje Natural y análisis cualitativo y cuantitativo sobre metadatos estructurales para clasificar de manera precisa correos legítimos frente a amenazas cibernéticas.

El objetivo principal de **CYCLOPS** es reducir la carga operativa de los analistas en centros de operaciones de seguridad mediante la automatización de la ingesta, análisis y categorización de eventos, permitiendo una integración futura con orquestadores de respuesta SOAR y XDR.

---
<br>

## Integrantes del Proyecto
| Cristian Díaz |

---
<br>

## Almacenamiento de Datos y Datasets

El pipeline de ingesta y procesamiento de datos centraliza múltiples fuentes provenientes de plataformas especializadas como Kaggle. Para garantizar la reproducibilidad, auditoría y revisión docente sin sobrecargar el repositorio con archivos pesados, se cuenta con una estructura de almacenamiento organizada en las fases Raw, Unified, normalized y tokanization/lematization.

* **Repositorio Oficial de Datasets en Google Drive:** https://drive.google.com/drive/folders/1j3hjgW__ssZssPMRjrJVJT5CMo59T3YM?usp=sharing

---
<br>

## Documentación Teórica y Base de Conocimiento - Notion

Como parte de la investigación aplicada para el desarrollo de **CYCLOPS**, se mantiene una base de conocimiento viva en Notion. Esta documentación compila la fundamentación teórica, análisis de ciberseguridad, matemáticas aplicadas y conceptos clave utilizados a lo largo del proyecto, tales como:

* **Ingeniería de Características y Ciberseguridad:** Detección de palabras de urgencia, identificación de código malicioso embebido, vectores de evasión y el trilema del atacante.
* **Procesamiento de Lenguaje Natural - NLP:** Tokenización, remoción de stopwords, lematización, expresiones regulares y vectorización TF-IDF.
* **Ciencia de Datos y Escalado:** Manejo de DataFrames, distribuciones, desviación estándar, valores atípicos y escalado robusto con RobustScaler.
* **Privacidad y Seguridad de Datos:** Hashing de direcciones IP, anonimización y normalización de texto.

* **Base de Conocimiento en Notion:** https://app.notion.com/p/CYCLOPS-3e959de529f58051b74efe5d873eea90?source=copy_link.

---
<br>

## Componentes del Sistema

* **Capa de Pipeline de Datos - data_pipeline:** Encargada de la ingesta, unificación de conjuntos de datos heterogéneos, limpieza, anonimización, lematización NLP y extracción de características cuantitativas.
* **Capa de Dominio - domain:** Define las reglas de negocio puras, modelos de entidad de ciberseguridad y esquemas de transferencia de datos bajo Clean Architecture.
* **Capa de Infraestructura - infrastructure:** Conectores a bases de datos relacionales, repositorios y cargadores de modelos de Machine Learning.
* **Módulo de Escalado de Datos:** Implementación de RobustScaler alineada a los principios de prevención de fuga de datos mediante la separación estricta Train y Test en proporción 80 a 20.
* **Artefactos Serializados - models:** Almacenamiento en disco de transformadores y clasificadores congelados en formato pkl para su consumo inmediato en tiempo de ejecución.

---
<br>

## Flujo Operativo del Sistema

```text
[ Correo Entrante / Raw Data ]
              │
              ▼
[ Pipeline de Datos - NLP + Cleaning + Anonymization ]
              │
              ▼
[ Extracción de Métricas - Text, Counts, Urgency, Flags ]
              │
              ▼
[ División Estricta Train 80% / Test 20% ]
              │
              ▼
[ Escalado Robusto - RobustScaler + Vectorización TF-IDF ]
              │
              ▼
[ Persistencia de Artefactos .pkl / Inferencia del Modelo ]
              │
              ▼
[ Diagnóstico de Amenaza / Gestión del Incidente ]
