// Keep contact validation and CAPTCHA handling identical in all four languages.
(() => {
  const form = document.getElementById("lead-form");
  const container = form?.querySelector(".g-recaptcha");
  if (!form || !container) return;
  const language = document.documentElement.lang.slice(0, 2);
  const messages = {
    es: ["Cargando verificación…", "Completa la verificación para enviar tu solicitud.", "No se pudo conectar con la verificación. Reintenta sin perder tus datos.", "La verificación venció. Complétala de nuevo.", "Reintentar verificación", "Solicitud enviada. El equipo de INNOVEN dará seguimiento a tu requerimiento."],
    en: ["Loading verification…", "Complete verification to send your request.", "Could not connect to verification. Retry without losing your details.", "Verification expired. Complete it again.", "Retry verification", "Request sent. The INNOVEN team will follow up with you."],
    fr: ["Chargement de la vérification…", "Terminez la vérification pour envoyer votre demande.", "Connexion à la vérification impossible. Réessayez sans perdre vos données.", "La vérification a expiré. Recommencez-la.", "Réessayer la vérification", "Demande envoyée. L’équipe INNOVEN assurera le suivi."],
    it: ["Caricamento della verifica…", "Completa la verifica per inviare la richiesta.", "Impossibile collegarsi alla verifica. Riprova senza perdere i dati.", "La verifica è scaduta. Completala di nuovo.", "Riprova la verifica", "Richiesta inviata. Il team INNOVEN darà seguito alla richiesta."],
  }[language] || ["Loading verification…", "Complete verification to send your request.", "Could not connect to verification. Please retry.", "Verification expired. Complete it again.", "Retry verification", "Request sent. The INNOVEN team will follow up."];
  const status = document.getElementById("captcha-error");
  const retry = document.getElementById("captcha-retry");
  const submitButton = form.querySelector('button[type="submit"]');
  let submissionId = crypto.randomUUID();
  let sending = false;
  const deliveryMessages = {
    es: ["Enviando solicitud…", "No se pudo confirmar el envío. Tus datos siguen aquí; vuelve a verificar y reintenta."],
    en: ["Sending request…", "Delivery could not be confirmed. Your details are still here; verify again and retry."],
    fr: ["Envoi de la demande…", "L’envoi n’a pas été confirmé. Vos données sont conservées ; vérifiez à nouveau et réessayez."],
    it: ["Invio della richiesta…", "Invio non confermato. I dati sono conservati; verifica di nuovo e riprova."],
  }[language] || ["Sending request…", "Delivery could not be confirmed. Please verify again and retry."];
  let script;
  let timer;
  let requested = false;
  let widgetId;
  retry.textContent = messages[4];
  function show(message, canRetry = false) {
    status.textContent = message;
    status.classList.toggle("hidden", !message);
    retry.classList.toggle("hidden", !canRetry);
  }
  function unavailable() {
    clearTimeout(timer);
    if (widgetId === undefined) {
      requested = false;
      script?.remove();
    }
    show(messages[2], true);
  }
  // Google's automatic mode initializes the first widget on this page as 0.
  // Configure callbacks before adding its API script.
  container.dataset.callback = "innovenCaptchaSolved";
  container.dataset.expiredCallback = "innovenCaptchaExpired";
  container.dataset.errorCallback = "innovenCaptchaError";
  window.innovenCaptchaSolved = () => show("");
  window.innovenCaptchaExpired = () => show(messages[3], true);
  window.innovenCaptchaError = unavailable;
  window.innovenCaptchaReady = () => {
    clearTimeout(timer);
    widgetId = 0;
    show(messages[1]);
  };
  function loadCaptcha() {
    if (requested) return;
    requested = true;
    show(messages[0]);
    container.dataset.size = container.parentElement.clientWidth < 304 ? "compact" : "normal";
    script = document.createElement("script");
    // Google's documented alternate endpoint for networks blocking google.com.
    script.src = `https://www.recaptcha.net/recaptcha/api.js?onload=innovenCaptchaReady&hl=${language}`;
    script.async = true;
    script.onerror = unavailable;
    timer = setTimeout(unavailable, 20000);
    document.head.appendChild(script);
  }
  retry.addEventListener("click", () => {
    if (widgetId !== undefined) {
      window.grecaptcha.reset(widgetId);
      show(messages[1]);
    } else {
      loadCaptcha();
    }
  });
  form.addEventListener("focusin", loadCaptcha);
  form.addEventListener("pointerdown", loadCaptcha);
  form.addEventListener("input", (event) => {
    if (event.target.name !== "g-recaptcha-response") submissionId = crypto.randomUUID();
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (sending || !form.reportValidity()) return;
    loadCaptcha();
    let response = "";
    try {
      response = widgetId === undefined ? "" : window.grecaptcha?.getResponse(widgetId);
    } catch {
      // The automatic widget may still be initializing after the API callback.
    }
    if (!response) {
      if (!retry.classList.contains("hidden")) return;
      show(messages[1]);
      return;
    }
    const fields = Object.fromEntries(new FormData(form));
    const payload = {
      nombre: fields.nombre, empresa: fields.empresa, email: fields.email,
      telefono: fields.telefono, servicio: fields.servicio, mensaje: fields.mensaje,
      website: fields.website || "", captchaToken: response, submissionId,
    };
    sending = true;
    submitButton.disabled = true;
    form.setAttribute("aria-busy", "true");
    show(deliveryMessages[0]);
    const controller = new AbortController();
    const sendTimer = setTimeout(() => controller.abort(), 25000);
    try {
      const result = await fetch("https://app.innovenca.com/api/innoven/contact", {
        method: "POST", mode: "cors", credentials: "omit", referrerPolicy: "origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload), signal: controller.signal,
      });
      const receipt = await result.json();
      if (!result.ok || receipt.ok !== true || receipt.submissionId !== payload.submissionId) throw new Error("Delivery not confirmed");
      if (submissionId === payload.submissionId) {
        form.reset();
        submissionId = crypto.randomUUID();
      }
      window.grecaptcha.reset(widgetId);
      show(messages[5]);
    } catch {
      // A failed/uncertain request must not erase the visitor's information.
      window.grecaptcha.reset(widgetId);
      show(deliveryMessages[1], true);
    } finally {
      clearTimeout(sendTimer);
      sending = false;
      submitButton.disabled = false;
      form.setAttribute("aria-busy", "false");
    }
  });
})();
