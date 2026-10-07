"""Build calendar.ics from program.json (RFC 5545, Europe/Amsterdam)."""
import json, pathlib, datetime as dt

ROOT = pathlib.Path(__file__).resolve().parent.parent
V = json.loads((ROOT / 'program.json').read_text(encoding='utf-8'))
C = {c['code']: c for c in V['courses']}
C['PRG'] = {'name': 'Programme', 'short': 'Programme'}
STAMP = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
NL = '\n'

VTIMEZONE = [
    'BEGIN:VTIMEZONE', 'TZID:Europe/Amsterdam',
    'BEGIN:DAYLIGHT', 'TZOFFSETFROM:+0100', 'TZOFFSETTO:+0200', 'TZNAME:CEST',
    'DTSTART:19700329T020000', 'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU', 'END:DAYLIGHT',
    'BEGIN:STANDARD', 'TZOFFSETFROM:+0200', 'TZOFFSETTO:+0100', 'TZNAME:CET',
    'DTSTART:19701025T030000', 'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU', 'END:STANDARD',
    'END:VTIMEZONE',
]


def escape(s):
    s = str(s).replace('\\', '\\\\').replace(';', '\\;').replace(',', '\\,')
    return s.replace(NL, '\\n')


def fold(line):
    """Fold lines longer than 75 octets without splitting a UTF-8 character."""
    if len(line.encode('utf-8')) <= 75:
        return line
    parts, cur, limit = [], '', 75
    for ch in line:
        if len((cur + ch).encode('utf-8')) > limit:
            parts.append(cur)
            cur, limit = '', 74
        cur += ch
    parts.append(cur)
    return '\r\n '.join(parts)


def ymd(s):
    return s.replace('-', '')


def next_day(s):
    return (dt.date.fromisoformat(s) + dt.timedelta(days=1)).strftime('%Y%m%d')


def event(uid, summary, description, date, start=None, end=None, until=None, location=None):
    L = ['BEGIN:VEVENT', f'UID:{uid}@unu-merit-calendar', f'DTSTAMP:{STAMP}', f'SUMMARY:{escape(summary)}']
    if start:
        if not end:
            h, m = map(int, start.split(':'))
            end = f'{h + 2:02d}:{m:02d}'
            description += NL + NL + 'End time not given in the sources; shown as two hours.'
        L.append(f'DTSTART;TZID=Europe/Amsterdam:{ymd(date)}T{start.replace(":", "")}00')
        L.append(f'DTEND;TZID=Europe/Amsterdam:{ymd(date)}T{end.replace(":", "")}00')
    else:
        L.append(f'DTSTART;VALUE=DATE:{ymd(date)}')
        L.append(f'DTEND;VALUE=DATE:{next_day(until or date)}')
        L.append('TRANSP:TRANSPARENT')
    if location:
        L.append(f'LOCATION:{escape(location)}')
    L.append(f'DESCRIPTION:{escape(description.strip())}')
    L.append('END:VEVENT')
    return L


def bullets(title, items):
    return NL + title + NL + NL.join(f'- {x}' for x in items)


out = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//unu-merit-calendar//EN', 'CALSCALE:GREGORIAN',
       'METHOD:PUBLISH', 'X-WR-CALNAME:UNU-MERIT Year 1 2026-27', 'X-WR-TIMEZONE:Europe/Amsterdam'] + VTIMEZONE
for s in V['sessions']:
    c = C[s['course']]
    r = s.get('readings', {})
    d = [f"{c['name']} · {s['number']} ({s['source_label']})", f"Lecturer: {s.get('lecturer') or '-'}"]
    if s.get('confidence') != 'HIGH':
        d.append('Date or time not confirmed: see notes.')
    d += [f'Note: {n}' for n in s.get('notes', [])]
    if r.get('required'):
        d.append(bullets('Required / core readings:', r['required']))
    if r.get('optional'):
        d.append(bullets('Optional:', r['optional']))
    if r.get('additional'):
        d.append(NL + f"Plus {len(r['additional'])} additional readings (see the website).")
    out += event(s['id'], f"{c['short']} {s['number']}: {s['title']}", NL.join(d), s['date'],
                 s.get('start'), s.get('end'), location=s.get('room'))
for t in V['deadlines']:
    if not t.get('date'):
        continue
    label = {'exam': 'EXAM', 'presentation': 'PRESENTATION'}.get(t['type'], 'DUE')
    d = C[t['course']]['name'] + NL + t['details'] + ('' if t['confidence'] == 'HIGH' else NL + 'Not confirmed.')
    out += event(t['id'], f"{label}: {t['title']}", d, t['date'])
for e in V['events']:
    out += event(e['id'], e['title'], e.get('details') or '', e['start'], until=e.get('end'))
out.append('END:VCALENDAR')
text = '\r\n'.join(fold(x) for x in out) + '\r\n'
(ROOT / 'calendar.ics').write_bytes(text.encode('utf-8'))
print('calendar.ics', out.count('BEGIN:VEVENT'), 'events')
