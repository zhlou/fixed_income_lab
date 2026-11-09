/* Curves and prices are calculated in Python. Imported history stays in this browser. */
(() => {
  const money = value => value === null ? 'Unavailable' : `$${value.toFixed(2)}`;
  const rate = value => value === null ? '—' : `${(value * 100).toFixed(4)}%`;
  const factor = value => value === null ? '—' : value.toFixed(6);
  async function request(path, body, options={}) {
    const response = await fetch(`/api/curves/${path}`, {...options, ...(body === undefined ? {} : {
      method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)
    })});
    const data = await response.json();
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Check the highlighted inputs and supported ranges.');
    return data;
  }
  function grid(headers, rows) {
    const wrapper=element('div',undefined,'table-scroll'), result=element('table'), head=element('thead'), tr=element('tr'), body=element('tbody');
    wrapper.tabIndex=0;wrapper.setAttribute('role','region');wrapper.setAttribute('aria-label',headers.join(', '));
    headers.forEach(label=>{const th=element('th',label);th.scope='col';tr.append(th);});head.append(tr);
    rows.forEach(values=>{const row=element('tr');values.forEach((value,index)=>{const cell=element(index?'td':'th',String(value));if(!index)cell.scope='row';row.append(cell);});body.append(row);});
    result.append(head,body);wrapper.append(result);return wrapper;
  }
  function card(title) {const node=element('section',undefined,'card');node.append(element('h2',title));return node;}
  function metrics(values) {
    const node=element('div',undefined,'metrics');
    values.forEach(([label,value])=>{const cell=element('div',undefined,'metric');cell.append(element('span',label),element('strong',value));node.append(cell);});return node;
  }
  function chart(container, series, label, minimumStep) {
    container.replaceChildren();
    const points=series.flatMap(s=>s.points);
    if(!points.length){container.append(element('p','No data'));return;}
    const width=Math.max(260,container.clientWidth),height=300,left=62,right=width-22,top=70,bottom=250;
    const maxX=Math.max(...points.map(p=>p[0])),minY=Math.min(...points.map(p=>p[1])),maxY=Math.max(...points.map(p=>p[1]));
    const padding=minY===maxY ? minimumStep : 0;
    const axis=roundedAxis(minY-padding,maxY+padding,minimumStep);
    const x=v=>left+v/maxX*(right-left),y=v=>bottom-(v-axis.minimum)/(axis.maximum-axis.minimum)*(bottom-top);
    const svg=svgElement('svg',{viewBox:`0 0 ${width} ${height}`,role:'img','aria-label':`${label}. Linear maturity spacing in years. Values follow in the table.`});
    svg.append(svgElement('text',{x:0,y:16,'font-size':12},label));
    for(const v of axis.ticks){
      svg.append(svgElement('line',{x1:left,x2:right,y1:y(v),y2:y(v),stroke:'#ddd'}),svgElement('text',{x:left-6,y:y(v)+4,'text-anchor':'end','font-size':11,'data-axis-tick':'y'},v.toFixed(3)));
    }
    [0,.25,.5,.75,1].forEach(part=>svg.append(svgElement('text',{x:x(maxX*part),y:272,'text-anchor':'middle','font-size':11},`${(maxX*part).toFixed(1)}y`)));
    series.forEach((s,index)=>{
      const color=colors[index%colors.length];
      svg.append(svgElement('text',{x:0,y:35+index*17,fill:color,'font-size':12},s.name));
      let previous=null;
      s.points.forEach(([t,v])=>{
        if(previous)svg.append(svgElement('line',{x1:x(previous[0]),y1:y(previous[1]),x2:x(t),y2:y(v),stroke:color,'stroke-width':2,'stroke-dasharray':index?'5 3':'none'}));
        const point=svgElement('circle',{cx:x(t),cy:y(v),r:3,fill:color,tabindex:0,'aria-label':`${s.name}, ${t} years, ${v.toFixed(6)}`});
        point.append(svgElement('title',{},`${t} years · ${v.toFixed(6)}`));svg.append(point);previous=[t,v];
      });
    });
    svg.append(svgElement('text',{x:(left+right)/2,y:295,'text-anchor':'middle','font-size':12},'Remaining maturity · linear years'));container.append(svg);
  }
  document.querySelectorAll('[data-curve-synthetic]').forEach(root=>{
    const form=root.querySelector('form'),results=root.querySelector('[data-curve-results]'),error=root.querySelector('[data-curve-error]');
    let epoch=0,controller,last;
    function invalidate(){epoch++;controller?.abort();results.classList.add('curve-stale');results.setAttribute('aria-busy','false');}
    function render(data){
      last=data;results.replaceChildren();
      const pricing=root.dataset.experiment==='curve-pricing';
      results.append(metrics(pricing ? [['4% note price',money(data.initial_price)],['Recovered D(2)',factor(data.nodes[4][1])],['6% calibration price',money(data.calibration_price)]] : [['Initial 4% note price',money(data.initial_price)],['Remaining note price',money(data.remaining_price)],['Payments received',money(data.cash_received)]]));
      const plot=card('Hypothetical discount factors'),canvas=element('div',undefined,'chart');plot.append(canvas);results.append(plot);
      chart(canvas,[{name:'Unchanged curve by remaining maturity',points:data.nodes}],'Discount factor · dollars today per $1',0.005);
      plot.append(element('p','Calculations interpolate linearly in log discount factors between the listed nodes. Chart lines connect the supplied nodes. D(0) = 1. Factors above one imply negative spot rates. Payments beyond the final node are outside this curve’s support.'));
      plot.append(grid(['Years','Discount factor'],data.nodes.map(([t,d])=>[t,factor(d)])));
      const payments=card('Remaining payments after settlement');payments.append(grid(['Years remaining','Payment','Discount factor','Present value'],data.cashflows.map(f=>[f.time_years,money(f.amount),factor(f.discount_factor),money(f.present_value)])));
      if(!data.cashflows.length)payments.append(element('p','All payments have arrived. Remaining bond value is $0.00.'));
      if(!pricing)payments.append(element('p',`Price change ${money(data.price_change)} · ending wealth ${money(data.ending_wealth)} with received payments held at zero interest.`));
      if(!pricing)payments.append(element('p',`Six-month forward beginning in six months · ${rate(data.forward_rate)} annual nominal semiannual. Implied by today’s discount factors.`));
      results.append(payments);
    }
    async function calculate(){
      invalidate();const current=epoch;controller=new AbortController();error.textContent='';results.setAttribute('aria-busy','true');
      try{
        const data=await request('synthetic',{calibration_price:Number(form.elements.calibration_price.value),horizon:Number(form.elements.horizon.value)},{signal:controller.signal});
        if(current!==epoch)return;render(data);results.classList.remove('curve-stale');
      }catch(e){if(current===epoch&&e.name!=='AbortError')error.textContent=e.message;}
      finally{if(current===epoch)results.setAttribute('aria-busy','false');}
    }
    form.addEventListener('input',invalidate);
    form.addEventListener('change',event=>{if(event.target.name==='horizon')form.requestSubmit();});
    form.elements.calibration_price.addEventListener('change',()=>{const input=form.elements.calibration_price;if(input.value&&Number.isFinite(input.valueAsNumber||Number(input.value)))input.value=Number(input.value).toFixed(2);});
    form.addEventListener('submit',event=>{event.preventDefault();calculate();});
    root.querySelector('[data-curve-reset]').addEventListener('click',()=>{form.reset();calculate();});
    window.addEventListener('resize',()=>{if(last)render(last);});calculate();
  });
  document.querySelectorAll('input[name="curve_mode"]').forEach(input=>input.addEventListener('change',()=>{
    document.querySelectorAll('[data-curve-panel]').forEach(panel=>panel.hidden=panel.dataset.curvePanel!==input.value);
    window.dispatchEvent(new Event('resize'));
  }));
  document.querySelectorAll('[data-curve-history]').forEach(root=>{
    const form=root.querySelector('form'),results=root.querySelector('[data-fed-results]'),error=root.querySelector('[data-fed-error]');
    const status=root.querySelector('[data-fed-import-status]'),options=root.querySelector('[data-fed-datasets]'),importer=root.querySelector('[data-fed-import]'),exporter=root.querySelector('[data-fed-export]');
    const dates=new window.FilabHistoryDates(root);
    let db,sample,selected,metadata=[],epoch=0,selectionEpoch=0,controller,last;
    function invalidate(){epoch++;controller?.abort();results.classList.add('curve-stale');results.setAttribute('aria-busy','false');}
    function get(store,key){return new Promise((resolve,reject)=>{const tx=db.transaction(store),req=tx.objectStore(store).get(key);req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);});}
    function open(){return new Promise((resolve,reject)=>{
      const req=indexedDB.open('filab-fed-curves',1);
      req.onupgradeneeded=()=>['metadata','snapshots','raw'].forEach(name=>req.result.createObjectStore(name));
      req.onerror=()=>reject(req.error);req.onblocked=()=>reject(new Error('Close other tabs using Fed history, then reload.'));
      req.onsuccess=()=>{db=req.result;db.onversionchange=()=>{db.close();db=null;};resolve();};
    });}
    function persist(snapshot,raw){return new Promise((resolve,reject)=>{
      const tx=db.transaction(['metadata','snapshots','raw'],'readwrite');
      const meta={id:snapshot.id,imported_at:new Date().toISOString(),count:snapshot.rows.length,coverage:snapshot.coverage};
      tx.objectStore('metadata').put(meta,snapshot.id);tx.objectStore('snapshots').put(snapshot,snapshot.id);tx.objectStore('raw').put(raw,snapshot.id);
      tx.oncomplete=()=>resolve(meta);tx.onerror=tx.onabort=()=>reject(tx.error||new Error('Browser storage is unavailable or full.'));
    });}
    function availability(){dates.setAvailability({snapshot_id:selected.id,coverage:selected.coverage,published_dates:selected.rows.filter(r=>r.values[0]!==null).map(r=>r.date)});}
    async function select(id){
      invalidate();const current=++selectionEpoch;dates.clearAvailability();exporter.disabled=true;
      try{
        const snapshot=id===sample.id?sample:await get('snapshots',id);
        if(current!==selectionEpoch)return;
        if(!snapshot)throw new Error('Saved dataset is unavailable.');
        selected=snapshot;availability();exporter.disabled=id===sample.id;
        status.textContent='Dataset selected. Compare dates to replace the displayed result.';
      }catch(e){if(current===selectionEpoch){error.textContent=e.message;availability();exporter.disabled=selected.id===sample.id;catalog();}}
    }
    function catalog(){
      options.replaceChildren(element('legend','Dataset version'));
      [{id:sample.id,label:'Bundled October 29–30, 2026 sample · includes source-check dates'},...metadata.map(m=>({id:m.id,label:`${m.id.slice(0,12)} · ${m.count} rows · imported ${m.imported_at}`}))].forEach(item=>{
        const label=element('label',undefined,'history-option'),input=element('input');input.type='radio';input.name='fed_dataset';input.value=item.id;input.checked=item.id===selected.id;
        input.addEventListener('change',()=>select(item.id));label.append(input,document.createTextNode(item.label));options.append(label);
      });
    }
    function render(data){
      last=data;results.replaceChildren();
      const source=card('Selected result and source');
      source.append(element('p',`Dataset ${data.snapshot_id} · ${data.first.date} versus ${data.second.date}.`));
      source.append(element('p',data.convention));
      const meta=metadata.find(m=>m.id===data.snapshot_id);
      source.append(element('p',meta?`Imported ${meta.imported_at}. Source acquisition time unknown.`:`Bundled excerpt · source acquired ${sample.source.retrieved_at}. Parent SHA-256 ${sample.source.parent_sha256}.`));
      [data.first,data.second].forEach(d=>source.append(element('p',`${d.date} · ${d.status}${d.supported_range?` · published maturity range ${d.supported_range.join('–')} years`:''}${d.reconstruction_matches===false?' · parameter reconstruction differs from published yields beyond rounding precision':''}`)));
      results.append(source);
      const plot=card('Continuously compounded zero yields'),canvas=element('div',undefined,'chart');plot.append(canvas);results.append(plot);
      chart(canvas,[data.first,data.second].map(d=>({name:d.date,points:d.nodes.map(n=>[n.maturity,n.zero_rate*100])})),'Annual zero yield (%)',0.001);
      plot.append(element('p','Dots show published nodes. Connecting lines guide the eye. Discount factors in the table use published zero yields.'));
      plot.append(grid(['Years',data.first.date,data.second.date,'Zero-yield change (bp)'],data.changes.map(n=>[n.maturity,rate(n.first),rate(n.second),n.change_bp===null?'—':n.change_bp.toFixed(4)])));
      [data.first,data.second].forEach(d=>plot.append(element('h3',d.date),grid(['Years','Zero rate','Discount factor','Instantaneous forward','Par yield'],d.nodes.map(n=>[n.maturity,rate(n.zero_rate),factor(n.discount_factor),rate(n.forward_rate),rate(n.par_rate)]))));
      const value=data.valuation,payments=card('Model-derived synthetic note valuation');
      payments.append(element('p',value.status));
      payments.append(metrics([['Dirty price per $100',money(value.dirty_price)],['Accrued interest',value.accrued_interest==null?'—':money(value.accrued_interest)],['Clean price per $100',money(value.clean_price)]]));
      payments.append(element('p',data.short_end));
      if(value.reproduction_error!==undefined)payments.append(element('p',`Maximum parameter reproduction error ${(value.reproduction_error*10000).toFixed(4)} bp.`));
      payments.append(grid(['Payment date','Years remaining','Amount','Coverage','Discount factor','Present value'],value.cashflows.map(f=>[f.payment_date,f.time_years.toFixed(6),money(f.amount),f.supported?'Within range':'Unsupported',factor(f.discount_factor),money(f.present_value)])));
      results.append(payments);
    }
    async function compare(){
      if(!selected)return;invalidate();const current=epoch;controller=new AbortController();error.textContent='';results.setAttribute('aria-busy','true');
      const rows=new Map(selected.rows.map(r=>[r.date,r]));
      try{
        const data=await request('compare',{snapshot_id:selected.id,first:rows.get(form.elements.first.value)||null,second:rows.get(form.elements.second.value)||null,first_date:form.elements.first.value,second_date:form.elements.second.value,valuation:form.elements.valuation.value,maturity_years:Number(form.elements.maturity_years.value),coupon_rate:Number(form.elements.coupon_rate.value)/100,age_months:Number(form.elements.age_months.value)},{signal:controller.signal});
        if(current!==epoch)return;render(data);results.classList.remove('curve-stale');
      }catch(e){if(current===epoch&&e.name!=='AbortError')error.textContent=e.message;}
      finally{if(current===epoch)results.setAttribute('aria-busy','false');}
    }
    form.addEventListener('input',invalidate);form.addEventListener('submit',event=>{event.preventDefault();compare();});
    root.querySelector('[data-fed-reset]').addEventListener('click',async()=>{form.reset();await select(sample.id);catalog();compare();});
    importer.addEventListener('change',async()=>{
      const file=importer.files[0];if(!file)return;
      importer.disabled=true;status.textContent='Validating Fed CSV…';
      try{
        if(file.size>24000000)throw new Error('Fed CSV exceeds 24 MB.');
        if(!db)throw new Error('Browser storage is unavailable. Bundled dates remain readable.');
        const response=await fetch('/api/curves/normalize',{method:'POST',headers:{'Content-Type':'text/csv'},body:file});
        const snapshot=await response.json();if(!response.ok)throw new Error(snapshot.detail||'CSV validation failed.');
        const existing=metadata.find(m=>m.id===snapshot.id);
        if(existing){status.textContent='This exact CSV is already saved. Select its existing version below.';return;}
        const meta=await persist(snapshot,file);metadata.push(meta);catalog();status.textContent='Import saved. Select the new dataset version, then compare dates.';
      }catch(e){status.textContent=`Import failed. ${e.message}`;}
      finally{importer.disabled=false;importer.value='';}
    });
    exporter.addEventListener('click',async()=>{
      try{const raw=await get('raw',selected.id);if(!raw)throw new Error('Raw source unavailable.');const url=URL.createObjectURL(raw),a=element('a');a.href=url;a.download=`fed-${selected.id.slice(0,12)}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
      catch(e){status.textContent=e.message;}
    });
    window.addEventListener('resize',()=>{if(last)render(last);});
    (async()=>{
      try{
        sample=await request('bundled');selected=sample;
        try{await open();metadata=await new Promise((resolve,reject)=>{const req=db.transaction('metadata').objectStore('metadata').getAll();req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);});}
        catch(e){status.textContent=`Browser storage unavailable. ${e.message}`;}
        catalog();availability();compare();
      }catch(e){error.textContent=e.message;results.setAttribute('aria-busy','false');}
    })();
  });
})();
