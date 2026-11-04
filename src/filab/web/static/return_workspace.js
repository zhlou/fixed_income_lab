'use strict';
// Shared navigation and error visibility for focused lessons and the full tool.
function bindReturnWorkspace(root) {
  const form = $('form', root), results = $('.return-results', root);
  const narrow = window.matchMedia('(max-width:1199px)');
  function fitChart() {
    if (!document.body.classList.contains('return-lesson') || !window.matchMedia('(min-width:1200px) and (max-height:760px)').matches) return;
    const svg = $('[data-return-chart] svg',root); if (!svg) return;
    const height = Math.max(140,results.getBoundingClientRect().bottom - (svg.getBoundingClientRect().top + results.scrollTop) - 6);
    const view = svg.viewBox.baseVal;
    $('[data-return-chart]',root).style.setProperty('--return-chart-max-width',`${height*view.width/view.height}px`);
  }
  const resize = new ResizeObserver(()=>requestAnimationFrame(fitChart));
  resize.observe(results); const metrics=$('.metrics',results);if(metrics)resize.observe(metrics);
  function showView(view, moveFocus=false) {
    root.dataset.view = view;
    $$('[data-return-view]', root).forEach(button => button.setAttribute('aria-pressed', String(button.dataset.returnView === view)));
    if (moveFocus && narrow.matches) {
      root.scrollIntoView({block:'start', behavior:'instant'});
      $(`[data-return-view="${view}"]`, root).focus({preventScroll:true});
    }
  }
  $$('[data-return-view]', root).forEach(button => button.addEventListener('click', () => showView(button.dataset.returnView, true)));
  $('[data-return-show-results]', root).addEventListener('click', () => {
    showView('results', true); results.scrollTop = 0;
    if (!narrow.matches) {
      if (!document.body.classList.contains('return-lesson')) results.scrollIntoView({block:'start', behavior:'instant'});
      results.focus({preventScroll:true});
    }
  });
  root.addEventListener('keydown', event => {
    const menu = event.target.closest('.return-tool-menu');
    if (event.key === 'Escape' && menu?.open) {menu.open = false; $('summary', menu).focus();}
  });
  new MutationObserver(records => {
    const input = records.map(record => record.target).find(node => node.getAttribute('aria-invalid') === 'true');
    if (!input) return;
    const group = input.closest('.return-input-group'); if (group) group.open = true;
    if (narrow.matches) showView('inputs');
    (input.closest('.choice-group') || input).scrollIntoView({block:'nearest', behavior:'instant'});
  }).observe(form, {subtree:true, attributes:true, attributeFilter:['aria-invalid']});
  return {results, narrow, showView, fitChart};
}
