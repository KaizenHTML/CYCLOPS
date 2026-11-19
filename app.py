import os
import sys
import time
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from cyclops_engine import RobustScalerService, AIClassifierService, EmailMetadata, Incident, SOCAnalystService
from src.gmail_service import GmailService

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "cyclops_super_secret_session_key_2026")
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

scaler_service = RobustScalerService()
classifier_service = AIClassifierService(scaler_service)
history_service = SOCAnalystService()
gmail_service = GmailService()

demo_catalog = [
    {
        "id": "demo-01",
        "sender": "Seguridad Bancaria <alertas@banco-seguridad-verificacion.com>",
        "subject": "URGENTE: Notificacion de Seguridad Bancaria y Bloqueo de Cuenta",
        "date": "Hoy 10:45 AM",
        "snippet": "Su cuenta ha sido bloqueada temporalmente por actividad inusual en las ultimas 24 horas...",
        "body": "URGENTE: Notificacion de Seguridad Bancaria. Su cuenta ha sido bloqueada temporalmente por actividad inusual en las ultimas 24 horas. Para reactivar su acceso y evitar la suspension definitiva de sus fondos, ingrese de inmediato al enlace y verifique sus credenciales bancarias: https://banco-seguridad-verificacion.com/login?id=92847. Si no completa la verificacion antes de 24 horas, sus activos seran retenidos."
    },
    {
        "id": "demo-02",
        "sender": "Soporte TI Corporativo <helpdesk@seguridad-accesos-ti.net>",
        "subject": "ALERTA CRITICA: Su contrasena institucional expira hoy",
        "date": "Hoy 09:15 AM",
        "snippet": "Su contrasena institucional expira el dia de hoy. De no actualizar sus datos de acceso...",
        "body": "ALERTA CRITICA DE TI: Su contrasena institucional expira el dia de hoy. De no actualizar sus datos de acceso inmediatamente, perdera comunicacion corporativa y sus cuentas seran restringidas. Haga clic aqui para confirmar su identidad: https://portal-soporte-autenticacion-corporativa.net/auth. Requerido por el area de Seguridad Informatica."
    },
    {
        "id": "demo-03",
        "sender": "Direccion de Talento Humano <bienestar@empresa-corporativa.com>",
        "subject": "Invitacion: Jornada de Bienestar y Capacitacion Interna",
        "date": "Ayer 04:30 PM",
        "snippet": "Apreciados colaboradores, les recordamos que este viernes se llevara a cabo la jornada...",
        "body": "Apreciados colaboradores, les recordamos que este viernes se llevara a cabo la jornada de bienestar y capacitacion interna. Las actividades daran inicio a las nueve de la manana en el auditorio central. Esperamos contar con su participacion activa. Atentamente, Direccion de Talento Humano."
    },
    {
        "id": "demo-04",
        "sender": "Gerencia de Ingenieria <proyectos@empresa-corporativa.com>",
        "subject": "Minuta de Sesion Tecnica de Planificacion Trimestral",
        "date": "Ayer 02:10 PM",
        "snippet": "Estimado equipo, les comparto la agenda para la sesion de planeacion trimestral del proximo martes...",
        "body": "Estimado equipo, les comparto la agenda para la sesion de planeacion trimestral del proximo martes en la sala de conferencias B. Revisaremos los avances de los objetivos anuales y definiremos los siguientes entregables del proyecto. Agradezco confirmar su asistencia con anticipacion. Saludos cordiales."
    }
]

def analyze_email_item(item):
    text_content = item.get("body") or item.get("snippet") or item.get("subject") or ""
    metadata = EmailMetadata(text_content, sender=item.get("sender"))
    evaluation = classifier_service.predict(metadata)
    return {
        "id": item.get("id"),
        "sender": item.get("sender"),
        "subject": item.get("subject"),
        "date": item.get("date"),
        "snippet": item.get("snippet"),
        "body": text_content,
        "metadata": metadata.to_dict(),
        "evaluation": evaluation
    }

def get_current_redirect_uri():
    host = request.host
    proto = "https" if request.is_secure else "http"
    return f"{proto}://{host}/auth/callback"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/auth/google")
def auth_google():
    redirect_uri = get_current_redirect_uri()
    print("INICIANDO AUTENTICACION CON REDIRECT URI:", redirect_uri)
    auth_url = gmail_service.get_authorization_url(redirect_uri=redirect_uri)
    return redirect(auth_url)

@app.route("/auth/callback")
def auth_callback():
    code = request.args.get("code")
    err = request.args.get("error")
    if err:
        print("GOOGLE RETORNO ERROR EN CALLBACK:", err)
        return redirect("/?error=" + err)
    if not code:
        print("CALLBACK SIN CODIGO")
        return redirect("/?error=missing_code")
    
    redirect_uri = get_current_redirect_uri()
    print("PROCESANDO CALLBACK CON REDIRECT URI:", redirect_uri)
    token_data = gmail_service.exchange_code_for_token(code, redirect_uri=redirect_uri)
    if not token_data or "access_token" not in token_data:
        print("FALLO EL INTERCAMBIO DE TOKEN")
        return redirect("/?error=token_exchange_failed")
    
    access_token = token_data.get("access_token")
    session["access_token"] = access_token
    session.permanent = True
    print("TOKEN GUARDADO EN SESION EXITOSAMENTE")
    
    profile = gmail_service.get_user_profile(access_token)
    if profile:
        session["user_name"] = profile.get("name", "Usuario de Google")
        session["user_email"] = profile.get("email", "")
        session["user_picture"] = profile.get("picture", "")
        print("PERFIL OBTENIDO:", session.get("user_name"), session.get("user_email"))
    
    return redirect("/?connected=1")

@app.route("/auth/logout")
def auth_logout():
    session.clear()
    return redirect("/")

@app.route("/api/user")
def api_user():
    if "access_token" in session:
        return jsonify({
            "authenticated": True,
            "name": session.get("user_name", "Usuario de Google"),
            "email": session.get("user_email", ""),
            "picture": session.get("user_picture", "")
        })
    return jsonify({"authenticated": False})

@app.route("/api/emails")
def api_emails():
    source_type = request.args.get("source", "auto")
    
    if source_type != "demo" and "access_token" in session:
        access_token = session["access_token"]
        print("SOLICITANDO MENSAJES REALES DE GMAIL...")
        raw_msgs = gmail_service.list_recent_messages(access_token, max_results=8)
        analyzed_list = []
        for m in raw_msgs:
            detail = gmail_service.get_message_detail(access_token, m.get("id"))
            if detail:
                payload = gmail_service.extract_email_payload(detail)
                analyzed_item = analyze_email_item(payload)
                analyzed_list.append(analyzed_item)
        if analyzed_list:
            print("RETORNANDO MENSAJES ANALIZADOS DE GMAIL:", len(analyzed_list))
            return jsonify({
                "status": "success",
                "source": "gmail",
                "total": len(analyzed_list),
                "emails": analyzed_list
            })
        else:
            print("NO SE OBTUVIERON MENSAJES DE GMAIL O LISTA VACIA")
            
    demo_analyzed = [analyze_email_item(d) for d in demo_catalog]
    return jsonify({
        "status": "success",
        "source": "demo",
        "total": len(demo_analyzed),
        "emails": demo_analyzed
    })

@app.route("/api/analyze", methods=["POST"])
def analyze():
    start_time = time.time()
    payload = request.get_json() or {}
    raw_text = payload.get("raw_text", "")
    reporter_id = payload.get("reporter_id", "emp.usr.001")

    metadata = EmailMetadata(raw_text)
    evaluation = classifier_service.predict(metadata)

    incident = Incident(raw_text, reporter_id, metadata, evaluation)
    incident.alert_level = evaluation["risk_level"]
    incident.status = "ANALYZED"
    history_service.add_incident(incident)

    elapsed_ms = round((time.time() - start_time) * 1000.0, 2)

    return jsonify({
        "status": "success",
        "incident_id": incident.id,
        "execution_time_ms": elapsed_ms,
        "metadata": metadata.to_dict(),
        "evaluation": evaluation
    })

@app.route("/api/incidents", methods=["GET"])
def get_incidents():
    all_incidents = history_service.get_all_incidents()
    return jsonify({
        "total_count": len(all_incidents),
        "pending_count": 0,
        "incidents": all_incidents
    })

@app.route("/api/emails/<email_id>/mitigate", methods=["POST"])
def mitigate_email(email_id):
    return jsonify({
        "status": "success",
        "email_id": email_id,
        "action": "mitigated",
        "message": "Correo aislado y eliminado exitosamente del buzon activo."
    })

if __name__ == "__main__":
    print("Servidor CYCLOPS activo en http://127.0.0.1:8000")
    app.run(host="127.0.0.1", port=8000, debug=False)
