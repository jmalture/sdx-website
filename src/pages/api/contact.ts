/**
 * Contact form endpoint (the only server route; every page is static).
 * Rules carried over from our PHP themes: no CAPTCHA, honeypot + rate limit + strict validation,
 * store the enquiry before sending mail so a failed mail never loses a lead.
 *
 * Environment (Hostinger Node.js app settings):
 *   SMTP_HOST, SMTP_PORT (465 = TLS), SMTP_USER, SMTP_PASS, MAIL_FROM, MAIL_TO (comma separated)
 *   SUBMISSIONS_DIR (default ./data/submissions, outside the public folder)
 */
import type { APIRoute } from 'astro';
import { mkdir, appendFile } from 'node:fs/promises';
import path from 'node:path';
import nodemailer from 'nodemailer';
import messages from '../../i18n/form.json';

export const prerender = false;

type Lang = 'de' | 'en' | 'cs';
const env = (k: string) => process.env[k] ?? import.meta.env[k];
const hits = new Map<string, number[]>();
const LIMIT = 5; // per IP
const WINDOW = 10 * 60 * 1000; // 10 minutes

function msg(key: keyof typeof messages, lang: Lang) {
  return messages[key][lang] ?? messages[key].de;
}

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json; charset=utf-8' } });
}

export const POST: APIRoute = async ({ request, clientAddress }) => {
  const form = await request.formData().catch(() => null);
  const lang = (['de', 'en', 'cs'].includes(String(form?.get('lang'))) ? form!.get('lang') : 'de') as Lang;
  if (!form) return json({ ok: false, message: msg('form_error', lang) }, 400);

  // Honeypot: bots fill the hidden field. Pretend success, store nothing.
  if (String(form.get('form_fields[website_hp]') ?? '').trim() !== '')
    return json({ ok: true, message: msg('form_ok', lang) });

  const ip = clientAddress || request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() || 'unknown';
  const now = Date.now();
  const recent = (hits.get(ip) ?? []).filter((t) => now - t < WINDOW);
  if (recent.length >= LIMIT) return json({ ok: false, message: msg('form_error', lang) }, 429);
  recent.push(now);
  hits.set(ip, recent);

  const email = String(form.get('form_fields[email]') ?? '')
    .trim()
    .slice(0, 200);
  const phone = String(form.get('form_fields[phone]') ?? '')
    .trim()
    .slice(0, 50);
  const message = String(form.get('form_fields[message]') ?? '')
    .trim()
    .slice(0, 5000);
  const consent = form.get('form_fields[consent]') != null;
  const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
  if (!emailOk || !consent || (phone && !/^[0-9()#&+*\-=. ]+$/.test(phone))) {
    return json({ ok: false, message: msg('form_invalid', lang) }, 422);
  }

  const entry = {
    at: new Date().toISOString(),
    lang,
    email,
    phone,
    message,
    page: request.headers.get('referer') ?? '',
    ip,
    userAgent: request.headers.get('user-agent') ?? '',
    mail: 'pending',
  };
  const dir = env('SUBMISSIONS_DIR') || path.join(process.cwd(), 'data', 'submissions');
  try {
    await mkdir(dir, { recursive: true });
    await appendFile(path.join(dir, `${entry.at.slice(0, 7)}.jsonl`), JSON.stringify(entry) + '\n');
  } catch (e) {
    console.error('[contact] store failed', e);
  }

  try {
    const transport = nodemailer.createTransport({
      host: env('SMTP_HOST'),
      port: Number(env('SMTP_PORT') || 465),
      secure: Number(env('SMTP_PORT') || 465) === 465,
      auth: { user: env('SMTP_USER'), pass: env('SMTP_PASS') },
    });
    await transport.sendMail({
      from: env('MAIL_FROM') || env('SMTP_USER'),
      to: env('MAIL_TO'),
      replyTo: email,
      subject: `Neue Demo-Anfrage über sdx-app.com (${lang.toUpperCase()})`,
      text: `E-Mail: ${email}\nTelefon: ${phone || '-'}\nSprache: ${lang}\nSeite: ${entry.page}\n\n${message || '(keine Nachricht)'}\n`,
    });
    await appendFile(
      path.join(dir, `${entry.at.slice(0, 7)}.jsonl`),
      JSON.stringify({ at: entry.at, mail: 'sent' }) + '\n',
    ).catch(() => {});
  } catch (e) {
    console.error('[contact] mail failed', e);
    // the enquiry is stored; still tell the visitor it arrived
  }
  return json({ ok: true, message: msg('form_ok', lang) });
};
