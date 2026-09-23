<script setup lang="ts">
const props = defineProps<{ panel: 'app' | 'sigarh' }>()
const { hospital, pending, brandingError, tenantId, refreshBranding } = useHospitalBranding()
const logoFailed = ref(false)
watch(() => hospital.value?.logo_url, () => { logoFailed.value = false })
const isSigarh = computed(() => props.panel === 'sigarh')
const name = computed(() => pending.value ? 'Cargando hospital…' : brandingError.value ? 'Acceso institucional' : hospital.value?.name || 'Portal hospitalario')
const initials = computed(() => (hospital.value?.name || 'Hospital').split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0]).join('').toUpperCase())
const otherPanel = computed(() => ({ path: isSigarh.value ? '/app/login' : '/sigarh/login', query: tenantId.value ? { tenant: tenantId.value } : {} }))
const home = computed(() => ({ path: '/', query: tenantId.value ? { tenant: tenantId.value } : {} }))
const features = computed(() => isSigarh.value ? [
  { icon: 'i-heroicons-user-group', title: 'Personas', text: 'Información de tu equipo en un solo lugar.' },
  { icon: 'i-heroicons-calendar-days', title: 'Organización', text: 'Programación, turnos y gestión diaria.' },
] : [
  { icon: 'i-heroicons-heart', title: 'Atención', text: 'Cada etapa del cuidado, conectada.' },
  { icon: 'i-heroicons-document-text', title: 'Continuidad', text: 'La información clínica que acompaña al paciente.' },
])
useHead({ title: computed(() => `${isSigarh.value ? 'SIGARH' : 'App'} · ${hospital.value?.name || 'Acceso hospitalario'}`),
  link: [{ rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap' }] })
</script>
<template>
  <main class="hospital-access" :class="{ 'hospital-access--sigarh': isSigarh }">
    <section class="identity-panel" aria-label="Identidad del hospital">
      <NuxtLink :to="home" class="back-link"><UIcon name="i-heroicons-arrow-up-left" aria-hidden="true" /> Volver al hospital</NuxtLink>
      <div class="identity-content">
        <div class="hospital-mark" :aria-busy="pending">
          <img v-if="!pending && hospital?.logo_url && !logoFailed" :src="hospital.logo_url" :alt="`Logo de ${hospital.name}`" @error="logoFailed = true" />
          <span v-else class="hospital-initials" aria-hidden="true">{{ pending ? '…' : initials }}</span>
        </div>
        <p class="eyebrow">{{ isSigarh ? 'Gestión institucional' : 'Atención hospitalaria' }}</p>
        <h1>{{ name }}</h1>
        <p class="identity-description">{{ isSigarh ? 'Un equipo conectado para cuidar mejor.' : 'La información que necesitas. El cuidado que importa.' }}</p>
        <div class="feature-list">
          <div v-for="feature in features" :key="feature.title" class="feature">
            <span class="feature-icon"><UIcon :name="feature.icon" aria-hidden="true" /></span>
            <div><h2>{{ feature.title }}</h2><p>{{ feature.text }}</p></div>
          </div>
        </div>
      </div>
      <div class="identity-footer"><span class="identity-dot" /> Plataforma de gestión hospitalaria <span v-if="hospital?.hospital_level">· {{ hospital.hospital_level }}</span></div>
    </section>
    <section class="access-panel" :aria-label="isSigarh ? 'Acceso a SIGARH' : 'Acceso a App'">
      <div class="access-top"><span class="panel-tag"><UIcon :name="isSigarh ? 'i-heroicons-squares-2x2' : 'i-heroicons-heart'" aria-hidden="true" />{{ isSigarh ? 'SIGARH' : 'APP HOSPITALARIA' }}</span><span>Acceso institucional</span></div>
      <div class="access-form">
        <div v-if="brandingError" class="branding-notice" role="alert">No se pudo cargar el hospital. <button type="button" @click="refreshBranding()">Reintentar</button></div>
        <div v-else-if="hospital && !hospital.is_active" class="branding-notice" role="alert">El acceso a este hospital está desactivado.</div>
        <slot />
        <NuxtLink v-if="tenantId && !brandingError" class="other-access" :to="otherPanel">{{ isSigarh ? 'Ir a App hospitalaria' : 'Ir a SIGARH' }}<UIcon name="i-heroicons-arrow-right" aria-hidden="true" /></NuxtLink>
      </div>
      <footer><UIcon name="i-heroicons-lock-closed" aria-hidden="true" /><span>Uso exclusivo del personal autorizado · {{ new Date().getFullYear() }}</span></footer>
    </section>
  </main>
</template>
<style scoped>
.hospital-access { --ink:#243a35; --ink-soft:#6f7e78; --teal:#287953; --teal-dark:#1e6041; --teal-soft:#eaf5ee; --paper:#fff; --line:#dfe9e2; --radius:12px; --radius-lg:20px; display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); min-height:100dvh; background:#fff; color:var(--ink); font-family:'Poppins','Inter',sans-serif; }
.hospital-access:not(.hospital-access--sigarh) { --ink:#263c46; --ink-soft:#687d83; --teal:#287d83; --teal-dark:#20676c; --teal-soft:#e9f4f4; --line:#dfe9eb; }
.identity-panel { display:flex; flex-direction:column; justify-content:space-between; padding:40px clamp(28px,5.5vw,90px); background:linear-gradient(145deg,var(--teal-soft),#f7faf8 75%); border-right:1px solid var(--line); }
.back-link { display:inline-flex; align-items:center; gap:9px; align-self:flex-start; font-size:12px; color:var(--ink-soft); text-decoration:none; }
.back-link span { width:16px; height:16px; }
.identity-content { padding:55px 0; max-width:500px; }
.hospital-mark { width:130px; height:106px; display:grid; place-items:center; background:white; border:1px solid var(--line); border-radius:22px; padding:16px; box-shadow:0 8px 26px #264a3510; }
.hospital-mark img { width:100%; height:100%; object-fit:contain; }
.hospital-initials { color:var(--teal); font-weight:500; font-size:34px; letter-spacing:-.05em; }
.eyebrow { margin:30px 0 14px; color:var(--teal); font-size:11px; font-weight:500; letter-spacing:.12em; text-transform:uppercase; }
h1 { font-size:clamp(30px,3.3vw,48px); line-height:1.2; letter-spacing:-.035em; font-weight:500; overflow-wrap:anywhere; margin:0; }
.identity-description { max-width:350px; color:var(--ink-soft); font-size:15px; line-height:1.9; margin:20px 0 32px; }
.feature-list { display:grid; gap:20px; border-top:1px solid var(--line); padding-top:28px; }
.feature { display:flex; gap:15px; align-items:center; }
.feature-icon { flex:none; display:grid; place-items:center; width:43px; height:43px; color:var(--teal); border:1px solid var(--line); border-radius:13px; background:#ffffffa6; }
.feature-icon span { width:20px; height:20px; }
.feature h2 { margin:0 0 4px; font-size:13px; font-weight:500; letter-spacing:0; }
.feature p { margin:0; color:var(--ink-soft); font-size:11px; line-height:1.7; }
.identity-footer { display:flex; align-items:center; flex-wrap:wrap; gap:8px; color:var(--ink-soft); font-size:10px; }
.identity-dot { width:6px; height:6px; border-radius:50%; background:var(--teal); }
.access-panel { display:flex; flex-direction:column; padding:40px clamp(24px,5vw,80px) 28px; min-width:0; }
.access-top { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; color:var(--ink-soft); font-size:10px; }
.panel-tag { display:flex; align-items:center; gap:7px; padding:8px 11px; border:1px solid var(--line); border-radius:8px; color:var(--teal); font-size:10px; letter-spacing:.04em; font-weight:500; }
.panel-tag span { width:16px; height:16px; }
.access-form { margin:auto; padding:45px 0; width:100%; max-width:420px; }
.other-access { display:flex; align-items:center; justify-content:center; gap:9px; color:var(--teal); font-size:12px; margin-top:26px; text-decoration:none; }
.other-access span { width:15px; height:15px; }
.branding-notice { padding:12px; margin-bottom:18px; border-radius:10px; background:#fff5e7; color:#825715; font-size:12px; line-height:1.6; }
.branding-notice button { text-decoration:underline; margin-left:6px; cursor:pointer; }
footer { display:flex; align-items:center; justify-content:center; gap:8px; font-size:10px; color:var(--ink-soft); text-align:center; }
footer > span:first-child { width:13px; height:13px; flex:none; }
.hospital-access :deep(.login-card) { border:0; border-radius:0; padding:0; box-shadow:none; max-width:100%; background:transparent; font-family:inherit; animation:none; }
.hospital-access :deep(.login-card h2) { color:var(--ink); font-size:29px; font-weight:500; line-height:1.3; letter-spacing:-.03em; }
.hospital-access :deep(.login-card .intro) { font-size:13px; line-height:1.8; margin:12px 0 30px; color:var(--ink-soft); }
.hospital-access :deep(.login-card label) { font-size:12px; font-weight:500; }
.hospital-access :deep(.login-card input) { height:50px; background:#fafcfb; border-color:var(--line); border-radius:10px; padding-left:44px; font-family:inherit; font-size:13px; }
.hospital-access :deep(.login-card .input-icon) { left:15px; width:18px; height:18px; color:var(--ink-soft); }
.hospital-access :deep(.login-card .toggle-btn) { color:var(--ink-soft); }
.hospital-access :deep(.login-card .toggle-btn span) { width:19px; height:19px; }
.hospital-access :deep(.login-card .label-row a) { font-size:10px; color:var(--teal); }
.hospital-access :deep(.login-card .submit) { height:49px; border-radius:10px; background:var(--teal); font-size:13px; font-weight:500; }
.hospital-access :deep(.login-card .submit:hover:not(:disabled)) { background:var(--teal-dark); }
.hospital-access :deep(.login-card .help) { font-size:11px; margin-top:22px; }
.hospital-access :deep(.login-card .help a) { color:var(--teal); }
.hospital-access :deep(.security-row) { display:none; }
.hospital-access :deep(a:focus-visible),.hospital-access :deep(button:focus-visible) { outline:2px solid var(--teal); outline-offset:4px; }
@media(max-width:800px) { .hospital-access { grid-template-columns:1fr; } .identity-panel { padding:22px 24px; border-right:0; border-bottom:1px solid var(--line); } .identity-content { display:grid; grid-template-columns:64px 1fr; gap:0 16px; max-width:none; padding:24px 0 4px; align-items:center; } .hospital-mark { width:64px; height:64px; border-radius:15px; padding:8px; grid-row:1/3; } .hospital-initials { font-size:23px; } .eyebrow { margin:0 0 5px; font-size:9px; } h1 { font-size:25px; line-height:1.3; } .identity-description,.feature-list,.identity-footer { display:none; } .access-panel { padding:24px; } .access-form { padding:35px 0; } .access-top { max-width:420px; width:100%; margin:auto; } footer { margin-bottom:8px; } }
@media(prefers-reduced-motion:reduce) { .hospital-access :deep(*) { animation:none!important; transition:none!important; } }
</style>
