export const useCitaPdf = () => {
  const { api } = useApi()
  const imprimiendoId = ref('')

  const abrirComprobante = async (citaId: string) => {
    imprimiendoId.value = citaId
    try {
      const blob = await api<Blob>(`/app/consulta-externa/citas/${citaId}/comprobante.pdf`, {
        responseType: 'blob',
        headers: { Accept: 'application/pdf' },
      })
      const url = URL.createObjectURL(blob)
      window.open(url, '_blank', 'noopener,noreferrer')
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000)
    } finally {
      imprimiendoId.value = ''
    }
  }

  return { abrirComprobante, imprimiendoId }
}
