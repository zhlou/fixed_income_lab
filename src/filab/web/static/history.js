/* All financial differences come from Python. Rendering never fills a missing rate. */
(() => {
  const bp = value => value === null ? 'Unavailable' : `${value > 0 ? '+' : ''}${value.toFixed(0)} bp`;
  const rate = observation => observation === null ? 'Missing tenor' : `${observation.original_percent}%`;
  async function request(url, options) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Check your dates and year range.');
    return data;
  }
  function table(headers, rows) {
    const result = element('table'), head = element('thead'), heading = element('tr'), body = element('tbody');
    headers.forEach(value => {const th=element('th',value); th.scope='col'; heading.append(th);});
    head.append(heading); result.append(head,body);
    rows.forEach(values => {const row=element('tr'); values.forEach((value,index)=>{const cell=element(index?'td':'th',String(value)); if(!index)cell.scope='row'; row.append(cell);}); body.append(row);});
    return result;
  }
  function chart(container, data) {
    container.replaceChildren();
    const values = data.tenors.flatMap(t => [t.first?.rate, t.second?.rate]).filter(v => v !== undefined);
    if (!values.length) {container.append(element('p','No published values on these exact dates. Choose dates within coverage.')); return;}
    const low=Math.floor(Math.min(...values)*100)/100-.001, high=Math.ceil(Math.max(...values)*100)/100+.001;
    const x=v=>58+v/30*580, y=v=>255-(v-low)/(high-low)*210;
    const svg=svgElement('svg',{viewBox:'0 0 680 315',role:'img','aria-label':`Nominal par yields: ${data.dates.join(' versus ')}. Full values follow in the table.`});
    for(let i=0;i<=4;i++){const value=low+(high-low)*i/4; svg.append(svgElement('line',{x1:58,x2:638,y1:y(value),y2:y(value),stroke:'#ddd'}),svgElement('text',{x:51,y:y(value)+4,'text-anchor':'end','font-size':11},`${(value*100).toFixed(1)}%`));}
    [0,1,5,10,20,30].forEach(v=>svg.append(svgElement('text',{x:x(v),y:276,'text-anchor':'middle','font-size':11},String(v))));
    svg.append(svgElement('text',{x:345,y:304,'text-anchor':'middle','font-size':12},'Constant maturity · years'));
    ['first','second'].forEach((key,i)=>{
      let path='';
      data.tenors.forEach(t=>{if(t[key]===null){path='';return;} const px=x(t.years),py=y(t[key].rate); if(path)svg.append(svgElement('line',{x1:path[0],y1:path[1],x2:px,y2:py,stroke:colors[i],'stroke-width':2,'stroke-dasharray':i?'5 3':'none'})); path=[px,py]; const dot=svgElement('circle',{cx:px,cy:py,r:3.5,fill:colors[i],tabindex:0,'aria-label':`${data.dates[i]}, ${t.label}, ${rate(t[key])}`}); dot.append(svgElement('title',{},`${data.dates[i]} · ${t.label}: ${rate(t[key])}`));svg.append(dot);});
      svg.append(svgElement('text',{x:60+i*250,y:22,fill:colors[i],'font-size':12},`${i?'Dashed':'Solid'}: ${data.dates[i]}`));
    });
    container.append(svg);
  }
  document.querySelectorAll('[data-history]').forEach(root=>{
    const form=root.querySelector('[data-compare-form]'), error=root.querySelector('[data-history-error]'), results=root.querySelector('.history-results');
    let catalog, selected, bundled, sequence=0, controller, refreshing=false, refreshed;
    const revision=()=>root.querySelector('[name="revision"]:checked')?.value === 'hypothetical';
    function invalidate() {sequence++; controller?.abort(); results.setAttribute('aria-busy','true'); results.classList.add('history-stale'); error.textContent='Inputs changed. Compare dates to update the results.';}
    function render(data) {
      root.querySelector('[data-spread-first]').textContent=bp(data.spread_bp[0]);
      root.querySelector('[data-spread-second]').textContent=bp(data.spread_bp[1]);
      root.querySelector('[data-spread-change]').textContent=bp(data.spread_change_bp);
      chart(root.querySelector('[data-history-chart]'),data);
      const states={published:'published row',no_published_row:'no published row (nonpublication or source gap)',outside_coverage:'outside cached coverage'};
      root.querySelector('[data-date-states]').textContent=data.dates.map((day,i)=>`${day}: ${states[data.date_states[i]]}`).join('. ')+'.';
      root.querySelector('[data-history-table]').replaceChildren(table(['Tenor',data.dates[0],data.dates[1],'Change · bp'],data.tenors.map(t=>[t.label,t.first===null&&data.date_states[0]!=='published'?'No row':rate(t.first),t.second===null&&data.date_states[1]!=='published'?'No row':rate(t.second),t.included?bp(t.change_bp):'Excluded'])));
      root.querySelector('[data-sample-note]').textContent=`Common tenors: ${data.common_tenors.join(', ') || 'none'}. Excluded: ${data.excluded_tenors.join(', ') || 'none'}. 2y/10y common-date sample: ${data.spread_sample_dates.length} published dates; ${data.spread_excluded_dates.length} excluded published dates. No dates are filled.`;
      const evidence=root.querySelector('[data-history-provenance]'); evidence.replaceChildren();
      evidence.append(element('p',data.data_kind === 'hypothetical' ? 'HYPOTHETICAL REVISION · the second-date ten-year yield has been changed for this experiment.' : 'Historical observations · Treasury nominal constant-maturity par yields.'));
      evidence.append(element('p',`Snapshot: ${data.snapshot_id}`, 'history-hash'));
      evidence.append(element('p',`Cached coverage: ${data.coverage.map(v=>v.join(' to ')).join('; ')}. Latest published observation: ${data.published_dates.at(-1)}. ${data.published_dates.length} published rows.`));
      evidence.append(element('p','Observation dates describe the source rows. Exact publication times are unknown. Treasury usually posts by 6 p.m. Eastern, subject to delays. Feed updated timestamps do not establish historical availability.'));
      Object.entries(data.sources).forEach(([year,source])=>{
        const p=element('p',`${year} · retrieved ${source.retrieved_at} · original: percent per annum; normalized: decimal per annum. `);
        const link=element('a','Official source response'); link.href=source.url; link.target='_blank';link.rel='noopener';p.append(link); evidence.append(p,element('p',`Raw SHA-256: ${source.sha256}`,'history-hash'));
      });
      const coverageRows=data.tenors.map(t=>[t.label, data.missing_counts[t.label]]);
      evidence.append(table(['Tenor','Missing on published rows'],coverageRows));
      const days=element('details'), summary=element('summary','Inspect included and excluded dates');days.append(summary,element('p',`Published dates: ${data.published_dates.join(', ')}`),element('p',`2y/10y included: ${data.spread_sample_dates.join(', ') || 'none'}`),element('p',`2y/10y excluded: ${data.spread_excluded_dates.join(', ') || 'none'}`)); evidence.append(days);
      const note=root.querySelector('[data-revision-result]');if(note)note.textContent=data.data_kind==='hypothetical'?'Hypothetical result. The source snapshot was not modified.':'Published sample. Refreshing data never rewrites this pinned version.';
      root.querySelector('[data-snapshot-download]')?.setAttribute('href',`/api/history/snapshots/${selected}`);
    }
    async function compareDates() {
      const ticket=++sequence;controller?.abort();controller=new AbortController();error.textContent='';results.setAttribute('aria-busy','true');results.classList.add('history-stale');
      try {
        const query=new URLSearchParams({snapshot_id:selected,first:form.elements.first.value,second:form.elements.second.value,hypothetical_revision:revision()});
        const data=await request(`/api/history/compare?${query}`,{signal:controller.signal});
        if(ticket!==sequence)return;
        render(data);results.setAttribute('aria-busy','false');results.classList.remove('history-stale');
      } catch(e) {if(ticket===sequence && e.name!=='AbortError'){error.textContent=e.message;results.setAttribute('aria-busy','false');}}
    }
    function showSnapshots() {
      const options=root.querySelector('[data-snapshot-options]');if(!options)return;
      const current=catalog.snapshots.find(s=>s.id===catalog.active_snapshot_id);
      root.querySelector('[data-cache-summary]').textContent=`Latest saved coverage: ${current.coverage.map(c=>c.join(' to ')).join('; ')}. Latest observation: ${current.latest_observation}.`;
      options.replaceChildren(element('legend','Snapshot · an open comparison keeps this version'));
      catalog.snapshots.forEach(s=>{const label=element('label',undefined,'history-option'), input=element('input');input.type='radio';input.name='snapshot';input.value=s.id;input.checked=s.id===selected;input.addEventListener('change',()=>{selected=s.id;invalidate();compareDates();});label.append(input,element('span',`${s.bundled?'Pinned lesson sample':'Saved dataset'} · ${s.coverage.map(c=>c.join(' to ')).join('; ')} · ${s.row_count} rows · latest observation ${s.latest_observation} · saved ${s.created_at}`));options.append(label);});
    }
    form.addEventListener('submit',e=>{e.preventDefault();if(form.reportValidity())compareDates();});
    form.addEventListener('input',invalidate);
    root.querySelector('[data-reset-history]').addEventListener('click',()=>{form.reset();selected=bundled;root.querySelector('[value="observed"]')?.click();showSnapshots();compareDates();});
    root.querySelector('[data-missing-date]')?.addEventListener('click',()=>{form.elements.first.value='2025-02-17';compareDates();});
    root.querySelectorAll('[name="revision"]').forEach(r=>r.addEventListener('change',compareDates));
    const refreshForm=root.querySelector('[data-refresh-form]');
    refreshForm?.addEventListener('submit',async e=>{
      e.preventDefault();if(refreshing||!refreshForm.reportValidity())return;
      refreshing=true;const button=refreshForm.querySelector('button'),status=root.querySelector('[data-refresh-status]');button.disabled=true;root.querySelector('[data-use-refreshed]').hidden=true;status.textContent='Starting refresh…';
      try {
        const job=await request('/api/history/refresh',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({start_year:Number(refreshForm.elements.start_year.value),end_year:Number(refreshForm.elements.end_year.value)})});
        let state;
        do {await new Promise(resolve=>setTimeout(resolve,900));state=await request(`/api/history/refresh/${job.job_id}`);status.textContent=state.message;} while(state.state==='running');
        if(state.state==='complete'){refreshed=state.snapshot_id;catalog=await request('/api/history/snapshots');showSnapshots();root.querySelector('[data-use-refreshed]').hidden=false;}
      } catch(e) {status.textContent=e.message+' Your current comparison and cached snapshots are retained.';}
      finally {refreshing=false;button.disabled=false;}
    });
    root.querySelector('[data-use-refreshed]')?.addEventListener('click',()=>{selected=refreshed;showSnapshots();compareDates();});
    request('/api/history/snapshots').then(data=>{
      catalog=data;bundled=data.bundled_snapshot_id;selected=bundled;showSnapshots();
      if(refreshForm){['start_year','end_year'].forEach(name=>{refreshForm.elements[name].value=data.default_year;refreshForm.elements[name].max=data.current_year;});}
      compareDates();
    }).catch(e=>{error.textContent=e.message;results.setAttribute('aria-busy','false');});
  });
})();
