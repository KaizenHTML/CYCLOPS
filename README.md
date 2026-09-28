# PMI: Phishing MCP Intelligence

## Integrantes
Cristian Camilo Garavito Díaz
<br>
<br>
<br>

## Descripción del Proyecto
El objetivo principal es construir un sistema inteligente para la detección automática de amenazas de ciberseguridad, específicamente enfocado en ataques de phishing y spam, utilizando arquitecturas de Machine Learning y conectando el motor de análisis a un servidor basado en Model Context Protocol.

## Almacenamiento de Datos y Datasets
Los datos unificados y procesados del proyecto se encuentran alojados en el almacenamiento centralizado en la nube para garantizar el control de versiones de grandes volúmenes de información.

* **Repositorio de Datasets en Google Drive:** [Ingresar enlace de Google Drive aquí]

## Arquitectura de Implementación: Dashboard SOC y Aplicación Web
El sistema está diseñado bajo una arquitectura web de alto rendimiento orientada a analistas de centros de operaciones de seguridad.

## Componentes del Sistema
* **Backend:** API REST desarrollada en FastAPI para orquestación de datos e inferencia en tiempo real.
* **Frontend:** Interfaz dinámica desarrollada en Streamlit para procesamiento interactivo y visualización de métricas.

## Flujo Operativo

### Módulo de Análisis Manual
* Panel con área de entrada de texto donde el analista ingresa el contenido crudo de correos sospechosos.
* Procesamiento en tiempo real mediante el pipeline de normalización y extracción de características.
* Generación inmediata de diagnósticos con niveles de riesgo y probabilidades asociadas.

### Módulo de Integración API y Webhooks
* Autenticación segura mediante el protocolo OAuth 2.0 con la API de Gmail.
* Ingesta y lectura automatizada de correos no procesados directamente desde la bandeja de entrada.
* Ejecución transparente de la canalización de preparación de datos y clasificación de amenazas.
* Presentación de resultados en una tabla interactiva con alertas de alto contraste para la identificación rápida de incidentes críticos.

## Estructura del Repositorio
```plaintext
PMI/
├── data/
│   └── processed/          # Datasets normalizados y listos para modelado
├── src/
│   ├── data_pipeline/     # Scripts de ingesta y normalización de texto
│   ├── ml_models/         # Vectorizadores y modelos de ML entrenados
│   ├── mcp_server/        # Servidor FastAPI e integraciones MCP
│   └── dashboard/         # Interfaz de usuario Streamlit
├── tests/                 # Pruebas unitarias y de integración
├── README.md              # Documentación principal
└── requirements.txt       # Dependencias del proyecto
```
