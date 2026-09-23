<!-- pages/admin/index.vue -->
<template>
  <div class="admin-dashboard">
    <section class="admin-launcher" aria-labelledby="launcher-title">
      <h1 id="launcher-title">&iquest;Qu&eacute; deseas <span>realizar hoy?</span></h1>
      <p>Administra tu red hospitalaria desde un solo lugar.</p>
      <div class="admin-launcher-grid">
        <NuxtLink v-for="acceso in accesosRapidos" :key="acceso.to" :to="acceso.to" class="admin-launcher-card">
          <UIcon :name="acceso.icono" class="launcher-icon" />
          <span>{{ acceso.label }}</span>
        </NuxtLink>
      </div>
    </section>
    <section class="admin-overview">
      <div class="overview-heading"><h2>Tu red hospitalaria, <span>en cifras</span></h2><p>Resumen de la plataforma</p></div>
    <div v-if="!loading && stats && !sistemaSaludable" class="dash-fade-in grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
      <NuxtLink
        v-if="(stats?.hospitales_con_error ?? 0) > 0 || (stats?.hospitales_pendientes ?? 0) > 0"
        to="/admin/hospitales"
        class="salud-card salud-card--alert"
      >
        <UIcon name="i-heroicons-server-stack" class="w-5 h-5 shrink-0" />
        <div class="min-w-0">
          <p class="text-sm font-semibold truncate">
            {{ stats?.hospitales_con_error ?? 0 }} hospital(es) con error de aprovisionamiento
          </p>
          <p class="text-xs opacity-80 truncate">{{ stats?.hospitales_pendientes ?? 0 }} pendientes de aprovisionar · revisar y reintentar</p>
        </div>
        <UIcon name="i-heroicons-arrow-right" class="w-4 h-4 ml-auto shrink-0" />
      </NuxtLink>
      <NuxtLink
        v-if="(stats?.auditoria_fallback_pendientes ?? 0) > 0"
        to="/admin/auditoria"
        class="salud-card salud-card--warn"
      >
        <UIcon name="i-heroicons-shield-exclamation" class="w-5 h-5 shrink-0" />
        <div class="min-w-0">
          <p class="text-sm font-semibold truncate">{{ stats?.auditoria_fallback_pendientes ?? 0 }} eventos de auditoría sin escribir</p>
          <p class="text-xs opacity-80 truncate">quedaron en fallback, reintentar antes de que se acumulen</p>
        </div>
        <UIcon name="i-heroicons-arrow-right" class="w-4 h-4 ml-auto shrink-0" />
      </NuxtLink>
    </div>
    <div v-else-if="!loading && stats" class="dash-fade-in flex items-center gap-2 mb-6 text-xs font-medium px-3 py-2 rounded-lg w-fit" style="background: var(--ok-soft); color: var(--ok)">
      <UIcon name="i-heroicons-check-circle" class="w-4 h-4" />
      Todo en orden: sin hospitales con error, sin auditoría pendiente de escribir.
    </div>

    <!-- KPI Cards mejorados -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div v-for="i in 4" :key="i" class="stat-card animate-pulse">
        <div class="h-3 w-20 rounded mb-3" style="background: var(--line)" />
        <div class="h-6 w-14 rounded" style="background: var(--line)" />
      </div>
    </div>

    <div v-else-if="error" class="text-sm rounded-lg px-4 py-3 mb-6" style="background: var(--alert-soft); color: var(--alert)">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 inline mr-2" />
      No se pudo cargar el dashboard: {{ error }}
    </div>

    <div v-else class="admin-metrics">
      <NuxtLink to="/admin/hospitales" class="admin-metric"><UIcon name="i-heroicons-building-office-2" /><span>Hospitales activos</span><strong>{{ stats?.active_hospitals ?? 0 }}</strong><small>De {{ stats?.total_hospitals ?? 0 }} registrados</small></NuxtLink>
      <NuxtLink to="/admin/usuarios" class="admin-metric"><UIcon name="i-heroicons-users" /><span>Cuentas totales</span><strong>{{ stats?.total_users ?? 0 }}</strong><small>{{ stats?.active_users ?? 0 }} activas</small><small v-if="stats?.usuarios_es_parcial" class="partial-data">Datos parciales: {{ stats.usuarios_hospitales_consultados }}/{{ stats.usuarios_hospitales_totales }} hospitales consultados</small></NuxtLink>
      <NuxtLink to="/admin/modulos" class="admin-metric"><UIcon name="i-heroicons-squares-plus" /><span>M&oacute;dulos habilitados</span><strong>{{ stats?.active_module_assignments ?? 0 }}</strong><small>{{ tiposDeModulo }} tipos de m&oacute;dulo</small></NuxtLink>
      <NuxtLink to="/admin/auditoria" class="admin-metric"><UIcon name="i-heroicons-shield-check" /><span>Eventos de auditor&iacute;a</span><strong>{{ stats?.audit_events_24h ?? 0 }}</strong><small>&Uacute;ltimas 24 horas</small></NuxtLink>
    </div>
    </section>

    <!-- Fila: Notificaciones (timeline) + Usuarios recientes (avatares) + Accesos rápidos -->
    <div class="admin-activity-grid grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
      <div class="dash-card" style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <div class="flex items-center justify-between mb-3">
          <p class="text-sm font-semibold flex items-center gap-1.5" style="color: var(--ink)">
            <UIcon name="i-heroicons-bell-alert" class="w-4 h-4" style="color: var(--navy)" />
            Notificaciones
          </p>
          <span v-if="notifNoLeidas" class="text-xs font-semibold px-2 py-0.5 rounded-full" style="background: var(--alert-soft); color: var(--alert)">
            {{ notifNoLeidas }} sin leer
          </span>
        </div>

        <div v-if="loadingNotifs" class="flex items-center gap-2 py-6 text-sm justify-center" style="color: var(--ink-soft)">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
          Cargando…
        </div>
        <div v-else-if="!notificacionesRecientes.length" class="py-6 text-sm text-center" style="color: var(--ink-soft)">
          Sin notificaciones.
        </div>
        <ul v-else class="notif-timeline">
          <li
            v-for="n in notificacionesRecientes"
            :key="n.id"
            class="notif-timeline-item"
            :class="{ 'notif-timeline-item--unread': !n.is_read }"
            @click="abrirNotificacion(n)"
          >
            <span class="notif-timeline-dot" :class="`notif-timeline-dot--${n.nivel}`" />
            <div class="min-w-0 flex-1 pb-3">
              <p class="text-xs font-medium truncate" style="color: var(--ink)">{{ n.titulo }}</p>
              <p class="text-[11px] truncate" style="color: var(--ink-soft)">{{ n.cuerpo }}</p>
            </div>
          </li>
        </ul>
      </div>

      <div class="dash-card" style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <p class="text-sm font-semibold mb-3 flex items-center gap-1.5" style="color: var(--ink)">
          <UIcon name="i-heroicons-user-plus" class="w-4 h-4" style="color: var(--teal)" />
          Usuarios recientes
        </p>
        <div v-if="loading" class="flex items-center gap-2 py-6 text-sm justify-center" style="color: var(--ink-soft)">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
          Cargando…
        </div>
        <div v-else-if="!usuariosRecientes.length" class="py-6 text-sm text-center" style="color: var(--ink-soft)">
          Sin registros todavía.
        </div>
        <ul v-else class="space-y-2.5">
          <li v-for="(u, i) in usuariosRecientes" :key="i" class="flex items-center gap-2.5">
            <div class="avatar-chip" :style="{ background: avatarGradiente(u.panel) }">
              {{ iniciales(u.name) }}
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-xs font-medium truncate" style="color: var(--ink)">{{ u.name }}</p>
              <p class="text-[11px] truncate" style="color: var(--ink-soft)">{{ u.tenant_name }} · {{ etiquetaPanel(u.panel) }}</p>
            </div>
            <span class="text-[10px] shrink-0" style="color: var(--ink-soft)">{{ tiempoRelativo(u.created_at) }}</span>
          </li>
        </ul>
      </div>

    </div>

    <!-- Fila: gráficos principales -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
      <!-- Curva: hospitales creados por mes -->
      <div class="lg:col-span-2" style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <div class="flex items-center justify-between mb-4">
          <div>
            <p class="text-sm font-semibold" style="color: var(--ink)">Hospitales registrados por mes</p>
            <p class="text-xs" style="color: var(--ink-soft)">últimos 6 meses · total: {{ registrosPorMes.reduce((a, b) => a + b.valor, 0) }}</p>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-medium px-2.5 py-1 rounded" style="background: var(--mist); color: var(--teal)">
              <UIcon name="i-heroicons-arrow-trending-up" class="w-3 h-3 inline mr-0.5" />
              Datos reales
            </span>
          </div>
        </div>
        <ClientOnly>
          <ApexChart
            type="area"
            height="230"
            :options="areaChartOptions"
            :series="areaChartSeries"
          />
        </ClientOnly>
      </div>

      <!-- Anillo: distribución de usuarios por panel -->
      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <p class="text-sm font-semibold mb-3" style="color: var(--ink)" title="Incluye cuentas centrales y de hospitales con base física propia">Usuarios por panel</p>
        <ClientOnly>
          <ApexChart
            type="radialBar"
            height="230"
            :options="radialChartOptions"
            :series="[usoModulos.app, usoModulos.sigarh]"
          />
        </ClientOnly>
        <div class="grid grid-cols-2 gap-2 mt-1">
          <div class="flex items-center justify-between text-xs px-3 py-2 rounded-lg" style="background: var(--mist)">
            <span class="flex items-center gap-1.5" style="color: var(--ink-soft)">
              <span class="w-2 h-2 rounded-full" style="background: var(--teal)" />
              APP
            </span>
            <span class="font-mono-data font-semibold" style="color: var(--ink)">{{ usoModulos.app }}%</span>
          </div>
          <div class="flex items-center justify-between text-xs px-3 py-2 rounded-lg" style="background: var(--mist)">
            <span class="flex items-center gap-1.5" style="color: var(--ink-soft)">
              <span class="w-2 h-2 rounded-full" style="background: var(--navy)" />
              SIGARH
            </span>
            <span class="font-mono-data font-semibold" style="color: var(--ink)">{{ usoModulos.sigarh }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Fila: Gráficos adicionales -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
      <!-- Donut: Distribución de usuarios por panel -->
      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <div class="flex items-center justify-between mb-3">
          <p class="text-sm font-semibold" style="color: var(--ink)" title="Cuentas panel APP y SIGARH, sin contar cuentas panel admin">Usuarios por panel (APP / SIGARH)</p>
          <span class="text-xs" style="color: var(--ink-soft)">Total: {{ usuariosPorPanel.app + usuariosPorPanel.sigarh }}</span>
        </div>
        <ClientOnly>
          <ApexChart
            type="donut"
            height="200"
            :options="donutChartOptions"
            :series="usuariosPorPanelSeries"
          />
        </ClientOnly>
        <div class="flex flex-wrap justify-center gap-4 mt-1">
          <div class="flex items-center gap-1.5 text-xs">
            <span class="w-2 h-2 rounded-full" style="background: #0891b2"></span>
            <span style="color: var(--ink-soft)">APP {{ usuariosPorPanel.app }}</span>
          </div>
          <div class="flex items-center gap-1.5 text-xs">
            <span class="w-2 h-2 rounded-full" style="background: #6366f1"></span>
            <span style="color: var(--ink-soft)">SIGARH {{ usuariosPorPanel.sigarh }}</span>
          </div>
        </div>
      </div>

      <!-- Columnas: Eventos de auditoría por acción -->
      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <p class="text-sm font-semibold mb-3" style="color: var(--ink)">Eventos de auditoría</p>
        <ClientOnly>
          <ApexChart
            type="bar"
            height="200"
            :options="barChartOptions"
            :series="barChartSeries"
          />
        </ClientOnly>
        <div class="flex flex-wrap gap-x-3 gap-y-1 text-xs mt-1 px-1" style="color: var(--ink-soft)">
          <span v-for="(total, accion) in accionesAuditoria" :key="accion" class="flex items-center gap-1">
            {{ accion }}: {{ total }}
          </span>
        </div>
      </div>

      <!-- Actividad por hora -->
      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <div class="flex items-center justify-between mb-3">
          <p class="text-sm font-semibold" style="color: var(--ink)">Actividad por hora</p>
          <span class="text-xs" style="color: var(--ink-soft)">hoy</span>
        </div>
        <div class="grid grid-cols-6 gap-1.5">
          <div v-for="hora in actividadHoras" :key="hora.label" class="text-center">
            <div class="h-10 rounded-md transition-all duration-300 hover:scale-110 cursor-pointer" 
                 :style="{ background: `rgba(8, 145, 178, ${hora.opacidad})`, height: `${20 + hora.altura}px` }"
                 :title="`${hora.value} eventos`">
            </div>
            <span class="text-[10px]" style="color: var(--ink-soft)">{{ hora.label }}</span>
          </div>
        </div>
        <div class="flex items-center justify-between text-xs mt-2" style="color: var(--ink-soft)">
          <span class="flex items-center gap-1">
            <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
            Pico: {{ horaPico.label }}
          </span>
          <span class="flex items-center gap-1">
            <UIcon name="i-heroicons-users" class="w-3.5 h-3.5" />
            {{ horaPico.value }} eventos
          </span>
        </div>
      </div>
    </div>

    <!-- Fila: Distribución por nivel + Top hospitales -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
      <!-- Distribución por nivel MINSA -->
      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <div class="flex items-center justify-between mb-4">
          <p class="text-sm font-semibold" style="color: var(--ink)">Hospitales por nivel</p>
          <span class="text-xs px-2.5 py-1 rounded-full" style="background: var(--mist); color: var(--ink-soft)">MINSA</span>
        </div>
        <div class="space-y-3.5">
          <div v-for="nivel in distribucionNiveles" :key="nivel.code">
            <div class="flex items-center justify-between text-xs">
              <span class="font-medium flex items-center gap-2" style="color: var(--ink)">
                <span class="w-2 h-2 rounded-full" :style="{ background: nivel.color }"></span>
                {{ nivel.code }}
              </span>
              <span class="font-mono-data" style="color: var(--ink-soft)">{{ nivel.cantidad }}</span>
            </div>
            <div class="h-2 rounded-full overflow-hidden mt-1" style="background: var(--mist)">
              <div
                class="h-full rounded-full transition-all duration-500"
                :style="{ width: `${(nivel.cantidad / maxNivel) * 100}%`, background: nivel.color }"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Top hospitales mejorado -->
      <div class="lg:col-span-2" style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
        <div class="flex items-center justify-between mb-4">
          <p class="text-sm font-semibold" style="color: var(--ink)">Hospitales con más módulos</p>
          <span class="text-xs" style="color: var(--ink-soft)">Top 4</span>
        </div>
        <div class="space-y-3">
          <div
            v-for="(h, i) in topHospitalesModulos"
            :key="h.id"
            class="flex items-center gap-3 p-2 rounded-lg transition-all hover:translate-x-1" 
            :style="i % 2 === 0 ? { background: 'var(--mist)' } : {}"
          >
            <span class="text-xs font-bold w-5 h-5 flex items-center justify-center rounded-full shrink-0" 
                  :style="{ background: i === 0 ? 'var(--teal)' : 'var(--mist)', color: i === 0 ? 'white' : 'var(--ink-soft)' }">
              {{ i + 1 }}
            </span>
            <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style="background: var(--mist)">
              <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" style="color: var(--navy)" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate" style="color: var(--ink)">{{ h.name }}</p>
              <div class="h-1.5 rounded-full overflow-hidden" style="background: var(--mist)">
                <div class="h-full rounded-full transition-all duration-500" :style="{ width: `${(h.modules / maxModulosTop) * 100}%`, background: 'var(--teal)' }" />
              </div>
            </div>
            <span class="text-sm font-mono-data font-semibold shrink-0 flex items-center gap-1" style="color: var(--teal)">
              <UIcon name="i-heroicons-cube" class="w-3.5 h-3.5" />
              {{ h.modules }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Fila: Métricas adicionales -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div class="flex items-center gap-4 p-4 rounded-lg" style="background: var(--paper); box-shadow: var(--shadow-card)">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center" style="background: rgba(8, 145, 178, 0.12)">
          <UIcon name="i-heroicons-calendar-days" class="w-6 h-6" style="color: var(--teal)" />
        </div>
        <div>
          <p class="text-xs" style="color: var(--ink-soft)">Hospitales registrados</p>
          <p class="text-xl font-bold" style="color: var(--ink)">{{ stats?.total_hospitals ?? 0 }}</p>
          <p class="text-xs flex items-center gap-0.5" style="color: var(--ok)">
            <UIcon name="i-heroicons-arrow-trending-up" class="w-3 h-3" />
            Total histórico
          </p>
        </div>
      </div>
      <div class="flex items-center gap-4 p-4 rounded-lg" style="background: var(--paper); box-shadow: var(--shadow-card)">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center" style="background: rgba(99, 102, 241, 0.12)">
          <UIcon name="i-heroicons-prescription" class="w-6 h-6" style="color: #6366f1" />
        </div>
        <div>
          <p class="text-xs" style="color: var(--ink-soft)">Hospitales activos</p>
          <p class="text-xl font-bold" style="color: var(--ink)">{{ stats?.active_hospitals ?? 0 }}</p>
          <p class="text-xs flex items-center gap-0.5" style="color: var(--ok)">
            <UIcon name="i-heroicons-arrow-trending-up" class="w-3 h-3" />
            Disponibles
          </p>
        </div>
      </div>
      <div class="flex items-center gap-4 p-4 rounded-lg" style="background: var(--paper); box-shadow: var(--shadow-card)">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center" style="background: rgba(245, 158, 11, 0.12)">
          <UIcon name="i-heroicons-clock" class="w-6 h-6" style="color: var(--warn)" />
        </div>
        <div>
          <p class="text-xs" style="color: var(--ink-soft)">Usuarios activos</p>
          <p class="text-xl font-bold" style="color: var(--ink)">{{ stats?.active_users ?? 0 }}</p>
          <p class="text-xs flex items-center gap-0.5" style="color: var(--alert)">
            <UIcon name="i-heroicons-arrow-trending-up" class="w-3 h-3" />
            Con acceso vigente
          </p>
        </div>
      </div>
      <div class="flex items-center gap-4 p-4 rounded-lg" style="background: var(--paper); box-shadow: var(--shadow-card)">
        <div class="w-12 h-12 rounded-xl flex items-center justify-center" style="background: rgba(239, 68, 68, 0.12)">
          <UIcon name="i-heroicons-heart" class="w-6 h-6" style="color: var(--alert)" />
        </div>
        <div>
          <p class="text-xs" style="color: var(--ink-soft)">Eventos hoy</p>
          <p class="text-xl font-bold" style="color: var(--ink)">{{ stats?.audit_events_24h ?? 0 }}</p>
          <p class="text-xs flex items-center gap-0.5" style="color: var(--ok)">
            <UIcon name="i-heroicons-arrow-trending-down" class="w-3 h-3" />
            Últimas 24 horas
          </p>
        </div>
      </div>
    </div>

    <!-- Hospitales recientes -->
    <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
      <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid var(--line)">
        <div class="flex items-center gap-2">
          <h2 class="text-sm font-semibold" style="color: var(--ink)">Hospitales recientes</h2>
          <span class="text-xs px-2 py-0.5 rounded-full" style="background: var(--mist); color: var(--ink-soft)">Últimos 5</span>
        </div>
        <NuxtLink to="/admin/hospitales" class="text-sm font-medium flex items-center gap-1 transition-all hover:gap-2" style="color: var(--teal)">
          Ver todos
          <UIcon name="i-heroicons-arrow-right" class="w-3.5 h-3.5" />
        </NuxtLink>
      </div>

      <div v-if="loadingHospitales" class="flex items-center gap-2 p-5 text-sm" style="color: var(--ink-soft)">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
        Cargando…
      </div>

      <div v-else-if="errorHospitales" class="flex items-center gap-2 p-5 text-sm" style="color: var(--alert)">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
        {{ errorHospitales }}
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm" style="min-width: 480px">
          <thead>
            <tr style="border-bottom: 1px solid var(--line)">
              <th class="text-left font-semibold px-5 py-2.5 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">
                <UIcon name="i-heroicons-building-office-2" class="w-3.5 h-3.5 inline mr-1.5" />
                Nombre
              </th>
              <th class="text-left font-semibold px-5 py-2.5 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Nivel MINSA</th>
              <th class="text-left font-semibold px-5 py-2.5 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Estado</th>
              <th class="text-left font-semibold px-5 py-2.5 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">
                <UIcon name="i-heroicons-cube" class="w-3.5 h-3.5 inline mr-1.5" />
                Módulos
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="h in hospitalesRecientes"
              :key="h.id"
              style="border-bottom: 1px solid var(--line)"
              class="hover:bg-mist/20 transition-colors"
            >
              <td class="px-5 py-3">
                <div class="flex items-center gap-2.5">
                  <div class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0" style="background: var(--mist)">
                    <UIcon name="i-heroicons-building-office-2" class="w-3.5 h-3.5" style="color: var(--navy)" />
                  </div>
                  <span style="color: var(--ink)">{{ h.name }}</span>
                </div>
              </td>
              <td class="px-5 py-3 font-mono-data" style="color: var(--ink-soft)">{{ h.hospital_level ?? '—' }}</td>
              <td class="px-5 py-3">
                <span class="badge" :class="h.is_active ? 'badge--ok' : 'badge--neutral'">
                  {{ h.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-5 py-3">
                <span class="text-xs font-mono-data" style="color: var(--ink-soft)">
                  {{ h.active_modules.length }}
                </span>
              </td>
            </tr>
            <tr v-if="!hospitalesRecientes.length">
              <td colspan="4" class="py-10">
                <div class="flex flex-col items-center gap-3">
                  <div
                    class="w-56 h-28 bg-no-repeat bg-center bg-contain opacity-90"
                    style="background-image: url('/hospital-empty.svg')"
                  />
                  <p class="text-sm" style="color: var(--ink-soft)">Sin hospitales registrados todavía.</p>
                  <NuxtLink to="/admin/hospitales/create" class="btn-primary text-sm mt-1">
                    <UIcon name="i-heroicons-plus" class="w-4 h-4 inline mr-1" />
                    Crear el primero
                  </NuxtLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface DashboardStats {
  total_hospitals: number
  active_hospitals: number
  total_users: number
  active_users: number
  active_module_assignments: number
  audit_events_24h: number
  modules_distribution: Record<string, number>
  hospitals_by_month: { label: string; value: number }[]
  users_by_panel: Record<string, number>
  hospitals_by_level: { code: string; count: number }[]
  top_hospitals_by_modules: { id: string; name: string; modules: number }[]
  audit_events_by_hour: { label: string; value: number }[]
  audit_actions: Record<string, number>
  usuarios_hospitales_consultados: number
  usuarios_hospitales_totales: number
  usuarios_es_parcial: boolean
  actualizado_en: string
  hospitales_con_error: number
  hospitales_pendientes: number
  auditoria_fallback_pendientes: number
  usuarios_recientes: { name: string; email: string; panel: string; tenant_name: string; created_at: string }[]
}

interface Hospital {
  id: string
  name: string
  hospital_level?: string
  is_active: boolean
  active_modules: string[]
}

interface Notificacion {
  id: string
  titulo: string
  cuerpo: string | null
  nivel: string
  link: string | null
  is_read: boolean
  created_at: string
}

const { api } = useApi()
const authStore = useAuthStore()
const router = useRouter()

const stats = ref<DashboardStats | null>(null)
const hospitalesRecientes = ref<Hospital[]>([])
const errorHospitales = ref('')
const loading = ref(true)
const loadingHospitales = ref(true)
const error = ref('')
const notificacionesRecientes = ref<Notificacion[]>([])
const notifNoLeidas = ref(0)
const loadingNotifs = ref(true)

const sistemaSaludable = computed(() => {
  if (!stats.value) return true
  return stats.value.hospitales_con_error === 0
    && stats.value.hospitales_pendientes === 0
    && stats.value.auditoria_fallback_pendientes === 0
})

const accesosRapidos = [
  { to: '/admin/hospitales/create', label: 'Crear hospital', icono: 'i-heroicons-plus-circle', fondo: 'linear-gradient(135deg, #0891b2, #0e7490)' },
  { to: '/admin/modulos', label: 'Módulos', icono: 'i-heroicons-squares-plus', fondo: 'linear-gradient(135deg, #f59e0b, #d97706)' },
  { to: '/admin/modulos/dependencias', label: 'Dependencias', icono: 'i-heroicons-link', fondo: 'linear-gradient(135deg, #6366f1, #4f46e5)' },
  { to: '/admin/niveles-hospitalarios', label: 'Niveles MINSA', icono: 'i-heroicons-academic-cap', fondo: 'linear-gradient(135deg, var(--navy), #0f2840)' },
  { to: '/admin/usuarios', label: 'Usuarios', icono: 'i-heroicons-users', fondo: 'linear-gradient(135deg, #6366f1, #4338ca)' },
  { to: '/admin/auditoria', label: 'Auditoría', icono: 'i-heroicons-shield-check', fondo: 'linear-gradient(135deg, var(--alert), #b91c1c)' },
  { to: '/admin/reportes/mensuales', label: 'Reporte mensual', icono: 'i-heroicons-chart-bar', fondo: 'linear-gradient(135deg, #0891b2, #0e7490)' },
  { to: '/admin/reportes/hospitales-modulos', label: 'Hosp. × módulos', icono: 'i-heroicons-table-cells', fondo: 'linear-gradient(135deg, #f59e0b, #d97706)' },
]

const usuariosRecientes = computed(() => stats.value?.usuarios_recientes ?? [])

const iniciales = (nombre: string) => (nombre || '?')
  .trim()
  .split(/\s+/)
  .slice(0, 2)
  .map(p => p[0]?.toUpperCase())
  .join('')

const avatarGradiente = (panel: string) => ({
  admin: 'linear-gradient(135deg, var(--navy), #0f2840)',
  app: 'linear-gradient(135deg, #0891b2, #0e7490)',
  sigarh: 'linear-gradient(135deg, #6366f1, #4338ca)',
}[panel] || 'linear-gradient(135deg, #64748b, #475569)')

const etiquetaPanel = (panel: string) => ({ admin: 'Admin ERP', app: 'Hospitalario', sigarh: 'SIGARH' }[panel] || panel)

const tiempoRelativo = (iso: string) => {
  const ms = Date.now() - new Date(iso).getTime()
  const min = Math.round(ms / 60000)
  if (min < 1) return 'ahora'
  if (min < 60) return `${min} min`
  const horas = Math.round(min / 60)
  if (horas < 24) return `${horas} h`
  return `${Math.round(horas / 24)} d`
}

const abrirNotificacion = async (n: Notificacion) => {
  if (!n.is_read) {
    try {
      await api(`/admin/notificaciones/${n.id}/leer`, { method: 'PATCH' })
      n.is_read = true
      notifNoLeidas.value = Math.max(0, notifNoLeidas.value - 1)
    } catch {
      // no bloquea la navegacion si falla marcar como leida
    }
  }
  if (n.link) router.push(n.link)
}
const minutosDesdeActualizacion = computed(() => {
  if (!stats.value?.actualizado_en) return 0
  const ms = Date.now() - new Date(stats.value.actualizado_en).getTime()
  return Math.max(0, Math.round(ms / 60000))
})

const nombreUsuario = computed(() => authStore.user?.name || 'bienvenido')

const saludoHora = computed(() => {
  const hora = new Date().getHours()
  if (hora < 12) return 'Buenos días, aquí tienes el panorama completo de la plataforma.'
  if (hora < 19) return 'Buenas tardes, aquí tienes el panorama completo de la plataforma.'
  return 'Buenas noches, aquí tienes el panorama completo de la plataforma.'
})

const registrosPorMes = computed(() => stats.value?.hospitals_by_month.map(item => ({ label: item.label, valor: item.value })) ?? [])
const usuariosPorPanel = computed(() => ({
  app: stats.value?.users_by_panel.app ?? 0,
  sigarh: stats.value?.users_by_panel.sigarh ?? 0,
}))
const usuariosPorPanelSeries = computed(() => [usuariosPorPanel.value.app, usuariosPorPanel.value.sigarh])
const tiposDeModulo = computed(() => Object.keys(stats.value?.modules_distribution ?? {}).length)
const porcentajeHospitalesActivos = computed(() => {
  const total = stats.value?.total_hospitals ?? 0
  if (!total) return 0
  return Math.round(((stats.value?.active_hospitals ?? 0) / total) * 100)
})
const coberturaModulos = computed(() => Math.min(100, Math.round(
  ((stats.value?.active_module_assignments ?? 0) / Math.max((stats.value?.active_hospitals ?? 0) * Math.max(tiposDeModulo.value, 1), 1)) * 100,
)))
const usoModulos = computed(() => ({
  app: stats.value?.total_users ? Math.round((usuariosPorPanel.value.app / stats.value.total_users) * 100) : 0,
  sigarh: stats.value?.total_users ? Math.round((usuariosPorPanel.value.sigarh / stats.value.total_users) * 100) : 0,
}))
const distribucionNiveles = computed(() => (stats.value?.hospitals_by_level ?? []).map((nivel, index) => ({
  code: nivel.code,
  cantidad: nivel.count,
  color: ['var(--teal)', 'var(--navy)', '#6366f1', 'var(--warn)', 'var(--alert)'][index % 5],
})))
const maxNivel = computed(() => Math.max(...distribucionNiveles.value.map(n => n.cantidad), 1))

const topHospitalesModulos = computed(() => stats.value?.top_hospitals_by_modules ?? [])
const maxModulosTop = computed(() => Math.max(...topHospitalesModulos.value.map(h => h.modules), 1))
const actividadHoras = computed(() => {
  const eventos = stats.value?.audit_events_by_hour ?? []
  const maximo = Math.max(...eventos.map(item => item.value), 1)
  return eventos.map(item => ({ ...item, altura: (item.value / maximo) * 40, opacidad: 0.2 + (item.value / maximo) * 0.8 }))
})
const horaPico = computed(() => actividadHoras.value.reduce(
  (pico, hora) => hora.value > pico.value ? hora : pico,
  { label: '—', value: 0, altura: 0, opacidad: 0.2 },
))
const accionesAuditoria = computed(() => stats.value?.audit_actions ?? {})

// ── ApexCharts ──

const areaChartSeries = computed(() => [
  { name: 'Hospitales', data: registrosPorMes.value.map(m => m.valor) },
])

const areaChartOptions = computed(() => ({
  chart: {
    toolbar: { show: false },
    fontFamily: 'IBM Plex Sans, sans-serif',
    zoom: { enabled: false },
  },
  colors: ['#0891b2'],
  stroke: {
    curve: 'smooth',
    width: 3,
  },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.35,
      opacityTo: 0.03,
      stops: [0, 90, 100],
    },
  },
  markers: {
    size: 4,
    colors: ['#fff'],
    strokeColors: '#0891b2',
    strokeWidth: 2,
    hover: { size: 6 },
  },
  dataLabels: { enabled: false },
  xaxis: {
    categories: registrosPorMes.value.map(m => m.label),
    labels: { style: { colors: '#4a5c66', fontSize: '12px' } },
    axisBorder: { show: false },
    axisTicks: { show: false },
  },
  yaxis: { labels: { style: { colors: '#4a5c66', fontSize: '11px' } } },
  grid: { borderColor: '#dce5e7', strokeDashArray: 3 },
  tooltip: { theme: 'light' },
}))

const heroRingOptions = computed(() => ({
  chart: { fontFamily: 'IBM Plex Sans, sans-serif', sparkline: { enabled: true } },
  colors: ['#5fd4c6'],
  plotOptions: {
    radialBar: {
      hollow: { size: '55%' },
      track: { background: 'rgba(255,255,255,0.12)' },
      dataLabels: {
        name: { show: false },
        value: {
          show: true, offsetY: 5, fontSize: '13px', fontWeight: 700, color: '#fff',
          formatter: (val: number) => `${val}%`,
        },
      },
    },
  },
  stroke: { lineCap: 'round' },
}))

const radialChartOptions = computed(() => ({
  chart: { fontFamily: 'IBM Plex Sans, sans-serif' },
  colors: ['#0891b2', '#0b5fa8'],
  plotOptions: {
    radialBar: {
      hollow: { size: '45%' },
      track: { background: '#eef3f4' },
      dataLabels: {
        name: { show: false },
        value: { show: false },
      },
    },
  },
  labels: ['Panel APP', 'Panel SIGARH'],
  legend: { show: false },
  stroke: { lineCap: 'round' },
}))

const donutChartOptions = computed(() => ({
  chart: { fontFamily: 'IBM Plex Sans, sans-serif' },
  colors: ['#0891b2', '#6366f1'],
  labels: ['APP', 'SIGARH'],
  legend: { show: false },
  plotOptions: {
    pie: {
      donut: {
        size: '70%',
        labels: {
          show: true,
          total: { show: true, label: 'Total', color: '#1a2e3b', fontSize: '14px' },
        },
      },
    },
  },
  stroke: { width: 0 },
  dataLabels: { enabled: false },
}))

const barChartSeries = computed(() => [
  { name: 'Eventos', data: Object.values(accionesAuditoria.value) },
])

const barChartOptions = computed(() => ({
  chart: {
    type: 'bar',
    toolbar: { show: false },
    fontFamily: 'IBM Plex Sans, sans-serif',
  },
  colors: ['#0891b2', '#6366f1', '#f59e0b', '#ef4444'],
  plotOptions: {
    bar: {
      borderRadius: 6,
      columnWidth: '55%',
      distributed: true,
    },
  },
  dataLabels: { enabled: false },
  xaxis: {
    categories: Object.keys(accionesAuditoria.value),
    labels: { style: { colors: '#4a5c66', fontSize: '11px' } },
  },
  yaxis: {
    labels: { style: { colors: '#4a5c66', fontSize: '11px' } },
  },
  grid: { borderColor: '#dce5e7', strokeDashArray: 3 },
  tooltip: { theme: 'light' },
}))

onMounted(async () => {
  try {
    stats.value = await api<DashboardStats>('/admin/dashboard')
  } catch (e: any) {
    error.value = apiErr(e, 'Error de conexión')
  } finally {
    loading.value = false
  }

  try {
    const data = await api<Hospital[]>('/admin/hospitales')
    hospitalesRecientes.value = data.slice(0, 5)
  } catch (e: any) {
    errorHospitales.value = apiErr(e, 'No se pudieron cargar los hospitales recientes')
  } finally {
    loadingHospitales.value = false
  }

  try {
    const [lista, noLeidas] = await Promise.all([
      api<{ items: Notificacion[]; total: number }>('/admin/notificaciones?limit=5'),
      api<{ count: number }>('/admin/notificaciones/no-leidas'),
    ])
    notificacionesRecientes.value = lista.items
    notifNoLeidas.value = noLeidas.count
  } catch {
    notificacionesRecientes.value = []
  } finally {
    loadingNotifs.value = false
  }
})
</script>

<style scoped>
.banner-pulse {
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  animation: banner-draw 4s ease-in-out infinite;
}

@keyframes banner-draw {
  0% { stroke-dashoffset: 1; opacity: 0.3; }
  50% { stroke-dashoffset: 0; opacity: 1; }
  100% { stroke-dashoffset: -1; opacity: 0.3; }
}

.banner-float {
  animation: banner-drift 6s ease-in-out infinite;
}
.banner-float--1 { animation-duration: 7s; }
.banner-float--2 { animation-duration: 5.5s; animation-delay: 0.5s; }
.banner-float--3 { animation-duration: 6.5s; animation-delay: 1s; }
.banner-float--4 { animation-duration: 8s; animation-delay: 1.5s; }
.banner-float--5 { animation-duration: 9s; animation-delay: 2s; }

@keyframes banner-drift {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.banner-cross {
  animation: banner-pulse-fade 3s ease-in-out infinite;
}
.banner-cross--delay {
  animation-delay: 1.5s;
}
.banner-cross--delay2 {
  animation-delay: 2.5s;
}

@keyframes banner-pulse-fade {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

.banner-particle {
  animation: banner-particle-float 8s ease-in-out infinite;
}
.banner-particle--delay {
  animation-delay: 2s;
}
.banner-particle--delay2 {
  animation-delay: 4s;
}
.banner-particle--delay3 {
  animation-delay: 6s;
}

@keyframes banner-particle-float {
  0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.3; }
  25% { transform: translate(-8px, -12px) scale(1.2); opacity: 0.6; }
  50% { transform: translate(5px, -20px) scale(0.8); opacity: 0.8; }
  75% { transform: translate(10px, -5px) scale(1.3); opacity: 0.5; }
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}
.badge--ok {
  background: rgba(8, 145, 178, 0.12);
  color: var(--teal);
}

/* Entrada suave de las tarjetas del dashboard, en cascada por columna */
.dash-fade-in,
.dash-card {
  animation: dash-fade-up 0.4s ease-out backwards;
}
.dash-card:nth-child(2) { animation-delay: 0.06s; }

@keyframes dash-fade-up {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Tarjetas de salud del sistema: alertas accionables, nunca solo color */
.salud-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.9rem 1.1rem;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.salud-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md, var(--shadow-card));
}
.salud-card--alert { background: var(--alert-soft); color: var(--alert-dark, var(--alert)); }
.salud-card--warn { background: var(--warn-soft); color: var(--warn-dark, var(--warn)); }

.acceso-rapido {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.75rem;
  border-radius: 10px;
  background: var(--mist);
  transition: transform 0.15s ease, background 0.15s ease;
}
.acceso-rapido:hover {
  transform: translateY(-1px);
  background: var(--line);
}

/* Timeline de notificaciones: linea vertical conectando los puntos, para que
   se lea como una secuencia de eventos y no como una lista plana mas. */
.notif-timeline {
  position: relative;
  padding-left: 1.1rem;
}
.notif-timeline::before {
  content: '';
  position: absolute;
  left: 3px;
  top: 4px;
  bottom: 4px;
  width: 1px;
  background: var(--line);
}
.notif-timeline-item {
  position: relative;
  display: flex;
  cursor: pointer;
  padding: 0.15rem 0.4rem 0 0;
  border-radius: 6px;
  transition: background 0.15s ease;
}
.notif-timeline-item:hover { background: var(--mist); }
.notif-timeline-item--unread .notif-timeline-dot { box-shadow: 0 0 0 3px var(--mist); }
.notif-timeline-dot {
  position: absolute;
  left: -1.1rem;
  top: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.notif-timeline-dot--exito { background: var(--ok, #16a34a); }
.notif-timeline-dot--error { background: var(--alert, #dc2626); }
.notif-timeline-dot--alerta { background: var(--warn, #d97706); }
.notif-timeline-dot--info { background: var(--teal, #0891b2); }

/* KPI hero: la unica tarjeta con fondo oscuro degradado, para que la
   metrica principal no se confunda con el resto de tarjetas planas. */
.kpi-hero {
  background: linear-gradient(135deg, var(--navy) 0%, #123a5c 60%, #0f2840 100%);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.kpi-hero-link {
  margin-top: 0.75rem;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #5fd4c6;
  width: fit-content;
  transition: gap 0.15s ease;
}
.kpi-hero-link:hover { gap: 0.5rem; }

/* KPI cards livianas: fondo con un tinte sutil de su color (--kpi-tint), en
   vez de blanco plano identico en las cuatro tarjetas. */
.kpi-card {
  background: linear-gradient(160deg, var(--kpi-tint, transparent), var(--paper) 55%);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 20px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md, var(--shadow-card));
}
.kpi-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 10px -4px rgba(0,0,0,0.35);
}
.kpi-bar { transition: width 0.6s ease; }

.avatar-chip {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: white;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

@media (prefers-reduced-motion: reduce) {
  .dash-fade-in, .dash-card { animation: none; }
  .salud-card, .acceso-rapido, .kpi-card { transition: none; }
}

.admin-launcher { max-width:none; margin:0 auto; padding:16px 0 28px; text-align:center; }
.admin-launcher h1 { font-size:clamp(26px,2.8vw,38px); font-weight:600; line-height:1.3; margin:0 0 14px; color:var(--ink); }
.admin-launcher h1 span,.overview-heading h2 span { color:var(--teal); }
.admin-launcher>p { color:var(--ink-soft); font-size:14px; margin-bottom:24px; }
.admin-launcher-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px; }
.admin-launcher-card { flex:0 1 calc((100% - 72px)/4); display:flex; flex-direction:column; align-items:center; justify-content:center; gap:12px; min-height:132px; padding:20px 16px; background:white; border:1px solid transparent; border-radius:20px; box-shadow:0 16px 30px rgba(40,30,70,.07); color:var(--ink); font-size:16px; text-decoration:none; }
.admin-launcher-card:hover { border-color:var(--teal); }
.launcher-icon { width:38px; height:38px; color:var(--teal); }
.admin-overview { background:#f0ecfa; border-radius:20px; padding:24px; margin-bottom:24px; }
.overview-heading { text-align:center; margin-bottom:18px; }
.overview-heading h2 { font-size:26px; margin:0 0 8px; }
.overview-heading p { color:var(--ink-soft); font-size:14px; }
.admin-metrics { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:20px; }
.admin-metric { display:flex; flex-direction:column; align-items:flex-start; gap:8px; background:white; border-radius:16px; padding:18px; color:var(--ink); text-decoration:none; }
.admin-metric>span:first-child { width:28px; height:28px; color:var(--teal); }
.admin-metric strong { font-size:32px; font-weight:500; }
.admin-metric small { font-size:12px; color:var(--ink-soft); }
.admin-metric .partial-data { color:var(--alert); }
.admin-dashboard .avatar-chip { background:var(--teal-soft) !important; color:var(--teal); }
.admin-dashboard .dash-card { min-height:0; }
.admin-activity-grid { align-items:start; }
@media(max-width:1000px) { .admin-launcher-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } .admin-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media(max-width:540px) { .admin-launcher { padding:20px 0 32px; } .admin-launcher-grid { grid-template-columns:1fr; } .admin-launcher-card { min-height:110px; } .admin-overview { padding:20px; } .admin-metrics { grid-template-columns:1fr; } }
</style>
