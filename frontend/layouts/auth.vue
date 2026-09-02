<!-- layouts/auth.vue -->
<template>
  <div class="min-h-screen flex" style="background: var(--mist)">
    <div
      class="hidden lg:flex w-[42%] flex-col justify-between p-12"
      style="background: var(--navy); color: white"
    >
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded flex items-center justify-center" style="background: var(--teal)">
          <span class="text-sm font-bold">+</span>
        </div>
        <span class="font-semibold tracking-tight">ERP Hospitalario</span>
      </div>

      <div>
        <h1 class="text-3xl font-semibold leading-tight mb-3">
          Gestión clínica y administrativa en un solo sistema
        </h1>
        <p class="text-sm" style="color: #b8ccd6">
          Admisión, historias clínicas, farmacia, laboratorio y recursos humanos,
          integrados por establecimiento.
        </p>
      </div>

      <p class="text-xs" style="color: #7fa1b3">
        Plataforma multi-establecimiento — Perú
      </p>
    </div>

    <div class="flex-1 flex items-center justify-center p-6">
      <div class="w-full max-w-sm">
        <slot />
      </div>
    </div>
  </div>
</template>