/* A calendar over the selected local snapshot. Presence never implies all tenors. */
(() => {
  const labels={published:'Published row',no_published_row:'No published row',outside_coverage:'Outside cached coverage'};
  const marks={published:'●',no_published_row:'—',outside_coverage:'?'};
  let sequence=0;
  function day(year,month,number) {
    const result=new Date(0);result.setUTCFullYear(year,month,number);result.setUTCHours(0,0,0,0);return result;
  }
  function iso(value) {
    const year=value.getUTCFullYear();
    return year<1||year>9999?null:`${String(year).padStart(4,'0')}-${String(value.getUTCMonth()+1).padStart(2,'0')}-${String(value.getUTCDate()).padStart(2,'0')}`;
  }
  function parse(value) {
    if(!/^\d{4}-\d{2}-\d{2}$/.test(value))return null;
    const [year,month,number]=value.split('-').map(Number), result=day(year,month-1,number);
    return iso(result)===value?result:null;
  }
  function shiftMonth(value,amount) {
    const first=day(value.getUTCFullYear(),value.getUTCMonth()+amount,1);
    return day(first.getUTCFullYear(),first.getUTCMonth(),Math.min(value.getUTCDate(),day(first.getUTCFullYear(),first.getUTCMonth()+1,0).getUTCDate()));
  }
  function state(value,data) {
    if(!data)return null;
    if(!data.coverage.some(([start,end])=>start<=value&&value<=end))return 'outside_coverage';
    return data.published.has(value)?'published':'no_published_row';
  }
  class HistoryDates {
    constructor(root, onMonthChange=()=>{}) {
      this.onMonthChange=onMonthChange;
      this.root=root;this.data=null;this.fields=[...root.querySelectorAll('[data-history-date]')];
      this.id=`history-calendar-${++sequence}`;
      this.dialog=element('dialog',undefined,'history-calendar');this.dialog.id=this.id;
      this.dialog.setAttribute('aria-labelledby',this.id+'-title');
      this.dialog.setAttribute('aria-describedby',this.id+'-help');
      const top=element('div',undefined,'history-calendar-top');
      this.title=element('h2');this.title.id=this.id+'-title';
      const close=element('button','Close','history-calendar-close');close.type='button';close.addEventListener('click',()=>this.close());top.append(this.title,close);
      const nav=element('div',undefined,'history-calendar-nav');
      const previous=element('button','←'),next=element('button','→');
      previous.type=next.type='button';previous.setAttribute('aria-label','Previous month');next.setAttribute('aria-label','Next month');
      previous.addEventListener('click',()=>this.moveMonth(-1));next.addEventListener('click',()=>this.moveMonth(1));
      this.previous=previous;this.next=next;
      this.month=element('h3');this.month.id=this.id+'-month';this.month.setAttribute('aria-live','polite');nav.append(previous,this.month,next);
      this.grid=element('table',undefined,'history-calendar-grid');this.grid.setAttribute('role','grid');this.grid.setAttribute('aria-labelledby',this.month.id);
      const head=element('thead'),row=element('tr');
      ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'].forEach(name=>{const cell=element('th',name.slice(0,2));cell.scope='col';cell.setAttribute('abbr',name);row.append(cell);});head.append(row);this.body=element('tbody');this.grid.append(head,this.body);
      const legend=element('div',undefined,'history-calendar-legend');
      Object.keys(labels).forEach(key=>{const item=element('span',undefined,'history-calendar-key');const mark=element('span',marks[key]);mark.dataset.state=key;mark.setAttribute('aria-hidden','true');item.append(mark,document.createTextNode(' '+labels[key]));legend.append(item);});
      const note=element('p','Published dates can still have missing tenors.','tiny-note');
      const help=element('p','Arrow keys: days · Page Up/Down: months · Shift + Page Up/Down: years · Escape: close','tiny-note');help.id=this.id+'-help';
      this.loadStatus=element('p',undefined,'tiny-note');this.loadStatus.setAttribute('role','status');
      this.retry=element('button','Retry month');this.retry.type='button';this.retry.hidden=true;this.retry.addEventListener('click',()=>this.notifyMonth(true));
      this.dialog.append(top,nav,this.grid,this.loadStatus,this.retry,legend,note,help);root.append(this.dialog);
      this.dialog.addEventListener('cancel',event=>{event.preventDefault();this.close();});
      this.dialog.addEventListener('click',event=>{if(event.target!==this.dialog)return;const box=this.dialog.getBoundingClientRect();if(event.clientX<box.left||event.clientX>box.right||event.clientY<box.top||event.clientY>box.bottom)this.close();});
      this.dialog.addEventListener('keydown',event=>this.key(event));
      this.fields.forEach(field=>{
        const input=field.querySelector('input'),button=field.querySelector('[data-open-calendar]');
        button.setAttribute('aria-controls',this.id);button.setAttribute('aria-expanded','false');button.disabled=true;
        button.addEventListener('click',()=>this.open(field));input.addEventListener('input',()=>{this.sync();const value=parse(input.value);if(value)this.onMonthChange(iso(value).slice(0,7));});
      });
      this.clearAvailability();
    }
    static parse(value) {return parse(value);}
    static iso(value) {return iso(value);}
    static shiftMonth(value,amount) {return shiftMonth(value,amount);}
    static state(value,data) {return state(value,data);}
    get snapshotId() {return this.data?.snapshot_id;}
    clearAvailability(message='Loading date availability…') {
      this.close(false);this.data=null;this.message=message;this.sync();
    }
    setAvailability(data) {
      // Snapshot metadata is immutable; preserve focus in an already-open grid.
      if(this.snapshotId===data.snapshot_id){this.sync();return;}
      this.data={snapshot_id:data.snapshot_id,coverage:data.coverage,published_dates:data.published_dates,published:new Set(data.published_dates)};this.sync();
      if(this.dialog.open){const focused=document.activeElement?.matches('.history-calendar-day');this.render();if(focused)this.focusDay();}
    }
    sync() {
      this.fields.forEach(field=>{
        const input=field.querySelector('input'),button=field.querySelector('[data-open-calendar]'),status=field.querySelector('[data-date-status]');
        const valid=parse(input.value), current=valid?state(input.value,this.data):null;
        input.setCustomValidity(input.value&&!valid?'Enter a real date in YYYY-MM-DD format.':'');
        status.textContent=!valid?'Enter a date as YYYY-MM-DD.':!this.data?this.message:`${marks[current]} ${labels[current]} in this snapshot`;
        status.dataset.state=current||'unknown';button.disabled=!this.data;
        button.setAttribute('aria-label',`Open calendar for ${input.name==='first'?'first':'second'} observation date${valid?', '+input.value:''}`);
      });
    }
    open(field) {
      if(!this.data)return;
      this.field=field;this.input=field.querySelector('input');this.opener=field.querySelector('[data-open-calendar]');
      this.focusDate=parse(this.input.value)||parse(this.data.published_dates[0])||new Date();
      this.title.textContent=this.input.name==='first'?'First observation date':'Second observation date';
      this.opener.setAttribute('aria-expanded','true');this.render();this.dialog.showModal();this.focusDay();this.notifyMonth();
    }
    notifyMonth(force=false) {this.onMonthChange(iso(this.focusDate).slice(0,7),force);}
    setLoadStatus(message,retry=false) {this.loadStatus.textContent=message;this.retry.hidden=!retry;}
    close(restore=true) {
      if(!this.dialog.open)return;
      this.dialog.close();this.opener.setAttribute('aria-expanded','false');if(restore)this.opener.focus();
    }
    render() {
      const year=this.focusDate.getUTCFullYear(),month=this.focusDate.getUTCMonth();
      this.month.textContent=new Intl.DateTimeFormat('en-US',{month:'long',year:'numeric',timeZone:'UTC'}).format(this.focusDate);
      this.previous.disabled=year===1&&month===0;this.next.disabled=year===9999&&month===11;
      const first=day(year,month,1),start=1-first.getUTCDay();this.body.replaceChildren();
      for(let week=0;week<6;week++){
        const row=element('tr');
        for(let weekday=0;weekday<7;weekday++){
          const value=day(year,month,start+week*7+weekday),date=iso(value),cell=element('td');
          if(date){
            const current=state(date,this.data),button=element('button',undefined,'history-calendar-day');button.type='button';button.dataset.date=date;button.dataset.state=current;
            button.tabIndex=date===iso(this.focusDate)?0:-1;
            button.classList.toggle('other-month',value.getUTCMonth()!==month);
            cell.setAttribute('aria-selected',String(date===this.input.value));
            button.setAttribute('aria-label',`${new Intl.DateTimeFormat('en-US',{dateStyle:'full',timeZone:'UTC'}).format(value)} · ${labels[current]}${date===this.input.value?' · selected':''}`);
            const marker=element('span',marks[current],'history-calendar-mark');marker.setAttribute('aria-hidden','true');button.append(element('span',value.getUTCDate()),marker);
            button.addEventListener('focus',()=>{this.focusDate=value;this.grid.querySelectorAll('button').forEach(other=>other.tabIndex=other===button?0:-1);});
            button.addEventListener('click',()=>{this.input.value=date;this.input.dispatchEvent(new Event('input',{bubbles:true}));this.close();});cell.append(button);
          }
          row.append(cell);
        }
        this.body.append(row);
      }
    }
    focusDay() {this.body.querySelector('button[tabindex="0"]')?.focus();}
    moveMonth(amount,focus=false) {
      const next=shiftMonth(this.focusDate,amount);if(!iso(next))return;this.focusDate=next;this.render();if(focus)this.focusDay();this.notifyMonth();
    }
    key(event) {
      if(event.key==='Tab'){
        // Explicit cycling also covers browsers that skip buttons in their native Tab order.
        const stops=[...this.dialog.querySelectorAll('button:not(:disabled)')].filter(button=>!button.hidden&&button.tabIndex>=0);
        const index=stops.indexOf(document.activeElement),step=event.shiftKey?-1:1;
        event.preventDefault();stops[(index+step+stops.length)%stops.length].focus();return;
      }
      if(!event.target.matches('.history-calendar-day'))return;
      const moves={ArrowLeft:-1,ArrowRight:1,ArrowUp:-7,ArrowDown:7,Home:-this.focusDate.getUTCDay(),End:6-this.focusDate.getUTCDay()};
      if(event.key==='PageUp'||event.key==='PageDown'){
        event.preventDefault();this.moveMonth((event.key==='PageUp'?-1:1)*(event.shiftKey?12:1),true);
      }else if(Object.hasOwn(moves,event.key)){
        event.preventDefault();const previousMonth=iso(this.focusDate).slice(0,7);const next=day(this.focusDate.getUTCFullYear(),this.focusDate.getUTCMonth(),this.focusDate.getUTCDate()+moves[event.key]);if(!iso(next))return;this.focusDate=next;this.render();this.focusDay();if(iso(next).slice(0,7)!==previousMonth)this.notifyMonth();
      }
    }
  }
  window.FilabHistoryDates=HistoryDates;
})();
