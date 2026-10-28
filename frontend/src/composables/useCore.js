export function useCore() {
  const bulan = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
  ]

  const getNamaBulan = (no) => {
    if (!no && no !== 0) return ""
    const index = Number(no) - 1
    return bulan[index] || ""
  }

  const formatTanggalIndonesia = (tgl) => {
    if (!tgl) return ""

    const d = new Date(tgl)
    if (isNaN(d)) return ""

    const tanggal = d.getDate()
    const bulanNama = bulan[d.getMonth()]
    const tahun = d.getFullYear()

    return `${tanggal} ${bulanNama} ${tahun}`
  }

  return {
    bulan,
    getNamaBulan,
    formatTanggalIndonesia
  }
}
