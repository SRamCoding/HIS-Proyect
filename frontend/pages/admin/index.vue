<!-- pages/admin/index.vue -->
<template>
  <div>
    <!-- Banner de bienvenida mejorado con SVG más elaborado -->
    <div
      class="relative overflow-hidden mb-6 flex items-stretch"
      style="border-radius: var(--radius-lg); box-shadow: var(--shadow-card); height: 190px; background: linear-gradient(135deg, var(--navy) 0%, #1a3a5c 50%, #0f2840 100%)"
    >
      <div class="relative z-10 flex flex-col justify-center px-8 py-6 flex-1 min-w-0">
        <div class="flex items-center gap-3 mb-1">
          <div class="w-11 h-11 rounded-full flex items-center justify-center" style="background: rgba(255,255,255,0.08); backdrop-filter: blur(8px); border: 1px solid rgba(255,255,255,0.06)">
            <UIcon name="i-heroicons-user-circle" class="w-6 h-6 text-white/90" />
          </div>
          <div>
            <h1 class="text-2xl font-bold text-white truncate">Hola, {{ nombreUsuario }}</h1>
            <p class="text-sm text-white/70">{{ saludoHora }}</p>
          </div>
        </div>
        <div class="flex items-center gap-5 mt-1.5 text-xs text-white/60">
          <span class="flex items-center gap-1.5">
            <UIcon name="i-heroicons-check-circle" class="w-3.5 h-3.5 text-emerald-400" />
            Sistema operativo
          </span>
          <span class="flex items-center gap-1.5">
            <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
            Última actualización: {{ minutosDesdeActualizacion }} min
          </span>
        </div>
      </div>

      <div class="relative hidden sm:block shrink-0" style="width: 44%; max-width: 440px">
        <svg class="absolute inset-0 w-full h-full" viewBox="0 0 440 190" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
          <!-- Círculos decorativos -->
          <circle class="banner-float banner-float--1" cx="370" cy="35" r="50" fill="rgba(255,255,255,0.04)" />
          <circle class="banner-float banner-float--2" cx="290" cy="140" r="34" fill="rgba(255,255,255,0.035)" />
          <circle class="banner-float banner-float--3" cx="405" cy="148" r="22" fill="rgba(255,255,255,0.06)" />
          <circle class="banner-float banner-float--4" cx="330" cy="18" r="14" fill="rgba(94, 212, 198, 0.12)" />
          <circle class="banner-float banner-float--5" cx="420" cy="75" r="8" fill="rgba(255,255,255,0.05)" />

          <!-- Cruces médicas -->
          <g class="banner-cross" transform="translate(340,50)" opacity="0.4">
            <rect x="-3.5" y="-16" width="7" height="32" rx="2" fill="#e0f2fe" />
            <rect x="-16" y="-3.5" width="32" height="7" rx="2" fill="#e0f2fe" />
          </g>
          <g class="banner-cross banner-cross--delay" transform="translate(400,95)" opacity="0.3">
            <rect x="-2.5" y="-12" width="5" height="24" rx="2" fill="#e0f2fe" />
            <rect x="-12" y="-2.5" width="24" height="5" rx="2" fill="#e0f2fe" />
          </g>
          <g class="banner-cross banner-cross--delay2" transform="translate(310,145)" opacity="0.25">
            <rect x="-2" y="-9" width="4" height="18" rx="2" fill="#e0f2fe" />
            <rect x="-9" y="-2" width="18" height="4" rx="2" fill="#e0f2fe" />
          </g>

          <!-- Línea de pulso -->
          <path
            class="banner-pulse"
            d="M0,105 L75,105 L95,105 L112,55 L130,150 L150,100 L170,100 L188,72 L206,100 L410,100"
            fill="none"
            stroke="#5fd4c6"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
            pathLength="1"
          />

          <!-- Icono de hospital SVG -->
          <g transform="translate(60, 75)" opacity="0.25">
            <rect x="0" y="6" width="28" height="22" rx="2" fill="none" stroke="#5fd4c6" stroke-width="1.5" />
            <rect x="8" y="14" width="4" height="14" fill="#5fd4c6" opacity="0.4" />
            <rect x="16" y="14" width="4" height="14" fill="#5fd4c6" opacity="0.4" />
            <rect x="10" y="0" width="8" height="6" rx="1" fill="#5fd4c6" opacity="0.3" />
            <line x1="14" y1="0" x2="14" y2="6" stroke="#5fd4c6" stroke-width="1" opacity="0.3" />
          </g>

          <!-- Partículas decorativas -->
          <circle cx="150" cy="30" r="3" fill="rgba(94, 212, 198, 0.15)" class="banner-particle" />
          <circle cx="220" cy="160" r="2.5" fill="rgba(255,255,255,0.08)" class="banner-particle banner-particle--delay" />
          <circle cx="180" cy="170" r="2" fill="rgba(94, 212, 198, 0.1)" class="banner-particle banner-particle--delay2" />
          <circle cx="130" cy="155" r="3.5" fill="rgba(255,255,255,0.06)" class="banner-particle banner-particle--delay3" />
        </svg>
      </div>
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

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px; border-left: 3px solid var(--teal)">
        <div class="flex items-start justify-between mb-2">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background: var(--mist)">
              <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--teal)" />
            </div>
            <div>
              <p class="text-xs font-medium uppercase tracking-wider" style="color: var(--ink-soft)">Hospitales Activos</p>
              <p class="text-2xl font-bold font-mono-data leading-tight" style="color: var(--ink)">
                {{ stats?.active_hospitals ?? '—' }}
              </p>
            </div>
          </div>
        </div>
        <div class="mt-2">
          <div class="h-1 rounded-full overflow-hidden" style="background: var(--mist)">
            <div class="h-full rounded-full" style="width: 78%; background: var(--teal)" />
          </div>
        </div>
      </div>

      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px; border-left: 3px solid #6366f1">
        <div class="flex items-start justify-between mb-2">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background: var(--ok-soft)">
              <UIcon name="i-heroicons-users" class="w-5 h-5" style="color: #6366f1" />
            </div>
            <div>
              <p class="text-xs font-medium uppercase tracking-wider" style="color: var(--ink-soft)">Usuarios Totales</p>
              <p class="text-2xl font-bold font-mono-data leading-tight" style="color: var(--ink)">
                {{ stats?.total_users ?? '—' }}
              </p>
            </div>
          </div>
          <span class="text-xs font-medium flex items-center gap-0.5 px-2 py-1 rounded-full" style="background: var(--ok-soft); color: var(--ok)">
            <UIcon name="i-heroicons-arrow-trending-up" class="w-3.5 h-3.5" />
            {{ stats?.active_users ?? 0 }} activos
          </span>
        </div>
        <div class="flex items-center gap-3 mt-1 text-xs" style="color: var(--ink-soft)">
          <span class="flex items-center gap-1">
            <UIcon name="i-heroicons-user-group" class="w-3.5 h-3.5" style="color: #6366f1" />
            Panel APP: {{ usuariosPorPanel.app }}
          </span>
          <span class="flex items-center gap-1">
            <UIcon name="i-heroicons-user" class="w-3.5 h-3.5" style="color: var(--teal)" />
            SIGARH: {{ usuariosPorPanel.sigarh }}
          </span>
        </div>
      </div>

      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px; border-left: 3px solid var(--warn)">
        <div class="flex items-start justify-between mb-2">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background: var(--warn-soft)">
              <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--warn)" />
            </div>
            <div>
              <p class="text-xs font-medium uppercase tracking-wider" style="color: var(--ink-soft)">Módulos habilitados</p>
              <p class="text-2xl font-bold font-mono-data leading-tight" style="color: var(--ink)">
                {{ stats?.active_module_assignments ?? '—' }}
              </p>
            </div>
          </div>
          <span class="text-xs font-medium flex items-center gap-0.5 px-2 py-1 rounded-full" style="background: var(--mist); color: var(--ink-soft)">
            <UIcon name="i-heroicons-minus" class="w-3.5 h-3.5" />
            asignaciones
          </span>
        </div>
        <div class="mt-2">
          <p class="text-xs truncate" style="color: var(--ink-soft)">
            {{ tiposDeModulo }} tipos en {{ stats?.active_hospitals ?? 0 }} hospitales
          </p>
          <div class="h-1 rounded-full overflow-hidden mt-2" style="background: var(--mist)">
            <div class="h-full rounded-full" :style="{ width: `${coberturaModulos}%`, background: 'var(--warn)' }" />
          </div>
        </div>
      </div>

      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px; border-left: 3px solid var(--alert)">
        <div class="flex items-start justify-between mb-2">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center" style="background: var(--alert-soft)">
              <UIcon name="i-heroicons-shield-exclamation" class="w-5 h-5" style="color: var(--alert)" />
            </div>
            <div>
              <p class="text-xs font-medium uppercase tracking-wider" style="color: var(--ink-soft)">Eventos Auditoría</p>
              <p class="text-2xl font-bold font-mono-data leading-tight" style="color: var(--ink)">
                {{ stats?.audit_events_24h ?? 0 }}
              </p>
            </div>
          </div>
          <span class="text-xs font-medium flex items-center gap-0.5 px-2 py-1 rounded-full" style="background: var(--alert-soft); color: var(--alert)">
            <UIcon name="i-heroicons-arrow-trending-down" class="w-3.5 h-3.5" />
            últimas 24 h
          </span>
        </div>
        <div class="mt-1 flex items-center gap-3 text-xs" style="color: var(--ink-soft)">
          <span class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full" style="background: var(--ok)"></span>
            Eventos reales
          </span>
          <span class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full" style="background: var(--warn)"></span>
            Registrados
          </span>
        </div>
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
        <p class="text-sm font-semibold mb-3" style="color: var(--ink)">Usuarios por panel</p>
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
          <p class="text-sm font-semibold" style="color: var(--ink)">Usuarios por panel</p>
          <span class="text-xs" style="color: var(--ink-soft)">Total: {{ stats?.total_users ?? 0 }}</span>
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

      <table v-else class="w-full text-sm">
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
}

interface Hospital {
  id: string
  name: string
  hospital_level?: string
  is_active: boolean
  active_modules: string[]
}

const { api } = useApi()
const authStore = useAuthStore()

const stats = ref<DashboardStats | null>(null)
const hospitalesRecientes = ref<Hospital[]>([])
const loading = ref(true)
const loadingHospitales = ref(true)
const error = ref('')
const minutosDesdeActualizacion = ref(2)

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
  labels: ['Médicos', 'Administrativos'],
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
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }

  try {
    const data = await api<Hospital[]>('/admin/hospitales')
    hospitalesRecientes.value = data.slice(0, 5)
  } finally {
    loadingHospitales.value = false
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
.badge--neutral {
  background: var(--mist);
  color: var(--ink-soft);
}
</style>
