/* Pure calendar rules; no browser, dependencies, network, or timezone assumptions. */
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const context={window:{}};
vm.runInNewContext(fs.readFileSync('src/filab/web/static/history_dates.js','utf8'),context);
const Calendar=context.window.FilabHistoryDates;

test('strict dates include real leap days and reject invalid or normalized dates',()=>{
  for(const value of ['2025-02-18','2024-02-29','2000-02-29','0001-01-01','0099-12-31','9999-12-31'])assert.equal(Calendar.iso(Calendar.parse(value)),value);
  for(const value of ['2025-02-29','1900-02-29','2025-04-31','2025-00-01','2025-13-01','2025-02-00','0000-01-01','2025-2-18','','not-a-date','2025-02-18T00:00:00Z'])assert.equal(Calendar.parse(value),null,value);
});

test('month and year movement clamp the day rather than skipping a month',()=>{
  assert.equal(Calendar.iso(Calendar.shiftMonth(Calendar.parse('2025-01-31'),1)),'2025-02-28');
  assert.equal(Calendar.iso(Calendar.shiftMonth(Calendar.parse('2024-01-31'),1)),'2024-02-29');
  assert.equal(Calendar.iso(Calendar.shiftMonth(Calendar.parse('2024-02-29'),12)),'2025-02-28');
  assert.equal(Calendar.iso(Calendar.shiftMonth(Calendar.parse('2025-01-15'),-1)),'2024-12-15');
  assert.equal(Calendar.iso(Calendar.shiftMonth(Calendar.parse('0001-01-01'),-1)),null);
  assert.equal(Calendar.iso(Calendar.shiftMonth(Calendar.parse('9999-12-31'),1)),null);
});

test('availability distinguishes gaps, coverage limits, and unloaded metadata',()=>{
  const data={coverage:[['2025-02-01','2025-02-28'],['2025-04-01','2025-04-30']],published:new Set(['2025-02-14','2025-02-18','2025-04-01'])};
  assert.equal(Calendar.state('2025-02-14',data),'published');
  assert.equal(Calendar.state('2025-02-17',data),'no_published_row');
  assert.equal(Calendar.state('2025-02-01',data),'no_published_row');
  assert.equal(Calendar.state('2025-02-28',data),'no_published_row');
  assert.equal(Calendar.state('2025-03-03',data),'outside_coverage');
  assert.equal(Calendar.state('2025-01-31',data),'outside_coverage');
  assert.equal(Calendar.state('2025-05-01',data),'outside_coverage');
  assert.equal(Calendar.state('2025-02-14',null),null);
});
