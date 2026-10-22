// Request Google's widget only after the visitor interacts with the lead form.
(() => {
  const form = document.getElementById("lead-form");
  const container = form?.querySelector(".g-recaptcha");
  if (!form || !container) return;
  let requested = false;
  let rendered = false;
  window.innovenCaptchaReady = () => {
    if (rendered) return;
    window.grecaptcha.render(container, {
      sitekey: container.dataset.sitekey,
      theme: container.dataset.theme || "dark",
    });
    rendered = true;
  };
  function loadCaptcha() {
    if (requested) return;
    requested = true;
    if (window.grecaptcha?.render) {
      window.innovenCaptchaReady();
      return;
    }
    const script = document.createElement("script");
    script.src = "https://www.google.com/recaptcha/api.js?onload=innovenCaptchaReady&render=explicit";
    script.async = true;
    script.onerror = () => {
      requested = false;
      script.remove();
      document.getElementById("captcha-error")?.classList.remove("hidden");
    };
    document.head.appendChild(script);
  }
  form.addEventListener("focusin", loadCaptcha);
  form.addEventListener("pointerdown", loadCaptcha);
  form.addEventListener("submit", loadCaptcha);
})();
