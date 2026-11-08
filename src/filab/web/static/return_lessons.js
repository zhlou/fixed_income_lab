'use strict';
$$('[data-return-lesson]').forEach(root => {
  const spec = JSON.parse($('[data-return-lesson-spec]', root).textContent);
  const form = $('form', root), state = $('[data-return-state]', root), fullLink = $('[data-full-calculator]', root);
  const {results, narrow, showView, fitChart} = bindReturnWorkspace(root);
  let activeExample = spec.default_example;
  const dollars = value => money(Math.abs(value) < .005 ? 0 : value);
  const format = (value, kind) => kind === 'money' ? dollars(value) : kind === 'percent' ? percent(value,4) : String(value);
  function restore(values) {
    for (const field of spec.controls) {
      if (field.kind === 'choice') setChoice(field.name, values[field.name], root);
      else {
        const input = form.elements.namedItem(field.name);
        input.value = field.rate ? Number((values[field.name] * 100).toPrecision(12)) : values[field.name];
        const slider = $(`[data-pair="${input.id}"]`, root); if (slider) slider.value = input.value;
      }
    }
  }
  function update() {
    for (const field of spec.controls) {
      const holder = $(`[data-lesson-field="${field.name}"]`, root);
      const visible = !field.when || choiceValue(field.when.field, root) === field.when.value;
      holder.hidden = !visible; $$('input', holder).forEach(input => input.disabled = !visible);
    }
  }
  function inputs() {
    const controls = {};
    for (const field of spec.controls) {
      const item = form.elements.namedItem(field.name);
      if ($(`input[name="${field.name}"]`, root).disabled) continue;
      controls[field.name] = field.kind === 'choice' ? choiceValue(field.name, root)
        : field.kind === 'date' ? item.value : Number(item.value) / (field.rate ? 100 : 1);
    }
    return {example:activeExample, controls};
  }
  function invalidate() {
    state.textContent = 'Results need updating.';
    fullLink.setAttribute('aria-disabled','true'); fullLink.title = 'Update the inputs before continuing with this scenario';
  }
  fullLink.addEventListener('click',event=>{if(fullLink.getAttribute('aria-disabled')==='true')event.preventDefault();});
  function render(data) {
    state.textContent = 'Results are up to date.';
    const focus = data.focus, r = data.result;
    const cards = focus.metrics.map((m,index) => {
      const node = element('div', undefined, 'metric' + (index === 0 ? ' primary-metric' : ''));
      node.append(element('span',m.label),element('strong',format(m.value,m.kind)),element('small',m.detail));
      return node;
    });
    $('[data-lesson-metrics]',root).replaceChildren(...cards);
    const plot = focus.plot, maxDay = plot.curves[0].points.at(-1).x;
    drawLines($('[data-return-chart]',root), {...plot,
      x_ticks:Array.from(new Set(Array.from({length:6},(_,i)=>Math.round(maxDay*i/5))))}, true);
    requestAnimationFrame(fitChart);
    $('[data-lesson-insight]',root).textContent = focus.note;
    table($('[data-lesson-table]',root),focus.columns.map(column=>column[0]),
      focus.rows.map(row=>row.map((value,index)=>format(value,focus.columns[index][1]))));
    $('[data-lesson-totals]',root).textContent = `Net profit ${dollars(r.net_profit)}; holding-period return ${percent(r.total_return,6)}. This return covers the whole selected period and is not annualized. Cash and profit reconcile within display rounding.`;
    const study = {schema_version:1,kind:'filab-bond-return',conventions:data.conventions,inputs:data.inputs};
    fullLink.href = '/tools/bond-return#scenario=' + encodeURIComponent(JSON.stringify(study));
    fullLink.removeAttribute('aria-disabled');
    fullLink.title = 'Continue in the full calculator with these inputs';
  }
  restore(spec.initial); update();
  $$('input',form).forEach(input=>{input.defaultValue=input.value;if(input.type==='radio')input.defaultChecked=input.checked;});
  form.addEventListener('input',invalidate);form.addEventListener('change',invalidate);
  $('.reset',root).addEventListener('click',()=>{activeExample=spec.default_example;invalidate();});
  const calculate = bindCalculator(root,'/api/lesson-returns/'+spec.slug,inputs,render,update);
  $$('[data-lesson-example]',root).forEach(button=>button.addEventListener('click',()=>{
    activeExample=button.dataset.lessonExample;
    restore(spec.examples.find(example=>example.id===activeExample).controls);invalidate();update();calculate();
    results.scrollTop=0;showView('results',narrow.matches);if(!narrow.matches)button.focus({preventScroll:true});
  }));
});
