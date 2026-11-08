const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const context={window:{},setTimeout,clearTimeout};
vm.runInNewContext(fs.readFileSync('src/filab/web/static/history_months.js','utf8'),context);
const Loader=context.window.FilabHistoryMonths;
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
const tick=()=>new Promise(resolve=>setTimeout(resolve,5));

test('rapid navigation debounces to latest month and wait flushes immediately',async()=>{
  const loaded=[],applied=[];
  const loader=new Loader({load:async month=>{loaded.push(month);return {month};},apply:r=>applied.push(r.month),status:()=>{},delay:1000});
  loader.schedule('2026-09');loader.schedule('2026-08');loader.schedule('2026-07');
  await loader.wait();assert.deepEqual(loaded,['2026-07']);assert.deepEqual(applied,['2026-07']);
});

test('requests serialize, deduplicate and discard an older month response',async()=>{
  const first=deferred(),loaded=[],applied=[];
  const loader=new Loader({load:async month=>{loaded.push(month);if(month==='2026-09')await first.promise;return {month};},apply:r=>applied.push(r.month),status:()=>{},delay:0});
  loader.schedule('2026-09');await tick();loader.schedule('2026-09');
  loader.schedule('2026-08');await tick();assert.deepEqual(loaded,['2026-09']);
  const idle=loader.wait();first.resolve();await idle;
  assert.deepEqual(loaded,['2026-09','2026-08']);assert.deepEqual(applied,['2026-08']);
});

test('reset cancels queued work and suppresses a pending response or error',async()=>{
  const first=deferred(),applied=[],statuses=[];
  const loader=new Loader({load:()=>first.promise,apply:r=>applied.push(r),status:s=>statuses.push(s),delay:0});
  loader.schedule('2026-09');await tick();loader.cancel();first.reject(new Error('late failure'));await loader.wait();
  assert.deepEqual(applied,[]);assert.equal(statuses.length,1);
  loader.schedule('2026-08');loader.cancel();await loader.wait();assert.deepEqual(applied,[]);
});

test('errors preserve old results and forced retry can apply a warning',async()=>{
  const applied=[],statuses=[];let calls=0;
  const loader=new Loader({load:async(month,force)=>{calls++;if(!force)throw new Error('offline');return {month,warning:'Showing cached coverage'};},apply:r=>applied.push(r),status:(s,retry)=>statuses.push({s,retry}),delay:0});
  loader.schedule('2026-09');await loader.wait();assert.equal(applied.length,0);assert.equal(statuses.at(-1).retry,true);
  loader.schedule('2026-09',true);await loader.wait();assert.equal(calls,2);assert.equal(applied.length,1);assert.equal(statuses.at(-1).s,'Showing cached coverage');
});
