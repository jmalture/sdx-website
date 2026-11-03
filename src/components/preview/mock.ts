/**
 * Shared helpers of the Preview page: the six file kinds and the HTML of their rendered mini previews.
 * Used by the hero, formats, views, fullscreen, details, audit, widget and use-case sections.
 * Everything drawn here is an illustrative mock-up (no real screenshots); texts come from src/i18n/preview.json (keys "mock_*").
 */
export type Kind = 'pdf' | 'xlsx' | 'pptx' | 'json' | 'txt' | 'mp4' | 'cad';

/** Order of the files in every file list of the page. */
export const KINDS: Kind[] = ['pdf', 'xlsx', 'pptx', 'json', 'mp4', 'txt'];

export const COLORS: Record<Kind, string> = {
  pdf: '#F04438',
  xlsx: '#1A9B4B',
  pptx: '#F59000',
  json: '#8E10C0',
  txt: '#5B6475',
  mp4: '#0A9BD6',
  cad: '#2A73FF',
};

export const LABELS: Record<Kind, string> = {
  pdf: 'PDF',
  xlsx: 'XLSX',
  pptx: 'PPTX',
  json: 'JSON',
  txt: 'TXT',
  mp4: 'MP4',
  cad: 'DWG',
};

type T = Record<string, string>;

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function fileName(kind: Kind, t: T) {
  return t[`mock_f_${kind}`];
}

/** Small coloured file type badge. */
export function ft(kind: Kind) {
  return `<span class="spv-ft" style="--c:${COLORS[kind]}" aria-hidden="true">${LABELS[kind]}</span>`;
}

/** Rendered mini preview of one file kind. The wrapper fills its .spv-stage parent. */
export function pv(kind: Kind, t: T, on = false) {
  const cls = `spv-pv spv-pv-${kind}${on ? ' is-on' : ''}`;
  const e = (k: string) => esc(t[k]);
  let body = '';
  if (kind === 'pdf') {
    body = `<div class="pg"><div class="hd"><b class="lg">SDX GmbH</b><span>${e('mock_inv_title')}</span></div>
<dl><div><dt>${e('mock_inv_no')}</dt><dd>RE-2026-0412</dd></div><div><dt>${e('mock_inv_period')}</dt><dd>${e('mock_inv_period_val')}</dd></div></dl>
<div class="ls"><i class="w90"></i><i class="w70"></i><i class="w80"></i><i class="w90"></i><i class="w60"></i><i class="w80"></i></div>
<div class="tot"><span>${e('mock_inv_amount')}</span><b>${e('mock_inv_amount_val')}</b></div></div>
<span class="pn" aria-hidden="true">1 / 2</span>`;
  } else if (kind === 'xlsx') {
    const rows = [
      [e('mock_x_r1'), '12.4', '14.1', '+1.7'],
      [e('mock_x_r2'), '8.0', '7.6', '-0.4'],
      [e('mock_x_r3'), '5.3', '6.9', '+1.6'],
      [e('mock_x_r4'), '3.1', '3.1', '0.0'],
    ];
    body = `<div class="gr"><span class="co"></span><span class="co">A</span><span class="co">B</span><span class="co">C</span><span class="co">D</span>
<span class="rn">1</span><b>${e('mock_x_h1')}</b><b>Q3</b><b>Q4</b><b>${e('mock_x_h4')}</b>
${rows
  .map(
    (r, i) =>
      `<span class="rn">${i + 2}</span>${r.map((c, j) => `<span${i === 2 && j === 2 ? ' class="sel"' : j > 0 ? ' class="nu"' : ''}>${j > 0 ? c.replace('.', t.mock_dec) : c}</span>`).join('')}`,
  )
  .join('')}</div>
<div class="tb"><span class="on">${e('mock_x_tab1')}</span><span>${e('mock_x_tab2')}</span></div>`;
  } else if (kind === 'pptx') {
    body = `<div class="th" aria-hidden="true"><i class="on"></i><i></i><i></i></div>
<div class="sl"><b>${e('mock_p_title')}</b><span>${e('mock_p_sub')}</span><div class="ch" aria-hidden="true"><i style="--h:38%"></i><i style="--h:62%"></i><i style="--h:50%"></i><i style="--h:86%"></i></div></div>
<span class="pn" aria-hidden="true">2 / 12</span>`;
  } else if (kind === 'json') {
    body = `<pre class="cd" aria-label="${e('mock_json_label')}"><code><span class="k0">{</span>
  <span class="k">"name"</span>: <span class="s">"export-config"</span>,
  <span class="k">"version"</span>: <span class="n">3</span>,
  <span class="k">"active"</span>: <span class="b">true</span>,
  <span class="k">"targets"</span>: [<span class="s">"archive"</span>],
  <span class="k">"owner"</span>: <span class="s">"${e('mock_json_owner')}"</span>
<span class="k0">}</span></code></pre>`;
  } else if (kind === 'txt') {
    body = `<div class="tx"><b>${e('mock_t_title')}</b><p>${e('mock_t_l1')}</p><p>${e('mock_t_l2')}</p><p>${e('mock_t_l3')}</p><p class="mu">${e('mock_t_l4')}</p></div>`;
  } else if (kind === 'mp4') {
    body = `<div class="vd" aria-hidden="true"><span class="pl"><svg viewBox="0 0 24 24"><path d="M8 5.5v13l11-6.5z"/></svg></span>
<span class="wv"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span></div>
<div class="bar"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg><span class="tr"><i></i></span><em>0:42 / 2:10</em></div>`;
  } else {
    body = `<div class="cv" aria-hidden="true"><svg viewBox="0 0 160 100"><path d="M18 14h124v72H18z"/><path d="M18 50h58M76 14v36M76 50v36M104 50h38M104 50v36"/><path d="M60 14h12M104 62h12" class="dr"/><circle cx="46" cy="32" r="8"/></svg></div>
<span class="pn" aria-hidden="true">${e('mock_cad_label')}</span>`;
  }
  return `<div class="${cls}" data-k="${kind}">${body}</div>`;
}
