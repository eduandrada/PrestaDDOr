window.PrestamosSettings = {
  async load() { const r=await fetch('/settings'); return r.json(); },
  async save(data) { const r=await fetch('/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); const d=await r.json(); if(!r.ok) throw new Error(d.error||'No se pudieron guardar los ajustes'); return d; }
};
