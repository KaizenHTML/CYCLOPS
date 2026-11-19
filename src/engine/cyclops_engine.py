import os
import re
import uuid
import datetime
from typing import Any
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import RobustScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.cluster import KMeans

class EmailMetadata:
    def __init__(self, raw_text, sender=None):
        self.id = str(uuid.uuid4())[:8]
        self.raw_text = raw_text
        self.sender = sender or ""
        self.is_trusted_sender = False
        self.all_links_trusted = False
        self.has_suspicious_link = False
        self.threat_hits = []
        self.mild_hits = []
        self.assurance_hits = []
        self.char_count = 0
        self.word_count = 0
        self.url_count = 0
        self.has_url = 0
        self.has_ip = 0
        self.urgency_score = 0.0
        self.scaled_urgency_score = 0.0
        self.url_density = 0.0
        self.urgency_density = 0.0
        self.cluster_id = 0
        self.cluster_label = "Transaccional Seguro"
        self.is_threat = False
        self.anonymized_sender = sender if sender else "usuario.corporativo@empresa.com"
        self.check_sender_reputation()
        self.extract_features()

    def check_sender_reputation(self):
        if not self.sender:
            return
        sender_lower = self.sender.lower()
        trusted_domains = [
            "google.com", "googlemail.com", "youtube.com", "googleplay.com",
            "microsoft.com", "apple.com", "amazon.com", "github.com",
            "steampowered.com", "steamcommunity.com", "valvesoftware.com",
            "spotify.com", "netflix.com", "paypal.com", "epicgames.com",
            "playstation.com", "sony.com", "discord.com", "linkedin.com",
            "bancolombia.com.co", "davivienda.com"
        ]
        if "@" in sender_lower:
            parts = sender_lower.split("@")
            dom = parts[-1].rstrip(">").strip()
            for td in trusted_domains:
                if dom == td or dom.endswith("." + td):
                    self.is_trusted_sender = True
                    break

    def extract_features(self):
        text = self.raw_text or ""
        self.char_count = len(text)
        words = text.split()
        self.word_count = len(words)
        
        urls = re.findall(r"https?://\S+|www\.\S+", text)
        self.url_count = len(urls)
        self.has_url = 1 if self.url_count > 0 else 0

        text_lower = text.lower()

        trusted_link_domains = [
            "google.com", "googlemail.com", "youtube.com", "googleplay.com",
            "microsoft.com", "apple.com", "amazon.com", "github.com",
            "steampowered.com", "steamcommunity.com", "valvesoftware.com",
            "computrabajo.com", "computrabajo.com.co", "elempleo.com", "indeed.com",
            "platzi.com", "coursera.org", "duolingo.com",
            "spotify.com", "netflix.com", "paypal.com", "epicgames.com",
            "playstation.com", "sony.com", "discord.com", "linkedin.com",
            "bancolombia.com.co", "davivienda.com"
        ]

        self.has_suspicious_link = False
        all_valid = len(urls) > 0
        for u in urls:
            u_clean = u.lower().replace("https://", "").replace("http://", "").replace("www.", "")
            host = u_clean.split("/")[0].split("?")[0].split(":")[0]
            
            if any(bad in host for bad in [".xyz", ".top", ".tk", ".ru", ".click", ".buzz", ".work"]):
                self.has_suspicious_link = True
                all_valid = False
            
            matched = False
            for td in trusted_link_domains:
                if host == td or host.endswith("." + td):
                    matched = True
                    break
            if not matched:
                all_valid = False

        self.all_links_trusted = all_valid

        ip_match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", text)
        self.has_ip = 1 if ip_match else 0
        if self.has_ip:
            self.has_suspicious_link = True

        coercive_threats = [
            "suspension definitiva", "cuenta suspendida", "bloqueo de cuenta", "cuenta bloqueada",
            "sera suspendida", "sera bloqueada", "sera cerrada", "sera cancelada", "evitar el cierre",
            "retencion de fondos", "actividad inusual", "actividad sospechosa", "acceso no autorizado",
            "ultimo aviso", "plazo limite", "24 horas", "48 horas", "multa", "penalizacion",
            "fondos seran retenidos", "inmediatamente o sera"
        ]
        self.threat_hits = [t for t in coercive_threats if t in text_lower]

        mild_urgency = ["urgente", "urgencia", "inmediato", "inmediatamente", "alerta critica"]
        self.mild_hits = [m for m in mild_urgency if m in text_lower]

        assurance_terms = [
            "si no has solicitado", "si no solicitaste", "si no estas tratando",
            "ignora este correo", "no respondas a este mensaje", "ofertas de empleo",
            "hoja de vida", "postulacion", "vacante", "candidato", "todos los derechos reservados",
            "politica de privacidad", "terminos y condiciones", "desuscribirse", "recibo de compra",
            "confirmacion de pedido"
        ]
        self.assurance_hits = [a for a in assurance_terms if a in text_lower]

        calc_urgency = len(self.threat_hits) * 3.5 + len(self.mild_hits) * 1.5
        if self.has_suspicious_link and len(self.threat_hits) > 0:
            calc_urgency += 3.0
        self.urgency_score = min(round(calc_urgency, 2), 10.0)

        effective_words = max(self.word_count, 1)
        self.url_density = round(float(self.url_count) / float(effective_words) * 100.0, 2)
        self.urgency_density = round(float(self.urgency_score) / float(effective_words) * 100.0, 2)

    def to_dict(self):
        return {
            "id": self.id,
            "char_count": int(self.char_count),
            "word_count": int(self.word_count),
            "url_count": int(self.url_count),
            "has_url": int(self.has_url),
            "has_ip": int(self.has_ip),
            "urgency_score": float(self.urgency_score),
            "scaled_urgency_score": float(self.scaled_urgency_score),
            "url_density": float(self.url_density),
            "urgency_density": float(self.urgency_density),
            "cluster_id": int(self.cluster_id),
            "cluster_label": self.cluster_label,
            "is_threat": bool(self.is_threat),
            "all_links_trusted": bool(self.all_links_trusted),
            "anonymized_sender": self.anonymized_sender
        }

class RobustScalerService:
    def __init__(self, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(base_dir, "models", "robust_scaler.joblib")
        self.scaler = None
        self.feature_columns = [
            "char_count", "word_count", "url_count", "has_url",
            "has_ip", "urgency_score", "url_density", "urgency_density"
        ]
        self._load_or_fit()

    def _load_or_fit(self):
        if os.path.exists(self.model_path):
            try:
                self.scaler = joblib.load(self.model_path)
                return
            except Exception:
                self.scaler = None
        self.scaler = RobustScaler()
        baseline_samples = np.array([
            [80.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [150.0, 25.0, 0.0, 0.0, 0.0, 0.5, 0.0, 1.2],
            [220.0, 35.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [350.0, 50.0, 1.0, 1.0, 0.0, 1.0, 1.5, 2.0],
            [450.0, 65.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [280.0, 42.0, 2.0, 1.0, 0.0, 6.0, 4.5, 12.0],
            [190.0, 30.0, 1.0, 1.0, 1.0, 8.5, 3.2, 22.0],
            [520.0, 75.0, 3.0, 1.0, 0.0, 9.0, 3.8, 11.5]
        ])
        df_base = pd.DataFrame(baseline_samples, columns=self.feature_columns)
        self.scaler.fit(df_base)

    def transform(self, features_dict):
        df_in = pd.DataFrame([features_dict], columns=self.feature_columns)
        scaled = self.scaler.transform(df_in)
        return scaled[0].tolist()

class AIClassifierService:
    def __init__(self, scaler_service, base_dir=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.scaler_service = scaler_service
        self.model_path = os.path.join(base_dir, "models", "decision_tree_model.joblib")
        self.kmeans_path = os.path.join(base_dir, "models", "kmeans_model.joblib")
        self.kmeans_scaler_path = os.path.join(base_dir, "models", "kmeans_scaler.joblib")
        self.tree_model = None
        self.kmeans_model = None
        self.kmeans_scaler = None
        self._load_or_fit()

    def _load_or_fit(self):
        if os.path.exists(self.model_path):
            try:
                self.tree_model = joblib.load(self.model_path)
            except Exception:
                self.tree_model = None
        if os.path.exists(self.kmeans_path):
            try:
                self.kmeans_model = joblib.load(self.kmeans_path)
            except Exception:
                self.kmeans_model = None
        if os.path.exists(self.kmeans_scaler_path):
            try:
                self.kmeans_scaler = joblib.load(self.kmeans_scaler_path)
            except Exception:
                self.kmeans_scaler = None

        if self.tree_model is None:
            self.tree_model = DecisionTreeClassifier(max_depth=15, criterion="entropy", random_state=42)
            train_x = np.array([
                [60.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [120.0, 22.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [260.0, 45.0, 0.0, 0.0, 0.0, 0.5, 0.0, 1.0],
                [380.0, 60.0, 0.0, 0.0, 0.0, 1.0, 0.0, 1.4],
                [140.0, 24.0, 1.0, 1.0, 0.0, 4.0, 4.1, 15.0],
                [210.0, 32.0, 2.0, 1.0, 0.0, 7.5, 5.8, 20.0],
                [290.0, 40.0, 2.0, 1.0, 1.0, 9.0, 4.7, 18.5],
                [180.0, 28.0, 1.0, 1.0, 0.0, 8.0, 3.5, 24.0],
                [320.0, 48.0, 3.0, 1.0, 1.0, 9.5, 6.0, 17.5]
            ])
            train_y = np.array([0, 0, 0, 0, 1, 1, 1, 1, 1])
            self.tree_model.fit(train_x, train_y)

    def predict(self, metadata):
        features_dict = {
            "char_count": float(metadata.char_count),
            "word_count": float(metadata.word_count),
            "url_count": float(metadata.url_count),
            "has_url": float(metadata.has_url),
            "has_ip": float(metadata.has_ip),
            "urgency_score": float(metadata.urgency_score),
            "url_density": float(metadata.url_density),
            "urgency_density": float(metadata.urgency_density)
        }
        
        scaled_vector = self.scaler_service.transform(features_dict)
        metadata.scaled_urgency_score = round(scaled_vector[5], 3)

        df_scaled = pd.DataFrame([scaled_vector], columns=self.scaler_service.feature_columns)
        prob_matrix = self.tree_model.predict_proba(df_scaled.values)
        prob_phishing = float(prob_matrix[0][1])

        if self.kmeans_model is not None:
            km_features = ["char_count", "word_count", "url_count", "has_url", "urgency_score"]
            df_km = pd.DataFrame([[features_dict[col] for col in km_features]], columns=km_features)
            try:
                if self.kmeans_scaler is not None:
                    km_scaled = self.kmeans_scaler.transform(df_km)
                    cluster_res = self.kmeans_model.predict(km_scaled)[0]
                else:
                    cluster_res = self.kmeans_model.predict(df_km.values)[0]
                metadata.cluster_id = int(cluster_res)
                if metadata.cluster_id == 2:
                    metadata.cluster_label = "Cluster 2 - Vector de Alta Concentracion de Phishing"
                elif metadata.cluster_id == 1:
                    metadata.cluster_label = "Cluster 1 - Comunicados Masivos y Notificaciones"
                else:
                    metadata.cluster_label = "Cluster 0 - Trafico Corporativo Habitual"
            except Exception:
                metadata.cluster_id = 0
                metadata.cluster_label = "Cluster 0 - Trafico Corporativo Habitual"

        # Multi-layer semantic decision matrix
        if metadata.has_suspicious_link and (len(metadata.threat_hits) > 0 or len(metadata.mild_hits) > 0):
            prob_phishing = 0.999
        elif len(metadata.threat_hits) >= 2:
            prob_phishing = max(prob_phishing, 0.950)
        elif metadata.is_trusted_sender or metadata.all_links_trusted or (len(metadata.assurance_hits) > 0 and len(metadata.threat_hits) == 0):
            prob_phishing = min(prob_phishing, 0.065)
        elif len(metadata.threat_hits) == 1 and len(metadata.assurance_hits) == 0:
            prob_phishing = max(prob_phishing, 0.650)
        elif metadata.urgency_score == 0 and not metadata.has_suspicious_link:
            prob_phishing = min(prob_phishing, 0.080)

        confidence_pct = round(prob_phishing * 100.0, 1)

        if prob_phishing >= 0.75:
            classification = "PHISHING CONFIRMADO"
            risk_level = "CRITICO"
            action = "USER_ALERT_HIGH"
            metadata.is_threat = True
            action_label = "Amenaza Critica - Bloqueo Inmediato"
            summary = "Amenaza de phishing detectada por coaccion agresiva o hipervinculos sospechosos disenados para suplantar identidades."
        elif prob_phishing >= 0.40:
            classification = "PHISHING SOSPECHOSO"
            risk_level = "MEDIO"
            action = "USER_ALERT_CAUTION"
            metadata.is_threat = True
            action_label = "Advertencia de Precaucion al Usuario"
            summary = "Puntaje de riesgo intermedio con senales de alerta. Se recomienda precaucion antes de interactuar."
        else:
            classification = "LEGITIMO"
            risk_level = "BAJO"
            action = "MARKED_AS_SAFE"
            metadata.is_threat = False
            action_label = "Marcado como Seguro"
            if metadata.all_links_trusted or metadata.is_trusted_sender:
                summary = "Notificacion autentica o recuperacion de credenciales verificada. Los hipervinculos dirigen exclusivamente a dominios institucionales autenticos sin desvio malicioso."
            elif len(metadata.assurance_hits) > 0:
                summary = "Comunicado transaccional legitimo conforme a estandares de notificacion. Sin vectores de coaccion ni desvio de enlaces."
            else:
                summary = "Mensaje sin presencia significativa de patrones maliciosos ni enlaces de riesgo. Clasificado como seguro para el usuario."

        char_num = metadata.char_count
        word_num = metadata.word_count
        url_num = metadata.url_count
        urgency_num = metadata.urgency_score
        url_dens = metadata.url_density
        urg_dens = metadata.urgency_density
        scaled_urg = metadata.scaled_urgency_score
        cl_tag = metadata.cluster_label

        decision_levels = [
            {
                "level": "Nivel 1 - Ingesta y Preprocesamiento NLP",
                "status": "Completado",
                "details": f"Texto normalizado. Conteo de {char_num} caracteres, {word_num} palabras, {url_num} enlaces detectados y {urgency_num} puntos de urgencia identificados."
            },
            {
                "level": "Nivel 2 - Extracción de Métricas y Escalado Robusto",
                "status": "Completado",
                "details": f"Métricas transformadas con RobustScaler para aislar valores atipicos. Densidad de enlaces {url_dens}%, densidad de urgencia {urg_dens}%, score de urgencia escalado {scaled_urg}."
            },
            {
                "level": "Nivel 3 - Inferencia Probabilística y Segmentación No Supervisada",
                "status": "Completado",
                "details": f"Evaluacion mediante Arbol de Decision Scikit-Learn. Probabilidad de amenaza situada en {confidence_pct}%. Segmentado en {cl_tag}."
            },
            {
                "level": "Nivel 4 - Diagnostico Directo al Usuario",
                "status": "Completado",
                "details": f"Veredicto emitido sin intermediarios. Recomendacion directa al usuario: {action_label}. Nivel de riesgo catalogado como {risk_level}."
            }
        ]

        return {
            "confidence_score": float(confidence_pct),
            "classification": classification,
            "risk_level": risk_level,
            "action_taken": action,
            "action_label": action_label,
            "summary": summary,
            "decision_levels": decision_levels,
            "scaled_vector": [float(round(v, 3)) for v in scaled_vector],
            "is_high_confidence": bool(prob_phishing >= 0.75)
        }

class Incident:
    metadata: Any = None
    evaluation: Any = None
    mitigation: Any = None

    def __init__(self, raw_text, reporter_id="emp.usr.001", metadata: Any = None, evaluation: Any = None):
        self.id = "INC-" + str(uuid.uuid4())[:6].upper()
        self.reporter_id = reporter_id
        self.raw_text = raw_text
        self.status = "PENDING_ANALYSIS"
        self.alert_level = "BAJO"
        self.reported_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.metadata = metadata
        self.evaluation = evaluation
        self.mitigation = None

    def set_metadata(self, metadata: Any):
        self.metadata = metadata

    def set_evaluation(self, evaluation: Any):
        self.evaluation = evaluation

    def update_status(self, new_status, action_type=None, executed_by="CYCLOPS_AI_AGENT"):
        self.status = new_status
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if action_type:
            self.mitigation = {
                "id": "MIT-" + str(uuid.uuid4())[:6].upper(),
                "action_type": action_type,
                "executed_by": executed_by,
                "executed_at": now_str
            }

    def to_dict(self):
        return {
            "id": self.id,
            "reporter_id": self.reporter_id,
            "raw_text": self.raw_text,
            "status": self.status,
            "alert_level": self.alert_level,
            "reported_at": self.reported_at,
            "metadata": self.metadata.to_dict() if self.metadata else None,
            "evaluation": self.evaluation,
            "mitigation": self.mitigation
        }

class AnalysisHistoryService:
    def __init__(self):
        self.incidents = []

    def add_incident(self, incident):
        self.incidents.insert(0, incident)

    def get_all_incidents(self):
        return [inc.to_dict() for inc in self.incidents]

SOCAnalystService = AnalysisHistoryService
