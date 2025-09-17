(function(){
  const fileInput = document.getElementById('fileInput');
  const sampleBtn = document.getElementById('sampleBtn');
  const table = document.getElementById('dataTable');
  const logEl = document.getElementById('log');

  fileInput.addEventListener('change', handleFile, false);
  sampleBtn.addEventListener('click', () => loadFromRows(sampleRows()), false);

  function log(msg){
    console.log(msg);
    logEl.textContent += msg + "\n";
  }

  function handleFile(e){
    const f = e.target.files[0];
    if(!f){ return; }
    log('Reading file: ' + f.name);
    const reader = new FileReader();
    reader.onload = function(ev){
      try {
        const data = new Uint8Array(ev.target.result);
        const wb = XLSX.read(data, { type: 'array' });
        const sheetName = wb.SheetNames[0];
        const sheet = wb.Sheets[sheetName];
        const rows = XLSX.utils.sheet_to_json(sheet, { header:1, raw: false });
        loadFromRows(rows);
      } catch (err) {
        log('Error parsing file: ' + err.message);
        alert('Σφάλμα στην ανάγνωση του αρχείου. Δες console για λεπτομέρειες.');
      }
    };
    reader.onerror = function(err){
      log('FileReader error: ' + err);
      alert('Σφάλμα κατά το διάβασμα του αρχείου.');
    };
    reader.readAsArrayBuffer(f);
  }

  function sampleRows(){
    return [
      ['Project', 'Type', 'Name', 'X', 'E', 'F', 'G', 'H', 'I', 'J'],
      ['Info',    'More', 'Trim Column C', '', '', '', '', '', '', 'Sum check'],
      ['p1', 't1', '  Alice  ', '', '10', '5', '', '2', '', '17'],
      ['p2', 't2', 'Bob', '', '3.5', '1.5', '', '0', '', '5.0'],
      ['p3', 't3', ' Γιώργος ', '', '2,5', '2,5', '', '1', '', '6'],
      ['p4', 't4', '', '', '1', '1', '', '1', '', '3'],
    ];
  }

  function parseNumber(v){
    if (v === undefined || v === null || v === '') return 0;
    let s = String(v).trim();
    s = s.replace(/[^\d\-,.]/g, '');
    if (s.indexOf(',') !== -1 && s.indexOf('.') === -1) {
      s = s.replace(',', '.');
    } else {
      s = s.replace(/,/g, '');
    }
    const n = parseFloat(s);
    return isNaN(n) ? 0 : n;
  }

  function loadFromRows(rows){
    try {
      logEl.textContent = '';
      if (!Array.isArray(rows)) throw new Error('Rows must be array');
      const headers = rows.slice(0,2);
      let data = rows.slice(2);

      data.forEach(r => {
        if (r && r.length > 2 && r[2] !== undefined && r[2] !== null) {
          r[2] = String(r[2]).trim();
        }
      });

      data.sort((a,b) => {
        const va = (a && a[2]) ? String(a[2]).toLowerCase() : '';
        const vb = (b && b[2]) ? String(b[2]).toLowerCase() : '';
        return va.localeCompare(vb);
      });

      renderTable(headers, data);
      log('Loaded ' + data.length + ' data rows (sorted by column C).');
    } catch(err) {
      console.error(err);
      alert('Σφάλμα: ' + err.message);
    }
  }

  function renderTable(headers, rows){
    table.innerHTML = '';
    const headerRow = headers[1] || headers[0] || [];
    let maxCols = headerRow.length;
    rows.forEach(r => { if (Array.isArray(r) && r.length > maxCols) maxCols = r.length; });

    const trh = document.createElement('tr');
    for (let c=0;c<maxCols;c++){
      const th = document.createElement('th');
      const hVal = (headerRow[c] !== undefined && headerRow[c] !== null && headerRow[c] !== '') ? headerRow[c] : (headers[0] && headers[0][c] ? headers[0][c] : ('Col ' + (c+1)));
      th.textContent = hVal;
      trh.appendChild(th);
    }
    const thAction = document.createElement('th'); thAction.textContent = 'Actions';
    trh.appendChild(thAction);
    table.appendChild(trh);

    rows.forEach((r, rowIndex) => {
      const tr = document.createElement('tr');
      tr.dataset.row = rowIndex;

      for (let c=0;c<maxCols;c++){
        const td = document.createElement('td');
        const val = (r && r[c] !== undefined && r[c] !== null) ? r[c] : '';
        td.textContent = val;

        if (c === 9) {
          const e = parseNumber((r && r[4]) ? r[4] : 0);
          const f = parseNumber((r && r[5]) ? r[5] : 0);
          const h = parseNumber((r && r[7]) ? r[7] : 0);
          const j = parseNumber((r && r[9]) ? r[9] : 0);
          const sum = e + f + h;
          const eps = 1e-9;
          if (Math.abs(sum - j) > eps) {
            td.classList.add('red');
          }
        }

        tr.appendChild(td);
      }

      const tdAct = document.createElement('td');

      const btnDone = document.createElement('button');
      btnDone.textContent = 'Done';
      btnDone.className = 'action';
      btnDone.title = 'Σήμανση ως done (πράσινο)';
      btnDone.onclick = () => {
        tr.classList.toggle('done');
        if (tr.classList.contains('done')) tr.classList.remove('check');
      };

      const btnCheck = document.createElement('button');
      btnCheck.textContent = 'Check';
      btnCheck.className = 'action';
      btnCheck.title = 'Σήμανση ως check (πορτοκαλί)';
      btnCheck.onclick = () => {
        tr.classList.toggle('check');
        if (tr.classList.contains('check')) tr.classList.remove('done');
      };

      tdAct.appendChild(btnDone);
      tdAct.appendChild(btnCheck);
      tr.appendChild(tdAct);

      table.appendChild(tr);
    });
  }

})();