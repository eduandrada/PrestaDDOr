window.PrestamosMarquee = {
  async refresh() {
    try { const r=await fetch('/api/news/latest'); if(!r.ok) return []; const d=await r.json(); return d.items||[]; }
    catch(e){ console.warn('News marquee:',e); return []; }
  }
};
