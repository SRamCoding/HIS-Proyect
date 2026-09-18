<script setup lang="ts">
const benefits = [
  { icon: 'i-heroicons-user-group', title: 'Atención', text: 'Mejores experiencias para pacientes y profesionales.' },
  { icon: 'i-heroicons-shield-check', title: 'Seguridad', text: 'Tu información, siempre protegida.' },
  { icon: 'i-heroicons-phone', title: 'Soporte', text: 'Un equipo listo para ayudarte.' },
]
</script>

<template>
  <main class="hospital-auth">
    <section class="visual-panel" aria-label="Portal Hospitalario">
      <div class="visual-content">
        <div class="portal-logo"><img src="/app/logo-portal-hospitalario.png" alt="Portal Hospitalario — Acceso institucional seguro" /></div>
        <div class="portal-message">
          <h1>Tecnología para una<br /> atención más humana<br /> y eficiente.</h1>
          <p>Conecta personas, procesos y servicios<br /> en un solo lugar.</p>
        </div>
        <ul class="portal-benefits">
          <li v-for="benefit in benefits" :key="benefit.title">
            <span class="benefit-icon"><UIcon :name="benefit.icon" aria-hidden="true" /></span>
            <div><strong>{{ benefit.title }}</strong><p>{{ benefit.text }}</p></div>
          </li>
        </ul>
      </div>
      <div class="hospital-art"><img src="/app/hospital-illustration.png" alt="" /></div>
    </section>
    <section class="auth-panel" aria-label="Acceso institucional">
      <div class="form-area"><slot /></div>
      <footer>
        <span>© {{ new Date().getFullYear() }} Portal Hospitalario</span>
        <span>Términos de uso</span>
        <span>Privacidad</span>
      </footer>
    </section>
  </main>
</template>

<style scoped>
.hospital-auth {
  --ink: #082a4a;
  --ink-soft: #5b7185;
  --teal: #009fa3;
  --teal-soft: #009fa320;
  --radius: 10px;
  display: grid;
  grid-template-columns: 51% 49%;
  grid-template-rows: minmax(0, 1fr);
  min-height: 125dvh;
  height: 125dvh;
  zoom: .8;
  color: var(--ink);
  background: #fcfdfe;
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
}
.visual-panel { position: relative; isolation: isolate; display: flex; flex-direction: column; min-width: 0; min-height: 0; overflow: hidden; background: #f8fbfd; }
.visual-panel::before { content: ''; position: absolute; inset: 65% 0 0; z-index: -1; background: url('/app/bg-abstract.png') center bottom / cover no-repeat; opacity: .4; mask-image: linear-gradient(to bottom, transparent, #000 120px); }
.visual-content { padding: clamp(40px, 5vh, 60px) clamp(32px, 7vw, 130px) 0; }
/* The supplied logo includes transparent margins; crop only that empty area. */
.portal-logo { position: relative; width: 330px; max-width: 100%; aspect-ratio: 4.5; overflow: hidden; }
.portal-logo img { position: absolute; width: 108%; max-width: none; height: auto; left: -7%; top: 50%; transform: translateY(-51.5%); }
.portal-message { margin-top: 56px; }
.portal-message h1 { margin: 0; font-size: clamp(32px, 2.5vw, 44px); line-height: 1.12; font-weight: 700; letter-spacing: -.035em; }
.portal-message > p { margin: 16px 0 0; color: var(--ink-soft); font-size: 20px; line-height: 1.5; }
.portal-benefits { list-style: none; display: grid; gap: 18px; margin: 24px 0 0; padding: 0; }
.portal-benefits li { display: flex; align-items: center; gap: 20px; }
.benefit-icon { display: grid; place-items: center; flex-shrink: 0; width: 56px; height: 56px; border-radius: 50%; background: #dff0ff; color: #0875ae; }
.portal-benefits li:nth-child(2) .benefit-icon { background: #ddf2f3; color: #008493; }
.benefit-icon :deep(.iconify) { width: 28px; height: 28px; }
.portal-benefits strong { font-size: 16px; font-weight: 700; }
.portal-benefits p { margin: 4px 0 0; max-width: 320px; font-size: 15px; line-height: 1.45; color: var(--ink-soft); }
.hospital-art { position: relative; flex: 1; min-height: 0; margin-top: 12px; }
.hospital-art img { position: absolute; width: 100%; height: 140%; top: -32%; left: 0; object-fit: contain; object-position: center bottom; }
.auth-panel { display: flex; flex-direction: column; min-width: 0; min-height: 0; padding: 44px clamp(28px, 5vw, 90px) 32px; }
.form-area { flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center; }
footer { display: flex; flex-wrap: wrap; justify-content: center; gap: 14px; margin-top: 40px; color: var(--ink-soft); font-size: 13px; line-height: 1.5; }
footer span + span::before { content: '·'; margin-right: 14px; color: #9db6c6; }
@media (min-width: 768px) and (max-height: 800px) {
  .visual-content { padding-top: 32px; }
  .portal-message { margin-top: 36px; }
  .portal-message h1 { font-size: 34px; }
  .portal-message > p { font-size: 18px; margin-top: 12px; }
  .portal-benefits { gap: 12px; margin-top: 18px; }
  .benefit-icon { width: 48px; height: 48px; }
  .auth-panel { padding-top: 24px; padding-bottom: 24px; }
  footer { margin-top: 24px; }
}
@media (min-width: 768px) and (max-width: 1199px) {
  .hospital-auth { grid-template-columns: 46% 54%; }
  .visual-content { padding-left: 32px; padding-right: 24px; }
  .portal-message h1 { font-size: 30px; }
  .portal-message > p { font-size: 17px; }
  .portal-benefits li { gap: 14px; }
  .portal-benefits p { font-size: 14px; }
  .auth-panel { padding-left: 24px; padding-right: 24px; }
  footer { font-size: 11px; gap: 10px; }
}
@media (max-width: 767px) {
  .hospital-auth { zoom: 1; grid-template-columns: minmax(0, 1fr); grid-template-rows: auto 1fr; height: auto; min-height: 100dvh; }
  .visual-content { padding: 20px 24px 12px; }
  .visual-panel::before { display: none; }
  .portal-logo { width: 290px; margin: 0 auto; }
  .portal-message, .portal-benefits, .hospital-art { display: none; }
  .auth-panel { padding: 8px 20px 20px; }
  .form-area { align-items: center; }
  footer { margin-top: 20px; font-size: 10px; gap: 8px; }
  footer span + span::before { margin-right: 8px; }
}
</style>
