<template>
  <main class="auth-page">
    <div class="brand-mark">
      <span class="brand-mark__icon"><UIcon name="i-heroicons-plus" class="w-3.5 h-3.5" /></span>
      <span class="brand-mark__text">ERP Hospitalario</span>
    </div>

    <section class="auth-center">
      <div class="form-container">
        <slot />
      </div>

      <div class="trust-row">
        <div class="trust-item">
          <UIcon name="i-heroicons-shield-check" />
          <span>Datos cifrados</span>
        </div>
        <div class="trust-item">
          <UIcon name="i-heroicons-server-stack" />
          <span>Infraestructura en la nube</span>
        </div>
        <div class="trust-item">
          <UIcon name="i-heroicons-clock" />
          <span>Soporte 24/7</span>
        </div>
      </div>

      <footer class="auth-footer">
        <span>© {{ new Date().getFullYear() }} ERP Hospitalario</span>
        <span class="footer-separator">•</span>
        <a href="#">Términos de uso</a>
        <span class="footer-separator">•</span>
        <a href="#">Privacidad</a>
      </footer>
    </section>

    <!-- Botón flotante de soporte 24h -->
    <a
      href="https://atencionalcliente.techquk.com/"
      target="_blank"
      rel="noopener noreferrer"
      class="support-fab"
      aria-label="Soporte 24 horas"
    >
      <span class="support-fab__ring" />
      <span class="support-fab__pulse" />
      <span class="support-fab__body">
        <svg
          class="support-fab__icon"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M4 13.5V12a8 8 0 0 1 16 0v1.5"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
          />
          <rect x="2.5" y="12.5" width="4" height="6" rx="1.6" fill="currentColor" />
          <rect x="17.5" y="12.5" width="4" height="6" rx="1.6" fill="currentColor" />
          <path
            d="M18.5 18.5v1a2.5 2.5 0 0 1-2.5 2.5h-2.6"
            stroke="currentColor"
            stroke-width="1.8"
            stroke-linecap="round"
          />
          <circle cx="12" cy="22" r="1.2" fill="currentColor" />
        </svg>
        <span class="support-fab__dot" />
      </span>
      <span class="support-fab__tooltip">
        <strong>Soporte 24h</strong>
        <small>Estamos en línea</small>
      </span>
    </a>
  </main>
</template>

<script setup lang="ts">
</script>

<style scoped>
.auth-page {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 24px 32px;
  background: var(--paper);
  font-family: 'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif;
}

.brand-mark {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 48px;
}
.brand-mark__icon {
  display: inline-grid;
  place-items: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--navy);
  color: #fff;
}
.brand-mark__text {
  color: var(--navy);
  font-size: 15px;
  font-weight: 750;
}

.auth-center {
  flex: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.form-container {
  width: 100%;
  max-width: 420px;
  display: flex;
  justify-content: center;
}

.trust-row {
  display: flex;
  align-items: center;
  gap: 22px;
  margin-top: 36px;
  flex-wrap: wrap;
  justify-content: center;
}
.trust-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--ink-soft);
  font-size: 11px;
  font-weight: 500;
}
.trust-item :deep(svg) {
  width: 14px;
  height: 14px;
  color: var(--teal);
}

.auth-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
  color: var(--ink-soft);
  font-size: 10px;
}
.auth-footer a {
  color: var(--ink-soft);
  text-decoration: none;
}
.auth-footer a:hover {
  text-decoration: underline;
}
.footer-separator {
  color: var(--line);
}

/* BOTÓN FLOTANTE DE SOPORTE 24H */
.support-fab {
  position: fixed;
  z-index: 50;
  right: 28px;
  bottom: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  text-decoration: none;
}
.support-fab__body {
  position: relative;
  z-index: 3;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(150deg, var(--teal, #5fd4c6) 0%, var(--navy, #0b5fa8) 115%);
  box-shadow:
    0 10px 24px rgba(11, 51, 80, 0.35),
    0 2px 6px rgba(11, 51, 80, 0.22),
    inset 0 1px 1px rgba(255, 255, 255, 0.35);
  transition: transform 0.22s cubic-bezier(.34,1.56,.64,1), box-shadow 0.22s ease;
}
.support-fab:hover .support-fab__body {
  transform: translateY(-3px) scale(1.06);
  box-shadow:
    0 16px 30px rgba(11, 51, 80, 0.4),
    0 4px 10px rgba(11, 51, 80, 0.25),
    inset 0 1px 1px rgba(255, 255, 255, 0.4);
}
.support-fab:active .support-fab__body {
  transform: translateY(0) scale(0.97);
}
.support-fab__icon {
  width: 27px;
  height: 27px;
  color: #ffffff;
  filter: drop-shadow(0 1px 1px rgba(0,0,0,0.15));
}
.support-fab__dot {
  position: absolute;
  right: 3px;
  bottom: 3px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #34d399;
  border: 2.5px solid #ffffff;
  box-shadow: 0 0 0 1px rgba(11, 51, 80, 0.15);
}
.support-fab__ring {
  position: absolute;
  inset: -5px;
  border-radius: 50%;
  border: 1.5px solid rgba(95, 212, 198, 0.55);
  opacity: 0;
  animation: support-fab-ring 2.6s ease-out infinite;
}
.support-fab__pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: var(--teal, #5fd4c6);
  opacity: 0.45;
  animation: support-fab-pulse 2.6s ease-out infinite;
}
@keyframes support-fab-pulse {
  0% { transform: scale(0.9); opacity: 0.45; }
  100% { transform: scale(1.6); opacity: 0; }
}
@keyframes support-fab-ring {
  0% { transform: scale(0.85); opacity: 0.6; }
  100% { transform: scale(1.35); opacity: 0; }
}
.support-fab__tooltip {
  position: absolute;
  z-index: 2;
  right: 74px;
  top: 50%;
  display: flex;
  flex-direction: column;
  gap: 1px;
  transform: translateY(-50%) translateX(6px);
  padding: 8px 14px;
  border-radius: 10px;
  background: var(--navy, #0b3350);
  box-shadow: 0 8px 18px rgba(11, 51, 80, 0.3);
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.support-fab__tooltip::after {
  content: '';
  position: absolute;
  right: -5px;
  top: 50%;
  transform: translateY(-50%);
  width: 10px;
  height: 10px;
  background: var(--navy, #0b3350);
  clip-path: polygon(0 0, 0 100%, 100% 50%);
}
.support-fab__tooltip strong {
  color: #fff;
  font-size: 12.5px;
  font-weight: 700;
}
.support-fab__tooltip small {
  color: #9fc3d6;
  font-size: 10.5px;
  font-weight: 500;
}
.support-fab:hover .support-fab__tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

@media (max-width: 560px) {
  .auth-page { padding: 28px 16px 24px; }
  .brand-mark { margin-bottom: 32px; }
  .trust-row { gap: 14px; }
  .support-fab { right: 18px; bottom: 18px; width: 54px; height: 54px; }
  .support-fab__body { width: 54px; height: 54px; }
  .support-fab__icon { width: 24px; height: 24px; }
  .support-fab__tooltip { display: none; }
}
</style>
