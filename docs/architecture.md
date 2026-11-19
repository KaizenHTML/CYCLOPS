# Arquitectura General del Sistema - CYCLOPS

Este documento describe la arquitectura tecnica, la estructura de clases y el modelo de datos relacional para la plataforma **CYCLOPS** bajo la vision de Monolito Modular Limpio y respuesta autonoma centrada en el usuario final.

---

## 1. Diagrama de Componentes

Ilustra la organizacion modular del sistema, detallando la separacion entre la capa de presentacion web responsiva, la API REST en Flask, el motor de inferencia hibrida con Arbol de Decision y KMeans K=3, y los repositorios de persistencia de artefactos.

* **Diagrama de Componentes en PDF:** <a href="assets/component_diagram.pdf">Ver Diagrama en PDF</a>

---

## 2. Diagrama de Clases - Dominio y Servicios Backend

Define la estructura orientada a objetos, servicios de dominio y objetos de valor que componen la logica de negocio en el backend: `Incident`, `EmailMetadata`, `RobustScalerService`, `AIClassifierService` y `EvaluationResult`.

* **Diagrama de Clases en PDF:** <a href="assets/class_diagram.pdf">Ver Diagrama en PDF</a>

---

## 3. Diagrama Entidad-Relacion - Base de Datos

Muestra el diseno conceptual y fisico de tablas relacionales como INCIDENTS, EMAIL_METADATA, AI_EVALUATIONS y AUTONOMOUS_MITIGATIONS para garantizar la trazabilidad de incidentes, metadatos estructurados y directrices de mitigacion emitidas al usuario.

* **Diagrama Entidad-Relacion en PDF:** <a href="assets/entity-relationship_diagram.pdf">Ver Diagrama en PDF</a>

---

## 4. Diagrama de Historias de Usuario y Flujo Autonomo

Describe el flujo de procesamiento condicional y la secuencia operativa entre el Usuario Final y el Agente de Inteligencia Artificial CYCLOPS, mapeando las historias de usuario desde la ingesta en tiempo real hasta la mitigacion directa sin intermediarios.

* **Diagrama de Historias de Usuario en PDF:** <a href="assets/user_stories.pdf">Ver Diagrama en PDF</a>
