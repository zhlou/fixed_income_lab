'use strict';
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
const money = value => new Intl.NumberFormat('en-US', {style:'currency', currency:'USD', maximumFractionDigits:2}).format(value);
const percent = (value, digits=2) => {const rounded=(value * 100).toFixed(digits);return `${Number(rounded)===0?(0).toFixed(digits):rounded}%`;};
const colors = ['#356b58', '#bb6a43', '#527d9c'];
let tooltipSequence = 0;
function element(tag, text, className) { const node=document.createElement(tag); if(text !== undefined) node.textContent=text; if(className) node.className=className; return node; }
function svgElement(tag, attributes={}, text) { const node=document.createElementNS('http://www.w3.org/2000/svg',tag); for(const [key,value] of Object.entries(attributes)) node.setAttribute(key,String(value)); if(text !== undefined) node.textContent=text; return node; }
function niceAxis(minimum,maximum,percentage=false){
  // Choose a 1/2/5 decade step, with at least 5 displayed units.
  // Sub-dollar charts use cents, and percentage charts use percentage points.
  const scale=percentage?100:(Math.max(Math.abs(minimum),Math.abs(maximum))<1?100:1);
  const low=minimum*scale,high=maximum*scale;
  const rough=Math.max((high-low)/5,percentage?0.05:5),decade=10**Math.floor(Math.log10(rough));
  const step=[1,2,5,10].find(value=>value*decade>=rough-1e-10)*decade;
  const start=Math.floor(low/step),end=Math.max(start+1,Math.ceil(high/step));
  const ticks=Array.from({length:end-start+1},(_,i)=>Number(((start+i)*step/scale).toPrecision(12)));
  return {minimum:ticks[0],maximum:ticks.at(-1),step:step/scale,ticks};
}
function table(container, headers, rows, totals) {
  const result=element('table'), head=element('thead'), tr=element('tr');
  for(const label of headers){const th=element('th',label); th.scope='col'; tr.append(th);} head.append(tr); result.append(head);
  const body=element('tbody'); for(const row of rows){const line=element('tr'); for(const value of row)line.append(element('td',value));body.append(line);}result.append(body);
  if(totals){const foot=element('tfoot'), line=element('tr');totals.forEach(value=>line.append(element('td',value)));foot.append(line);result.append(foot);}
  container.replaceChildren(result);
}
function legend(container, entries){const node=element('div',undefined,'legend');for(const [label,color,dashed] of entries){const item=element('span'), swatch=element('i');if(dashed){swatch.style.borderTop=`2px dashed ${color}`;swatch.style.height='0';}else swatch.style.background=color;item.append(swatch,document.createTextNode(label));node.append(item);}container.append(node);}
function drawLines(container, model, compact=false){
  const W=700,H=compact?280:325,L=60,R=18,T=30,B=58, pw=W-L-R, ph=H-T-B;
  const points=model.curves.flatMap(curve=>curve.points), xs=points.map(p=>p.x), ys=points.map(p=>p.y);
  const xmin=Math.min(...xs),xmax=Math.max(...xs);let ymin=Math.min(...ys),ymax=Math.max(...ys);
  const pad=(ymax-ymin || 1)*0.07;
  const axis=model.y_domain?niceAxis(...model.y_domain,model.percent_y):niceAxis(!model.percent_y&&ymin>=0?Math.max(0,ymin-pad):ymin-pad,ymax+pad,model.percent_y);
  ymin=axis.minimum;ymax=axis.maximum;
  const x=value=>L+(value-xmin)/(xmax-xmin || 1)*pw, y=value=>T+(ymax-value)/(ymax-ymin)*ph;
  const svg=svgElement('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':`${model.title}. ${model.x_label}. ${model.y_label}. Use left and right arrow keys to inspect values.`,tabindex:'0'});
  svg.append(svgElement('title',{},model.title));svg.append(svgElement('desc',{},'Line chart with numerical values available in the accompanying tables.'));
  for(const value of axis.ticks){const py=y(value);svg.append(svgElement('line',{x1:L,x2:W-R,y1:py,y2:py,stroke:'#e8ede2'}));svg.append(svgElement('text',{x:L-9,y:py+3,'text-anchor':'end','data-axis-tick':'y'},model.percent_y?percent(value,axis.step<0.01?2:0):value.toLocaleString('en-US',{maximumFractionDigits:2})));}
  for(let i=0;i<=5;i++){const value=xmin+(xmax-xmin)*i/5;svg.append(svgElement('text',{x:x(value),y:H-B+21,'text-anchor':'middle'},model.percent_x===false?value.toFixed(model.x_unit==='days'?0:1):percent(value,1)));}
  svg.append(svgElement('text',{x:L,y:14,class:'axis-label'},model.y_label));svg.append(svgElement('text',{x:L+pw/2,y:H-11,'text-anchor':'middle',class:'axis-label'},model.x_label));
  if(model.reference_y>=ymin&&model.reference_y<=ymax)svg.append(svgElement('line',{x1:L,x2:W-R,y1:y(model.reference_y),y2:y(model.reference_y),stroke:'#a2ae96','stroke-dasharray':'4 4'}));
  if(model.reference_x>=xmin&&model.reference_x<=xmax)svg.append(svgElement('line',{x1:x(model.reference_x),x2:x(model.reference_x),y1:T,y2:H-B,stroke:'#b3bfaa','stroke-dasharray':'3 5'}));
  const curveColor=(curve,i)=>curve.baseline?'#98a89d':('baseline' in curve?colors[0]:colors[i%colors.length]);
  model.curves.forEach((curve,i)=>{
    svg.append(svgElement('polyline',{points:curve.points.map(p=>`${x(p.x)},${y(p.y)}`).join(' '),fill:'none',stroke:curveColor(curve,i),'stroke-width':curve.baseline?2:2.8,'stroke-dasharray':curve.baseline?'6 5':'none','stroke-linejoin':'round','data-curve':curve.baseline?'baseline':'selected'}));
    if(curve.marker)svg.append(svgElement('circle',{cx:x(curve.marker.x),cy:y(curve.marker.y),r:curve.baseline?4:5,fill:curveColor(curve,i),stroke:'white','stroke-width':1.5,'data-selected-marker':curve.baseline?'baseline':'selected'}));
  });
  const hover=svgElement('line',{x1:L,x2:L,y1:T,y2:H-B,stroke:'#62765d','stroke-dasharray':'2 3',visibility:'hidden'});svg.append(hover);
  const tooltip=element('div',undefined,'chart-tooltip');tooltip.hidden=true;
  const readout=element('p','Hover over the chart or focus it and use ← → to inspect values.','tiny-note');readout.setAttribute('aria-live','polite');
  let selected=0;
  function inspect(index,announce=false){
    selected=Math.max(0,Math.min(model.curves[0].points.length-1,index));const point=model.curves[0].points[selected];
    const lines=[model.percent_x===false?`${point.x.toFixed(model.x_unit==='days'?0:2)} ${model.x_unit||'years'}`:`${model.x_label.startsWith('Annual coupon')?'Coupon':'YTM'} ${percent(point.x)}`];
    for(const curve of model.curves){const p=curve.points[selected];lines.push(`${curve.label}: ${model.percent_y?percent(p.y):p.y.toFixed(2)}`);}
    const px=x(point.x);hover.setAttribute('x1',px);hover.setAttribute('x2',px);hover.setAttribute('visibility','visible');tooltip.textContent=lines.join('\n');tooltip.hidden=false;
    tooltip.style.left=`${Math.min(66,Math.max(3,px/W*100+2))}%`;tooltip.style.top='28px';if(announce)readout.textContent=lines.join(' · ');
  }
  svg.addEventListener('pointermove',event=>{const box=svg.getBoundingClientRect();const value=xmin+((event.clientX-box.left)/box.width*W-L)/pw*(xmax-xmin);const index=model.curves[0].points.reduce((best,p,i,all)=>Math.abs(p.x-value)<Math.abs(all[best].x-value)?i:best,0);inspect(index);});
  svg.addEventListener('pointerleave',()=>{tooltip.hidden=true;hover.setAttribute('visibility','hidden');});
  svg.addEventListener('keydown',event=>{if(event.key==='ArrowRight'||event.key==='ArrowLeft'){event.preventDefault();inspect(selected+(event.key==='ArrowRight'?1:-1),true);}});
  container.replaceChildren(svg,tooltip);legend(container,model.curves.map((curve,i)=>[curve.label,curveColor(curve,i),curve.baseline]));if(!compact)container.append(readout);
}
function drawTimeline(container, flows, basics, compact=false){
  const W=700,L=70,R=30,T=25,plotHeight=compact?75:145,pw=W-L-R;
  const xMax=flows.at(-1).time_years || 0.5;
  const inset=Math.min(28,pw/(flows.length+1));
  const x=time=>L+inset+(pw-2*inset)*time/xMax;
  const width=Math.max(1,Math.min(23,(pw-2*inset)/Math.max(flows.length,1)*(basics?0.5:0.26)));
  const hasCoupons=flows.some(flow=>flow.coupon>0);
  const axisNumber=value=>new Intl.NumberFormat('en-US',{maximumFractionDigits:2}).format(value);
  container.replaceChildren();
  const tooltip=element('div',undefined,'chart-tooltip timeline-tooltip');
  tooltip.id=`timeline-tooltip-${++tooltipSequence}`;tooltip.setAttribute('role','tooltip');tooltip.hidden=true;
  let hovered=null,focused=null;
  function hideTooltip(){tooltip.hidden=true;$$('.timeline-bar',container).forEach(bar=>bar.removeAttribute('aria-describedby'));}
  function showTooltip(bar){
    tooltip.textContent=bar.getAttribute('aria-label');tooltip.hidden=false;
    $$('.timeline-bar',container).forEach(other=>other.removeAttribute('aria-describedby'));
    bar.setAttribute('aria-describedby',tooltip.id);
    const bounds=container.getBoundingClientRect(),anchor=bar.getBoundingClientRect();
    const left=anchor.left-bounds.left+anchor.width/2-tooltip.offsetWidth/2;
    const top=anchor.top-bounds.top-tooltip.offsetHeight-10;
    tooltip.style.left=`${Math.max(4,Math.min(bounds.width-tooltip.offsetWidth-4,left))}px`;
    tooltip.style.top=`${Math.max(4,Math.min(bounds.height-tooltip.offsetHeight-4,top))}px`;
  }
  function paymentBar(attributes,label,time,value){
    const bar=svgElement('rect',{...attributes,class:'timeline-bar',tabindex:0,role:'img',
      'data-value':value,'aria-label':`${label}\nAt ${time} years\n${money(value)}`});
    bar.addEventListener('pointerenter',()=>{hovered=bar;showTooltip(bar);});
    bar.addEventListener('pointerleave',()=>{hovered=null;if(focused)showTooltip(focused);else hideTooltip();});
    bar.addEventListener('focus',()=>{focused=bar;showTooltip(bar);});
    bar.addEventListener('blur',()=>{focused=null;if(hovered)showTooltip(hovered);else hideTooltip();});
    bar.addEventListener('keydown',event=>{if(event.key==='Escape'){event.preventDefault();hideTooltip();}});
    bar.addEventListener('pointerup',event=>{if(event.pointerType==='touch'){bar.focus({preventScroll:true});showTooltip(bar);}});
    return bar;
  }
  function panel(kind,title,color,showTimeAxis){
    const section=element('section',undefined,'timeline-panel');section.dataset.panel=kind;
    const heading=element('h3',title);section.append(heading);
    const field=kind==='coupons'?'coupon':'principal';
    const pvField=kind==='coupons'?'coupon_present_value':'principal_present_value';
    const axis=niceAxis(0,Math.max(...flows.map(f=>basics?f[field]:Math.max(f[field],f[pvField])))*1.2);
    const maximum=axis.maximum;
    const bottom=T+plotHeight,H=bottom+(showTimeAxis?48:12),y=value=>bottom-value/maximum*plotHeight;
    const svg=svgElement('svg',{viewBox:`0 0 ${W} ${H}`,role:'group','aria-label':`${title}. Separate dollar scale; shared time axis. ${basics?'Promised payments.':'Promised payments beside their present values.'} Hover or focus a bar for its value. Exact amounts in the payment table.`});
    svg.append(svgElement('title',{},title));
    for(const value of axis.ticks){svg.append(svgElement('line',{x1:L,x2:W-R,y1:y(value),y2:y(value),stroke:'#e8ede2'}));svg.append(svgElement('text',{x:L-9,y:y(value)+4,'text-anchor':'end','data-axis-tick':'y'},axisNumber(value)));}
    svg.append(svgElement('text',{x:L,y:13,class:'axis-label'},'Dollars · this panel’s scale'));
    for(let i=0;i<=4;i++){const time=xMax*i/4;svg.append(svgElement('line',{x1:x(time),x2:x(time),y1:T,y2:bottom,stroke:'#edf0e8','stroke-dasharray':'2 4'}));if(showTimeAxis)svg.append(svgElement('text',{x:x(time),y:bottom+21,'text-anchor':'middle'},axisNumber(time)));}
    flows.forEach(flow=>{
      if(!flow[field])return;
      const group=svgElement('g'),px=x(flow.time_years);
      const barX=basics?px-width/2:px-width-1;
      const paymentType=kind==='coupons'?'Coupon':'Principal';
      group.append(paymentBar({x:barX,y:y(flow[field]),width,height:bottom-y(flow[field]),fill:color,rx:1},`${paymentType} · future payment`,flow.time_years,flow[field]));
      if(!basics)group.append(paymentBar({x:px+1,y:y(flow[pvField]),width,height:bottom-y(flow[pvField]),fill:colors[2],rx:1},`${paymentType} · present value`,flow.time_years,flow[pvField]));
      svg.append(group);
    });
    if(showTimeAxis)svg.append(svgElement('text',{x:L+pw/2,y:H-5,'text-anchor':'middle',class:'axis-label'},'Years from valuation · shared timeline'));
    section.append(svg);legend(section,[[basics?'Promised payment':'Future payment',color],...(!basics?[['Present value',colors[2]]]:[])]);container.append(section);
  }
  if(hasCoupons)panel('coupons','Coupon payments',colors[0],false);
  panel('principal','Principal repayment',colors[1],true);
  const caption=hasCoupons?'Panels use different vertical scales; compare dollar amounts using the labels.': 'No periodic coupons: only principal is paid at maturity.';
  container.append(element('p',caption,'tiny-note timeline-caption'));
  container.append(tooltip);
}
function readForm(form){const data={};for(const [name,value] of new FormData(form)){data[name]=form.elements.namedItem(name)?.type==='date'||['instrument','convention','payment_type','mode','price_type'].includes(name)?value:Number(value);}return data;}
function choiceValue(name,root){return $(`input[name="${name}"]:checked`,root)?.value;}
function setChoice(name,value,root){$$(`input[name="${name}"]`,root).forEach(input=>input.checked=input.value===value);}
function disableChoice(name,disabled,root){$$(`input[name="${name}"]`,root).forEach(input=>input.disabled=disabled);}
function clearErrors(root){$$('[data-error-for]',root).forEach(node=>node.textContent='');$$('[aria-invalid]',root).forEach(node=>node.removeAttribute('aria-invalid'));const error=$('[data-error]',root);if(error)error.textContent='';}
function showErrors(root,error){const issues=Array.isArray(error.detail)?error.detail:[];for(const issue of issues){const field=issue.loc?.[issue.loc.length-1],label=$(`[data-error-for="${field}"]`,root),input=$(`[name="${field}"]`,root);if(label)label.textContent=issue.msg;if(input)input.setAttribute('aria-invalid','true');}const alert=$('[data-error]',root);if(alert)alert.textContent=issues.length?'Check the highlighted inputs. Results show the last valid calculation.':(error.message||'The Python server could not complete this calculation.');}
function bindControls(root){$$('[data-pair]',root).forEach(range=>{const number=$(`[id="${range.dataset.pair}"]`,root);range.addEventListener('input',()=>{number.value=range.value;});number.addEventListener('input',()=>{if(number.value!=='')range.value=number.value;});});}
function bindCalculator(root,url,getPayload,render,updateState=()=>{}){
  let timer,controller,sequence=0;const form=$('form',root);bindControls(root);
  async function calculate(){const id=++sequence;if(controller)controller.abort();controller=new AbortController();clearErrors(root);updateState();
    const invalid=$$('input[type="number"],input[type="date"]',form).find(input=>!input.disabled&&(!input.checkValidity()||input.value===''));
    if(invalid){root.setAttribute('aria-busy','false');showErrors(root,{detail:[{loc:['body',invalid.name],msg:invalid.validationMessage||'Enter a valid number.'}]});return;}
    root.setAttribute('aria-busy','true');
    try{const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(getPayload()),signal:controller.signal});const result=await response.json();if(id!==sequence)return;if(!response.ok){showErrors(root,result);return;}render(result);}
    catch(error){if(error.name!=='AbortError'&&id===sequence)showErrors(root,{message:'Cannot reach the Python server. Check that it is running, then change an input to retry.'});}
    finally{if(id===sequence)root.setAttribute('aria-busy','false');}
  }
  function schedule(){// Invalidate in-flight work immediately, including during the debounce window.
    sequence++;if(controller)controller.abort();clearTimeout(timer);timer=setTimeout(calculate,180);
  }
  form.addEventListener('submit',event=>{event.preventDefault();clearTimeout(timer);calculate();});form.addEventListener('input',schedule);form.addEventListener('change',schedule);
  const reset=$('.reset',root);if(reset&&!reset.hasAttribute('data-custom-reset'))reset.addEventListener('click',()=>{form.reset();updateState();clearTimeout(timer);calculate();});
  calculate();return calculate;
}
const valuationRoot=$('[data-valuation]');
if(valuationRoot){const basics=valuationRoot.dataset.lesson==='bond-basics';
  const update=()=>{const zero=choiceValue('instrument',valuationRoot)==='zero';const coupon=$('[data-control="coupon_rate"]',valuationRoot);$$('input',coupon).forEach(input=>input.disabled=zero);
    const frequency=Number(choiceValue('frequency',valuationRoot)), maturity=$('[name="maturity_years"]',valuationRoot), range=$('[data-pair="maturity_years"]',valuationRoot);
    maturity.min=zero?'0':String(1/frequency);maturity.step=zero?'any':String(1/frequency);range.min=maturity.min;range.step=zero?'0.25':maturity.step;
    $('#maturity_years-hint',valuationRoot).textContent=zero?'Zero-coupon payments support fractional years.':'Coupon bonds require whole coupon periods.';
  };
  bindCalculator(valuationRoot,'/api/valuation',()=>{const input=readForm($('form',valuationRoot));input.coupon_rate=(input.coupon_rate??0)/100;input.ytm=(input.ytm??5)/100;return input;},data=>{
    $('[data-metric="main"]',valuationRoot).textContent=money(basics?data.payment_coupon:data.price);
    $('[data-metric="coupon"]',valuationRoot).textContent=money(basics?data.total_coupons:data.coupon_pv);
    $('[data-metric="principal"]',valuationRoot).textContent=money(basics?data.cashflows.at(-1).principal:data.principal_pv);
    if(!basics)$('[data-price-label]',valuationRoot).textContent=`${data.classification} · dollars per selected face value`;
    $('[data-count]',valuationRoot).textContent=`${data.cashflows.length} payment${data.cashflows.length===1?'':'s'}`;
    drawTimeline($('[data-chart]',valuationRoot),data.cashflows,basics);
    const headers=basics?['Year','Coupon','Principal','Total payment']:['Year','Payment','Discount factor','Present value'];
    const rows=data.cashflows.map(f=>basics?[f.time_years.toFixed(2),money(f.coupon),money(f.principal),money(f.amount)]:[f.time_years.toFixed(2),money(f.amount),f.discount_factor.toFixed(6),money(f.present_value)]);
    table($('[data-table]',valuationRoot),headers,rows,basics?['Total',money(data.total_coupons),money(data.cashflows.at(-1).principal),money(data.total_received)]:['Total',money(data.total_received),'—',money(data.price)]);
  },update);
}
const rateRoot=$('[data-rates]');if(rateRoot)bindCalculator(rateRoot,'/api/rates',()=>{const data=readForm($('form',rateRoot));data.rate/=100;return data;},data=>{$$('[data-rate]',rateRoot).forEach(node=>{const key=node.dataset.rate;node.textContent=key.endsWith('_rate')?percent(data[key],4):money(data[key]);});});
const yieldRoot=$('[data-yield]');if(yieldRoot){
  bindCalculator(yieldRoot,'/api/yield',()=>{
    const data=readForm($('form',yieldRoot));
    data.coupon_rate/=100;return data;
  },data=>{
    $$('[data-yield-metric]',yieldRoot).forEach(node=>node.textContent=percent(data[node.dataset.yieldMetric],4));
    $('[data-yield-check]',yieldRoot).textContent=`Entered price: ${money(data.price)}. Repriced at the implied yield: ${money(data.repriced)}. Difference: ${money(Math.abs(data.residual))}.`;
    table($('[data-table]',yieldRoot),['Year','Payment','Discount factor','Present value'],
      data.cashflows.map(flow=>[flow.time_years.toFixed(2),money(flow.amount),flow.discount_factor.toFixed(6),money(flow.present_value)]),
      ['Total',money(data.cashflows.reduce((sum,flow)=>sum+flow.amount,0)),'—',money(data.repriced)]);
    const classification=Math.abs(data.price-100)<1e-8?'At par':data.price<100?'Below par':'Above par';
    $('[data-yield-insight]',yieldRoot).textContent=`${classification}: coupon rate ${percent(data.coupon_rate)}, current yield ${percent(data.current_yield)}, YTM ${percent(data.ytm)}. Current yield excludes the gain or loss between purchase price and principal repayment. YTM is not a guaranteed holding-period return.`;
  },()=>{
    const frequency=Number(choiceValue('frequency',yieldRoot));
    for(const input of $$('[name="maturity_years"],[data-pair="yield-maturity"]',yieldRoot)){
      input.min=String(1/frequency);input.step=String(1/frequency);
    }
  });
  bindCentPrice(yieldRoot,'yield-price');
}
function bindCentPrice(root,id){
  const priceInput=$('[name="price"]',root),priceSlider=$(`[data-pair="${id}"]`,root);
  function roundPrice(){
    if(priceInput.value!==''&&Number.isFinite(Number(priceInput.value))){
      priceInput.value=Number(priceInput.value).toFixed(2);priceSlider.value=priceInput.value;
    }
  }
  priceInput.addEventListener('change',roundPrice);
  priceInput.addEventListener('blur',roundPrice);
  priceSlider.addEventListener('input',roundPrice);
  $('form',root).addEventListener('submit',roundPrice,true);
}
const settlementRoot=$('[data-settlement]');if(settlementRoot){
  bindCalculator(settlementRoot,'/api/settlement',()=>{
    const data=readForm($('form',settlementRoot));data.coupon_rate/=100;if('ytm' in data)data.ytm/=100;return data;
  },data=>{
    $$('[data-settlement-metric]',settlementRoot).forEach(node=>node.textContent=money(data[node.dataset.settlementMetric]));
    $('[data-settlement-summary]',settlementRoot).textContent=`Annual nominal YTM: ${percent(data.ytm,4)}. ${money(data.clean_price)} clean + ${money(data.accrued_interest)} accrued = ${money(data.dirty_price)} paid.${data.price_residual===null?'':` Repricing difference: ${money(Math.abs(data.price_residual))}.`}`;
    table($('[data-accrual-table]',settlementRoot),['Previous coupon','Next coupon','Elapsed days','Period days','Accrued fraction'],
      [[data.previous_coupon,data.next_coupon,data.elapsed_days,data.period_days,percent(data.elapsed_days/data.period_days,4)]]);
    table($('[data-table]',settlementRoot),['Payment date','Coupon','Principal','Discount factor','Present value'],
      data.cashflows.map(flow=>[flow.payment_date,money(flow.coupon),money(flow.principal),flow.discount_factor.toFixed(6),money(flow.present_value)]),
      ['Dirty price','','','',money(data.dirty_price)]);
    table($('[data-path-table]',settlementRoot),['Date','Clean','Accrued','Dirty'],data.path.map(p=>[p.date,money(p.clean),money(p.accrued),money(p.dirty)]));
    drawLines($('[data-chart]',settlementRoot),{title:'Clean and dirty prices at fixed YTM',x_label:'Years after selected settlement · fixed YTM',y_label:'Dollars per $100 face',percent_x:false,
      reference_y:100,curves:[{label:'Clean price',points:data.path.map(p=>({x:p.x,y:p.clean}))},{label:'Dirty price',points:data.path.map(p=>({x:p.x,y:p.dirty}))}]});
  },()=>{
    const solving=choiceValue('mode',settlementRoot)==='yield';
    for(const [id,disabled] of [['settlement-price',!solving],['settlement-ytm',solving]]){
      $$('input',$(`[data-control="${id}"]`,settlementRoot)).forEach(input=>input.disabled=disabled);
    }
    disableChoice('price_type',!solving,settlementRoot);
  });
  bindCentPrice(settlementRoot,'settlement-price');
}
const billRoot=$('[data-bills]');if(billRoot){
  bindCalculator(billRoot,'/api/bills',()=>{const data=readForm($('form',billRoot));data.discount_rate/=100;return data;},data=>{
    $('[data-bill-price]',billRoot).textContent=money(data.price);
    $$('[data-bill-metric]',billRoot).forEach(node=>node.textContent=percent(data[node.dataset.billMetric],4));
    table($('[data-table]',billRoot),['Measure','Value'],[['Price paid',money(data.price)],['Redemption',money(100)],['Interest dollars',money(data.interest)],
      ['Holding-period return',percent(data.holding_return,4)],['Simple annualization',percent(data.simple_annual_rate,4)],['Coupon-equivalent yield',percent(data.investment_rate,4)],['Days / year basis',`${data.days_to_maturity} / ${data.year_days}`]]);
    $('[data-bill-insight]',billRoot).textContent=`${data.method}. Holding-period return covers ${data.days_to_maturity} days. The annualized yields are quotation conventions, not additional cash payments.`;
    drawLines($('[data-chart]',billRoot),{title:'Discount and coupon-equivalent yield by bill maturity',x_label:'Days to maturity',y_label:'Annualized yield',percent_x:false,x_unit:'days',percent_y:true,reference_x:data.year_days/2,curves:data.curves});
  });
}
const experimentRoot=$('[data-experiment]');if(experimentRoot){let mode='maturity';const form=$('form',experimentRoot);
  const defaults={maturity:{coupon_rate:4,maturity_years:20},coupon:{coupon_rate:6,maturity_years:10},sensitivity:{coupon_rate:0,maturity_years:10}};
  const instructions={maturity:'Change maturity. The annual coupon stays at 4%.',coupon:'Change the coupon. Maturity stays at 10 years.',sensitivity:'Switch payment type. Maturity stays at 10 years.'};
  function update(){
    for(const name of ['coupon_rate','maturity_years']){
      const disabled=(name==='coupon_rate'&&mode!=='coupon')||(name==='maturity_years'&&mode!=='maturity');
      $$('input',$(`[data-control="${name}"]`,form)).forEach(input=>input.disabled=disabled);
    }
    $('[data-timing-control]',form).hidden=mode!=='sensitivity';
    disableChoice('payment_type',mode!=='sensitivity',form);
    if(mode==='sensitivity'){
      const coupon=choiceValue('payment_type',form)==='zero'?0:4;
      $('[name="coupon_rate"]',form).value=coupon;$('[data-pair="coupon_rate"]',form).value=coupon;
    }
    $('[data-variable-instruction]',form).textContent=instructions[mode];
  }
  const calculate=bindCalculator(experimentRoot,'/api/experiments',()=>{
    const data=readForm(form);
    return {mode,ytm:data.ytm/100,coupon_rate:mode==='coupon'?data.coupon_rate/100:0.04,
      maturity_years:mode==='maturity'?data.maturity_years:10,payment_type:mode==='sensitivity'?data.payment_type:'zero'};
  },data=>{
    $('[data-chart-title]',experimentRoot).textContent=data.title;drawLines($('[data-chart]',experimentRoot),data);
    table($('[data-table]',experimentRoot),data.headers,data.rows);
    const allRows=data.curves[0].points.map((p,i)=>[percent(p.x),...data.curves.map(c=>c.points[i].y.toFixed(4))]);
    table($('[data-plot-table]',experimentRoot),['YTM',...data.curves.map(c=>c.label)],allRows);
    $('[data-insight]',experimentRoot).textContent=data.insight;
    $('[data-timeline-label]',experimentRoot).textContent=data.timeline_label;
    drawTimeline($('[data-selected-timeline]',experimentRoot),data.timeline.cashflows,true,true);
  },update);
  function setMode(next,reset=false){mode=next;for(const [name,value] of Object.entries(defaults[mode])){$(`[name="${name}"]`,form).value=value;$(`[data-pair="${name}"]`,form).value=value;}
    setChoice('payment_type','zero',form);if(reset){$('[name="ytm"]',form).value=5;$('[data-pair="ytm"]',form).value=5;}
    $$('[data-mode]',experimentRoot).forEach(button=>{const selected=button.dataset.mode===mode;button.classList.toggle('selected',selected);button.setAttribute('aria-pressed',String(selected));});update();calculate();}
  $$('[data-mode]',experimentRoot).forEach(button=>button.addEventListener('click',()=>setMode(button.dataset.mode)));
  $('.reset',form).addEventListener('click',()=>setMode(mode,true));
}
const homeChart=$('[data-home-chart]');if(homeChart)fetch('/api/experiments',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'maturity'})}).then(response=>{if(!response.ok)throw Error();return response.json();}).then(data=>drawLines($('#home-chart'),data,true)).catch(()=>$('#home-chart').replaceChildren(element('p','Start the Python server to load the experiment.','loading')));
const navToggle=$('#nav-toggle');if(navToggle){
  const backdrop=$('.nav-backdrop');
  function setNavigation(open,restoreFocus=false){document.body.classList.toggle('nav-open',open);navToggle.setAttribute('aria-expanded',String(open));backdrop.hidden=!open;if(restoreFocus)navToggle.focus();}
  navToggle.addEventListener('click',()=>{const open=!document.body.classList.contains('nav-open');setNavigation(open);if(open)($('#course-nav [aria-current="page"]')||$('#course-nav a')).focus();});
  backdrop.addEventListener('click',()=>setNavigation(false,true));
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&document.body.classList.contains('nav-open'))setNavigation(false,true);});
  $$('a',$('#course-nav')).forEach(link=>link.addEventListener('click',()=>setNavigation(false)));
  window.addEventListener('resize',()=>{if(!document.body.classList.contains('lesson-page')&&window.innerWidth>680)setNavigation(false);});
}
if(window.katex)$$('.math').forEach(node=>{try{window.katex.render(node.textContent,node,{displayMode:node.classList.contains('block'),throwOnError:false,strict:'ignore'});}catch(error){console.warn('Formula could not be rendered',error);}});
