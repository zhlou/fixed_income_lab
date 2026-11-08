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
  function chart(container, data, scale) {
    container.replaceChildren();
    const values = data.tenors.flatMap(t => [t.first?.rate, t.second?.rate]).filter(v => v !== undefined);
    if (!values.length) {container.append(element('p','No published values on these exact dates. Choose dates within coverage.')); return;}
    const width=Math.max(260,Math.round(container.clientWidth)), height=310;
    const left=54,right=width-23,top=65,bottom=250;
    const log=scale==='log', minimum=1/12, maximum=30;
    const x=v=>left+(log?Math.log(v/minimum)/Math.log(maximum/minimum):v/maximum)*(right-left);
    const low=Math.floor(Math.min(...values)*100)/100-.001, high=Math.ceil(Math.max(...values)*100)/100+.001;
    const y=v=>bottom-(v-low)/(high-low)*(bottom-top);
    const svg=svgElement('svg',{viewBox:`0 0 ${width} ${height}`,role:'img','data-x-scale':scale,'aria-label':`Nominal par yields: ${data.dates.join(' versus ')}. ${log?'Logarithmic':'Linear'} maturity axis; linear yield axis. Full values follow in the table.`});
    svg.append(svgElement('text',{x:left,y:14,'font-size':12},'Annual par yield (%)'));
    for(let i=0;i<=4;i++){const value=low+(high-low)*i/4; svg.append(svgElement('line',{x1:left,x2:right,y1:y(value),y2:y(value),stroke:'#ddd'}),svgElement('text',{x:left-7,y:y(value)+4,'text-anchor':'end','font-size':11},`${(value*100).toFixed(1)}%`));}
    const logTicks=width>=600?[[1/12,'1m'],[.25,'3m'],[.5,'6m'],[1,'1y'],[2,'2y'],[5,'5y'],[10,'10y'],[30,'30y']]:width>=430?[[1/12,'1m'],[.25,'3m'],[1,'1y'],[2,'2y'],[5,'5y'],[10,'10y'],[30,'30y']]:[[1/12,'1m'],[1,'1y'],[5,'5y'],[30,'30y']];
    const linearTicks=(width>=600?[0,1,5,10,20,30]:width>=430?[0,5,10,20,30]:[0,10,20,30]).map(v=>[v,v?`${v}y`:'0']);
    (log?logTicks:linearTicks).forEach(([v,label])=>svg.append(svgElement('text',{x:x(v),y:273,'text-anchor':'middle','font-size':11,'data-axis-tick':'x'},label)));
    svg.append(svgElement('text',{x:(left+right)/2,y:301,'text-anchor':'middle','font-size':12},log?'Maturity · log spacing':'Maturity · linear spacing'));
    ['first','second'].forEach((key,i)=>{
      let previous=null;
      data.tenors.forEach(t=>{
        if(t[key]===null){previous=null;return;}
        const px=x(t.years),py=y(t[key].rate);
        if(previous)svg.append(svgElement('line',{x1:previous[0],y1:previous[1],x2:px,y2:py,stroke:colors[i],'stroke-width':2,'stroke-dasharray':i?'5 3':'none'}));
        previous=[px,py];
        const dot=svgElement('circle',{cx:px,cy:py,r:3.5,fill:colors[i],tabindex:0,'data-maturity-years':t.years,'data-date':data.dates[i],'aria-label':`${data.dates[i]}, ${t.label}, ${rate(t[key])}`});
        dot.append(svgElement('title',{},`${data.dates[i]} · ${t.label}: ${rate(t[key])}`));svg.append(dot);
      });
      svg.append(svgElement('text',{x:width<430?left:left+i*(right-left)/2,y:width<430?33+i*17:39,fill:colors[i],'font-size':12},`${i?'Dashed':'Solid'}: ${data.dates[i]}`));
    });
    container.append(svg);
  }
  document.querySelectorAll('[data-history]').forEach(root=>{
    const form=root.querySelector('[data-compare-form]'), error=root.querySelector('[data-history-error]'), results=root.querySelector('.history-results');
    let catalog, selected, bundled, sequence=0, controller, refreshing=false, refreshed, lastResult, availabilitySequence=0;
    const lesson=root.dataset.pinned==='true';
    let monthLoader, latestMonth;
    const datePicker=new window.FilabHistoryDates(root,(month,force)=>queueMonth(month,force));
    function monthStatus(message,retry=false) {
      datePicker.setLoadStatus(message,retry);
      const status=root.querySelector('[data-month-status]');if(status)status.textContent=message;
      const button=root.querySelector('[data-retry-month]');if(button)button.hidden=!retry;
    }
    function queueMonth(month,force=false) {
      if(!selected)return;
      latestMonth=month;
      if(month<'1990-01'||month>`${catalog.current_year}-${String(catalog.current_month).padStart(2,'0')}`){
        monthLoader.cancel();monthStatus('Treasury months are available from January 1990 through the current month.');return;
      }
      const context=lessonContext();
      if(context&&!force&&selected===context.id&&month===context.defaults.first.slice(0,7)&&[form.elements.first.value,form.elements.second.value].every(value=>datePicker.data?.coverage.some(([a,b])=>a<=value&&value<=b))){
        monthLoader.cancel();monthStatus('Pinned lesson month · explore another month to load history.');return;
      }
      monthLoader.schedule(month,force);
    }
    monthLoader=new window.FilabHistoryMonths({
      status:monthStatus,
      load:async(month,force)=>{
        const [year,number]=month.split('-').map(Number);
        const job=await request('/api/history/month-load',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({year,month:number,base_snapshot_id:selected,force})});
        let state;
        do {await new Promise(resolve=>setTimeout(resolve,350));state=await request(`/api/history/jobs/${job.job_id}`);}while(state.state==='running');
        if(state.state!=='complete')throw new Error(state.message);
        const [dates,nextCatalog]=await Promise.all([request(`/api/history/snapshots/${state.snapshot_id}/dates`),request('/api/history/snapshots')]);
        return {...state,dates,catalog:nextCatalog};
      },
      apply:state=>{
        if(selected!==state.snapshot_id){selected=state.snapshot_id;invalidate();}
        ++availabilitySequence;catalog=state.catalog;datePicker.setAvailability(state.dates);updateLessonState();showSnapshots();
      }
    });
    root.querySelector('[data-retry-month]')?.addEventListener('click',()=>queueMonth(latestMonth,true));
    const chartContainer=root.querySelector('[data-history-chart]');
    const drawChart=()=>{if(lastResult)chart(chartContainer,lastResult,root.querySelector('[name="maturity_scale"]:checked').value);};
    root.querySelectorAll('[name="maturity_scale"]').forEach(input=>input.addEventListener('change',drawChart));
    let chartWidth=0;
    new ResizeObserver(entries=>{const width=Math.round(entries[0].contentRect.width);if(width>0&&width!==chartWidth){chartWidth=width;drawChart();}}).observe(chartContainer);
    const revision=()=>root.querySelector('[name="revision"]:checked')?.value === 'hypothetical';
    function lessonContext() {
      if(!lesson||!catalog)return null;
      const reference=root.querySelector('[name="history_sample"]:checked')?.value==='series-introduction';
      return {id:reference?catalog.reference_snapshot_id:bundled,defaults:reference?catalog.reference_defaults:catalog.example_defaults};
    }
    function updateLessonState() {
      const context=lessonContext();if(!context)return;
      const match=selected===context.id&&form.elements.first.value===context.defaults.first&&form.elements.second.value===context.defaults.second;
      const notice=root.querySelector('[data-lesson-example]');notice.dataset.mode=match?'worked-example':'exploration';
      notice.textContent=match?`Worked example · ${context.defaults.dates_label}. Using the pinned lesson observations.`:
        `Exploring history · the selected dates or dataset differ from the worked example (${context.defaults.dates_label}). The explanation below keeps its published example. Reset example restores ${catalog.example_defaults.dates_label} and the pinned observations.`;
    }
    function invalidate() {
      sequence++;controller?.abort();results.setAttribute('aria-busy','true');results.classList.add('history-stale');error.textContent='Inputs changed. Compare dates to update the results.';updateLessonState();
      const description=root.querySelector('[data-revision-description]');
      if(description)description.textContent=`Compare dates to inspect a hypothetical +10 bp ten-year revision for ${form.elements.second.value||'the second date'}. Saved source observations remain intact.`;
      const note=root.querySelector('[data-revision-result]');if(note)note.textContent='Compare dates to update this scenario.';
    }
    function refreshAvailability() {
      const ticket=++availabilitySequence, id=selected;datePicker.clearAvailability();
      request(`/api/history/snapshots/${id}/dates`).then(data=>{
        if(ticket===availabilitySequence&&selected===id)datePicker.setAvailability(data);
      }).catch(()=>{
        if(ticket===availabilitySequence&&selected===id&&datePicker.snapshotId!==id)datePicker.clearAvailability('Date availability unavailable. You can still type a date and compare.');
      });
    }
    function render(data) {
      datePicker.setAvailability(data);
      root.querySelector('[data-example-status]').textContent=`Displayed comparison: ${data.dates.join(' versus ')} · ${data.sample_label}`;updateLessonState();
      root.querySelector('[data-spread-first]').textContent=bp(data.spread_bp[0]);
      root.querySelector('[data-spread-second]').textContent=bp(data.spread_bp[1]);
      root.querySelector('[data-spread-change]').textContent=bp(data.spread_change_bp);
      lastResult=data;drawChart();
      const states={published:'published row',no_published_row:'no published row (nonpublication or source gap)',outside_coverage:'outside cached coverage'};
      root.querySelector('[data-date-states]').textContent=data.dates.map((day,i)=>`${day}: ${states[data.date_states[i]]}`).join('. ')+'.';
      root.querySelector('[data-history-table]').replaceChildren(table(['Tenor',data.dates[0],data.dates[1],'Change · bp'],data.tenors.map(t=>[t.label,t.first===null&&data.date_states[0]!=='published'?'No row':rate(t.first),t.second===null&&data.date_states[1]!=='published'?'No row':rate(t.second),t.included?bp(t.change_bp):'Excluded'])));
      root.querySelector('[data-sample-note]').textContent=`Common tenors: ${data.common_tenors.join(', ') || 'none'}. Excluded: ${data.excluded_tenors.join(', ') || 'none'}. 2y/10y common-date sample: ${data.spread_sample_dates.length} published dates; ${data.spread_excluded_dates.length} excluded published dates. No dates are filled.`;
      const evidence=root.querySelector('[data-history-provenance]'); evidence.replaceChildren();
      evidence.append(element('p',data.data_kind === 'hypothetical' ? (data.revision_scenario.applied?'HYPOTHETICAL REVISION · the second-date ten-year yield has been changed for this experiment.':'HYPOTHETICAL REVISION UNAVAILABLE · no source observation was changed.') : 'Historical observations · Treasury nominal constant-maturity par yields.'));
      evidence.append(element('p',`Snapshot: ${data.snapshot_id}`, 'history-hash'));
      evidence.append(element('p',`Cached coverage: ${data.coverage.map(v=>v.join(' to ')).join('; ')}. Latest published observation: ${data.published_dates.at(-1)||'none'}. ${data.published_dates.length} published rows.`));
      evidence.append(element('p','Observation dates describe the source rows. Exact publication times are unknown. Treasury usually posts by 6 p.m. Eastern, subject to delays. Feed updated timestamps do not establish historical availability.'));
      Object.entries(data.sources).forEach(([key,source])=>{
        const periods=source.coverage?(typeof source.coverage[0]==='string'?[source.coverage]:source.coverage):[[key+'-01-01',key+'-12-31']];
        const p=element('p',`${periods.map(c=>c.join(' to ')).join('; ')} · retrieved ${source.retrieved_at} · original: percent per annum; normalized: decimal per annum. `);
        const link=element('a','Official source response'); link.href=source.url; link.target='_blank';link.rel='noopener';p.append(link); evidence.append(p,element('p',`Raw SHA-256: ${source.sha256}`,'history-hash'));
      });
      const coverageRows=data.tenors.map(t=>[t.label, data.missing_counts[t.label]]);
      evidence.append(table(['Tenor','Missing on published rows'],coverageRows));
      const days=element('details'), summary=element('summary','Inspect included and excluded dates');days.append(summary,element('p',`Published dates: ${data.published_dates.join(', ')}`),element('p',`2y/10y included: ${data.spread_sample_dates.join(', ') || 'none'}`),element('p',`2y/10y excluded: ${data.spread_excluded_dates.join(', ') || 'none'}`)); evidence.append(days);
      const scenario=data.revision_scenario,description=root.querySelector('[data-revision-description]');
      if(description){
        const reason=data.date_states[1]==='outside_coverage'?'is outside cached coverage':data.date_states[1]==='no_published_row'?'has no published row':'has no published ten-year yield';
        description.textContent=scenario.original?`Hypothetical scenario for ${scenario.date}: increase the ten-year yield by ${scenario.change_bp} bp, from ${scenario.original.original_percent}% to ${scenario.revised.original_percent}%. Toggle the assumption, then inspect the comparison. Saved source observations remain intact.`:
          `A hypothetical revision is unavailable: ${scenario.date} ${reason}. Choose a date with a published ten-year yield. No missing rate is invented.`;
      }
      const note=root.querySelector('[data-revision-result]');if(note)note.textContent=data.data_kind==='hypothetical'?(scenario.applied?'Hypothetical result. The source snapshot was not modified.':'Hypothetical revision unavailable. No observation was changed.'):'Published observations. The hypothetical assumption has not been applied.';
      root.querySelector('[data-snapshot-download]')?.setAttribute('href',`/api/history/snapshots/${data.snapshot_id}`);
    }
    async function compareDates(loadMissing=false) {
      const inputs=[form.elements.first.value,form.elements.second.value];
      if(loadMissing){
        await monthLoader.wait();
        for(const value of inputs){
          if(!window.FilabHistoryDates.parse(value))return;
          if(!datePicker.data?.coverage.some(([a,b])=>a<=value&&value<=b)){queueMonth(value.slice(0,7));await monthLoader.wait();}
        }
        if(inputs[0]!==form.elements.first.value||inputs[1]!==form.elements.second.value)return;
      }
      const ticket=++sequence;controller?.abort();controller=new AbortController();error.textContent='';results.setAttribute('aria-busy','true');results.classList.add('history-stale');
      try {
        const query=new URLSearchParams({snapshot_id:selected,first:form.elements.first.value,second:form.elements.second.value,hypothetical_revision:revision()});
        const data=await request(`/api/history/compare?${query}`,{signal:controller.signal});
        if(ticket!==sequence)return;
        render(data);results.setAttribute('aria-busy','false');results.classList.remove('history-stale');
      } catch(e) {if(ticket===sequence && e.name!=='AbortError'){error.textContent=e.message;results.setAttribute('aria-busy','false');}}
    }
    function showSnapshots(rebuild=true) {
      const options=root.querySelector('[data-snapshot-options]');if(!options)return;
      const current=catalog.snapshots.find(s=>s.id===selected);
      root.querySelector('[data-cache-summary]').textContent=`Selected dataset coverage: ${current.coverage.map(c=>c.join(' to ')).join('; ')}. Latest observation: ${current.latest_observation||'none'}.`;
      if(!rebuild)return;
      options.replaceChildren(element('legend','Snapshot · an open comparison keeps this version'));
      catalog.snapshots.forEach(s=>{const label=element('label',undefined,'history-option'), input=element('input');input.type='radio';input.name='snapshot';input.value=s.id;input.checked=s.id===selected;input.addEventListener('change',()=>{monthLoader?.cancel();monthStatus('');selected=s.id;showSnapshots(false);invalidate();refreshAvailability();compareDates();});label.append(input,element('span',`${s.label} · ${s.coverage.map(c=>c.join(' to ')).join('; ')} · ${s.row_count} rows · latest observation ${s.latest_observation||'none'} · saved ${s.created_at}`));options.append(label);});
    }
    form.addEventListener('submit',e=>{e.preventDefault();if(form.reportValidity())compareDates(true);});
    form.addEventListener('input',invalidate);
    root.querySelector('[data-reset-history]').addEventListener('click',()=>{monthLoader?.cancel();monthStatus('');form.reset();root.querySelector('[name="maturity_scale"][value="log"]').checked=true;selected=lesson?bundled:catalog.viewer_snapshot_id;datePicker.sync();refreshAvailability();root.querySelector('[value="observed"]')?.click();showSnapshots();compareDates();});
    root.querySelector('[data-missing-date]')?.addEventListener('click',()=>{monthLoader.cancel();monthStatus('');selected=bundled;form.elements.first.value=catalog.example_defaults.missing_date;form.elements.second.value=catalog.example_defaults.second;const recent=root.querySelector('[name="history_sample"][value="recent"]');if(recent)recent.checked=true;datePicker.sync();refreshAvailability();compareDates();});
    const samples=root.querySelectorAll('[name="history_sample"]');
    samples.forEach(input=>{input.disabled=true;input.addEventListener('change',()=>{
      monthLoader.cancel();monthStatus('');
      const reference=input.value==='series-introduction', defaults=reference?catalog.reference_defaults:catalog.example_defaults;
      selected=reference?catalog.reference_snapshot_id:bundled;
      form.elements.first.value=defaults.first;form.elements.second.value=defaults.second;
      datePicker.sync();refreshAvailability();compareDates();
    });});
    root.querySelectorAll('[name="revision"]').forEach(r=>r.addEventListener('change',()=>{invalidate();compareDates(true);}));
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
    root.querySelector('[data-use-refreshed]')?.addEventListener('click',()=>{monthLoader?.cancel();monthStatus('');selected=refreshed;refreshAvailability();showSnapshots();compareDates();});
    request('/api/history/snapshots').then(data=>{
      catalog=data;bundled=data.bundled_snapshot_id;selected=lesson?bundled:data.viewer_snapshot_id;samples.forEach(input=>input.disabled=false);refreshAvailability();showSnapshots();
      if(refreshForm){['start_year','end_year'].forEach(name=>{refreshForm.elements[name].value=data.default_year;refreshForm.elements[name].max=data.current_year;});}
      compareDates();
    }).catch(e=>{error.textContent=e.message;results.setAttribute('aria-busy','false');});
  });
})();
