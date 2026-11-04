'use strict';
(() => {
  const root = $('[data-returns]');
  if (!root) return;
  const form = $('form', root), state = $('[data-return-state]', root);
  const exportInputs = $('[data-return-export]', root), exportLedger = $('[data-ledger-export]', root);
  const fileInput = $('[data-return-import]', root), fileError = $('[data-return-file-error]', root);
  const fileStatus = $('[data-return-file-status]', root);
  const {results, narrow, showView, fitChart} = bindReturnWorkspace(root);
  const rateFields = ['coupon_rate', 'comparison_coupon_rate', 'start_yield', 'end_yield', 'cash_rate'];
  const numberFields = ['face_value', 'comparison_face_value', 'price', 'comparison_price', 'cost_bp', ...rateFields];
  const dateFields = ['start_date', 'end_date', 'issue_date', 'maturity_date', 'comparison_maturity_date', 'shock_date'];
  const choiceFields = ['frequency', 'purchase_method', 'yield_path', 'cash_policy', 'end_treatment', 'include_comparison'];
  let validated = null, importSequence = 0;
  const dollars = value => money(Math.abs(value) < .005 ? 0 : value);
  const base = {start_date:'2026-11-14', end_date:'2026-11-16', issue_date:'2025-11-15', maturity_date:'2028-11-15',
    face_value:100, coupon_rate:.04, frequency:2, purchase_method:'yield', price:98.12, start_yield:.05,
    yield_path:'fixed', shock_date:'2026-11-16', end_yield:.06, cash_policy:'zero', cash_rate:.04, cost_bp:0,
    end_treatment:'liquidate', include_comparison:false, comparison_face_value:100, comparison_coupon_rate:.04,
    comparison_maturity_date:'2036-11-15', comparison_price:90};
  const examples = {
    coupon: {},
    maturity: {start_date:'2026-11-15', end_date:'2028-11-15'},
    shock: {start_date:'2026-11-15', end_date:'2027-05-15', shock_date:'2027-05-15', yield_path:'shock', end_yield:.07},
    'two-period': {start_date:'2025-11-15', end_date:'2027-11-15', maturity_date:'2027-11-15', frequency:1, cash_policy:'interest', cash_rate:.05},
  };
  function inputs() {
    const data = {};
    for (const name of numberFields) data[name] = Number(form.elements.namedItem(name).value) / (rateFields.includes(name) ? 100 : 1);
    for (const name of dateFields) data[name] = form.elements.namedItem(name).value;
    for (const name of choiceFields) data[name] = choiceValue(name, root);
    data.frequency = Number(data.frequency); data.include_comparison = data.include_comparison === 'yes';
    return data;
  }
  function restore(data) {
    for (const name of numberFields) {
      const input = form.elements.namedItem(name);
      input.value = rateFields.includes(name) ? Number((data[name] * 100).toPrecision(12)) : data[name];
      if (name === 'price' || name === 'comparison_price') input.value = Number(input.value).toFixed(2);
      const slider = $(`[data-pair="${input.id}"]`, root); if (slider) slider.value = input.value;
    }
    for (const name of dateFields) form.elements.namedItem(name).value = data[name];
    for (const name of choiceFields) setChoice(name, name === 'include_comparison' ? (data[name] ? 'yes' : 'no') : String(data[name]), root);
  }
  function invalidate() {
    validated = null; exportInputs.disabled = true; exportLedger.disabled = true; importSequence++;
    state.textContent = 'Results need updating.';
  }
  function update() {
    const comparison = choiceValue('include_comparison', root) === 'yes', clean = choiceValue('purchase_method', root) === 'clean';
    const shock = choiceValue('yield_path', root) === 'shock';
    const comparisonSection = $('[data-return-comparison]', root), shockSection = $('[data-return-shock]', root);
    comparisonSection.hidden = !comparison; $$('input', comparisonSection).forEach(input => input.disabled = !comparison);
    shockSection.hidden = !shock; $$('input', shockSection).forEach(input => input.disabled = !shock);
    for (const [id, enabled] of [['return-start-yield', !clean], ['return-price', clean], ['return-b-price', clean && comparison]]) {
      $$('input', $(`[data-control="${id}"]`, root)).forEach(input => input.disabled = !enabled);
    }
    const data = inputs(), labels = {
      horizon:`${data.start_date || 'Purchase date'} → ${data.end_date || 'Horizon'} · ${shock ? 'Dated yield change' : 'Fixed YTM'}`,
      bond:`${dollars(data.face_value)} face · ${percent(data.coupon_rate)} coupon · ${data.frequency} payments/year`,
      purchase:clean ? `${dollars(data.price)} clean / $100 face` : `${percent(data.start_yield)} nominal YTM assumption`,
      cash:`Cash at ${percent(data.cash_policy === 'interest' ? data.cash_rate : 0)} · ${data.cost_bp} bp · ${data.end_treatment === 'mark' ? 'Keep & value' : 'Sell at horizon'}`,
      comparison:comparison ? `${dollars(data.comparison_face_value)} face · ${percent(data.comparison_coupon_rate)} coupon` : 'Not included',
    };
    for (const [group, text] of Object.entries(labels)) $(`[data-return-group-summary="${group}"]`, root).textContent = text;
  }
  function render(data) {
    const r = data.result;
    validated = data; exportInputs.disabled = false; exportLedger.disabled = false;
    state.textContent = 'Results are up to date.';
    $$('[data-return-metric]', root).forEach(node => {
      const key = node.dataset.returnMetric; node.textContent = key === 'total_return' ? percent(r[key], 4) : dollars(r[key]);
    });
    drawLines($('[data-return-chart]', root), {title:'Hypothetical bond value, cash, and total wealth',
      percent_x:false, x_unit:'days', x_label:'Actual days after purchase settlement', y_label:'Portfolio dollars',
      x_ticks:Array.from(new Set(Array.from({length:6},(_,i)=>Math.round(r.path.at(-1).days*i/5)))),
      curves:[['Total wealth','wealth'], ['Bond dirty value','bond_value'], ['Credited cash','cash']].map(([label,key]) => ({label, points:r.path.map(p => ({x:p.days, y:p[key]}))}))}, true);
    requestAnimationFrame(fitChart);
    $('[data-return-insight]', root).textContent = `${data.inputs.start_date} to ${data.inputs.end_date}: ${dollars(r.ending_bond_value)} remaining bond value + ${dollars(r.ending_cash)} cash = ${dollars(r.ending_wealth)} ending wealth. Coupons of ${dollars(r.coupons)} are already credited to cash. Do not add them again. Return covers the full period and includes ${dollars(r.total_fees)} of trading costs.`;
    table($('[data-return-components]', root), ['Component', 'Dollars'], [
      ['Clean price change / principal recovery', dollars(r.clean_price_change)],
      ['Change in accrued interest', dollars(r.accrual_change)],
      ['Coupons received', dollars(r.coupons)], ['Cash-account interest', dollars(r.cash_interest)],
      ['Purchase costs', dollars(-r.purchase_fees)], ['Sale costs', dollars(-r.sale_fees)],
    ], ['Net profit = ending − beginning wealth', dollars(r.net_profit)]);
    $('[data-return-check]', root).textContent = `Opening cost: ${dollars(r.purchase_clean)} clean + ${dollars(r.purchase_accrued)} accrued + ${dollars(r.purchase_fees)} purchase costs = ${dollars(r.beginning_wealth)}. Reconciliation difference: ${dollars(r.reconciliation_residual)}. Displays round to cents; full precision is retained in the ledger export.`;
    table($('[data-return-cash-table]', root), ['Cash policy', 'Effective annual rate', 'Cash interest', 'Ending wealth', 'Period return'],
      data.cash_comparison.map(row => [row.label, percent(row.rate), dollars(row.cash_interest), dollars(row.ending_wealth), percent(row.total_return, 4)]));
    table($('[data-return-positions]', root), ['Position', 'Face bought', 'Purchase clean', 'Purchase accrued', 'Purchase dirty', 'Status', 'Sale / redemption / mark date', 'Terminal clean', 'Terminal accrued', 'Terminal dirty', 'Face held'],
      r.positions.map(p => [p.label, dollars(p.face_value), dollars(p.purchase_clean), dollars(p.purchase_accrued), dollars(p.purchase_dirty), p.status, p.date, dollars(p.clean), dollars(p.accrued), dollars(p.dirty), dollars(p.ending_face)]));
    $('[data-return-yields]', root).textContent = `Purchase nominal YTM: ${data.purchase_ytms.map(p => `${p.label} ${percent(p.ytm,6)}`).join('; ')}. ${data.inputs.purchase_method === 'clean' ? 'Solved from the entered clean quotes; accrued interest is added for settlement.' : 'Purchase prices are model-derived from the YTM assumption.'} Terminal dirty values are sale proceeds, principal redeemed, or retained bond marks; coupons and fees appear separately.`;
    const eventNames = {opening:'Opening capital', purchase:'Purchase', purchase_fee:'Purchase cost', coupon:'Coupon', redemption:'Redemption', sale:'Sale', sale_fee:'Sale cost', cash_interest:'Cash interest', valuation:'Valuation'};
    table($('[data-return-ledger]', root), ['#', 'Date', 'Event', 'Position', 'Cash Δ', 'Face Δ', 'Cash balance', 'Face balance', 'Dirty / $100', 'Bond value', 'Wealth'],
      r.ledger.map(e => [e.sequence, e.date, eventNames[e.event], e.position || 'Portfolio', dollars(e.cash_change), dollars(e.face_change), dollars(e.cash_balance), e.face_balance === null ? '—' : dollars(e.face_balance), e.dirty_price_per_100 === null ? '—' : dollars(e.dirty_price_per_100), e.bond_value === null ? '—' : dollars(e.bond_value), e.wealth === null ? '—' : dollars(e.wealth)]));
    table($('[data-return-path]', root), ['Date', 'Clean bond value', 'Accrued interest', 'Dirty bond value', 'Cash', 'Wealth'],
      r.path.map(p => [p.date, dollars(p.clean_value), dollars(p.accrued_interest), dollars(p.bond_value), dollars(p.cash), dollars(p.wealth)]));
  }
  restore({...base, ...examples[root.dataset.initialExample]}); update();
  const openingGroup = root.dataset.initialExample === 'two-period' ? 'cash' : root.dataset.initialExample === 'maturity' ? 'bond' : 'horizon';
  $$('[data-return-group]', root).forEach(group => group.open = group.dataset.returnGroup === openingGroup);
  // Reset returns to the lesson's opening experiment, including its radio cards.
  $$('input', form).forEach(input => {input.defaultValue = input.value; if (input.type === 'radio') input.defaultChecked = input.checked;});
  form.addEventListener('input', invalidate); form.addEventListener('change', invalidate);
  $('.reset', root).addEventListener('click', () => {invalidate(); fileInput.value = ''; fileError.textContent = ''; fileStatus.textContent = '';});
  // Register cent commits before calculator change handlers validate a quote.
  for (const name of ['price', 'comparison_price']) {
    const input = form.elements.namedItem(name), slider = $(`[data-pair="${input.id}"]`, root);
    const round = () => {if (input.value !== '' && Number.isFinite(Number(input.value))) {input.value = Number(input.value).toFixed(2); slider.value = input.value;}};
    input.addEventListener('change', round); input.addEventListener('blur', round); slider.addEventListener('input', round);
    form.addEventListener('submit', round, true);
  }
  const calculate = bindCalculator(root, '/api/returns', inputs, render, update);
  $$('[data-return-example]', root).forEach(button => button.addEventListener('click', () => {
    invalidate(); restore({...base, ...examples[button.dataset.returnExample]}); update(); fileError.textContent = ''; fileStatus.textContent = ''; calculate();
    results.scrollTop = 0; showView('results', narrow.matches);
    if (!narrow.matches) button.focus({preventScroll:true});
  }));
  function download(value, filename) {
    const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2) + '\n'], {type:'application/json'}));
    const link = element('a'); link.href = url; link.download = filename; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function study() {return {schema_version:1, kind:'filab-bond-return', conventions:'dated-return-ledger-v1', inputs:validated.inputs};}
  exportInputs.addEventListener('click', () => {if (!validated) return; download(study(), 'filab-bond-return-v1.json'); fileStatus.textContent = 'Inputs exported with all dates, cash treatment, costs, and conventions.';});
  exportLedger.addEventListener('click', () => {
    if (!validated) return;
    download({schema_version:1, kind:'filab-return-ledger', scenario:study(), results:validated, price_provenance:validated.price_provenance}, 'filab-return-ledger-v1.json');
    fileStatus.textContent = 'Full-precision ledger and results exported with the scenario. Import inputs to reproduce this hypothetical calculation.';
  });
  async function restoreStudy(saved, token) {
    const response = await fetch('/api/return-study', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(saved)});
    const result = await response.json(); if (token !== importSequence) return false;
    if (!response.ok) throw new Error('This scenario has unsupported or incomplete inputs or conventions.');
    const data = result.study.inputs;
    if (numberFields.some(name => {const input = form.elements.namedItem(name), v = data[name] * (rateFields.includes(name) ? 100 : 1), steps = (v - Number(input.min)) / Number(input.step); return v < Number(input.min) || v > Number(input.max) || Math.abs(steps - Math.round(steps)) > 1e-7;})) throw new Error('This scenario contains values outside the visible controls. Current inputs are unchanged.');
    invalidate(); restore(data); update(); await calculate(); return validated !== null;
  }
  fileInput.addEventListener('change', async () => {
    const file = fileInput.files[0]; if (!file) return;
    const token = ++importSequence; fileError.textContent = '';
    try {
      if (file.size > 30000) throw new Error('Choose an input-scenario JSON file smaller than 30 KB.');
      const saved = JSON.parse(await file.text());
      if (await restoreStudy(saved, token)) fileStatus.textContent = 'Scenario imported. All inputs and conventions restored.';
    } catch (error) {if (token === importSequence) fileError.textContent = error instanceof SyntaxError ? 'This file is not valid JSON. Current inputs are unchanged.' : error.message;}
    finally {fileInput.value = '';}
  });
  const transferred = new URLSearchParams(window.location.hash.slice(1)).get('scenario');
  if (transferred) {
    const token = ++importSequence;
    (async () => {
      try {
        if (transferred.length > 30000) throw new Error('This scenario link is too large. Open the calculator directly.');
        if (await restoreStudy(JSON.parse(transferred), token)) state.textContent = 'Results are up to date. Lesson inputs restored.';
      } catch (error) {
        if (token !== importSequence) return;
        fileError.textContent = 'The linked scenario could not be restored. ' + (error instanceof SyntaxError ? 'The link is not valid JSON.' : error.message);
        $('.return-saved', root).open = true;
      }
    })();
  }
})();
