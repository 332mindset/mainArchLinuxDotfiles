#!/usr/bin/env python3
"""Live, SVG-rendered Hyprlock cards. Only runs for the lifetime of the lock."""

import argparse
import ast
import base64
import calendar
import concurrent.futures
import datetime as dt
import fcntl
import html
import json
import math
import mimetypes
import os
from pathlib import Path
import re
import signal
import subprocess
import threading
import time
import textwrap
import tempfile
from urllib.parse import unquote, urlparse
from urllib.request import urlopen

HOME = Path.home()
ROOT = HOME / '.config/hypr'
ASSETS = ROOT / 'assets/hyprlock/dashboard'
RUNTIME = Path(os.environ.get('XDG_CACHE_HOME', HOME / '.cache')) / 'hyprlock-dashboard'
FONT = 'JetBrainsMono Nerd Font'
W, H = 1240, 306
# Catppuccin Mocha: text, subtext0, mauve
FG, MUTED, ACCENT = '#cdd6f4', '#a6adc8', '#cba6f7'
PANELS = [(0,0,314,H),(332,0,294,H),(644,0,288,H),(950,0,290,96),(950,114,290,192)]
NOTIFICATIONS = []
ICONS = {
    'music': '<path d="M9 18V5l12-3v13M9 8l12-3"/><ellipse cx="6" cy="18" rx="3" ry="3"/><ellipse cx="18" cy="15" rx="3" ry="3"/>',
    'previous': '<path d="M5 5v14M19 5L7 12l12 7z"/>',
    'next': '<path d="M19 5v14M5 5l12 7-12 7z"/>',
    'play': '<path d="M8 5l11 7-11 7z"/>',
    'pause': '<path d="M8 5v14M16 5v14"/>',
    'volume': '<path d="M11 4L5 9H2v6h3l6 5zM15 8q5 4 0 8M18 4q9 8 0 16"/>',
    'bell': '<path d="M5 16h14l-2-3V9a5 5 0 0 0-10 0v4zM10 20h4"/>',
    'trash': '<path d="M3 6h18M9 6V3h6v3M6 6l1 15h10l1-15M10 10v7M14 10v7"/>',
    'lock': '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V6a4 4 0 0 1 8 0v4"/>',
    'logout': '<path d="M10 3H4v18h6M10 12h12M17 7l5 5-5 5"/>',
    'reboot': '<path d="M20 7v5h-5M4 17v-5h5M5 7a8 8 0 0 1 13-2l2 3M4 16l2 3a8 8 0 0 0 13-2"/>',
    'power': '<path d="M12 2v10M6 5a9 9 0 1 0 12 0"/>',
    'left': '<path d="M15 5l-7 7 7 7"/>',
    'right': '<path d="M9 5l7 7-7 7"/>',
}


def run(args, timeout=1):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return p.stdout.rstrip('\r\n') if p.returncode == 0 else ''
    except (OSError, subprocess.TimeoutExpired):
        return ''


def atomic_text(path, value):
    # Concurrent clicks must never replace another writer's temporary file.
    with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,prefix=path.name+'.',delete=False) as handle:
        handle.write(value)
        tmp=Path(handle.name)
    try:
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


def svg_document(body, width=W, height=H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
            f'<g font-family="{FONT}" fill="{FG}">{body}</g></svg>')


def png(svg, path, width=None):
    args = ['rsvg-convert', '--format=png', '--output', str(path) + '.tmp']
    if width:
        args += ['--width', str(width)]
    subprocess.run(args, input=svg.encode(), check=True, timeout=10, capture_output=True)
    Path(str(path) + '.tmp').replace(path)


def text(x, y, value, size=12, color=FG, anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}">{html.escape(str(value))}</text>'


def rect(x, y, w, h, fill='#1e1e2e', opacity=.67, radius=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" fill-opacity="{opacity}"/>'


def icon(name, x, y, size=20, color=FG):
    return f'<g transform="translate({x} {y}) scale({size/24})" fill="none" stroke="{color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</g>'


def trim(value, length):
    value = ' '.join(str(value).split())
    return value if len(value) <= length else value[:length-1] + '…'


def russian_date():
    now=dt.datetime.now()
    days=['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота','Воскресенье']
    months=['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
    return f'{days[now.weekday()]}, {now.day} {months[now.month-1]}'


def glass(x,y,w,h):
    return (rect(x,y,w,h,'#1e1e2e',.45,14)+
            f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="14" fill="none" stroke="#ffffff" stroke-opacity=".10"/>')


def bar(x, y, w, fraction, height=4, color=FG):
    fraction = max(0, min(1, fraction))
    return rect(x,y,w,height,'#ffffff',.13,height/2) + (rect(x,y,w*fraction,height,color,1,height/2) if fraction else '')


def bus(method):
    output = run(['busctl','--user','--json=short','call','org.erikreider.swaync',
                  '/org/erikreider/swaync/cc','org.erikreider.swaync.cc',method], .5)
    try:
        return json.loads(output)['data'][0]
    except (ValueError, KeyError, IndexError, TypeError):
        return None


def media():
    fmt = '{{status}}\t{{playerName}}\t{{xesam:title}}\t{{xesam:artist}}\t{{position}}\t{{mpris:length}}\t{{mpris:artUrl}}'
    rows = run(['playerctl','--all-players','metadata','--format',fmt], .6).splitlines()
    rows.sort(key=lambda row: not row.startswith('Playing\t'))
    if not rows:
        return {}
    values = rows[0].split('\t',6)
    if len(values) != 7:
        return {}
    result = dict(zip(('status','player','title','artist','position','length','art'), values))
    for key in ('position','length'):
        try:
            result[key] = max(0,float(result[key]) / 1_000_000)
            if not math.isfinite(result[key]):
                result[key]=0
        except ValueError:
            result[key] = 0
    return result


def volume():
    output = run(['wpctl','get-volume','@DEFAULT_AUDIO_SINK@'], .5)
    match = re.search(r'Volume:\s*([\d.]+)',output)
    return (float(match[1]), 'MUTED' in output) if match else (None, False)


def gpu():
    result = run(['nvidia-smi','--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu',
                  '--format=csv,noheader,nounits'], .8)
    try:
        name, load, used, total, temp = result.splitlines()[0].split(', ')
        return dict(name=name, load=float(load),used=float(used),total=float(total),temp=float(temp))
    except (ValueError, IndexError):
        pass
    for device in sorted(Path('/sys/class/drm').glob('card[0-9]*/device')):
        try:
            return dict(name='GPU',load=float((device/'gpu_busy_percent').read_text()),
                        used=int((device/'mem_info_vram_used').read_text())/2**20,
                        total=int((device/'mem_info_vram_total').read_text())/2**20,temp=None)
        except (OSError, ValueError):
            continue
    return dict(name='GPU недоступен',load=None,used=None,total=None,temp=None)


def cpu_sample():
    values = list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:9]))
    return sum(values), sum(values[3:5])


def system(previous):
    sample = cpu_sample()
    delta = sample[0] - previous[0]
    load = 100*(1-(sample[1]-previous[1])/delta) if delta else 0
    memory = {k:int(v.split()[0]) for k,v in
              (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines())}
    total = memory['MemTotal']/2**20
    available = memory['MemAvailable']/2**20
    temp = None
    for hw in Path('/sys/class/hwmon').glob('hwmon*'):
        try:
            if (hw/'name').read_text().strip() in ('k10temp','coretemp'):
                temp = int((hw/'temp1_input').read_text())/1000
        except (OSError,ValueError):
            pass
    return sample, dict(cpu=max(0,min(100,load)),total=total,used=total-available,
                        available=available,mem=100*(1-available/total),temp=temp,
                        uptime=int(float(Path('/proc/uptime').read_text().split()[0])))


def image_uri(path):
    mime = mimetypes.guess_type(str(path))[0] or 'image/png'
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()


def album_art(url):
    if not url:
        return ''
    try:
        parsed = urlparse(url)
        if parsed.scheme == 'file':
            path = Path(unquote(parsed.path))
            if path.stat().st_size < 8*1024*1024:
                return image_uri(path)
        if parsed.scheme == 'https':
            with urlopen(url,timeout=2) as response:
                data = response.read(8*1024*1024+1)
                mime = response.headers.get_content_type()
            if len(data) <= 8*1024*1024 and mime in ('image/jpeg','image/png','image/webp'):
                return f'data:{mime};base64,' + base64.b64encode(data).decode()
    except (OSError, ValueError):
        pass
    return ''


def ring(x,y,value,label):
    radius = 25
    length = 2*math.pi*radius
    s = f'<circle cx="{x}" cy="{y}" r="{radius}" fill="none" stroke="#ffffff" stroke-opacity=".12" stroke-width="5"/>'
    if value is not None:
        s += f'<circle cx="{x}" cy="{y}" r="{radius}" fill="none" stroke="{ACCENT}" stroke-width="5" stroke-linecap="round" stroke-dasharray="{length*min(100,max(0,value))/100} {length}" transform="rotate(-90 {x} {y})"/>'
    return s + text(x,y+4,f'{value:.0f}%' if value is not None else '—',12,FG,'middle') + text(x,y+46,label,10,MUTED,'middle')


def clock_time(seconds):
    return f'{int(seconds)//60}:{int(seconds)%60:02}'


def board(state, panels=True):
    music, stats, graphics = state['music'],state['system'],state['gpu']
    s = ''.join(glass(*p) for p in PANELS) if panels else ''
    s += text(20,28,'Сейчас играет',11,MUTED) + icon('music',275,14,18,ACCENT)
    s += rect(20,49,84,84,'#313244',.75,8)
    if state.get('art'):
        s += f'<defs><clipPath id="cover"><rect x="20" y="49" width="84" height="84" rx="8"/></clipPath></defs><image x="20" y="49" width="84" height="84" preserveAspectRatio="xMidYMid slice" clip-path="url(#cover)" xlink:href="{state["art"]}"/>'
    else:
        s += icon('music',45,74,34,MUTED)
    title=music.get('title') or ('Без названия' if music else 'Нет активного плеера')
    lines=textwrap.wrap(' '.join(title.split()),width=22) or ['Без названия']
    if len(lines)>2:
        lines=lines[:2]
        lines[1]=trim(lines[1],21).rstrip('…')+'…'
    for i,line in enumerate(lines):
        s += text(120,75+i*18,line,12)
    s += text(120,114,trim(music.get('artist') or 'Запусти музыку перед блокировкой',25),10,MUTED)
    s += text(120,134,trim(music.get('player','MPRIS'),23),9,ACCENT)
    position,length = music.get('position',0),music.get('length',0)
    s += bar(20,164,274,position/length if length else 0)
    s += text(20,187,clock_time(position),9,MUTED)+text(294,187,clock_time(length),9,MUTED,'end')
    for name,x in [('previous',86),('pause' if music.get('status')=='Playing' else 'play',151),('next',216)]:
        s += icon(name,x,224,24)
    now = dt.datetime.now()
    offset = state.get('month_offset',0)
    year, month0 = divmod(now.year*12+now.month-1+offset,12)
    month = month0+1
    months = ['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
    s += text(352,28,f'{months[month-1]} {year}',11,MUTED)+icon('left',563,17,14)+icon('right',592,17,14)
    for i,day in enumerate(['Пн','Вт','Ср','Чт','Пт','Сб','Вс']):
        s += text(370+i*35,60,day,9,MUTED,'middle')
    for row,week in enumerate(calendar.monthcalendar(year,month)):
        for column,day in enumerate(week):
            if not day:
                continue
            x,y=370+column*35,92+row*31
            today = (year,month,day)==(now.year,now.month,now.day)
            if today:
                s += f'<circle cx="{x}" cy="{y-4}" r="13" fill="{ACCENT}"/>'
            s += text(x,y,day,11,'#11111b' if today else FG,'middle')
    s += text(664,28,'Система',11,MUTED)
    s += ring(708,79,stats['cpu'],'CPU')+ring(788,79,stats['mem'],'RAM')+ring(868,79,graphics['load'],'GPU')
    s += rect(664,148,120,65,'#ffffff',.055,7)+rect(792,148,120,65,'#ffffff',.055,7)
    s += text(674,164,'RAM',8,MUTED)+text(674,181,f'{stats["used"]:.1f} / {stats["total"]:.1f} GB',9)
    s += bar(674,190,100,stats['mem']/100,3,ACCENT)+text(674,205,f'Свободно {stats["available"]:.1f} GB',7,MUTED)
    s += text(802,164,'VRAM',8,MUTED)
    used,total=graphics['used'],graphics['total']
    s += text(802,181,f'{used:.0f} / {total:.0f} MB' if total else 'Нет данных',9)
    s += bar(802,190,100,used/total if total else 0,3,ACCENT)
    s += text(802,205,f'GPU {graphics["temp"]:.0f}°C' if graphics['temp'] is not None else 'GPU —',7,MUTED)
    s += text(664,250,trim(state['cpu_name'],33),9)
    s += text(664,269,trim(graphics['name'],33),9,MUTED)
    uptime=stats['uptime']
    temperature = f'  ·  {stats["temp"]:.0f}°C' if stats['temp'] is not None else ''
    s += text(664,287,f'Up {uptime//3600}h {uptime%3600//60}m'+temperature,9,MUTED)
    vol,muted=state['volume']
    s += text(970,28,'Громкость',11,MUTED)+text(1220,28,'MUTE' if muted else f'{vol*100:.0f}%' if vol is not None else '—',11,MUTED,'end')
    s += icon('volume',972,50,20,MUTED if muted else FG)
    s += bar(1006,55,178,0 if muted else vol or 0,12)
    s += text(1006,84,'−',15,MUTED)+text(1184,84,'+',15,MUTED,'end')
    s += text(1213,67,'×' if muted else '',18,MUTED,'middle')
    count=state['count']
    s += text(970,143,f'Уведомления  ·  {count if count is not None else "—"}',10,MUTED)
    s += icon('bell',1176,130,14,ACCENT if state['dnd'] else FG)+icon('trash',1205,130,14)
    if not NOTIFICATIONS or count == 0:
        s += icon('bell',1079,182,31,MUTED)
        message = f'В центре уведомлений: {count}' if count else 'Пока нет уведомлений' if count == 0 else 'Центр уведомлений недоступен'
        s += text(1095,244,message,10,MUTED,'middle')
        subtitle='Не беспокоить' if state['dnd'] else 'Новые сообщения появятся здесь' if count else 'SwayNC'
        s += text(1095,268,subtitle,9,MUTED,'middle')
    else:
        for i,item in enumerate(NOTIFICATIONS[:2]):
            y=157+i*69
            s += rect(970,y,250,59,'#ffffff',.055,6)+icon('bell',980,y+12,19,ACCENT)
            s += text(1009,y+19,trim(item['app'],26),10)
            s += text(1009,y+36,trim(item['summary'],29),9,MUTED)
            s += text(1009,y+50,f'{max(0,int(time.time()-item["time"]))//60} мин. назад',7,MUTED)
    return svg_document(s)


def monitor_notifications(stop):
    """Read only notifications arriving while locked; keep no message history on disk."""
    try:
        proc = subprocess.Popen(['dbus-monitor','--session',"type='method_call',interface='org.freedesktop.Notifications',member='Notify'"],
                                stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
    except OSError:
        return
    def terminate():
        stop.wait()
        if proc.poll() is None:
            proc.terminate()
    threading.Thread(target=terminate,daemon=True).start()
    fields=[]
    try:
        for line in proc.stdout:
            if stop.is_set():
                break
            if line.startswith('method call'):
                fields=[]
            match = re.match(r'\s+string (".*")\s*$',line)
            if match:
                try:
                    fields.append(ast.literal_eval(match[1]))
                except (ValueError,SyntaxError):
                    continue
                if len(fields)==4:
                    NOTIFICATIONS.insert(0,dict(app=fields[0],summary=fields[2],time=time.time()))
                    del NOTIFICATIONS[2:]
    finally:
        if proc.poll() is None:
            proc.terminate()
        proc.wait(timeout=2)


def wallpaper():
    state = HOME / '.local/state/wallpaper/current.json'
    try:
        path = Path(json.loads(state.read_text())['path'])
        if path.is_file():
            return path
    except (OSError,ValueError,KeyError,TypeError):
        pass
    return ROOT/'assets/hyprlock/elliot.jpeg'


def monitors():
    try:
        found=json.loads(run(['hyprctl','monitors','-j']))
        if found:
            outputs=[]
            for m in found:
                if m.get('disabled'):
                    continue
                width,height=m['width'],m['height']
                if m.get('transform',0)%2:
                    width,height=height,width
                outputs.append((m['name'],width/m.get('scale',1),height/m.get('scale',1)))
            if outputs:
                return outputs
    except (ValueError,KeyError,TypeError):
        pass
    return [('DVI-D-1',1920,1080),('HDMI-A-1',1366,768)]


def widget(kind, values):
    return kind+' {\n'+''.join(f'    {k} = {v}\n' for k,v in values.items())+'}\n\n'


def layout(outputs, destination):
    config = '# Generated by lock-dashboard.py; native PAM password field.\n'
    config += widget('general',dict(hide_cursor='false',ignore_empty_input='true'))
    config += 'animations {\n    enabled = true\n    bezier = smooth, 0.16, 1, 0.3, 1\n    animation = fadeIn, 1, 4, smooth\n    animation = fadeOut, 1, 3, smooth\n}\n\n'
    # Keep wallpaper underneath as a fallback if compositor screencopy is unavailable.
    background=dict(monitor='',color='rgba(11111bff)',blur_passes=4,blur_size=10,brightness=.75,contrast=.90,noise=.006,vibrancy=.06)
    config += widget('background',dict(background,path=str(wallpaper()),zindex=-4))
    config += widget('background',dict(background,path='screenshot',color='rgba(00000000)',zindex=-3))
    config += widget('shape',dict(monitor='',size='100%, 100%',position='0, 0',halign='center',valign='center',rounding=0,color='rgba(11111b59)',zindex=-2))
    helper = '~/.config/hypr/scripts/lock-dashboard.py'
    for name,width,height in outputs:
        scale=min((width-96)/W,height/840,1.4)
        n=lambda value:round(value*scale)
        common=dict(monitor=name,halign='center',valign='center')
        config += widget('label',dict(common,text='$TIME',font_family=FONT+' Light',font_size=n(90),color='rgba(cdd6f4ff)',position=f'0, {n(295)}',zindex=2))
        config += widget('label',dict(common,text=f'cmd[update:60000] {helper} --date',font_family=FONT,font_size=n(14),color='rgba(a6adc8ff)',position=f'0, {n(220)}',zindex=2))
        for x,y,w,h in PANELS:
            config += widget('shape',dict(common,size=f'{n(w)}, {n(h)}',position=f'{n(x+w/2-W/2)}, {n(H/2-y-h/2-26)}',color='rgba(1e1e2e73)',rounding=n(14),border_size=1,border_color='rgba(ffffff19)',zindex=0))
        config += widget('image',dict(common,path=str(ASSETS/'cards.png'),size=n(H),rounding=0,border_size=0,reload_time=1,position=f'0, {n(-26)}',zindex=1))
        # Coordinates share the SVG's center and scale, so clicks follow each monitor.
        def target(x,y,w,h,action):
            return widget('shape',dict(common,size=f'{n(w)}, {n(h)}',position=f'{n(x-W/2)}, {n(H/2-y-26)}',color='rgba(00000000)',rounding=5,zindex=4,onclick=f'{helper} --action {action}'))
        for x,action in [(98,'previous'),(163,'play-pause'),(228,'next')]:
            config += target(x,236,44,44,action)
        config += target(570,24,26,28,'month-previous')+target(599,24,26,28,'month-next')
        config += target(1183,137,24,24,'dnd')+target(1212,137,24,24,'clear')
        config += target(982,60,30,32,'mute')+target(1010,82,28,20,'volume-down')+target(1178,82,28,20,'volume-up')
        for i in range(11):
            config += target(1006+(i+.5)*178/11,60,178/11-1,18,f'volume-set-{i*10}')
        config += widget('input-field',dict(common,size=f'{n(290)}, {n(46)}',position=f'0, {n(-245)}',outline_thickness=1,outer_color='rgba(ffffff26)',inner_color='rgba(1e1e2e73)',font_color='rgba(cdd6f4ff)',check_color='rgba(cba6f7ff)',fail_color='rgba(f38ba8ff)',capslock_color='rgba(f9e2afff)',font_family=FONT,font_size=n(12),placeholder_text='Пароль',check_text='Проверка…',fail_text='Неверный пароль',fade_on_empty='false',rounding=n(14),dots_size=.17,dots_spacing=.3,dots_center='true',zindex=3))
        config += widget('label',dict(common,text='$LAYOUT[EN,RU]',font_family=FONT,font_size=n(9),color='rgba(7f849cff)',position=f'0, {n(-283)}',zindex=2))
        config += widget('image',dict(common,path=str(ASSETS/'dock.png'),size=n(56),rounding=0,border_size=0,position=f'0, {n(-336)}',zindex=3))
        for i,action in enumerate([None,'logout','reboot','poweroff']):
            x=n(-105+i*70)
            config += widget('shape',dict(common,size=f'{n(56)}, {n(56)}',position=f'{x}, {n(-336)}',color='rgba(1e1e2e73)',rounding=n(17),border_size=1,border_color='rgba(ffffff19)',zindex=1))
            if action:
                config += widget('shape',dict(common,size=f'{n(56)}, {n(56)}',position=f'{x}, {n(-336)}',color='rgba(00000000)',rounding=n(17),zindex=4,onclick=f'{helper} --action {action}'))
        config += widget('label',dict(common,text=f'cmd[update:1000] cat {RUNTIME}/hint',font_family=FONT,font_size=n(9),color='rgba(7f849cff)',position=f'0, {n(-386)}',zindex=2))
    atomic_text(destination,config)


def action(name):
    RUNTIME.mkdir(mode=0o700,parents=True,exist_ok=True)
    if name in ('previous','next','play-pause'):
        player = media().get('player')
        if player:
            run(['playerctl','--player',player,name])
    elif name in ('mute','volume-up','volume-down'):
        args=['set-mute','@DEFAULT_AUDIO_SINK@','toggle'] if name=='mute' else ['set-volume','-l','1','@DEFAULT_AUDIO_SINK@','5%+' if name=='volume-up' else '5%-']
        run(['wpctl',*args])
    elif re.fullmatch(r'volume-set-(?:[0-9]|[1-9][0-9]|100)',name):
        run(['wpctl','set-volume','-l','1','@DEFAULT_AUDIO_SINK@',f'{int(name.rsplit("-",1)[1])}%'])
    elif name in ('dnd','clear'):
        bus('ToggleDnd' if name=='dnd' else 'CloseAllNotifications')
    elif name.startswith('month-'):
        with (RUNTIME/'month.lock').open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            try:
                offset=int((RUNTIME/'month').read_text())
            except (OSError,ValueError):
                offset=0
            atomic_text(RUNTIME/'month',str(max(-120,min(120,offset+(-1 if name=='month-previous' else 1)))))
    elif name in ('logout','reboot','poweroff'):
        with (RUNTIME/'confirm.lock').open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            try:
                pending=json.loads((RUNTIME/'confirm').read_text())
            except (OSError,ValueError):
                pending={}
            if pending.get('action')==name and time.time()-pending.get('time',0)<5:
                (RUNTIME/'confirm').unlink(missing_ok=True)
                command=['hyprctl','dispatch','exit'] if name=='logout' else ['systemctl',name]
                subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            else:
                atomic_text(RUNTIME/'confirm',json.dumps(dict(action=name,time=time.time())))
                label={'logout':'выйти из сеанса','reboot':'перезагрузить','poweroff':'выключить'}[name]
                atomic_text(RUNTIME/'hint',f'Нажмите ещё раз в течение 5 с: {label}')


def serve():
    RUNTIME.mkdir(mode=0o700,parents=True,exist_ok=True)
    with (RUNTIME/'worker.lock').open('w') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            return
        stop=threading.Event()
        signal.signal(signal.SIGTERM,lambda *_:stop.set())
        signal.signal(signal.SIGINT,lambda *_:stop.set())
        threading.Thread(target=monitor_notifications,args=(stop,),daemon=True).start()
        previous=cpu_sample()
        state=initial_state()
        last_art=None
        next_gpu=0
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            while not stop.is_set():
                start=time.monotonic()
                tasks={key:pool.submit(func) for key,func in [('music',media),('volume',volume),('count',lambda:bus('NotificationCount')),('dnd',lambda:bus('GetDnd'))]}
                if start>=next_gpu:
                    tasks['gpu']=pool.submit(gpu)
                    next_gpu=start+5
                previous,state['system']=system(previous)
                for key,future in tasks.items():
                    state[key]=future.result()
                if state['music'].get('art')!=last_art:
                    last_art=state['music'].get('art')
                    state['art']=album_art(last_art)
                try:
                    state['month_offset']=int((RUNTIME/'month').read_text())
                except (OSError,ValueError):
                    state['month_offset']=0
                if state['count']==0:
                    NOTIFICATIONS.clear()
                try:
                    png(board(state,panels=False),ASSETS/'cards.png',W*2)
                except (OSError,subprocess.SubprocessError) as error:
                    # A broken cover image must not stop all live widgets.
                    print(f'Card rendering failed: {error}',flush=True)
                    state['art']=''
                    png(board(state,panels=False),ASSETS/'cards.png',W*2)
                try:
                    confirmed=json.loads((RUNTIME/'confirm').read_text())
                    if time.time()-confirmed.get('time',0)>=5:
                        (RUNTIME/'confirm').unlink(missing_ok=True)
                        atomic_text(RUNTIME/'hint','Введите пароль и нажмите Enter')
                except (OSError,ValueError):
                    pass
                stop.wait(max(.05,1-(time.monotonic()-start)))
        stop.set()


def initial_state():
    _,stats=system(cpu_sample())
    cpu_name=next((line.split(':',1)[1].strip() for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name')),'CPU')
    cpu_name=cpu_name.replace(' Eight-Core Processor','').replace(' Six-Core Processor','').replace('(R)','').replace('(TM)','')
    return dict(music={},volume=(None,False),system=stats,gpu=dict(name='GPU',load=None,used=None,total=None,temp=None),count=None,dnd=False,cpu_name=cpu_name)


def prepare():
    ASSETS.mkdir(parents=True,exist_ok=True)
    RUNTIME.mkdir(mode=0o700,parents=True,exist_ok=True)
    atomic_text(RUNTIME/'hint','Введите пароль и нажмите Enter')
    atomic_text(RUNTIME/'month','0')
    (RUNTIME/'confirm').unlink(missing_ok=True)
    state=initial_state()
    png(board(state,panels=False),ASSETS/'cards.png',W*2)
    png(svg_document(''.join(icon(name,16+i*70,16,24) for i,name in enumerate(('lock','logout','reboot','power'))),266,56),ASSETS/'dock.png',532)
    layout(monitors(),ROOT/'hyprlock-dashboard.conf')


def preview(path,width,height):
    state=initial_state()
    state['music']=media()
    state['volume']=volume()
    state['gpu']=gpu()
    scale=min((width-96)/W,height/840,1.4)
    body=('<defs><filter id="blur"><feGaussianBlur stdDeviation="26"/></filter></defs>'
          f'<image x="-40" y="-40" width="{width+80}" height="{height+80}" preserveAspectRatio="xMidYMid slice" filter="url(#blur)" xlink:href="{image_uri(wallpaper())}"/>'
          +rect(0,0,width,height,'#11111b',.51,0))
    x,y=(width-W*scale)/2,height/2-H*scale/2+26*scale
    inner=board(state).split(f'<g font-family="{FONT}" fill="{FG}">',1)[1].rsplit('</g></svg>',1)[0]
    body += f'<g transform="translate({x} {y}) scale({scale})">{inner}</g>'
    now=dt.datetime.now()
    body += text(width/2,height/2-295*scale+34*scale,now.strftime('%H:%M'),120*scale,FG,'middle')
    body += text(width/2,height/2-220*scale+7*scale,russian_date(),18.67*scale,MUTED,'middle')
    body += glass((width-290*scale)/2,height/2+222*scale,290*scale,46*scale)
    body += text(width/2,height/2+250*scale,'Пароль',16*scale,MUTED,'middle')
    body += text(width/2,height/2+287*scale,'EN',12*scale,MUTED,'middle')
    for i,name in enumerate(('lock','logout','reboot','power')):
        x=width/2+(-105+i*70)*scale
        body+=glass(x-28*scale,height/2+308*scale,56*scale,56*scale)
        body+=icon(name,x-12*scale,height/2+324*scale,24*scale)
    body+=text(width/2,height/2+390*scale,'Введите пароль и нажмите Enter',12*scale,MUTED,'middle')
    png(svg_document(body,width,height),path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare',action='store_true')
    modes.add_argument('--serve',action='store_true')
    modes.add_argument('--action')
    modes.add_argument('--preview',type=Path)
    modes.add_argument('--date',action='store_true')
    parser.add_argument('--width',type=int,default=1504)
    parser.add_argument('--height',type=int,default=840)
    args=parser.parse_args()
    if args.date:
        print(russian_date())
    elif args.prepare:
        prepare()
    elif args.serve:
        serve()
    elif args.action:
        action(args.action)
    else:
        preview(args.preview,args.width,args.height)


if __name__=='__main__':
    main()
