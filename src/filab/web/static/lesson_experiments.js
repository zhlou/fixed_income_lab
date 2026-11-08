'use strict';
$$('[data-core-experiment]').forEach(root => {
  const kind = root.dataset.coreExperiment;
  const form = $('form', root);
  const priceMode = () => choiceValue('direction', root) === 'price';
  const metric = (label, value, detail) => {
    const card = element('div', undefined, 'metric');
    card.append(element('span', label), element('strong', value), element('small', detail));
    return card;
  };
  const inputs = () => {
    if (kind === 'pricing') {
      const common = {face_value:100, coupon_rate:.04, maturity_years:2, frequency:2};
      return priceMode() ? {...common, ytm:Number(form.elements.ytm.value)/100}
        : {...common, price:Number(form.elements.price.value)};
    }
    return {shock_bp:Number(choiceValue('shock_bp', root)),
      face_value:kind === 'duration' ? Number(form.elements.face_value.value) : 100,
      maturity_years:kind === 'duration' ? 2 : 10};
  };
  function update() {
    if (kind !== 'pricing') return;
    for (const [id, disabled] of [['core-price',priceMode()], ['core-ytm',!priceMode()]]) {
      $(`[data-control="${id}"]`, root).hidden = disabled;
      $$('input', $(`[data-control="${id}"]`, root)).forEach(input => input.disabled = disabled);
    }
  }
  function render(data) {
    const cards = $('[data-core-metrics]', root), chart = $('[data-core-chart]', root);
    if (kind === 'pricing') {
      cards.replaceChildren(metric('Price', money(data.price), 'Dollars per $100 face'),
        metric('Annual nominal YTM', percent(data.ytm,4), 'Semiannual compounding'),
        metric('Current yield', percent(data.current_yield,4), 'Annual coupon dollars / price'));
      drawTimeline(chart, data.cashflows, false, true);
      table($('[data-core-table]',root), ['Years','Payment','Discount factor','Present value'],
        data.cashflows.map(flow => [flow.time_years.toFixed(1),money(flow.amount),flow.discount_factor.toFixed(6),money(flow.present_value)]),
        ['Price','','',money(data.price)]);
      $('[data-core-note]',root).textContent = 'Coupon rate stays at 4%. Each payment is discounted using the displayed YTM. Calculations retain full precision before rounding.';
      return;
    }
    const [a,b] = data.bonds;
    const curves = kind === 'duration' ? data.bonds.map(bond => ({label:bond.label,points:bond.points.map(p => ({x:p.shock_bp,y:p.exact_percent})),marker:{x:data.shock_bp,y:bond.selected.exact_percent}}))
      : [['Exact','exact_percent'],['Duration','duration_percent'],['Duration + convexity','convexity_percent']].map(([label,key]) => ({label,points:a.points.map(p => ({x:p.shock_bp,y:p[key]})),marker:{x:data.shock_bp,y:a.selected[key]}}));
    drawLines(chart, {title:kind === 'duration' ? 'Two-year and ten-year bonds' : 'Ten-year bond approximation',
      curves, x_label:'Yield change (bp)', y_label:'Immediate price change (%)', percent_x:false, x_unit:'bp', percent_y:true, reference_x:0, reference_y:0});
    if (kind === 'duration') {
      cards.replaceChildren(metric('Two-year loss / gain',percent(a.selected.exact_percent),'Exact repricing'),
        metric('Ten-year loss / gain',percent(b.selected.exact_percent),'Exact repricing'));
      table($('[data-core-table]',root), ['Bond','Price','Modified duration','DV01 · $/bp','Change · $'],
        data.bonds.map(bond => [bond.label,money(bond.risk.price),bond.risk.modified_duration.toFixed(6),money(bond.risk.dv01),money(bond.selected.exact_change)]));
      table($('[data-core-weights]',root), ['Years','Payment','PV','Weight','Weight × years'],
        a.cashflows.map(flow => [flow.time_years.toFixed(1),money(flow.amount),money(flow.present_value),percent(flow.weight,4),flow.weighted_time.toFixed(6)]));
      $('[data-core-note]',root).textContent = `Two-year Macaulay duration ${a.risk.macaulay_duration.toFixed(6)} years. DV01 is a positive local magnitude. Dollar amounts scale with face value.`;
    } else {
      cards.replaceChildren(metric('Exact change',money(a.selected.exact_change),'Selected yield shock'),
        metric('Duration estimate',money(a.selected.duration_change),'Starting slope'),
        metric('With convexity',money(a.selected.convexity_change),'Slope plus curvature'));
      table($('[data-core-table]',root), ['Method','Price change','Error · $'],
        [['Exact repricing',money(a.selected.exact_change),'—'],['Duration',money(a.selected.duration_change),money(a.selected.duration_error)],
          ['Duration + convexity',money(a.selected.convexity_change),money(a.selected.convexity_error)]]);
      $('[data-core-note]',root).textContent = `Modified duration ${a.risk.modified_duration.toFixed(6)}. Convexity ${a.risk.convexity.toFixed(6)} years². Signed error = estimate minus exact change.`;
    }
  }
  // The existing binder aborts stale requests, validates controls, and restores defaults.
  const endpoint = kind === 'pricing' ? () => priceMode() ? '/api/valuation' : '/api/yield' : () => '/api/risk';
  if (kind === 'pricing') bindCentPrice(root, 'core-price');
  bindCalculator(root, endpoint, inputs, render, update);
});
$$('[data-lesson-case]').forEach(button => button.addEventListener('click', () => {
  $$('[data-lesson-case]').forEach(option => option.setAttribute('aria-pressed', String(option === button)));
  $$('[data-case]').forEach(panel => panel.hidden = panel.dataset.case !== button.dataset.lessonCase);
}));
