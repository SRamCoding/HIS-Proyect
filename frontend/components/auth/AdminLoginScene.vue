<script setup lang="ts">
const features = [
  { icon: 'i-heroicons-squares-2x2', first: 'Control', second: 'multi-hospital' },
  { icon: 'i-heroicons-document-magnifying-glass', first: 'Auditoría', second: 'completa' },
  { icon: 'i-heroicons-shield-check', first: 'Seguridad', second: 'empresarial' },
]
// Indicadores de la composición de referencia, no datos de producción.
const metrics = [
  { icon: 'i-heroicons-building-office-2', value: '12', label: 'hospitales activos' },
  { icon: 'i-heroicons-users', value: '2,480', label: 'usuarios' },
  { icon: 'i-heroicons-cube', value: '36', label: 'módulos habilitados' },
  { icon: 'i-heroicons-server-stack', value: '99.98%', label: 'disponibilidad' },
]
</script>

<template>
  <section class="command-scene" aria-labelledby="network-title">
    <!-- Imagen y rótulos en un único sistema de coordenadas: no se desplazan al redimensionar. -->
    <svg class="scene-art" viewBox="0 0 1254 1254" preserveAspectRatio="none" aria-hidden="true">
      <image href="/admin-login/network-command-center.png" width="1254" height="1254" />
      <g class="hospital-captions" text-anchor="middle">
        <text x="818" y="178">Hospital Norte</text>
        <text x="1090" y="203">Hospital Centro</text>
        <text x="1131" y="363">Hospital Este</text>
        <text x="790" y="462">Hospital Oeste</text>
        <text x="1068" y="506">Hospital Sur</text>
        <text x="950" y="335" class="erp-caption">ERP CENTRAL</text>
      </g>
      <g fill="#b8d9e6" font-size="17">
        <text x="990" y="593">Gestión centralizada</text>
        <text x="990" y="616">en tiempo real</text>
        <path d="M990 629h44" stroke="#62d4df" stroke-width="2"/>
      </g>
      <!-- Pantalla de navegación: sustituye las barras vacías de la ilustración. -->
      <g transform="translate(97 837) skewY(2.5)">
        <rect width="253" height="242" rx="4" fill="#042c43" />
        <text x="17" y="22" class="screen-heading">ADMINISTRACIÓN CENTRAL</text>
        <g v-for="(label, index) in ['Hospitales', 'Módulos', 'Usuarios', 'Auditoría', 'Roles y permisos', 'Infraestructura']" :key="label" :transform="`translate(15 ${45 + index * 33})`">
          <rect x="-4" y="-13" width="225" height="27" rx="4" :fill="index === 0 ? '#10506a' : '#073248'" />
          <rect x="3" y="-7" width="12" height="12" rx="3" fill="none" stroke="#5cd3df" stroke-width="1.5"/>
          <text x="27" y="3" class="screen-label">{{ label }}</text>
          <path d="M201 -4l4 4-4 4" fill="none" stroke="#7baabb" stroke-width="1.4"/>
        </g>
      </g>
      <text x="392" y="862" class="screen-heading">RED HOSPITALARIA</text>
      <g transform="translate(596 872)">
        <rect width="224" height="218" rx="4" fill="#052e45" stroke="#1b5a72" />
        <text x="14" y="23" class="screen-heading">TRAZABILIDAD DEL ERP</text>
        <text x="14" y="42" class="screen-muted">Ejemplos de eventos auditables</text>
        <g v-for="(label, index) in ['Inicio de sesión', 'Actualización de permisos', 'Habilitación de módulos', 'Cambios de configuración', 'Registro de hospitales']" :key="label" :transform="`translate(15 ${66 + index * 32})`">
          <path d="M0 -8l7 -3 7 3v7c0 5-7 8-7 8S0 4 0-1z" fill="none" stroke="#5dd9df" stroke-width="1.4"/>
          <path d="M4 -1l2 2 4-5" fill="none" stroke="#5dd9df" stroke-width="1.3"/>
          <text x="24" y="2" class="screen-event">{{ label }}</text>
          <path d="M24 13h163" stroke="#174559"/>
        </g>
      </g>
      <text x="866" y="880" class="screen-heading">VISIÓN DE LA PLATAFORMA</text>
      <g transform="translate(858 963)">
        <rect width="235" height="134" rx="3" fill="#052d43" />
        <g v-for="(label, index) in ['Infraestructura', 'Base de datos', 'Integraciones', 'Servicios', 'Respaldos']" :key="label" :transform="`translate(12 ${19 + index * 24})`">
          <circle cx="3" cy="-3" r="3" fill="#58d3d9"/>
          <text x="15" y="1" class="screen-event">{{ label }}</text>
          <text x="210" y="1" text-anchor="end" class="screen-muted">DEMO</text>
        </g>
      </g>
    </svg>
    <svg class="mobile-network" viewBox="660 20 570 610" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
      <image href="/admin-login/network-command-center.png" width="1254" height="1254" />
    </svg>
    <header class="central-brand"><span class="medical-cross" aria-hidden="true">✚</span><span>ERP Hospitalario Central</span></header>
    <div class="scene-copy">
      <h1 id="network-title">Control total de tu<br /><span>red hospitalaria</span></h1>
      <p>Administra hospitales, módulos, usuarios, permisos<br class="desktop-break" /> y auditorías desde una plataforma centralizada.</p>
      <div class="feature-row"><div v-for="f in features" :key="f.first" class="feature"><span class="feature-icon"><UIcon :name="f.icon" aria-hidden="true" /></span><span>{{ f.first }}<br />{{ f.second }}</span></div></div>
    </div>
    <div class="metrics" aria-label="Indicadores ilustrativos, no datos reales"><div v-for="m in metrics" :key="m.label" class="metric"><span class="metric-icon"><UIcon :name="m.icon" aria-hidden="true" /></span><div><strong>{{ m.value }}</strong><span>{{ m.label }}</span></div></div><small>Indicadores ilustrativos de la plataforma</small></div>
  </section>
</template>

<style scoped>
.command-scene{position:sticky;top:0;align-self:start;isolation:isolate;min-width:0;height:100svh;min-height:700px;overflow:hidden;background:#032439;color:#f6fbff;font-family:Inter,Arial,sans-serif}
.mobile-network{display:none}
.scene-art{position:absolute;inset:0;width:100%;height:100%;z-index:-1;pointer-events:none}
.hospital-captions{fill:#eefaff;font-size:16px;font-weight:500;paint-order:stroke;stroke:#032439;stroke-width:4px;stroke-linejoin:round}
.erp-caption{font-size:15px;font-weight:700}
.screen-heading{fill:#bdeaf3;font-size:12px;font-weight:700;letter-spacing:.6px}
.screen-label{fill:#d5edf6;font-size:14px}
.screen-event{fill:#c5e4ef;font-size:12px}
.screen-muted{fill:#81aabb;font-size:10px}
.central-brand{display:flex;align-items:center;gap:16px;padding:28px 6%;border-bottom:1px solid #c4e6ef14;font-size:clamp(18px,1.5vw,27px);font-weight:600;letter-spacing:-.035em}
.medical-cross{width:42px;height:42px;flex-shrink:0;display:grid;place-items:center;border-radius:14px;background:#167588;font-size:28px;font-weight:700;line-height:1}
.scene-copy{position:absolute;left:6%;top:18%;width:58%}
.scene-copy h1{font-size:clamp(28px,min(2.8vw,5.7svh),52px);line-height:1.12;font-weight:750;letter-spacing:-.045em;margin:0 0 20px;text-shadow:0 2px 14px #001b2e}
.scene-copy h1 span{color:#5ad4dd}
.scene-copy p{font-size:clamp(13px,min(1.13vw,2.1svh),19px);line-height:1.6;color:#c6dce9;margin:0;letter-spacing:-.015em;max-width:550px}
.feature-row{display:flex;gap:clamp(16px,2vw,32px);margin-top:26px}
.feature{display:flex;align-items:center;gap:10px;font-size:clamp(11px,.85vw,14px);line-height:1.5;white-space:nowrap}
.feature-icon{display:grid;place-items:center;width:40px;aspect-ratio:1;flex-shrink:0;border:1px solid #70d5dc55;border-radius:12px;color:#6be0e5;background:#073447aa}
.feature-icon :deep(.iconify){width:22px;height:22px}
.metrics{position:absolute;left:6%;right:4.5%;top:53%;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.metric{display:flex;align-items:center;gap:10px;padding:12px;border:1px solid #71b9cc44;border-radius:12px;background:#0a354bd9;backdrop-filter:blur(10px)}
.metric-icon{display:grid;place-items:center;width:27px;height:27px;color:#6cdae1}
.metric-icon :deep(.iconify){width:25px;height:25px}
.metric strong{display:block;font-size:clamp(19px,min(1.65vw,3.2svh),29px);font-weight:650;letter-spacing:-.04em;line-height:1.15}
.metric div>span{display:block;font-size:clamp(9px,.72vw,12px);margin-top:5px;color:#bed4df}
.metrics small{grid-column:1/-1;text-align:right;font-size:9px;line-height:1.2;color:#b5cbd6}
@media(min-width:961px) and (max-height:760px){
 .central-brand{padding-top:20px;padding-bottom:20px}
 .scene-copy{top:18%}
 .scene-copy h1{margin-bottom:16px}
 .feature-row{margin-top:18px}
 .metrics{top:53%}
 .metric{padding:12px;gap:7px}
}
@media(max-width:1150px) and (min-width:961px){
 .central-brand{font-size:19px;gap:12px}
 .desktop-break{display:none}
 .scene-copy h1{font-size:28px}
 .scene-copy p{max-width:340px}
 .feature-row{gap:16px}
 .feature{font-size:10px;gap:6px}
 .feature-icon{width:32px}
 .metrics{gap:7px}
 .metric{padding:12px 8px;gap:5px}
 .metric-icon{width:20px;flex-shrink:0}
 .metric strong{font-size:19px}
}
/* Composición móvil independiente: mapa sin deformar y texto en columnas separadas. */
@media(max-width:960px){
 .command-scene{position:relative;display:grid;grid-template-columns:minmax(0,1fr) minmax(0,210px);grid-template-rows:auto auto;align-items:center;gap:14px 12px;height:auto;min-height:0;padding:24px max(24px,calc((100% - 520px)/2)) 36px;box-sizing:border-box;background:radial-gradient(ellipse at 85% 45%,#0a354e,#05263a 65%)}
 .scene-art,.feature-row,.metrics{display:none}
 .central-brand{grid-column:1/-1;grid-row:1;padding:0;border:0;font-size:19px;gap:10px;letter-spacing:-.025em}
 .medical-cross{width:34px;height:34px;font-size:23px;border-radius:10px}
 .scene-copy{position:static;grid-column:1;grid-row:2;width:auto;min-width:0;margin:0;padding:0}
 .scene-copy h1{font-size:29px;line-height:1.15;margin:0;letter-spacing:-.035em;text-shadow:none}
 .scene-copy h1 br{display:none}
 .scene-copy h1 span{display:block;margin-top:4px;color:#71d5dc}
 .scene-copy p{font-size:12px;line-height:1.6;margin:14px 0 0;color:#b9cdd9}
 .desktop-break{display:none}
 .mobile-network{display:block;grid-column:2;grid-row:2;width:100%;height:auto;aspect-ratio:570/610;min-width:0;pointer-events:none;mask-image:radial-gradient(ellipse 65% 65% at center,#000 55%,transparent 100%)}
}
@media(max-width:600px){
 .command-scene{grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);padding:20px 20px 32px;gap:12px}
 .central-brand{font-size:clamp(14px,4vw,18px)}
 .medical-cross{width:30px;height:30px;font-size:21px}
 .scene-copy h1{font-size:clamp(22px,5.8vw,30px)}
 .scene-copy p{display:none}
 .mobile-network{max-width:180px;justify-self:end}
}
@media(max-width:360px){
 .command-scene{padding-left:16px;padding-right:16px;column-gap:8px}
 .scene-copy h1{font-size:21px}
}
</style>
