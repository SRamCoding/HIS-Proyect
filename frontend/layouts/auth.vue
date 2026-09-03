<template>
  <main class="auth-page">
    <section class="auth-shell">
      <aside class="brand-panel" aria-label="Información de ERP Hospitalario">
        <div class="photo-panel">
          <img
            src="/ban.png"
            alt="Médico del sistema"
            class="photo-img"
          />
          <div class="photo-overlay" />
        </div>

        <div class="brand-copy">
          <div class="brand-rule" />

          <Transition name="slide-fade" mode="out-in">
            <div :key="slideActual">
              <p class="eyebrow">{{ slides[slideActual].eyebrow }}</p>
              <h1>{{ slides[slideActual].title }}</h1>
              <p class="description">{{ slides[slideActual].description }}</p>
            </div>
          </Transition>

          <div class="stats-row">
            <div class="stat-item">
              <UIcon name="i-heroicons-building-office-2" class="stat-icon" />
              <div>
                <strong>+50</strong>
                <span>Hospitales</span>
              </div>
            </div>
            <div class="stat-item">
              <UIcon name="i-heroicons-users" class="stat-icon" />
              <div>
                <strong>+3,200</strong>
                <span>Usuarios</span>
              </div>
            </div>
            <div class="stat-item">
              <UIcon name="i-heroicons-heart" class="stat-icon" />
              <div>
                <strong>99.9%</strong>
                <span>Disponibilidad</span>
              </div>
            </div>
          </div>

          <div class="slide-dots">
            <button
              v-for="(s, i) in slides"
              :key="i"
              class="slide-dot"
              :class="{ 'slide-dot--active': i === slideActual }"
              :aria-label="`Ver slide ${i + 1}`"
              @click="irASlide(i)"
            />
          </div>

          <svg class="pulse-svg" viewBox="0 0 400 60" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <path
              class="pulse-path"
              d="M0,32 L48,32 L64,32 L76,12 L92,52 L108,32 L134,32 L146,20 L158,32 L400,32"
              fill="none"
              stroke="#5fd4c6"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              pathLength="1"
            />
          </svg>
        </div>
      </aside>

      <section class="form-panel">
       

        <div class="form-panel__content">
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
        </div>
      </section>
    </section>

    <!-- Botón flotante de soporte 24h -->
    <a
      href="https://atencionalcliente.techquk.com/"
      target="_blank"
      rel="noopener noreferrer"
      class="support-fab"
      aria-label="Soporte 24 horas"
    >
      <span class="support-fab__pulse" />
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
      <span class="support-fab__tooltip">Soporte 24h</span>
    </a>
  </main>
</template>

<script setup lang="ts">
const slides = [
  {
    eyebrow: 'BIENVENIDO A',
    title: 'Tu sistema hospitalario, en un solo lugar',
    description: 'Gestiona admisión, historias clínicas, farmacia, laboratorio y recursos humanos con seguridad.',
  },
  {
    eyebrow: 'MULTI-ESTABLECIMIENTO',
    title: 'Un panel para cada hospital de tu red',
    description: 'Administra múltiples establecimientos con módulos independientes desde una sola plataforma.',
  },
  {
    eyebrow: 'ACCESO SEGURO',
    title: 'Roles y permisos por establecimiento',
    description: 'Cada usuario accede solo a lo que le corresponde, con auditoría completa de la actividad.',
  },
]

const slideActual = ref(0)
let intervalId: ReturnType<typeof setInterval> | undefined

const irASlide = (i: number) => {
  slideActual.value = i
  reiniciarIntervalo()
}

const avanzarSlide = () => {
  slideActual.value = (slideActual.value + 1) % slides.length
}

const reiniciarIntervalo = () => {
  if (intervalId) clearInterval(intervalId)
  intervalId = setInterval(avanzarSlide, 4000)
}

onMounted(() => {
  reiniciarIntervalo()
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
})
</script>

<style scoped>
.auth-page {
  height: 100vh;
  overflow: hidden;
  display: block;
  padding: 0;
  background: var(--paper);
  font-family: 'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif;
}
.auth-shell {
  width: 100%;
  height: 100vh;
  display: grid;
  grid-template-columns: 38% 62%;
  overflow: hidden;
  background: var(--paper);
}
.brand-panel {
  display: grid;
  grid-template-rows: 48% 52%;
  height: 100%;
  overflow: hidden;
  color: #fff;
}
.photo-panel {
  position: relative;
  overflow: hidden;
  background: var(--navy);
}
.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center 20%;
}
.photo-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(11,95,168,0.05) 0%, rgba(11,95,168,0.35) 100%);
}
.brand-copy {
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 42px 40px 24px;
  background: linear-gradient(145deg, var(--navy), var(--navy-hover));
  overflow: hidden;
}
.brand-copy::after {
  content: '';
  position: absolute;
  width: 220px;
  height: 220px;
  right: -120px;
  bottom: -135px;
  border-radius: 50%;
  background: rgba(95, 212, 198, 0.12);
}
.brand-rule {
  width: 3px;
  height: 54px;
  margin: 0 0 14px;
  background: var(--teal);
}
.eyebrow {
  margin: 0 0 6px;
  color: #9fc3d6;
  font-size: 10px;
  letter-spacing: .15em;
  font-weight: 700;
}
.brand-copy h1 {
  max-width: 265px;
  min-height: 66px;
  margin: 0;
  font-size: 24px;
  line-height: 1.15;
  letter-spacing: -.03em;
}
.description {
  max-width: 285px;
  min-height: 60px;
  margin: 14px 0 0;
  color: #b8ccd6;
  font-size: 12px;
  line-height: 1.65;
}
.stats-row {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 26px;
  margin-top: 20px;
}
.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.stat-icon {
  width: 20px;
  height: 20px;
  color: var(--teal);
  flex-shrink: 0;
}
.stat-item div {
  display: flex;
  flex-direction: column;
}
.stat-item strong {
  color: white;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.1;
}
.stat-item span {
  margin-top: 2px;
  color: #9fb8c4;
  font-size: 9px;
}
.slide-dots {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 6px;
  margin-top: 22px;
}
.slide-dot {
  width: 18px;
  height: 3px;
  border-radius: 2px;
  border: 0;
  background: rgba(255,255,255,0.25);
  cursor: pointer;
  padding: 0;
  transition: background 0.2s ease, width 0.2s ease;
}
.slide-dot--active {
  background: var(--teal);
  width: 26px;
}
.pulse-svg {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 44px;
  margin-top: auto;
  padding-top: 12px;
}
.pulse-path {
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  animation: pulse-draw 4s ease-in-out infinite;
}
@keyframes pulse-draw {
  0% { stroke-dashoffset: 1; opacity: 0.25; }
  50% { stroke-dashoffset: 0; opacity: 0.7; }
  100% { stroke-dashoffset: -1; opacity: 0.25; }
}
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}
.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* PANEL DERECHO */
.form-panel {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow-y: auto;
  overflow-x: hidden;
  background-image: url('/fondo.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.form-panel__content {
  position: relative;
  z-index: 1;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 56px 56px 32px;
}
.language-selector {
  position: absolute;
  z-index: 2;
  top: 28px;
  right: 32px;
  display: flex;
  align-items: center;
  gap: 8px;
  height: 36px;
  padding: 0 13px;
  border: 1px solid var(--line);
  border-radius: 20px;
  background: var(--paper);
  color: var(--ink);
  font: inherit;
  font-size: 11px;
  font-weight: 650;
  cursor: pointer;
  transition: background 0.15s ease, border-color 0.15s ease;
}
.language-selector:hover {
  background: var(--mist);
  border-color: #bacbd0;
}
.language-selector :deep(svg) {
  width: 15px;
  height: 15px;
}
.language-arrow {
  width: 12px;
  height: 12px;
}
.form-container {
  width: 100%;
  max-width: 460px;
  display: flex;
  justify-content: center;
}
.trust-row {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-top: 32px;
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
  width: 15px;
  height: 15px;
  color: var(--teal);
}
.auth-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 18px;
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
  right: 26px;
  bottom: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--teal, #5fd4c6);
  box-shadow: 0 6px 18px rgba(11, 95, 168, 0.28);
  text-decoration: none;
  transition: transform 0.18s ease, box-shadow 0.18s ease, width 0.25s ease, border-radius 0.25s ease;
}
.support-fab:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 24px rgba(11, 95, 168, 0.35);
}
.support-fab__icon {
  width: 26px;
  height: 26px;
  color: var(--navy, #0b5fa8);
  position: relative;
  z-index: 2;
}
.support-fab__pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: var(--teal, #5fd4c6);
  opacity: 0.55;
  animation: support-fab-pulse 2.2s ease-out infinite;
}
@keyframes support-fab-pulse {
  0% { transform: scale(1); opacity: 0.55; }
  100% { transform: scale(1.7); opacity: 0; }
}
.support-fab__tooltip {
  position: absolute;
  right: 68px;
  top: 50%;
  transform: translateY(-50%) translateX(6px);
  padding: 6px 12px;
  border-radius: 8px;
  background: var(--navy, #0b3350);
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.support-fab:hover .support-fab__tooltip {
  opacity: 1;
  transform: translateY(-50%) translateX(0);
}

@media (max-width: 760px) {
  .auth-shell { grid-template-columns: 1fr; }
  .brand-panel { display: none; }
  .form-panel__content { padding: 32px 24px; }
  .language-selector { top: 18px; right: 18px; }
  .trust-row { gap: 14px; }
  .support-fab { right: 16px; bottom: 16px; width: 50px; height: 50px; }
  .support-fab__tooltip { display: none; }
}
</style>