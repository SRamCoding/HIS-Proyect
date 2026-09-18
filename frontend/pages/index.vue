<template>
  <div v-if="!tenantId" />
  <div v-else class="hospital-landing">
    <a class="skip-link" href="#contenido">Saltar al contenido</a>
    <div v-if="cargando" class="page-state" role="status">
      <UIcon name="i-heroicons-arrow-path" class="loading-icon" /><p>Cargando información del hospital…</p>
    </div>
    <div v-else-if="error" class="page-state" role="alert">
      <UIcon name="i-heroicons-exclamation-triangle" class="state-icon" />
      <h1>No pudimos cargar el hospital</h1><p>{{ error }}</p>
      <button class="landing-button button-primary" @click="cargarHospital">Volver a intentar</button>
      <NuxtLink to="/login" class="text-link">Ir al acceso administrativo</NuxtLink>
    </div>
    <template v-else-if="hospital">
      <header class="site-header">
        <div class="landing-container header-inner">
          <a href="#inicio" class="hospital-brand" :aria-label="`${hospital.name}, inicio`"><span class="brand-cross" aria-hidden="true" /><span>{{ hospital.name }}</span></a>
          <template v-if="hospital.is_active">
            <nav class="desktop-nav" aria-label="Navegación principal">
              <a v-for="item in navegacion" :key="item.id" :href="`#${item.id}`" :class="{ active: seccionActiva === item.id }" :aria-current="seccionActiva === item.id ? 'location' : undefined">{{ item.label }}</a>
            </nav>
            <div class="header-access">
              <NuxtLink :to="accesoSigarh" class="landing-button button-outline"><UIcon name="i-heroicons-shield-check" />Portal SIGARH</NuxtLink>
              <NuxtLink :to="accesoHospital" class="landing-button button-primary"><UIcon name="i-heroicons-user" />Panel hospitalario</NuxtLink>
            </div>
            <button class="menu-toggle" :aria-expanded="menuAbierto" aria-controls="mobile-nav" :aria-label="menuAbierto ? 'Cerrar menú' : 'Abrir menú'" @click="menuAbierto = !menuAbierto"><UIcon :name="menuAbierto ? 'i-heroicons-x-mark' : 'i-heroicons-bars-3'" /></button>
          </template>
        </div>
        <nav v-if="hospital.is_active && menuAbierto" id="mobile-nav" class="mobile-nav" aria-label="Navegación móvil" @keydown.esc="menuAbierto = false">
          <a v-for="item in navegacion" :key="item.id" :href="`#${item.id}`" @click="menuAbierto = false">{{ item.label }}</a>
          <NuxtLink :to="accesoSigarh">Portal SIGARH <UIcon name="i-heroicons-arrow-up-right" /></NuxtLink>
          <NuxtLink :to="accesoHospital">Panel hospitalario <UIcon name="i-heroicons-arrow-up-right" /></NuxtLink>
        </nav>
      </header>
      <main v-if="!hospital.is_active" id="contenido" class="page-state"><UIcon name="i-heroicons-building-office-2" class="state-icon" /><h1>{{ hospital.name }}</h1><p>Este hospital no está activo actualmente.</p></main>
      <main v-else id="contenido">
        <section id="inicio" class="hero" aria-labelledby="hero-title">
          <img src="/landing/hero-consulta.jpg" alt="" class="hero-photo" fetchpriority="high" width="2172" height="724" />
          <div class="hero-shade" />
          <div class="landing-container hero-inner">
            <div class="hero-copy">
              <p class="hero-eyebrow"><UIcon name="i-heroicons-building-office-2" />Establecimiento de salud<span v-if="hospital.hospital_level"> · Nivel {{ hospital.hospital_level }}</span></p>
              <h1 id="hero-title">Cuidamos tu salud,<br /><span>cerca de ti</span></h1>
              <p class="hero-description">Atención integral y humana para ti y tu familia.<br class="desktop-break" /> Comprometidos con el bienestar de nuestra comunidad.</p>
              <div class="hero-actions">
                <a href="#servicios" class="landing-button button-primary"><UIcon name="i-heroicons-heart" />Ver servicios<UIcon name="i-heroicons-arrow-right" /></a>
                <a href="#nosotros" class="landing-button button-glass"><UIcon name="i-heroicons-information-circle" />Conocer el hospital</a>
              </div>
              <a v-if="servicioEmergencia" href="#servicios" class="emergency-note" @click.prevent="abrirServicio(servicioEmergencia)"><UIcon name="i-heroicons-bell-alert" /><strong>Emergencias</strong><span>Contigo cuando más lo necesitas.</span><UIcon name="i-heroicons-arrow-up-right" class="emergency-arrow" /></a>
              <p v-else class="care-note"><UIcon name="i-heroicons-shield-check" />Tu bienestar, nuestro compromiso.</p>
            </div>
            <p class="hero-signature">Salud para hoy,<br />bienestar para<br /><strong>toda la vida.</strong></p>
          </div>
          <svg class="hero-curve" viewBox="0 0 1440 32" preserveAspectRatio="none" aria-hidden="true"><path d="M0 8 Q720 52 1440 8 V32 H0Z" /></svg>
        </section>
        <div v-if="serviciosDestacados.length" class="landing-container featured-wrap">
          <div class="featured-services" aria-label="Servicios destacados">
            <button v-for="servicio in serviciosDestacados" :key="servicio.code || servicio.name" class="featured-service" @click="abrirServicio(servicio)"><UIcon :name="iconoServicio(servicio)" class="service-icon" /><span class="service-copy"><strong>{{ servicio.name }}</strong><span>{{ descripcionServicio(servicio) }}</span></span><UIcon name="i-heroicons-arrow-right" class="card-arrow" /></button>
          </div>
        </div>
        <section id="nosotros" class="about-section landing-container" aria-labelledby="about-title">
          <div class="about-intro"><p class="section-eyebrow">Quiénes somos</p><h2 id="about-title">Nuestra identidad institucional</h2><p>La salud nos une. Trabajamos para brindarte una atención cercana, con calidad y calidez en cada etapa de tu vida.</p></div>
          <div class="about-photo-wrap">
            <img src="/landing/consulta.jpg" alt="Médico escuchando a una paciente durante una consulta" class="about-photo" width="1200" height="675" loading="lazy" />
            <div class="photo-badge"><UIcon name="i-heroicons-chart-bar" /><span><strong>{{ serviciosAMostrar.length || 'Tu salud' }}</strong><small>{{ serviciosAMostrar.length ? 'servicios a tu disposición' : 'nuestra prioridad' }}</small></span></div>
          </div>
          <div class="identity-list">
            <article v-for="(item, index) in identidad" :key="item.titulo" class="identity-item"><span class="identity-number" aria-hidden="true">{{ String(index + 1).padStart(2, '0') }}</span><div><h3>{{ item.titulo }}</h3><p>{{ item.texto }}</p></div></article>
          </div>
          <div class="hospital-facts" aria-label="Nuestro hospital"><div v-for="dato in datosConfianza" :key="dato.label" class="hospital-fact"><UIcon :name="dato.icono" /><strong>{{ dato.valor }}</strong><span>{{ dato.label }}</span></div></div>
        </section>
        <section id="servicios" class="services-section" aria-labelledby="services-title">
          <div class="landing-container services-layout">
            <div class="services-intro">
              <p class="section-eyebrow">Nuestros servicios</p><h2 id="services-title">Servicios para una<br class="desktop-break" /> mejor comunidad</h2><p>Estamos para cuidar de ti y de tu familia, con un equipo humano comprometido.</p>
              <button v-if="serviciosAMostrar.length > 6" class="landing-button button-outline services-toggle" :aria-expanded="mostrarTodos" aria-controls="service-list" @click="mostrarTodos = !mostrarTodos">{{ mostrarTodos ? 'Ver menos servicios' : 'Ver todos los servicios' }}<UIcon :name="mostrarTodos ? 'i-heroicons-arrow-up' : 'i-heroicons-arrow-right'" /></button>
              <span v-else-if="serviciosAMostrar.length" class="service-count">{{ serviciosAMostrar.length }} servicios a tu disposición</span>
            </div>
            <div v-if="serviciosAMostrar.length" id="service-list" class="services-grid"><button v-for="servicio in serviciosVisibles" :key="servicio.code || servicio.name" class="service-card" @click="abrirServicio(servicio)"><UIcon :name="iconoServicio(servicio)" class="service-icon" /><span class="service-copy"><strong>{{ servicio.name }}</strong><span>{{ descripcionServicio(servicio) }}</span></span><UIcon name="i-heroicons-arrow-right" class="card-arrow" /></button></div>
            <div v-else class="services-empty"><UIcon name="i-heroicons-information-circle" /><p>Consulta con el hospital para conocer los servicios disponibles.</p><a href="#contacto" class="text-link">Ver información de contacto →</a></div>
          </div>
        </section>
        <section id="contacto" class="contact-section" aria-label="Información de contacto">
          <div class="landing-container contact-inner">
            <div v-if="hospital.address" class="contact-item"><span class="contact-icon"><UIcon name="i-heroicons-map-pin" /></span><div><strong>{{ hospital.address }}</strong><span>Nuestra ubicación</span></div></div>
            <a v-if="hospital.phone" :href="telefonoHref" class="contact-item"><span class="contact-icon"><UIcon name="i-heroicons-phone" /></span><div><strong>{{ hospital.phone }}</strong><span>Central telefónica</span></div></a>
            <a v-if="hospital.email" :href="`mailto:${hospital.email}`" class="contact-item"><span class="contact-icon"><UIcon name="i-heroicons-envelope" /></span><div><strong>{{ hospital.email }}</strong><span>Escríbenos</span></div></a>
            <div v-if="!hayContacto" class="contact-item"><span class="contact-icon"><UIcon name="i-heroicons-chat-bubble-left-right" /></span><div><strong>Estamos para orientarte</strong><span>Acércate a {{ hospital.name }} para más información.</span></div></div>
            <a v-if="hospital.email || hospital.phone" :href="hospital.email ? `mailto:${hospital.email}` : telefonoHref" class="landing-button button-primary contact-button"><UIcon name="i-heroicons-chat-bubble-left-right" />Contáctanos<UIcon name="i-heroicons-arrow-right" /></a>
          </div>
        </section>
      </main>
      <footer v-if="hospital.is_active" class="site-footer"><div class="landing-container footer-inner"><a href="#inicio" class="hospital-brand"><span class="brand-cross" aria-hidden="true" /><span>{{ hospital.name }}</span></a><p>© {{ anio }} · Todos los derechos reservados.</p><a href="#inicio" class="footer-top">Volver arriba<UIcon name="i-heroicons-arrow-up" /></a></div></footer>
      <dialog ref="servicioDialog" class="service-dialog" aria-labelledby="service-dialog-title" @click="cerrarAlFondo" @close="servicioSeleccionado = null">
        <template v-if="servicioSeleccionado">
          <button class="dialog-close" aria-label="Cerrar detalle del servicio" autofocus @click="servicioDialog?.close()"><UIcon name="i-heroicons-x-mark" /></button>
          <UIcon :name="iconoServicio(servicioSeleccionado)" class="dialog-icon" /><p class="section-eyebrow">Nuestros servicios</p><h2 id="service-dialog-title">{{ servicioSeleccionado.name }}</h2>
          <p class="dialog-description">{{ servicioSeleccionado.description || descripcionServicio(servicioSeleccionado) }}</p>
          <div class="dialog-info"><UIcon name="i-heroicons-information-circle" /><p>Consulta con el hospital los horarios, requisitos y disponibilidad de este servicio.</p></div>
          <a v-if="hospital.phone" :href="telefonoHref" class="landing-button button-primary"><UIcon name="i-heroicons-phone" />Llamar al hospital</a>
          <a v-else-if="hospital.email" :href="`mailto:${hospital.email}`" class="landing-button button-primary"><UIcon name="i-heroicons-envelope" />Consultar por correo</a>
          <p v-else-if="hospital.address" class="dialog-address"><UIcon name="i-heroicons-map-pin" />{{ hospital.address }}</p>
        </template>
      </dialog>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })
interface Servicio { code?: string; name: string; description: string | null }
interface HospitalPublico {
  id: string; name: string; is_active: boolean; hospital_level: string | null
  mission: string | null; vision: string | null; values: string | null
  address: string | null; phone: string | null; email: string | null; servicios: Servicio[]
}
const route = useRoute()
const { api } = useApi()
const authStore = useAuthStore()
const tenantId = computed(() => typeof route.query.tenant === 'string' ? route.query.tenant : '')
const hospital = ref<HospitalPublico | null>(null)
const cargando = ref(true)
const error = ref('')
const menuAbierto = ref(false)
const mostrarTodos = ref(false)
const seccionActiva = ref('inicio')
const servicioSeleccionado = ref<Servicio | null>(null)
const servicioDialog = ref<HTMLDialogElement | null>(null)
const anio = new Date().getFullYear()
const navegacion = [{ id: 'inicio', label: 'Inicio' }, { id: 'nosotros', label: 'Nosotros' }, { id: 'servicios', label: 'Servicios' }, { id: 'contacto', label: 'Contacto' }]
const accesoHospital = computed(() => ({ path: '/app/login', query: { tenant: hospital.value?.id } }))
const accesoSigarh = computed(() => ({ path: '/sigarh/login', query: { tenant: hospital.value?.id } }))
const telefonoHref = computed(() => `tel:${hospital.value?.phone?.replace(/[^+\d]/g, '') || ''}`)
const hayContacto = computed(() => hospital.value?.address || hospital.value?.phone || hospital.value?.email)
useHead(() => ({
  title: hospital.value ? `${hospital.value.name} | Cerca de ti` : 'Hospital | Atención a la comunidad',
  meta: [{ name: 'description', content: `Conoce ${hospital.value?.name || 'nuestro hospital'}, nuestros servicios e información de contacto. Atención cercana para ti y tu familia.` }],
}))
const identidad = computed(() => [
  { titulo: 'Misión', texto: hospital.value?.mission || 'Brindar atención de salud integral, oportuna y humana, con calidad y calidez para nuestra comunidad.' },
  { titulo: 'Visión', texto: hospital.value?.vision || 'Ser una institución de referencia por la calidad de nuestra atención y el compromiso con el bienestar de las personas.' },
  { titulo: 'Valores', texto: hospital.value?.values || 'Respeto, empatía, ética profesional y trabajo en equipo.' },
])
// Solo se publican los servicios configurados; no se inventa una cartera si está vacía.
const serviciosAMostrar = computed(() => hospital.value?.servicios ?? [])
const serviciosDestacados = computed(() => serviciosAMostrar.value.slice(0, 4))
const serviciosVisibles = computed(() => mostrarTodos.value ? serviciosAMostrar.value : serviciosAMostrar.value.slice(0, 6))
const servicioEmergencia = computed(() => serviciosAMostrar.value.find(servicio => servicio.code === 'emergencia'))
const datosConfianza = computed(() => [
  { icono: 'i-heroicons-building-office-2', valor: hospital.value?.hospital_level ? `Nivel ${hospital.value.hospital_level}` : 'Salud', label: hospital.value?.hospital_level ? 'Categoría del hospital' : 'Al servicio de la comunidad' },
  { icono: 'i-heroicons-user-group', valor: String(serviciosAMostrar.value.length), label: 'Servicios de atención' },
  { icono: 'i-heroicons-heart', valor: 'Cercanía', label: 'Atención humana' },
  { icono: 'i-heroicons-hand-raised', valor: 'Compromiso', label: 'Con tu bienestar' },
])
const presentacionServicios: Record<string, { icono: string; descripcion: string }> = {
  admision: { icono: 'i-heroicons-user', descripcion: 'Orientación y atención para nuestros usuarios.' },
  archivo_clinico: { icono: 'i-heroicons-document-text', descripcion: 'Gestión y cuidado de tu historia clínica.' },
  banco_sangre: { icono: 'i-heroicons-heart', descripcion: 'Tu donación puede salvar vidas.' },
  consulta_externa: { icono: 'i-heroicons-calendar-days', descripcion: 'Atención especializada para tu salud.' },
  emergencia: { icono: 'i-heroicons-bell-alert', descripcion: 'Atención cuando más lo necesitas.' },
  farmacia: { icono: 'i-heroicons-beaker', descripcion: 'Orientación y dispensación de medicamentos.' },
  hospitalizacion: { icono: 'i-heroicons-building-office-2', descripcion: 'Cuidado y acompañamiento en tu recuperación.' },
  laboratorio: { icono: 'i-heroicons-beaker', descripcion: 'Análisis para apoyar tu diagnóstico.' },
  imagenes: { icono: 'i-heroicons-photo', descripcion: 'Estudios de apoyo al diagnóstico médico.' },
  telesalud: { icono: 'i-heroicons-video-camera', descripcion: 'Acercamos la atención a nuestra comunidad.' },
  medicina_fisica: { icono: 'i-heroicons-hand-raised', descripcion: 'Acompañamos tu rehabilitación y recuperación.' },
  hemodialisis: { icono: 'i-heroicons-arrow-path', descripcion: 'Atención especializada para tu salud renal.' },
  procedimientos: { icono: 'i-heroicons-clipboard-document-list', descripcion: 'Procedimientos para el cuidado de tu salud.' },
}
const iconoServicio = (servicio: Servicio) => presentacionServicios[servicio.code || '']?.icono || 'i-heroicons-plus-circle'
const descripcionServicio = (servicio: Servicio) => presentacionServicios[servicio.code || '']?.descripcion || servicio.description || 'Conoce más sobre este servicio.'
async function abrirServicio(servicio: Servicio) {
  servicioSeleccionado.value = servicio
  await nextTick()
  servicioDialog.value?.showModal()
}
function cerrarAlFondo(event: MouseEvent) {
  const dialog = servicioDialog.value
  if (!dialog || event.target !== dialog) return
  const rect = dialog.getBoundingClientRect()
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close()
}
let ultimaCarga = 0
async function cargarHospital() {
  const carga = ++ultimaCarga
  cargando.value = true
  error.value = ''
  hospital.value = null
  menuAbierto.value = false
  mostrarTodos.value = false
  if (!tenantId.value) {
    await navigateTo(authStore.isAuthenticated ? authStore.panelRoute : '/login')
    return
  }
  try {
    const resultado = await api<HospitalPublico>(`/auth/tenant-publico/${encodeURIComponent(tenantId.value)}`)
    if (carga === ultimaCarga) hospital.value = resultado
  } catch (e: unknown) {
    if (carga === ultimaCarga) error.value = apiErr(e, 'No se pudo cargar la información de este hospital.')
  } finally {
    if (carga === ultimaCarga) cargando.value = false
  }
}
await cargarHospital()
watch(tenantId, cargarHospital)
function actualizarSeccion() {
  const ultima = [...navegacion].reverse().find(item => {
    const section = document.getElementById(item.id)
    return section && section.getBoundingClientRect().top <= 140
  })
  seccionActiva.value = ultima?.id || 'inicio'
  if (window.scrollY > 0 && window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 8) seccionActiva.value = 'contacto'
}
onMounted(() => {
  actualizarSeccion()
  window.addEventListener('scroll', actualizarSeccion, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', actualizarSeccion))
</script>

<style scoped src="~/assets/css/hospital-landing.css"></style>
