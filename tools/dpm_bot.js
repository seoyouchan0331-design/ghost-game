// 실행: rebuild로 play/helm-test.html을 만든 뒤 node tools/dpm_bot.js <play 폴더의 부모> '[{"id":"thief","st":2,"combo":[0,1]}]'  (SECS=60 기본, v: spam|charge|focus 사냥꾼, souls: 처형인 원혼)
// 허수아비 DPM 자동 측정: 투구·단계·스킬 조합마다 게임 시간을 빠르게 돌리며 최선의 운영을 흉내 낸다
const { chromium } = require('playwright');
const SECS = +(process.env.SECS || 60);
(async () => {
  const b = await chromium.launch(); const errs = [];
  const setup = async () => { const pg = await b.newPage({ viewport: { width: 960, height: 540 } }); pg.on('pageerror', e => errs.push(e.message));
  await pg.goto('file://' + process.argv[2] + '/play/helm-test.html'); await pg.waitForTimeout(1200);
  await pg.evaluate(() => {
    window.__run = (id, st, combo, variant, secs, souls) => {
      tEquip(id, st); const p = player; p.invuln = 1e9; p.gold = 999999;
      if (combo) { p.skPick = p.skPick || {}; p.skPick[id] = combo; }
      p.cds[id] = [0, 0]; p.execSouls = souls || 0; p.x = 160; p.dir = 1; p.act = null;
      dummyStart(); DUMMY.dur = 1e9; const e = DUMMY.e; e.x = e.minX = e.maxX = 300;
      let total = 0; const by = {}; const old = window.__onDmg;
      window.__onDmg = (q, d, tag) => { if (q === e) { total += d; by[tag] = (by[tag] || 0) + d; } };
      const ranged = id === 'hunter', D = ranged ? 170 : 22, steps = Math.round(secs / STEP);
      const helm = p.helm, cds = cdsOf(id);
      for (let i = 0; i < steps; i++) {
        e.hp = e.maxHp; p.invuln = 1e9; p.hp = p.maxHp ?? p.hp;
        const a = p.act;
        if (a) {
          if (a.wm === 'stance' && p.skKey) keys[p.skKey] = a.t < 1.37;
        } else if (!p.dashing) {
          const want = e.x - D; if (Math.abs(p.x - want) > 4 && !(keys.KeyX && ranged)) p.x = want; p.dir = 1;
          const sOk = !sLocked(id);
          if (variant === 'focus' && hgOf('hunter') >= 1) {
            if (!p.drawFull) keys.KeyX = true;
            else if (cds[0] <= 0) { keys.KeyX = false; p.drawT = p.drawT; pressed.KeyA = 1; }
            else if (sOk && cds[1] <= 0) { keys.KeyX = false; pressed.KeyS = 1; }
            else keys.KeyX = false;
          } else if (variant === 'charge' && hgOf('hunter') >= 1) {
            if (cds[0] <= 0) { keys.KeyX = false; pressed.KeyA = 1; } else if (sOk && cds[1] <= 0) { keys.KeyX = false; pressed.KeyS = 1; } else keys.KeyX = !p.drawFull;
          } else {
            keys.KeyX = false;
            const SD = { '금화 던지기': 75 }, k = cds[0] <= 0 ? 0 : sOk && cds[1] <= 0 ? 1 : -1;
            if (k >= 0) { const nm = helm.skills[k].name; if (SD[nm]) p.x = e.x - SD[nm]; pressed[k ? 'KeyS' : 'KeyA'] = 1; } else pressed.KeyX = 1;
          }
        }
        update(STEP); if (i % 2 === 0) render();
        if (i % 240 === 0) { texts.length = 0; if (objs.length > 300) objs = objs.filter((o) => o.kind !== 'blood' && o.kind !== 'coin'); }
      }
      for (const k in keys) keys[k] = false; window.__onDmg = old;
      return { dpm: Math.round(total / secs * 60), by: Object.fromEntries(Object.entries(by).map(([k, v]) => [k, Math.round(v / secs * 60)])), names: helm.skills.map((s) => s.name) };
    };
  }); return pg; };
  const jobs = JSON.parse(process.argv[3]); const out = [];
  for (const j of jobs) { const t0 = Date.now(); const pg = await setup(); const r = await pg.evaluate(([j, S]) => window.__run(j.id, j.st, j.combo, j.v, S, j.souls), [j, SECS]); out.push({ ...j, ...r, wall: Date.now() - t0 }); console.error(JSON.stringify(out[out.length - 1])); await pg.close(); }
  console.log(JSON.stringify(out)); if (errs.length) console.error('ERR', errs.slice(0, 3)); await b.close();
})();
