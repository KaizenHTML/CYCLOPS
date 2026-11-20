function clearInboxReadingPane() {
    currentEmailId = null;
    const subjectEl = document.getElementById("reading-subject");
    const senderEl = document.getElementById("reading-sender");
    const dateEl = document.getElementById("reading-date");
    const bodyEl = document.getElementById("reading-body");

    if (subjectEl) subjectEl.innerText = "Selecciona un correo para auditar";
    if (senderEl) senderEl.innerText = "Remitente: -";
    if (dateEl) dateEl.innerText = "Fecha: -";
    if (bodyEl) bodyEl.innerText = "Haz clic sobre cualquiera de los correos de la bandeja para desplegar su contenido completo e iniciar la auditoría en tiempo real.";

    const stChars = document.getElementById("inbox-val-char-count");
    const stWords = document.getElementById("inbox-val-url-count");
    const stHasUrl = document.getElementById("inbox-val-has-url");
    const stUrgency = document.getElementById("inbox-val-urgency-score");
    const stUrlDensity = document.getElementById("inbox-val-url-density");
    const stUrgDensity = document.getElementById("inbox-val-urgency-density");
    const stThreat = document.getElementById("inbox-val-is-threat");

    if (stChars) stChars.innerText = "-";
    if (stWords) stWords.innerText = "-";
    if (stHasUrl) stHasUrl.innerText = "-";
    if (stUrgency) stUrgency.innerText = "-";
    if (stUrlDensity) stUrlDensity.innerText = "-";
    if (stUrgDensity) stUrgDensity.innerText = "-";
    if (stThreat) stThreat.innerText = "-";

    const vBanner = document.getElementById("inbox-verdict-banner");
    const vTitle = document.getElementById("inbox-verdict-title");
    const vDesc = document.getElementById("inbox-verdict-desc");
    const vPill = document.getElementById("inbox-verdict-risk-pill");
    const pFill = document.getElementById("inbox-prob-progress-fill");
    const pVal = document.getElementById("inbox-prob-value-text");

    if (vBanner) {
        vBanner.style.backgroundColor = "#F8FAFD";
        vBanner.style.borderColor = "#DDE8F4";
        vBanner.style.color = "#64748B";
    }
    if (vTitle) vTitle.innerText = "Esperando selección";
    if (vDesc) vDesc.innerText = "Selecciona un correo para desplegar su evaluación.";
    if (vPill) {
        vPill.innerText = "Inactivo";
        vPill.style.backgroundColor = "#E2E8F0";
        vPill.style.color = "#475569";
    }
    if (pFill) {
        pFill.style.width = "0%";
        pFill.style.backgroundColor = "#CBD5E1";
    }
    if (pVal) pVal.innerText = "0.0%";
}

﻿document.addEventListener("DOMContentLoaded", function () {
    initCyclops();
});

if (document.readyState === "complete" || document.readyState === "interactive") {
    initCyclops();
}

let loadedEmails = [];
let currentEmailId = null;

function initCyclops() {
    if (window.cyclopsInitialized) {
        return;
    }
    window.cyclopsInitialized = true;
    if (window.location.search.indexOf("connected=1") !== -1) {
        alert("Cuenta de Google conectada exitosamente.");
    } else if (window.location.search.indexOf("error=") !== -1) {
        alert("Detalle de autorizacion de Google detectado: " + window.location.search);
    }
    fetchUserProfile();
    fetchInboxEmails("auto");
    initInboxEvents();
    fetchIncidents();
}


function fetchUserProfile() {
    fetch("/api/user?ts=" + new Date().getTime())
        .then(function (res) { return res.json(); })
        .then(function (data) {
            const userSlot = document.getElementById("header-user-area");
            const heroGoogleBtn = document.getElementById("btn-hero-google");
            if (!userSlot) return;

            if (data.authenticated) {
                const userName = data.name || "Usuario de Google";
                let avatarHtml = "";
                if (data.picture) {
                    avatarHtml = '<img src="' + data.picture + '" class="user-avatar-img">';
                } else {
                    avatarHtml = '<span class="user-avatar-img" style="display:flex;align-items:center;justify-content:center;background:#2E75D3;color:#FFF;font-weight:700;">U</span>';
                }
                userSlot.innerHTML = '<div class="user-badge-header">' + avatarHtml + '<span class="user-badge-text">' + userName + '</span><a href="/auth/logout" class="btn-logout-link">Cerrar sesión</a></div>';
                if (heroGoogleBtn) {
                    heroGoogleBtn.style.display = "none";
                }
            } else {
                userSlot.innerHTML = "";
            }
        })
        .catch(function () {});
}

function fetchInboxEmails(source) {
    const inboxList = document.getElementById("inbox-list");
    const badge = document.getElementById("inbox-source-badge");
    if (inboxList) {
        inboxList.innerHTML = '<div class="empty-state">Cargando mensajes del buzón...</div>';
    }

    const srcParam = source || "auto";
    fetch("/api/emails?source=" + srcParam + "&ts=" + new Date().getTime())
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (!data || !data.emails) return;
            loadedEmails = data.emails;

            if (badge) {
                badge.innerText = data.source === "gmail" ? "Gmail oficial conectado" : "Buzón de muestra";
                badge.style.backgroundColor = data.source === "gmail" ? "#D1FAE5" : "#E2E8F0";
                badge.style.color = data.source === "gmail" ? "#065F46" : "#475569";
            }

            renderInboxList();
            clearInboxReadingPane();
        })
        .catch(function () {
            if (inboxList) {
                inboxList.innerHTML = '<div class="empty-state">No se pudieron cargar los correos. Verifica la conexión o intenta con el buzón de muestra.</div>';
            }
        });
}

function renderInboxList() {
    const inboxList = document.getElementById("inbox-list");
    if (!inboxList) return;

    if (loadedEmails.length === 0) {
        inboxList.innerHTML = '<div class="empty-state">No hay correos en la bandeja.</div>';
        return;
    }

    inboxList.innerHTML = "";
    loadedEmails.forEach(function (item) {
        const card = document.createElement("div");
        const isAudited = Boolean(item.is_audited);

        let riskClass = "";
        let pillClass = "badge-risk-pending";
        let riskLabel = "No auditado";
        let conf = "Pendiente";

        if (isAudited && item.evaluation) {
            const risk = item.evaluation.risk_level || "BAJO";
            riskClass = risk === "CRITICO" ? "threat-critico" : (risk === "MEDIO" ? "threat-medio" : "threat-bajo");
            pillClass = risk === "CRITICO" ? "badge-risk-critico" : (risk === "MEDIO" ? "badge-risk-medio" : "badge-risk-bajo");
            riskLabel = risk === "CRITICO" ? "Amenaza crítica" : (risk === "MEDIO" ? "Sospechoso" : "Seguro");
            conf = (item.evaluation.confidence_score || 0) + "% certeza";
        }

        const activeClass = item.id === currentEmailId ? " active-email" : "";
        card.className = "inbox-card " + riskClass + activeClass;
        card.setAttribute("data-email-id", item.id);
        card.onclick = function () { selectEmail(item.id); };

        const headerDiv = document.createElement("div");
        headerDiv.className = "inbox-card-header";
        const senderSpan = document.createElement("span");
        senderSpan.className = "inbox-sender";
        senderSpan.textContent = item.sender || "Desconocido";
        const dateSpan = document.createElement("span");
        dateSpan.className = "inbox-date";
        dateSpan.textContent = item.date || "";
        headerDiv.appendChild(senderSpan);
        headerDiv.appendChild(dateSpan);

        const subjDiv = document.createElement("div");
        subjDiv.className = "inbox-subject";
        subjDiv.textContent = item.subject || "Sin asunto";

        const snipDiv = document.createElement("div");
        snipDiv.className = "inbox-snippet";
        snipDiv.textContent = item.snippet || "";

        const footerDiv = document.createElement("div");
        footerDiv.className = "inbox-card-footer";
        const pillSpan = document.createElement("span");
        pillSpan.className = "badge-risk-pill " + pillClass;
        pillSpan.textContent = riskLabel;
        const confSpan = document.createElement("span");
        confSpan.style.cssText = "font-size: 11px; color: #64748B; font-weight: 600;";
        confSpan.textContent = conf;
        footerDiv.appendChild(pillSpan);
        footerDiv.appendChild(confSpan);

        card.appendChild(headerDiv);
        card.appendChild(subjDiv);
        card.appendChild(snipDiv);
        card.appendChild(footerDiv);

        inboxList.appendChild(card);
    });
}

function resetInboxPanelsToPending() {
    const stChars = document.getElementById("inbox-val-char-count");
    const stWords = document.getElementById("inbox-val-url-count");
    const stHasUrl = document.getElementById("inbox-val-has-url");
    const stUrgency = document.getElementById("inbox-val-urgency-score");
    const stUrlDensity = document.getElementById("inbox-val-url-density");
    const stUrgDensity = document.getElementById("inbox-val-urgency-density");
    const stThreat = document.getElementById("inbox-val-is-threat");

    if (stChars) stChars.innerText = "-";
    if (stWords) stWords.innerText = "-";
    if (stHasUrl) stHasUrl.innerText = "-";
    if (stUrgency) stUrgency.innerText = "-";
    if (stUrlDensity) stUrlDensity.innerText = "-";
    if (stUrgDensity) stUrgDensity.innerText = "-";
    if (stThreat) stThreat.innerText = "Pendiente";

    const vBanner = document.getElementById("inbox-verdict-banner");
    const vTitle = document.getElementById("inbox-verdict-title");
    const vDesc = document.getElementById("inbox-verdict-desc");
    const vPill = document.getElementById("inbox-verdict-risk-pill");
    const pFill = document.getElementById("inbox-prob-progress-fill");
    const pVal = document.getElementById("inbox-prob-value-text");

    if (vBanner) {
        vBanner.style.backgroundColor = "#F8FAFD";
        vBanner.style.borderColor = "#DDE8F4";
        vBanner.style.color = "#64748B";
    }
    if (vTitle) vTitle.innerText = "Pendiente de auditoría";
    if (vDesc) vDesc.innerText = "Presiona el botón Ejecutar análisis de seguridad para auditar el correo e incorporarlo al historial del usuario.";
    if (vPill) {
        vPill.innerText = "Pendiente";
        vPill.style.backgroundColor = "#E2E8F0";
        vPill.style.color = "#475569";
    }
    if (pFill) {
        pFill.style.width = "0%";
        pFill.style.backgroundColor = "#CBD5E1";
    }
    if (pVal) pVal.innerText = "0.0%";
}

function displayInboxAuditedResults(evalData, meta) {
    const risk = evalData.risk_level || "BAJO";

    const stChars = document.getElementById("inbox-val-char-count");
    const stWords = document.getElementById("inbox-val-url-count");
    const stHasUrl = document.getElementById("inbox-val-has-url");
    const stUrgency = document.getElementById("inbox-val-urgency-score");
    const stUrlDensity = document.getElementById("inbox-val-url-density");
    const stUrgDensity = document.getElementById("inbox-val-urgency-density");
    const stThreat = document.getElementById("inbox-val-is-threat");

    if (stChars) stChars.innerText = meta.char_count || 0;
    if (stWords) stWords.innerText = meta.url_count || 0;
    if (stHasUrl) stHasUrl.innerText = meta.has_url ? "SI" : "NO";
    if (stUrgency) stUrgency.innerText = meta.urgency_score || 0;
    if (stUrlDensity) stUrlDensity.innerText = (meta.url_density || 0) + "%";
    if (stUrgDensity) stUrgDensity.innerText = (meta.urgency_density || 0) + "%";
    if (stThreat) stThreat.innerText = meta.is_threat ? "Amenaza confirmada" : "Seguro";

    const vBanner = document.getElementById("inbox-verdict-banner");
    const vTitle = document.getElementById("inbox-verdict-title");
    const vDesc = document.getElementById("inbox-verdict-desc");
    const vPill = document.getElementById("inbox-verdict-risk-pill");
    const pFill = document.getElementById("inbox-prob-progress-fill");
    const pVal = document.getElementById("inbox-prob-value-text");

    if (vPill) vPill.innerText = risk;
    if (pVal) pVal.innerText = (evalData.confidence_score || 0) + "%";
    if (pFill) pFill.style.width = (evalData.confidence_score || 0) + "%";

    if (risk === "CRITICO") {
        if (vBanner) {
            vBanner.style.backgroundColor = "#FEF2F2";
            vBanner.style.borderColor = "#F87171";
            vBanner.style.color = "#991B1B";
        }
        if (vTitle) vTitle.innerText = "Amenaza crítica detectada";
        if (vDesc) vDesc.innerText = evalData.summary || "Se detectaron patrones de suplantación o coacción en el mensaje. Se sugiere aislarlo de la bandeja.";
        if (vPill) {
            vPill.style.backgroundColor = "#FEE2E2";
            vPill.style.color = "#991B1B";
        }
        if (pFill) pFill.style.backgroundColor = "#EF4444";
    } else if (risk === "MEDIO") {
        if (vBanner) {
            vBanner.style.backgroundColor = "#FFFBEB";
            vBanner.style.borderColor = "#FCD34D";
            vBanner.style.color = "#92400E";
        }
        if (vTitle) vTitle.innerText = "Riesgo moderado";
        if (vDesc) vDesc.innerText = evalData.summary || "El mensaje presenta indicadores que ameritan revisión antes de interactuar.";
        if (vPill) {
            vPill.style.backgroundColor = "#FEF3C7";
            vPill.style.color = "#92400E";
        }
        if (pFill) pFill.style.backgroundColor = "#F59E0B";
    } else {
        if (vBanner) {
            vBanner.style.backgroundColor = "#ECFDF5";
            vBanner.style.borderColor = "#6EE7B7";
            vBanner.style.color = "#065F46";
        }
        if (vTitle) vTitle.innerText = "Mensaje verificado y seguro";
        if (vDesc) vDesc.innerText = evalData.summary || "Estructura conforme sin indicios de riesgo o remitente verificado.";
        if (vPill) {
            vPill.style.backgroundColor = "#D1FAE5";
            vPill.style.color = "#065F46";
        }
        if (pFill) pFill.style.backgroundColor = "#10B981";
    }
}

function selectEmail(emailId) {
    currentEmailId = emailId;
    const item = loadedEmails.find(function (e) { return e.id === emailId; });
    if (!item) return;

    const allCards = document.querySelectorAll(".inbox-card");
    allCards.forEach(function (c) {
        if (c.getAttribute("data-email-id") === emailId) {
            c.classList.add("active-email");
        } else {
            c.classList.remove("active-email");
        }
    });

    const subjectEl = document.getElementById("reading-subject");
    const senderEl = document.getElementById("reading-sender");
    const dateEl = document.getElementById("reading-date");
    const bodyEl = document.getElementById("reading-body");

    if (subjectEl) subjectEl.innerText = item.subject || "Sin asunto";
    if (senderEl) senderEl.innerText = "Remitente: " + (item.sender || "Desconocido");
    if (dateEl) dateEl.innerText = "Fecha: " + (item.date || "-");
    if (bodyEl) bodyEl.innerText = item.body || item.snippet || "";

    const btnAnalyze = document.getElementById("btn-inbox-run-analysis");

    if (item.is_audited && item.evaluation && item.metadata) {
        if (btnAnalyze) {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = "&#10004; Correo auditado - Reanalizar";
            btnAnalyze.style.backgroundColor = "#059669";
        }
        displayInboxAuditedResults(item.evaluation, item.metadata);
    } else {
        if (btnAnalyze) {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = "&#9889; Ejecutar análisis de seguridad";
            btnAnalyze.style.backgroundColor = "#2E75D3";
        }
        resetInboxPanelsToPending();
    }
}

function runInboxEmailAnalysis() {
    if (!currentEmailId) {
        alert("Por favor selecciona un correo de la bandeja primero.");
        return;
    }
    const item = loadedEmails.find(function (e) { return e.id === currentEmailId; });
    if (!item) return;

    const btnAnalyze = document.getElementById("btn-inbox-run-analysis");
    if (btnAnalyze) {
        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = "&#9203; Analizando mensaje...";
        btnAnalyze.style.backgroundColor = "#64748B";
    }

    fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            raw_text: item.body || item.snippet || item.subject,
            sender: item.sender || "",
            reporter_id: "usuario.gmail"
        })
    })
    .then(function (res) { return res.json(); })
    .then(function (data) {
        if (data.status === "success") {
            const meta = data.metadata || {};
            const evalData = data.evaluation || {};

            item.is_audited = true;
            item.evaluation = evalData;
            item.metadata = meta;

            displayInboxAuditedResults(evalData, meta);

            if (btnAnalyze) {
                btnAnalyze.disabled = false;
                btnAnalyze.innerHTML = "&#10004; Análisis registrado en historial";
                btnAnalyze.style.backgroundColor = "#059669";
            }

            fetchIncidents();
            renderInboxList();
        } else {
            alert("Error al procesar el análisis.");
            if (btnAnalyze) {
                btnAnalyze.disabled = false;
                btnAnalyze.innerHTML = "&#9889; Ejecutar análisis de seguridad";
                btnAnalyze.style.backgroundColor = "#2E75D3";
            }
        }
    })
    .catch(function () {
        alert("Ocurrió un error al comunicarse con el servidor.");
        if (btnAnalyze) {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = "&#9889; Ejecutar análisis de seguridad";
            btnAnalyze.style.backgroundColor = "#2E75D3";
        }
    });
}

function initInboxEvents() {
    const btnAnalyze = document.getElementById("btn-inbox-run-analysis");
    if (btnAnalyze) {
        btnAnalyze.onclick = runInboxEmailAnalysis;
    }

    const btnRefresh = document.getElementById("btn-refresh-inbox");
    if (btnRefresh) {
        btnRefresh.onclick = function () {
            fetchInboxEmails("auto");
        };
    }
}

document.addEventListener("click", function (e) {
    const target = e.target;
    if (!target) {
        return;
    }



    const clearBtn = target.closest("#btn-clear-text");
    if (clearBtn) {
        const area = document.getElementById("email-text-input");
        if (area) {
            area.value = "";
        }
        resetPanels();
        return;
    }

    const analyzeBtn = target.closest("#btn-analyze-email");
    if (analyzeBtn) {
        const area = document.getElementById("email-text-input");
        const rawText = area ? area.value.trim() : "";
        if (!rawText) {
            alert("Por favor ingrese o seleccione un mensaje para analizar.");
            return;
        }
        performAnalysis(rawText, analyzeBtn);
        return;
    }

    const tabBtn = target.closest(".tab-btn");
    if (tabBtn) {
        const tabTarget = tabBtn.getAttribute("data-tab");
        const tabButtons = document.querySelectorAll(".tab-btn");
        const tabPanels = document.querySelectorAll(".tab-panel");
        tabButtons.forEach(function (b) { b.classList.remove("active"); });
        tabPanels.forEach(function (p) { p.classList.remove("active"); });
        tabBtn.classList.add("active");
        const targetPanel = document.getElementById(tabTarget);
        if (targetPanel) {
            targetPanel.classList.add("active");
        }
        if (tabTarget === "tab-soc") {
            fetchIncidents();
        }
        return;
    }



    const socActionBtn = target.closest(".soc-action-btn");
    if (socActionBtn) {
        const incId = socActionBtn.getAttribute("data-incident-id");
        const actType = socActionBtn.getAttribute("data-action-type");
        resolveIncidentAction(incId, actType);
        return;
    }
});

function resetPanels() {
    document.getElementById("val-char-count").innerText = "-";
    document.getElementById("val-url-count").innerText = "-";
    document.getElementById("val-has-url").innerText = "-";
    document.getElementById("val-urgency-score").innerText = "-";
    document.getElementById("val-url-density").innerText = "-";
    document.getElementById("val-urgency-density").innerText = "-";
    document.getElementById("val-is-threat").innerText = "-";

    const verdictBanner = document.getElementById("verdict-banner");
    if (verdictBanner) {
        verdictBanner.className = "verdict-banner";
        verdictBanner.style.backgroundColor = "#F8FAFD";
        verdictBanner.style.borderColor = "#DDE8F4";
        verdictBanner.style.color = "#64748B";
    }

    const vTitle = document.getElementById("verdict-title");
    if (vTitle) vTitle.innerText = "Esperando análisis";
    const vDesc = document.getElementById("verdict-desc");
    if (vDesc) vDesc.innerText = "Ingresa un correo para activar el motor.";
    const vPill = document.getElementById("verdict-risk-pill");
    if (vPill) {
        vPill.innerText = "Inactivo";
        vPill.style.backgroundColor = "#E2E8F0";
        vPill.style.color = "#475569";
    }

    const pFill = document.getElementById("prob-progress-fill");
    if (pFill) {
        pFill.style.width = "0%";
        pFill.style.backgroundColor = "#CBD5E1";
    }
    const pVal = document.getElementById("prob-value-text");
    if (pVal) pVal.innerText = "0.0%";

    const rulesContainer = document.getElementById("decision-rules-container");
    if (rulesContainer) {
        rulesContainer.innerHTML = '<div class="empty-state">Ejecuta un análisis para visualizar la secuencia lógica de decisión en niveles.</div>';
    }

}

function performAnalysis(text, analyzeBtn) {
    if (analyzeBtn) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerText = "Analizando...";
    }

    fetch("/api/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            raw_text: text,
            reporter_id: "emp.usr.001"
        })
    })
    .then(function (res) { return res.json(); })
    .then(function (data) {
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerText = "Ejecutar análisis de seguridad";
        }
        if (!data || !data.metadata || !data.evaluation) {
            alert("Error al procesar la respuesta del modelo.");
            return;
        }

        const meta = data.metadata;
        const evalRes = data.evaluation;

        document.getElementById("val-char-count").innerText = meta.char_count;
        document.getElementById("val-url-count").innerText = meta.url_count;
        document.getElementById("val-has-url").innerText = meta.has_url ? "SI" : "NO";
        document.getElementById("val-urgency-score").innerText = meta.urgency_score;
        document.getElementById("val-url-density").innerText = meta.url_density + "%";
        document.getElementById("val-urgency-density").innerText = meta.urgency_density + "%";
        document.getElementById("val-is-threat").innerText = meta.is_threat ? "Amenaza confirmada" : "Seguro";

        const risk = evalRes.risk_level;
        const verdictBanner = document.getElementById("verdict-banner");
        const vTitle = document.getElementById("verdict-title");
        const vDesc = document.getElementById("verdict-desc");
        const vPill = document.getElementById("verdict-risk-pill");
        const pFill = document.getElementById("prob-progress-fill");
        const pVal = document.getElementById("prob-value-text");

        vPill.innerText = risk;
        pVal.innerText = evalRes.confidence_score + "%";
        pFill.style.width = evalRes.confidence_score + "%";

        if (risk === "CRITICO") {
            verdictBanner.style.backgroundColor = "#FEF2F2";
            verdictBanner.style.borderColor = "#F87171";
            verdictBanner.style.color = "#991B1B";
            vTitle.innerText = "Amenaza crítica detectada";
            vDesc.innerText = "Se detectaron múltiples indicadores de phishing y alta densidad de urgencia. Aislamiento automático ejecutado.";
            vPill.style.backgroundColor = "#FEE2E2";
            vPill.style.color = "#991B1B";
            pFill.style.backgroundColor = "#EF4444";
        } else if (risk === "MEDIO") {
            verdictBanner.style.backgroundColor = "#FFFBEB";
            verdictBanner.style.borderColor = "#FCD34D";
            verdictBanner.style.color = "#92400E";
            vTitle.innerText = "Riesgo moderado";
            vDesc.innerText = "El mensaje presenta indicios sospechosos que requieren precaución.";
            vPill.style.backgroundColor = "#FEF3C7";
            vPill.style.color = "#92400E";
            pFill.style.backgroundColor = "#F59E0B";
        } else {
            verdictBanner.style.backgroundColor = "#ECFDF5";
            verdictBanner.style.borderColor = "#6EE7B7";
            verdictBanner.style.color = "#065F46";
            vTitle.innerText = "Mensaje conforme y seguro";
            vDesc.innerText = "No se detectaron anomalías en el patrón del mensaje.";
            vPill.style.backgroundColor = "#D1FAE5";
            vPill.style.color = "#065F46";
            pFill.style.backgroundColor = "#10B981";
        }

        const rulesContainer = document.getElementById("decision-rules-container");
        if (rulesContainer && evalRes.decision_rules) {
            rulesContainer.innerHTML = "";
            evalRes.decision_rules.forEach(function (rule) {
                const item = document.createElement("div");
                item.className = "rule-item";
                item.innerHTML = '<span class="rule-badge">Nivel ' + rule.level + '</span><span class="rule-text">' + rule.description + '</span>';
                rulesContainer.appendChild(item);
            });
        }


        fetchIncidents();
    })
    .catch(function () {
        if (analyzeBtn) {
            analyzeBtn.disabled = false;
            analyzeBtn.innerText = "Ejecutar análisis de seguridad";
        }
        alert("Ocurrió un error al comunicarse con el servidor.");
    });
}

function fetchIncidents() {
    fetch("/api/incidents")
        .then(function (res) { return res.json(); })
        .then(function (data) {
            if (!data) return;
            const badge = document.getElementById("badge-soc-count");
            if (badge) {
                badge.innerText = data.total_count || 0;
            }
            renderIncidentsTable(data.incidents || []);
        })
        .catch(function () {});
}

function renderIncidentsTable(incidents) {
    const tbody = document.getElementById("soc-incidents-tbody");
    if (!tbody) { return; }
    if (!incidents || incidents.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No hay incidentes registrados en el sistema.</td></tr>';
        return;
    }

    tbody.innerHTML = "";
    incidents.forEach(function (inc) {
        const tr = document.createElement("tr");
        const conf = inc.evaluation ? inc.evaluation.confidence_score + "%" : "-";
        const risk = inc.evaluation ? inc.evaluation.risk_level : inc.alert_level;

        let statusBadge = '<span style="background-color: #E2E8F0; color: #475569; padding: 4px 8px; border-radius: 9999px; font-weight: 700; font-size: 11px;">' + inc.status + '</span>';
        if (inc.status === "PENDING_SOC_REVIEW") {
            statusBadge = '<span style="background-color: #FEF3C7; color: #92400E; padding: 4px 8px; border-radius: 9999px; font-weight: 700; font-size: 11px;">REVISIÓN SOC</span>';
        } else if (inc.status === "RESOLVED_QUARANTINE" || inc.status === "AUTO_MITIGATED_QUARANTINE") {
            statusBadge = '<span style="background-color: #FEE2E2; color: #991B1B; padding: 4px 8px; border-radius: 9999px; font-weight: 700; font-size: 11px;">CUARENTENA</span>';
        } else if (inc.status === "RESOLVED_FALSE_POSITIVE" || inc.status === "MARKED_AS_SAFE") {
            statusBadge = '<span style="background-color: #D1FAE5; color: #065F46; padding: 4px 8px; border-radius: 9999px; font-weight: 700; font-size: 11px;">SEGURO</span>';
        }

        let userRecommendation = '<span style="color: #059669; font-weight: 600;">Lectura e interacción segura</span>';
        if (risk === "CRITICO") {
            userRecommendation = '<span style="color: #DC2626; font-weight: 600;">Aislar mensaje y no abrir enlaces</span>';
        } else if (risk === "MEDIO") {
            userRecommendation = '<span style="color: #D97706; font-weight: 600;">Verificar remitente antes de responder</span>';
        }

        if (inc.status === "PENDING_SOC_REVIEW" || inc.status === "PENDING_ANALYSIS") {
            userRecommendation += '<div style="display: flex; gap: 6px; margin-top: 6px;"><button type="button" class="btn-action-small btn-threat-confirm soc-action-btn" data-incident-id="' + inc.id + '" data-action-type="CONFIRMED_THREAT">Aislar</button><button type="button" class="btn-action-small btn-safe-confirm soc-action-btn" data-incident-id="' + inc.id + '" data-action-type="FALSE_POSITIVE">Restaurar</button></div>';
        }

        const sender = inc.metadata ? inc.metadata.anonymized_sender : "usuario@corporativo.com";

        tr.innerHTML = '<td><strong>' + inc.id + '</strong></td><td>' + sender + '</td><td>' + inc.reported_at + '</td><td>' + conf + '</td><td>' + risk + '</td><td>' + statusBadge + '</td><td>' + userRecommendation + '</td>';
        tbody.appendChild(tr);
    });
}

function resolveIncidentAction(incidentId, action) {
    fetch("/api/incidents/" + incidentId + "/resolve", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ action: action })
    })
    .then(function (res) { return res.json(); })
    .then(function () {
        fetchIncidents();
    });
}
