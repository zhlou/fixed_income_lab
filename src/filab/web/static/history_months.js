/* Debounce calendar navigation, serialize requests, and discard stale results. */
(() => {
  class HistoryMonths {
    constructor({load, apply, status, delay=300}) {
      Object.assign(this,{load,apply,status,delay});this.epoch=0;this.waiters=[];
    }
    schedule(month,force=false) {
      if(!force&&(this.queued?.month===month||this.running?.month===month&&this.running.epoch===this.epoch))return;
      this.queued={month,force,epoch:++this.epoch};clearTimeout(this.timer);
      this.status(`Loading ${month}…`,false);
      this.timer=setTimeout(()=>{this.timer=null;this.drain();},this.delay);
    }
    cancel() {
      this.epoch++;this.queued=null;clearTimeout(this.timer);this.timer=null;this.finish();
    }
    async drain() {
      if(this.running||!this.queued)return;
      const task=this.queued;this.queued=null;this.running=task;
      try {
        const result=await this.load(task.month,task.force);
        if(task.epoch===this.epoch){this.apply(result);this.status(result.warning||`${task.month} ready${result.cache_hit?' · cached data':''}. Compare dates to update the curves.`,Boolean(result.warning));}
      } catch(error) {
        if(task.epoch===this.epoch)this.status('No data',true);
      } finally {
        this.running=null;
        if(this.queued&&!this.timer)this.drain();
        this.finish();
      }
    }
    finish() {
      if(!this.running&&!this.queued){this.waiters.splice(0).forEach(resolve=>resolve());}
    }
    wait() {
      clearTimeout(this.timer);this.timer=null;this.drain();
      return !this.running&&!this.queued?Promise.resolve():new Promise(resolve=>this.waiters.push(resolve));
    }
  }
  window.FilabHistoryMonths=HistoryMonths;
})();
