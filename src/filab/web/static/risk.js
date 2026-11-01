'use strict';
(() => {
  const root = $('[data-risk]');
  const dollars = value => money(Math.abs(value) < .005 ? 0 : value);
  if (!root) return;
  const form = $('form', root), exportButton = $('[data-risk-export]', root);
  const fileInput = $('[data-risk-import]', root), fileError = $('[data-file-error]', root);
  const state = $('[data-risk-state]', root);
  let validInputs = null, importSequence = 0;
  const rateFields = ['ytm', 'coupon_rate', 'comparison_coupon_rate'];
  const dateFields = ['issue_date', 'settlement_date', 'maturity_date', 'comparison_maturity_date'];
  const numberFields = ['face_value', ...rateFields, 'maturity_years', 'comparison_maturity_years'];
  function inputs() {
    const result = {mode:choiceValue('mode', root), frequency:Number(choiceValue('frequency', root)), shock_bp:Number(choiceValue('shock_bp', root))};
    for (const name of numberFields) result[name] = Number(form.elements.namedItem(name).value) / (rateFields.includes(name) ? 100 : 1);
    for (const name of dateFields) result[name] = form.elements.namedItem(name).value;
    return result;
  }
  function invalidate() {
    validInputs = null; exportButton.disabled = true; importSequence++;
    state.textContent = 'Inputs changed. Previous results remain visible until this comparison is validated.';
  }
  // Invalidate even in the debounce window, on reset, or while an import is validating.
  form.addEventListener('input', invalidate); form.addEventListener('change', invalidate);
  $('.reset', root).addEventListener('click', () => { invalidate(); fileInput.value=''; fileError.textContent=''; $('[data-file-status]', root).textContent=''; });
  function update() {
    const dated = choiceValue('mode', root) === 'dated';
    for (const [selector, visible] of [['[data-risk-dated]', dated], ['[data-risk-regular]', !dated]]) {
      $$(selector, root).forEach(section => { section.hidden = !visible; $$('input', section).forEach(input => input.disabled = !visible); });
    }
    $('[data-risk-convention]', root).textContent = dated
      ? 'Fixed settlement. Actual/Actual coupon accrual; simple first fractional period, compound later periods. Regular maturity-anchored dates; settlement on a coupon date is after payment. No stubs, holidays, settlement lags, or ex-coupon rules. Dirty-price numerical risk; no Macaulay conversion.'
      : 'Just after a coupon payment; regular whole periods, matching coupon/compounding frequencies. Clean = dirty, no accrued interest. Analytical yield risk. Hypothetical bonds; no time passes.';
  }
  function chart(node, title, curves) {
    drawLines(node, {title, curves, percent_x:false, x_unit:'bp', percent_y:true, x_label:'Yield change (basis points)', y_label:'Immediate price change (%)', reference_x:0, reference_y:0});
  }
  function weightsChart(bond) {
    const target=$('[data-risk-weights-chart]',root), W=700,H=230,L=55,R=20,T=30,B=45;
    const flows=bond.cashflows, last=flows.at(-1).time_years;
    const x=t=>L+t/last*(W-L-R), y=w=>H-B-w*(H-T-B);
    const svg=svgElement('svg',{viewBox:`0 0 ${W} ${H}`,role:'group','aria-label':'Bond A: present value weights by payment time. Focus a bar or read the table.'});
    for(const fraction of [0,.5,1]) {svg.append(svgElement('line',{x1:L,x2:W-R,y1:y(fraction),y2:y(fraction),stroke:'#e0e6db'}));svg.append(svgElement('text',{x:L-6,y:y(fraction)+4,'text-anchor':'end'},percent(fraction,0)));}
    for(const f of flows) {const bar=svgElement('rect',{x:x(f.time_years)-Math.min(6,(W-L-R)/flows.length/3),y:y(f.weight),width:Math.min(12,(W-L-R)/flows.length/1.5),height:(H-B)-y(f.weight),fill:colors[0],tabindex:0,role:'img','aria-label':`${f.date||f.time_years+' years'}: ${percent(f.weight,4)} of present value`});bar.append(svgElement('title',{},bar.getAttribute('aria-label')));svg.append(bar);}
    for(let i=0;i<=4;i++) svg.append(svgElement('text',{x:x(last*i/4),y:H-B+20,'text-anchor':'middle'},(last*i/4).toFixed(1)));
    svg.append(svgElement('text',{x:L,y:15,class:'axis-label'},'Share of present value'));
    svg.append(svgElement('text',{x:W/2,y:H-5,'text-anchor':'middle',class:'axis-label'},bond.risk.macaulay_duration===null?'Coupon-period years from settlement':'Years from valuation'));
    if(bond.risk.macaulay_duration!==null)svg.append(svgElement('line',{x1:x(bond.risk.macaulay_duration),x2:x(bond.risk.macaulay_duration),y1:T,y2:H-B,stroke:colors[1],'stroke-dasharray':'4 3'}));
    target.replaceChildren(svg);
  }
  function render(data) {
    const [a,b] = data.bonds;
    validInputs=inputs(); exportButton.disabled=false;
    state.textContent='Current inputs validated. All results below match this comparison.';
    $('[data-risk-duration]',root).textContent=a.risk.modified_duration.toFixed(4);
    $('[data-risk-dv01]',root).textContent=dollars(a.risk.dv01);
    $('[data-risk-convexity]',root).textContent=a.risk.convexity.toFixed(4);
    const measures=[['Dirty price','price',dollars],['Macaulay duration · years','macaulay_duration',v=>v===null?'Not reported for dated model':v.toFixed(4)],['Modified duration · years','modified_duration',v=>v.toFixed(6)],['Dollar duration · $ / unit yield','dollar_duration',dollars],['DV01 · $ / bp','dv01',dollars],['Convexity · years²','convexity',v=>v.toFixed(6)]];
    table($('[data-risk-summary]',root),['Measure','Bond A','Bond B'],[
      ...measures.map(([label,key,format])=>[label,...data.bonds.map(bond=>format(bond.risk[key]))]),
      ['Clean price',dollars(a.clean_price),dollars(b.clean_price)],['Accrued interest',dollars(a.accrued_interest),dollars(b.accrued_interest)]
    ]);
    chart($('[data-risk-comparison-chart]',root),'Exact immediate price changes',data.bonds.map(bond=>({label:bond.label,points:bond.points.map(p=>({x:p.shock_bp,y:p.exact_percent})),marker:{x:data.shock_bp,y:bond.selected.exact_percent}})));
    chart($('[data-risk-approximation-chart]',root),'Bond A approximation error', [['Exact','exact_percent'],['Duration','duration_percent'],['Duration + convexity','convexity_percent']].map(([label,key])=>({label,points:a.points.map(p=>({x:p.shock_bp,y:p[key]})),marker:{x:data.shock_bp,y:a.selected[key]}})));
    $('[data-risk-insight]',root).textContent=`At ${data.shock_bp>0?'+':''}${data.shock_bp} bp, A changes ${percent(a.selected.exact_percent)} and B changes ${percent(b.selected.exact_percent)}. Each percentage uses its own starting price. Compare timing and coupon weights to explain the difference.`;
    table($('[data-risk-selected]',root),['Bond','Initial dirty','Shocked dirty','Exact Δ $','Exact Δ %'],data.bonds.map(bond=>[bond.label,dollars(bond.risk.price),dollars(bond.selected.exact_price),dollars(bond.selected.exact_change),percent(bond.selected.exact_percent,4)]));
    weightsChart(a);
    $('[data-risk-weights-note]',root).textContent=data.mode==='regular'?'Orange dashed line: Macaulay duration, the weighted average payment time. Weights sum to 100%; weighted-time contributions sum to duration.':'Dates are contractual and unadjusted. The time column measures remaining coupon periods / frequency, not Actual/365 calendar years. No textbook Macaulay duration is asserted.';
    table($('[data-risk-weights]',root),[...(data.mode==='regular'?['Years']:['Payment date','Coupon-period years']),'Payment','Present value','PV weight',...(data.mode==='regular'?['Weight × years']:[])],a.cashflows.map(f=>[...(data.mode==='regular'?[f.time_years.toFixed(4)]:[f.date,f.time_years.toFixed(4)]),dollars(f.amount),dollars(f.present_value),percent(f.weight,4),...(data.mode==='regular'?[f.weighted_time.toFixed(6)]:[])]));
    table($('[data-risk-shocks]',root),['Bond','Shock bp','Exact Δ $','Exact Δ %','Duration Δ $','Duration Δ %','D+C Δ $','D+C Δ %','Duration error $','Error pp','D+C error $','Error pp'],data.bonds.flatMap(bond=>bond.scenarios.map(p=>[bond.label,p.shock_bp.toFixed(0),dollars(p.exact_change),percent(p.exact_percent,4),dollars(p.duration_change),percent(p.duration_percent,4),dollars(p.convexity_change),percent(p.convexity_percent,4),dollars(p.duration_error), (p.duration_error_percent*100).toFixed(6),dollars(p.convexity_error),(p.convexity_error_percent*100).toFixed(6)])));
    table($('[data-risk-convergence]',root),['Bond','Method / bump','Modified duration','Convexity'],data.bonds.flatMap(bond=>[
      ...(data.mode==='regular'?[[bond.label,'Analytical',bond.risk.modified_duration.toFixed(8),bond.risk.convexity.toFixed(8)]]:[]),
      ...bond.convergence.map(r=>[bond.label,`±${r.bump*10000} bp`,r.modified_duration.toFixed(8),r.convexity.toFixed(8)])
    ]));
  }
  const calculate=bindCalculator(root,'/api/risk',inputs,render,update);
  exportButton.addEventListener('click',()=>{
    if(!validInputs)return;
    const study={schema_version:1,kind:'filab-bond-risk',conventions:'nominal-yield-risk-v1',inputs:validInputs};
    const url=URL.createObjectURL(new Blob([JSON.stringify(study,null,2)+'\n'],{type:'application/json'}));
    const link=element('a');link.href=url;link.download='filab-bond-risk-v1.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    $('[data-file-status]',root).textContent='Comparison exported. Includes both bonds, dates, yield, frequency, face value, shock, and convention version.';
  });
  fileInput.addEventListener('change',async()=>{
    const file=fileInput.files[0];if(!file)return;
    const token=++importSequence;fileError.textContent='';
    try {
      if(file.size>30000)throw new Error('Choose a comparison JSON file smaller than 30 KB.');
      const study=JSON.parse(await file.text());
      const response=await fetch('/api/risk-study',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(study)});
      const result=await response.json();if(token!==importSequence)return;
      if(!response.ok)throw new Error('The file has unsupported inputs or conventions. Export a valid comparison from this tool.');
      const data=result.study.inputs;
      // Radio choices, integer-year sliders and bounded inputs must all be representable.
      if(!$(`input[name="shock_bp"][value="${data.shock_bp}"]`,root) || numberFields.some(name=>{const v=data[name]*(rateFields.includes(name)?100:1), input=form.elements.namedItem(name);return v<Number(input.min)||v>Number(input.max)||Math.abs((v-Number(input.min))/Number(input.step)-Math.round((v-Number(input.min))/Number(input.step)))>1e-7;}))throw new Error('This comparison uses values outside the visible controls.');
      invalidate();
      for(const name of ['mode','frequency','shock_bp'])setChoice(name,String(data[name]),root);
      for(const name of numberFields){const input=form.elements.namedItem(name);input.value=Number((data[name]*(rateFields.includes(name)?100:1)).toPrecision(12));const slider=$(`[data-pair="${input.id}"]`,root);if(slider)slider.value=input.value;}
      for(const name of dateFields)form.elements.namedItem(name).value=data[name];
      update(); await calculate();
      $('[data-file-status]',root).textContent='Comparison imported. Both bonds and conventions restored.';
    } catch(error) {if(token===importSequence)fileError.textContent=error instanceof SyntaxError?'This file is not valid JSON. Your comparison is unchanged.':error.message;}
    finally {fileInput.value='';}
  });
})();
