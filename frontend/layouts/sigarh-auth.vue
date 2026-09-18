<script setup lang="ts">
const benefits = [
  { icon: 'i-heroicons-user-group', title: 'Personas', text: 'Talento que cuida' },
  { icon: 'i-heroicons-calendar-days', title: 'Turnos', text: 'Organización eficiente' },
  { icon: 'i-heroicons-chart-bar', title: 'Desarrollo', text: 'Hospitales más fuertes' },
]
</script>

<template>
  <main class="sigarh-auth">
    <section class="brand-panel" aria-label="SIGARH, gestión de recursos humanos">
      <div class="brand-content">
        <img class="brand-logo" src="/img/logo-sigarh.png" alt="SIGARH — Sistema Integrado de Gestión de Recursos Humanos" width="2172" height="724" />
        <p class="erp-caption">Parte del ERP Hospitalario</p>
        <div class="brand-message">
          <div>
            <h1>Gestiona personal, turnos<br class="desktop-break" /> y talento humano con seguridad.</h1>
            <p>Un equipo comprometido,<br /> una mejor atención para todos.</p>
          </div>
          <aside class="brand-note" aria-hidden="true">Personas<br /> que hacen<br /> la diferencia</aside>
        </div>
        <ul class="benefits">
          <li v-for="benefit in benefits" :key="benefit.title">
            <span class="benefit-icon"><UIcon :name="benefit.icon" aria-hidden="true" /></span>
            <div><strong>{{ benefit.title }}</strong><span>{{ benefit.text }}</span></div>
          </li>
        </ul>
      </div>
      <div class="hospital-art"><img src="/img/hospital-illustration.png" alt="" /></div>
      <p class="brand-motto">Salud hoy. Personas siempre.</p>
    </section>

    <section class="login-panel" aria-label="Acceso a SIGARH">
      <div class="hospital-promise">
        <UIcon name="i-heroicons-plus" aria-hidden="true" />
        <span>Hospitales más humanos,<br /> organizaciones más fuertes.</span>
      </div>
      <div class="form-area"><slot /></div>
      <footer class="login-footer">
        <span>© {{ new Date().getFullYear() }} ERP Hospitalario</span>
        <span>Términos de uso</span>
        <span>Privacidad</span>
      </footer>
    </section>
  </main>
</template>

<style scoped>
.sigarh-auth {
  --ink: #082b45;
  --ink-soft: #587083;
  --teal: #009c9a;
  --teal-soft: #009c9a20;
  --alert: #9f2424;
  --alert-soft: #fff0f0;
  --radius: 10px;
  display: grid;
  grid-template-columns: 52% 48%;
  min-height: 100vh;
  min-height: 100svh;
  background: #fbfdff;
  color: var(--ink);
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}
.brand-panel { position: relative; isolation: isolate; display: flex; flex-direction: column; min-width: 0; overflow: hidden; background: #f2f8fd; }
.brand-panel::before { content: ''; position: absolute; inset: 0; z-index: -1; background: url('/img/bg-abstract.png') center / cover no-repeat; opacity: .45; }
.brand-content { padding: clamp(36px, 7vh, 76px) clamp(32px, 5.7vw, 96px) 0; }
.brand-logo { width: 390px; max-width: 100%; height: auto; object-fit: contain; }
.erp-caption { display: flex; align-items: center; gap: 18px; margin: 18px 0 32px; color: var(--ink-soft); font-size: 18px; }
.erp-caption::before { content: ''; width: 40px; height: 1px; background: #c6dce8; }
.brand-message { position: relative; }
.brand-message h1 { max-width: 570px; margin: 0; font-size: clamp(28px, 2.35vw, 40px); font-weight: 700; letter-spacing: -.035em; line-height: 1.25; }
.brand-message p { margin: 16px 0 0; color: var(--ink-soft); font-size: clamp(17px, 1.45vw, 22px); line-height: 1.45; }
.brand-note { display: none; }
.benefits { display: flex; justify-content: space-between; gap: 14px; list-style: none; padding: 0; margin: 30px 0 0; }
.benefits li { display: flex; align-items: center; gap: 12px; }
.benefit-icon { flex-shrink: 0; display: grid; place-items: center; width: 56px; height: 56px; border-radius: 50%; background: #dceeff; color: #09609e; }
.benefit-icon :deep(.iconify) { width: 28px; height: 28px; }
.benefits strong { display: block; font-size: 13px; font-weight: 600; }
.benefits div > span { display: block; margin-top: 4px; color: var(--ink-soft); font-size: 11px; line-height: 1.4; }
.hospital-art { position: relative; flex: 1; min-height: 215px; margin-top: 10px; }
.hospital-art img { position: absolute; left: 0; top: -50%; width: 100%; height: 180%; object-fit: contain; }
.brand-motto { display: flex; align-items: center; gap: 20px; margin: 0; padding: 12px 7% 32px; color: var(--ink-soft); font-size: 14px; }
.brand-motto::before { content: ''; width: 32px; height: 1px; background: #0b4562; }
.login-panel { display: flex; flex-direction: column; min-width: 0; padding: 28px clamp(24px, 4vw, 68px) 32px; }
.hospital-promise { display: flex; align-self: flex-end; align-items: center; gap: 22px; margin-bottom: 32px; color: var(--ink-soft); font-size: 13px; line-height: 1.3; }
.hospital-promise :deep(.iconify) { width: 36px; height: 36px; color: #009c9a; }
.hospital-promise span:last-child { padding-left: 22px; border-left: 1px solid #ccdae6; }
.form-area { flex: 1; display: flex; align-items: center; justify-content: center; width: 100%; }
.login-footer { display: flex; flex-wrap: wrap; justify-content: center; gap: 12px; margin-top: 28px; color: var(--ink-soft); font-size: 11px; line-height: 1.5; }
.login-footer span + span { border-left: 1px solid #b6c9d9; padding-left: 12px; }
@media (min-width: 1600px) {
  .brand-content { padding-right: 42px; }
  .brand-message { padding-right: 135px; }
  .brand-message h1 { font-size: 34px; }
  .brand-note { position: absolute; top: 0; right: 0; display: block; padding: 24px 0 24px 18px; border-left: 1px solid #a5d5e0; color: #587083; font-size: 12px; line-height: 1.65; letter-spacing: .1em; text-transform: uppercase; }
  .brand-note::before, .brand-note::after { content: ''; display: block; width: 28px; height: 2px; margin: 0 0 22px; background: #009c9a; }
  .brand-note::after { margin: 22px 0 0; }
}
@media (min-width: 768px) and (max-width: 1199px) {
  .sigarh-auth { grid-template-columns: 45% 55%; }
  .brand-content { padding: 48px 28px 0; }
  .brand-message h1 { font-size: 28px; }
  .benefits { flex-wrap: wrap; gap: 16px; }
  .benefits li { flex: 1 1 130px; }
  .benefit-icon { width: 42px; height: 42px; }
  .login-panel { padding: 24px 20px; }
  .desktop-break { display: none; }
}
@media (min-width: 768px) and (max-height: 800px) {
  .brand-content { padding-top: 30px; }
  .erp-caption { margin-bottom: 24px; }
  .benefits { margin-top: 24px; }
  .hospital-art { min-height: 180px; }
  .brand-motto { padding-bottom: 22px; }
  .hospital-promise { margin-bottom: 20px; }
  .login-panel { padding-top: 20px; padding-bottom: 22px; }
  .login-footer { margin-top: 20px; }
}
/* Compensate the 80% visual scale so both panels still fill the viewport. */
@media (min-width: 768px) {
  .sigarh-auth {
    zoom: .8;
    width: auto;
    height: 125dvh;
    min-height: 125dvh;
    grid-template-rows: minmax(0, 1fr);
  }
  .brand-panel, .login-panel { min-height: 0; }
  .hospital-art { min-height: 0; }
  .form-area { min-height: 0; }
  .form-area :deep(.login-card--sigarh) { animation: none; }
}
@media (max-width: 767px) {
  .sigarh-auth { grid-template-columns: minmax(0, 1fr); }
  .brand-content { padding: 26px 24px 18px; }
  .brand-logo { width: 280px; margin: 0 auto; }
  .erp-caption { justify-content: center; font-size: 13px; margin: 10px 0 0; }
  .erp-caption::before, .brand-message, .benefits, .hospital-art, .brand-motto, .hospital-promise { display: none; }
  .login-panel { padding: 8px 20px 24px; }
  .form-area { align-items: flex-start; }
  .login-footer { gap: 8px; font-size: 10px; margin-top: 24px; }
  .login-footer span + span { padding-left: 8px; }
}
</style>
