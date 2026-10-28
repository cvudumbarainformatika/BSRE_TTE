/**
 * Generate and open print dialog for PDF generation
 * Uses window.print() - user saves as PDF from print dialog
 */
export function generatePrintablePDF(data, config) {
  const { title, subtitle, tahun, headers, rows, totals, footer, orientation = 'portrait' } = config
  
  // Build HTML content
  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>${title} - ${tahun}</title>
      <style>
        @page {
          size: A4 ${orientation};
          margin: 15mm;
        }
        
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
          print-color-adjust: exact;
          -webkit-print-color-adjust: exact;
        }
        
        body {
          font-family: Arial, sans-serif;
          font-size: ${orientation === 'landscape' ? '7pt' : '9pt'};
        }
        
        .report-header {
          text-align: center;
          margin-bottom: 15px;
        }
        
        .report-header h1 {
          font-size: 14pt;
          font-weight: bold;
          margin-bottom: 5px;
        }
        
        .report-header h2 {
          font-size: 12pt;
          margin-bottom: 5px;
        }
        
        .report-header h3 {
          font-size: 12pt;
          font-weight: bold;
          margin-bottom: 10px;
        }
        
        .report-table {
          width: 100%;
          border-collapse: collapse;
          margin-bottom: 20px;
        }
        
        .report-table th {
          background-color: #2980b9;
          color: white;
          padding: 6px 4px;
          border: 1px solid #333;
          font-weight: bold;
          text-align: center;
          font-size: ${orientation === 'landscape' ? '7pt' : '8pt'};
        }
        
        .report-table td {
          padding: 4px;
          border: 1px solid #999;
          text-align: left;
        }
        
        .report-table td:first-child {
          text-align: center;
        }
        
        .report-table td.number {
          text-align: right;
        }
        
        .report-table tbody tr:nth-child(even) {
          background-color: #f5f5f5;
        }
        
        .report-table tfoot tr {
          background-color: #34495e;
          color: white;
          font-weight: bold;
        }
        
        .report-table tfoot td {
          padding: 6px 4px;
        }
        
        .report-footer {
          margin-top: 30px;
          page-break-inside: avoid;
        }
        
        .signature {
          float: right;
          text-align: center;
          font-size: 9pt;
          line-height: 1.4;
        }
        
        .signature p {
          margin: 2px 0;
        }
        
        .signature .name {
          margin-top: 50px;
          font-weight: bold;
        }
        
        .report-table tbody tr.subheader-row {
          background-color: #E7E6E6 !important;
        }

        .report-table td.subheader {
          font-weight: bold;
          text-align: left;
          background-color: #E7E6E6 !important;
        }

        .winner {
          background-color: #C6EFCE !important;
          color: #006100;
          text-align: center;
          -webkit-print-color-adjust: exact;
        }

        
        @media print {
          .report-table thead {
            display: table-header-group;
          }
          .report-table tbody tr.subheader-row {
            background-color: #E7E6E6 !important;
            -webkit-print-color-adjust: exact;
          }
        }
      </style>
    </head>
    <body>
      <div class="report-header">
        <h1>${title}</h1>
        <h2>${subtitle}</h2>
        <h3>TAHUN ${tahun}</h3>
      </div>
      
      <table class="report-table">
        <thead>
          ${headers.map(row => `
            <tr>
              ${row.map(cell => {
                const rowspan = cell.rowspan ? `rowspan="${cell.rowspan}"` : ''
                const colspan = cell.colspan ? `colspan="${cell.colspan}"` : ''
                return `<th ${rowspan} ${colspan}>${cell.label}</th>`
              }).join('')}
            </tr>
          `).join('')}
        </thead>
        <tbody>
          ${rows.map((row, idx) => `
            <tr class="${row.length === 1 && row[0].className === 'subheader' ? 'subheader-row' : ''}">
              ${row.map((cell, cellIdx) => {
                if (typeof cell === 'object' && cell !== null) {
                  const colspan = cell.colspan ? `colspan="${cell.colspan}"` : ''
                  const className = cell.className || ''
                  return `<td ${colspan} class="${className}">${cell.label}</td>`
                }
                const isNumber = cellIdx > 0 && !isNaN(String(cell).replace(/\./g, '')) && cell !== ''
                return `<td class="${isNumber ? 'number' : ''}">${cell}</td>`
              }).join('')}
            </tr>
          `).join('')}
        </tbody>
        <tfoot>
          <tr>
            ${totals.map((total, idx) => 
               `<td class="${idx > 0 ? 'number' : ''}">${total}</td>`
            ).join('')}
          </tr>
        </tfoot>
      </table>
      
      <div class="report-footer">
        <div class="signature">
          <p>Probolinggo, ${footer.tanggal}</p>
          <p style="font-weight: bold;">KEPALA DINAS</p>
          <p style="font-weight: bold;">KEPEMUDAAN OLAHRAGA DAN PARIWISATA</p>
          <p style="font-weight: bold;">KOTA PROBOLINGGO</p>
          <p class="name">${footer.namaKepalaDinas}</p>
          ${footer.jabatan ? `<p>${footer.jabatan}</p>` : ''}
          ${footer.nip ? `<p>NIP. ${footer.nip}</p>` : ''}
        </div>
      </div>
      
      <script>
        // Auto print when loaded
        window.onload = function() {
          window.print()
          
          // Close window after print dialog is closed (optional)
          window.onafterprint = function() {
            // window.close() // Uncomment if you want auto-close
          }
        }
      </script>
    </body>
    </html>
  `
  
  // Open new window with print content
  const printWindow = window.open('', '_blank', 'width=1200,height=800')
  
  if (!printWindow) {
    throw new Error('Pop-up blocked! Please allow pop-ups for this site.')
  }
  
  printWindow.document.open()
  printWindow.document.write(htmlContent)
  printWindow.document.close()
  
  return printWindow
}

/**
 * Generate custom PDF for Hotel Per Bulan report
 * Has unique layout with official header, 2-column details, and 2 tables
 */
export function generateHotelPerBulanPDF(hotelData, metadata) {
  const { title, subtitle, footer } = metadata
  
  // Helper to format numbers
  const fmtNum = (n) => {
    if (!n || n === 0) return '0'
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.')
  }

  // Helper to format float with 1 decimal
  const fmtFloat = (n) => {
    if (!n || n === 0) return '0.0'
    return n.toFixed(1)
  }

  // Group countries by Kawasan
  const countriesByKawasan = {}
  hotelData.Countries?.forEach(c => {
    if (!countriesByKawasan[c.Kawasan]) {
      countriesByKawasan[c.Kawasan] = []
    }
    countriesByKawasan[c.Kawasan].push(c)
  })

  const htmlContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>${title} - ${hotelData.NamaHotel}</title>
      <style>
        @page {
          size: A4 portrait;
          margin: 10mm 12mm;
        }
        
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
          print-color-adjust: exact;
          -webkit-print-color-adjust: exact;
        }
        
        body {
          font-family: Arial, sans-serif;
          font-size: 8pt;
          line-height: 1.2;
        }

        /* Official Letterhead */
        .letterhead {
          text-align: left;
          margin-bottom: 10px;
          margin-left: 50%;
        }

        .letterhead p {
          margin: 1px 0;
          font-size: 7pt;
        }

        .letterhead .title {
          font-weight: bold;
          font-size: 8pt;
        }

        /* Report Title */
        .report-title {
          text-align: center;
          margin: 10px 0;
        }

        .report-title h1 {
          font-size: 11pt;
          font-weight: bold;
          margin-bottom: 2px;
        }

        .report-title h2 {
          font-size: 10pt;
          font-weight: bold;
        }

        /* Hotel Details - 2 Column Layout */
        .hotel-details {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 15px;
          margin-bottom: 10px;
          font-size: 7pt;
        }

        .hotel-details dl {
          margin: 0;
        }

        .hotel-details dt {
          float: left;
          clear: left;
          width: 60%;
          font-weight: normal;
        }

        .hotel-details dd {
          margin-left: 60%;
          padding-left: 8px;
          font-weight: bold;
        }

        .hotel-details dd::before {
          content: ': ';
        }

        /* Tables Container - Side by Side */
        .tables-container {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
          margin-bottom: 15px;
        }

        .data-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 6pt;
        }

        .data-table th {
          background-color: #2980b9;
          color: white;
          padding: 3px 2px;
          border: 1px solid #333;
          font-weight: bold;
          text-align: center;
          font-size: 6pt;
        }

        .data-table td {
          padding: 2px 3px;
          border: 1px solid #999;
          text-align: left;
        }

        .data-table td.number {
          text-align: right;
        }

        .data-table td.center {
          text-align: center;
        }

        .data-table .kawasan-header {
          background-color: #ecf0f1;
          font-weight: bold;
          font-style: italic;
        }

        .data-table .province-row {
          background-color: #f8f9fa;
          font-weight: bold;
        }

        .data-table .kabupaten-row {
          padding-left: 12px;
        }

        .data-table tbody tr:nth-child(even):not(.kawasan-header):not(.province-row) {
          background-color: #f5f5f5;
        }

        /* Footer Signature */
        .signature {
          margin-top: 20px;
          text-align: right;
          font-size: 8pt;
        }

        .signature p {
          margin: 2px 0;
        }

        @media print {
          body {
            -webkit-print-color-adjust: exact;
          }

          .data-table tr {
            page-break-inside: avoid;
          }
        }
      </style>
    </head>
    <body>
      <!-- Letterhead -->
      <div class="letterhead">
        <p class="title">Kepada</p>
        <p>Yth. Sdr. Kepala Dinas Kepemudaan, Olahraga dan Pariwisata Kota Probolinggo</p>
        <p>Jl. Soekarno-Hatta No. 273</p>
        <p>Telp: (0335) 426653 Fax. (0335) 429996</p>
        <p>Email: probolinggocitytour@gmail.com</p>
      </div>

      <!-- Report Title -->
      <div class="report-title">
        <h1>${title}</h1>
        <h2>${subtitle.replace('\n', '<br>')}</h2>
      </div>

      <!-- Hotel Details - 2 Columns -->
      <div class="hotel-details">
        <!-- LEFT COLUMN -->
        <div>
          <dl>
            <dt>Nama Akomodasi</dt>
            <dd>${hotelData.NamaHotel}</dd>
            
            <dt>Jumlah Kamar</dt>
            <dd>${fmtNum(hotelData.JumlahKamar)}</dd>
            
            <dt>Jumlah Kamar yang Tersedia dalam 1 Bulan</dt>
            <dd>${fmtNum(hotelData.JumlahKamarTersedia)}</dd>
            
            <dt>Jumlah Kamar yang Terjual dalam 1 Bulan</dt>
            <dd>${fmtNum(hotelData.JumlahKamarTerjual)}</dd>
            
            <dt>Jumlah Kamar WISNUS yang Terjual dalam 1 Bu</dt>
            <dd>${fmtNum(hotelData.JumlahKamarWisnusTerjual)}</dd>
            
            <dt>Jumlah Kamar WISMAN yang Terjual dalam 1 Bu</dt>
            <dd>${fmtNum(hotelData.JumlahKamarWismanTerjual)}</dd>
            
            <dt>Jumlah Karyawan</dt>
            <dd>${fmtNum(hotelData.JumlahKaryawan)}</dd>
          </dl>
        </div>

        <!-- RIGHT COLUMN -->
        <div>
          <dl>
            <dt>Alamat</dt>
            <dd>${hotelData.Alamat || '-'}</dd>
            
            <dt>Jumlah Tempat Tidur</dt>
            <dd>${fmtNum(hotelData.TempatTidur)}</dd>
            
            <dt>Jumlah Tempat Tidur yang Tersedia dalam 1 Bulan</dt>
            <dd>${fmtNum(hotelData.TempatTidurTersedia)}</dd>
            
            <dt>Jumlah Tempat Tidur yang Terjual dalam 1 Bulan</dt>
            <dd>${fmtNum(hotelData.TempatTidurTerjual)}</dd>
            
            <dt>Jumlah Tempat Tidur WISNUS yang Terjual dalam 1 Bulan</dt>
            <dd>${fmtNum(hotelData.TempatTidurWisnusTerjual)}</dd>
            
            <dt>Jumlah Tempat Tidur WISMAN yang Terjual dalam 1 Bu</dt>
            <dd>${fmtNum(hotelData.TempatTidurWismanTerjual)}</dd>
            
            <dt>Rata2 Okupansi</dt>
            <dd>${fmtFloat(hotelData.RataOkupansi)}%</dd>
            
            <dt>Rata2 Lama Menginap</dt>
            <dd>${fmtFloat(hotelData.RataLamaMenginap)} Hari</dd>
          </dl>
        </div>
      </div>

      <!-- Tables - Side by Side -->
      <div class="tables-container">
        <!-- NEGARA KEBANGSAAN -->
        <div>
          <table class="data-table">
            <thead>
              <tr>
                <th rowspan="2">NEGARA KEBANGSAAN</th>
                <th colspan="2">Jenis Kelamin</th>
                <th rowspan="2">Jumlah</th>
              </tr>
              <tr>
                <th>Pria</th>
                <th>Wanita</th>
              </tr>
            </thead>
            <tbody>
              ${Object.entries(countriesByKawasan).map(([kawasan, countries]) => `
                <tr class="kawasan-header">
                  <td colspan="4">${kawasan}</td>
                </tr>
                ${countries.map((c, idx) => `
                  <tr>
                    <td>${idx + 1}. ${c.NamaNegara}</td>
                    <td class="number">${fmtNum(c.Pria)}</td>
                    <td class="number">${fmtNum(c.Wanita)}</td>
                    <td class="number">${fmtNum(c.Jumlah)}</td>
                  </tr>
                `).join('')}
              `).join('')}
            </tbody>
          </table>
        </div>

        <!-- ASAL PROVINSI -->
        <div>
          <table class="data-table">
            <thead>
              <tr>
                <th rowspan="2">ASAL PROVINSI</th>
                <th rowspan="2">Kabupaten/Kota</th>
                <th colspan="2">Jenis Kelamin</th>
                <th rowspan="2">Jumlah</th>
              </tr>
              <tr>
                <th>Pria</th>
                <th>Wanita</th>
              </tr>
            </thead>
            <tbody>
              ${(() => {
                let currentPulau = ''
                let rows = ''
                
                hotelData.Provinces?.forEach(p => {
                  // Check if we need a new Pulau header
                  if (p.Pulau && p.Pulau !== currentPulau) {
                    currentPulau = p.Pulau
                    rows += `
                      <tr class="kawasan-header">
                        <td colspan="5">${currentPulau}</td>
                      </tr>
                    `
                  }
                  
                  if (!p.NamaKabupaten) {
                    // Province row
                    rows += `
                      <tr class="province-row">
                        <td>${p.NamaProvinsi}</td>
                        <td class="center">-</td>
                        <td class="number">${fmtNum(p.Pria)}</td>
                        <td class="number">${fmtNum(p.Wanita)}</td>
                        <td class="number">${fmtNum(p.Jumlah)}</td>
                      </tr>
                    `
                  } else {
                    // Kabupaten row
                    rows += `
                      <tr class="kabupaten-row">
                        <td></td>
                        <td>${p.NamaKabupaten}</td>
                        <td class="number">${fmtNum(p.Pria)}</td>
                        <td class="number">${fmtNum(p.Wanita)}</td>
                        <td class="number">${fmtNum(p.Jumlah)}</td>
                      </tr>
                    `
                  }
                })
                
                return rows || '<tr><td colspan="5" class="center">Tidak ada data</td></tr>'
              })()}
            </tbody>
          </table>
        </div>
      </div>

      <!-- Footer Signature -->
      <div class="signature">
        <p>Probolinggo, ${footer.tanggal}</p>
        <p>Pimpinan</p>
      </div>
      
      <script>
        // Auto print when loaded
        window.onload = function() {
          window.print()
        }
      </script>
    </body>
    </html>
  `
  
  // Open new window with print content
  const printWindow = window.open('', '_blank', 'width=1200,height=800')
  
  if (!printWindow) {
    throw new Error('Pop-up blocked! Please allow pop-ups for this site.')
  }
  
  printWindow.document.open()
  printWindow.document.write(htmlContent)
  printWindow.document.close()
  
  return printWindow
}
