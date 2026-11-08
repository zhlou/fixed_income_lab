/* Browser-owned observations. Python validates bytes, snapshots, and financial arithmetic. */
(() => {
  async function api(path, body) {
    const response = await fetch(`/api/history/${path}`, body === undefined ? {} : {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(typeof result.detail === 'string' ? result.detail : 'Invalid Treasury dataset.');
    return result;
  }
  const readRequest = request => new Promise((resolve, reject) => {
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
  const base64 = bytes => {
    let text = '';
    for (let i = 0; i < bytes.length; i += 32768) text += String.fromCharCode(...bytes.subarray(i, i + 32768));
    return btoa(text);
  };
  class HistoryStore {
    async open() {
      this.bundled = await api('bundled-archive');
      this.memory = new Map(this.bundled.snapshots.map(snapshot => [snapshot.id, snapshot]));
      try {
        const request = indexedDB.open('fixed-income-lab-history', 1);
        request.onupgradeneeded = () => {
          request.result.createObjectStore('snapshots', {keyPath: 'id'});
          request.result.createObjectStore('raw');
          request.result.createObjectStore('acquisitions', {autoIncrement: true});
        };
        this.db = await readRequest(request);
        this.db.onversionchange = () => this.db.close();
      } catch (_) {this.db = null;}
      return this;
    }
    async get(id) {
      if (this.memory.has(id)) return this.memory.get(id);
      const value = this.db && await readRequest(this.db.transaction('snapshots').objectStore('snapshots').get(id));
      if (!value) throw new Error('Dataset unavailable in this browser.');
      return value;
    }
    async list() {
      const saved = this.db ? await readRequest(this.db.transaction('snapshots').objectStore('snapshots').getAll()) : [];
      const values = new Map(this.memory);
      saved.forEach(snapshot => values.set(snapshot.id, snapshot));
      return [...values.values()].sort((a, b) => b.created_at.localeCompare(a.created_at)).map(s => ({
        id: s.id, created_at: s.created_at, coverage: s.coverage, row_count: Object.keys(s.rows).length,
        latest_observation: Object.keys(s.rows).sort().at(-1), label: s.label || 'Saved in this browser'
      }));
    }
    async save(archive) {
      if (!this.db) throw new Error('Browser storage is unavailable.');
      // One transaction publishes a full year range or import, including all raw bytes.
      await new Promise((resolve, reject) => {
        const tx = this.db.transaction(['snapshots', 'raw', 'acquisitions'], 'readwrite');
        tx.oncomplete = resolve;
        tx.onabort = tx.onerror = () => reject(tx.error || new Error('Browser storage is full or unavailable.'));
        const snapshots = tx.objectStore('snapshots');
        archive.snapshots.forEach(snapshot => {
          const request = snapshots.get(snapshot.id);
          request.onsuccess = () => {if (!request.result) snapshots.put(snapshot);};
          Object.values(snapshot.sources).forEach(source => tx.objectStore('acquisitions').add(source));
        });
        Object.entries(archive.raw).forEach(([hash, raw]) => tx.objectStore('raw').put(raw, hash));
      });
    }
    async export(id) {
      const snapshot = await this.get(id), raw = {};
      for (const source of Object.values(snapshot.sources)) {
        const hash = source.sha256;
        raw[hash] = this.bundled.raw[hash] || (this.db && await readRequest(this.db.transaction('raw').objectStore('raw').get(hash)));
        if (!raw[hash]) throw new Error('Raw source bytes are unavailable.');
      }
      return {schema_version: 1, snapshots: [snapshot], raw};
    }
    async import(archive) {
      const checked = await api('validate-archive', archive);
      await this.save(checked);
      return checked.snapshots[0].id;
    }
    async download(year, month, snapshot) {
      const period = month ? `${year}${String(month).padStart(2, '0')}` : String(year);
      const parameter = month ? 'field_tdr_date_value_month' : 'field_tdr_date_value';
      const url = `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&${parameter}=${period}`;
      const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 15000);
      try {
        const response = await fetch(url, {mode: 'cors', credentials: 'omit', signal: controller.signal});
        if (!response.ok || response.type === 'opaque') throw new Error('No data');
        const reader = response.body.getReader(), chunks = [];
        let length = 0;
        while (true) {
          const {done, value} = await reader.read();
          if (done) break;
          length += value.length;
          if (length > 4000000) {await reader.cancel();throw new Error('No data');}
          chunks.push(value);
        }
        const bytes = new Uint8Array(length);
        let offset = 0;
        chunks.forEach(chunk => {bytes.set(chunk, offset);offset += chunk.length;});
        const raw = base64(bytes), retrieved_at = new Date().toISOString();
        const result = await api('normalize', {snapshot, year, month, raw_base64: raw, retrieved_at});
        return {snapshot: result.snapshot, raw: {[result.sha256]: raw}};
      } finally {clearTimeout(timer);}
    }
    async month(year, month, id, force, currentYear, currentMonth) {
      const snapshot = await this.get(id), start = `${year}-${String(month).padStart(2, '0')}-01`;
      const end = `${year}-${String(month).padStart(2, '0')}-${new Date(Date.UTC(year, month, 0)).getUTCDate()}`;
      const complete = snapshot.coverage.some(([a, b]) => a <= start && end <= b);
      const recent = Object.values(snapshot.sources).some(source => {
        const coverage = source.coverage && (typeof source.coverage[0] === 'string' ? [source.coverage] : source.coverage);
        return coverage?.some(([a, b]) => a <= start && b >= start) && Date.now() - Date.parse(source.retrieved_at) < 3600000;
      });
      if (!force && (complete || year === currentYear && month === currentMonth && recent)) return snapshot;
      if (!force && !(year === currentYear && month === currentMonth)) {
        const candidate = (await this.list()).find(s => s.coverage.some(([a, b]) => a <= start && end <= b));
        if (candidate) {
          const merged = await api('overlay', {snapshot, patch: await this.get(candidate.id), year, month});
          await this.save({snapshots: [merged], raw: {}});
          return merged;
        }
      }
      const acquired = await this.download(year, month, snapshot);
      await this.save({snapshots: [acquired.snapshot], raw: acquired.raw});
      return acquired.snapshot;
    }
    async years(first, last, id, status) {
      let snapshot = await this.get(id);
      const raw = {};
      for (let year = first; year <= last; year++) {
        status(`Downloading ${year} (${year - first + 1}/${last - first + 1})…`);
        const acquired = await this.download(year, null, snapshot);
        snapshot = acquired.snapshot;
        Object.assign(raw, acquired.raw);
      }
      await this.save({snapshots: [snapshot], raw});
      return snapshot.id;
    }
    async dates(id) {
      const snapshot = await this.get(id);
      return {snapshot_id: id, coverage: snapshot.coverage, published_dates: Object.keys(snapshot.rows).sort()};
    }
    async compare(id, first, second, hypothetical_revision, signal) {
      const response = await fetch('/api/history/compare', {
        method: 'POST', headers: {'Content-Type': 'application/json'}, signal,
        body: JSON.stringify({snapshot: await this.get(id), first, second, hypothetical_revision})
      });
      if (!response.ok) throw new Error('Comparison unavailable.');
      return response.json();
    }
  }
  window.FilabHistoryStore = HistoryStore;
})();
