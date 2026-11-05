"""Genera los SVG estilo Matrix del perfil (banner, tarjetas, píldoras y divisor).

Uso (necesita Pillow, fonttools y brotli):
    python scripts/banner/gen.py

Escribe en assets/. La línea «último push» del banner la actualiza a diario
.github/workflows/banner-en-vivo.yml con scripts/update_live.py.
"""
import base64, io, os, random
from PIL import Image
from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ASSETS = os.path.join(ROOT, 'assets')
random.seed(1999)

G0, G1, G2, G3, G4 = '#0a4a22', '#138a3b', '#25c45c', '#6cf597', '#b3ffcb'
BG = '#010a04'
LIVE_DEFAULT = 'último push: supplier-scout · 27 oct 2026'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def font_css(weights, text=None):
    """@font-face de JetBrains Mono embebida; si se da text, se recorta a esos caracteres."""
    css = []
    for w in weights:
        path = os.path.join(HERE, 'fonts', f'jetbrains-mono-latin-{w}-normal.woff2')
        data = open(path, 'rb').read()
        if text:
            f = TTFont(io.BytesIO(data), recalcTimestamp=False)
            opts = subset.Options()
            opts.flavor = 'woff2'
            sub = subset.Subsetter(opts)
            sub.populate(text=text)
            sub.subset(f)
            buf = io.BytesIO()
            f.flavor = 'woff2'
            f.save(buf)
            data = buf.getvalue()
        css.append("@font-face{font-family:'JBM';font-weight:%d;src:url(data:font/woff2;base64,%s) format('woff2')}"
                   % (w, base64.b64encode(data).decode()))
    return ''.join(css) + ".m{font-family:JBM,Consolas,'Courier New',monospace;white-space:pre}"


def glow_defs():
    return ('<filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.6" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
            '<filter id="glow2" x="-10%" y="-50%" width="120%" height="200%"><feGaussianBlur stdDeviation="5" result="b"/>'
            '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def rain(width, height, step, chars, size=15, dim=1.0):
    out = []
    for x in range(6, width, step):
        n = random.randint(10, 24)
        dur = round(random.uniform(4.5, 10), 2)
        begin = round(-random.uniform(0, dur), 2)
        spans = []
        for i in range(n):
            ch = esc(random.choice(chars))
            if i == n - 1:
                spans.append(f'<tspan x="{x}" dy="{size + 2}" fill="#e8ffe9" fill-opacity="{dim:.2f}">{ch}</tspan>')
            else:
                spans.append(f'<tspan x="{x}" dy="{size + 2}" fill-opacity="{(0.08 + 0.75 * (i / n) ** 1.6) * dim:.2f}">{ch}</tspan>')
        out.append(f'<text class="m" y="0" font-size="{size}" fill="{G2}">{"".join(spans)}'
                   f'<animateTransform attributeName="transform" type="translate" values="0 {-n * (size + 2)};0 {height + 20}" '
                   f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></text>')
    return ''.join(out)


# =====================================================================
# BANNER
# =====================================================================
CAT_SIT = ['..#.....#...........', '..##...##...........', '..#######...........', '.#########..........',
           '.##E###E##..........', '.####n####..........', '..#######...........', '...#####............',
           '..#######...........', '.#########..........', '.##########.........', '.###########........',
           '.############.......', '.############.......', '.#############......', '.#############......',
           '..############......', '..##.##..##.##......']
CAT_TAIL = {10: 14, 11: 15, 12: 16, 13: 16, 14: 15, 15: 14, 16: 13}  # fila: columna de la cola
CAT_WALK = ['............#.#.', '#...........###.', '.#..........#E#.', '..#.###########.', '...###########..', '...##########...']
CAT_LEGS = ['...#.#....#.#...', '....#.#..#.#....']
FUR = '#%8&$@MW'
CAT_RNG = random.Random(7)  # azar propio: los gatos no cambian el resto de los SVG


def cat_rows(mask, x0, y0, cw, ch, colors):
    """Texto por fila con caracteres densos donde la máscara tiene # (ojos y nariz aparte)."""
    out, eyes = [], []
    for r, row in enumerate(mask):
        line = ''.join(CAT_RNG.choice(FUR) if ch_ == '#' else ' ' for ch_ in row)
        if line.strip():
            out.append(f'<text class="m" x="{x0}" y="{y0 + (r + 1) * ch:.1f}" font-size="10" font-weight="700" '
                       f'fill="{colors[min(r * len(colors) // len(mask), len(colors) - 1)]}">{esc(line)}</text>')
        for c, ch_ in enumerate(row):
            if ch_ in 'En':
                eyes.append((x0 + c * cw, y0 + (r + 1) * ch, ch_))
    return ''.join(out), eyes


def cats(cw, ch):
    """Un gato sentado junto a la cara (parpadea y mueve la cola) y otro que cruza por arriba."""
    A = []
    x0, y0 = 600, 295
    bx, by = x0, y0 + 18 * ch  # base del gato: desde ahí se agranda
    body, eyes = cat_rows(CAT_SIT, x0, y0, cw, ch, [G4, G3, G3, G2])
    px, py = x0 + 13 * cw, y0 + 17 * ch
    tail = ''.join(f'<text class="m" x="{x0 + c * cw}" y="{y0 + (r + 1) * ch:.1f}" font-size="10" font-weight="700" fill="{G3}">'
                   f'{esc(CAT_RNG.choice(FUR))}{CAT_RNG.choice(FUR) if r in (12, 13) else ""}</text>' for r, c in CAT_TAIL.items())
    A.append(f'<g filter="url(#glow)" transform="translate({bx} {by:.1f}) scale(1.25) translate({-bx} {-by:.1f})"><g>{tail}<animateTransform attributeName="transform" type="rotate" '
             f'values="0 {px:.0f} {py:.0f};-14 {px:.0f} {py:.0f};0 {px:.0f} {py:.0f};8 {px:.0f} {py:.0f};0 {px:.0f} {py:.0f}" dur="3.2s" repeatCount="indefinite"/></g>{body}')
    for x, y, k in eyes:
        if k == 'n':
            A.append(f'<text class="m" x="{x}" y="{y:.1f}" font-size="10" font-weight="700" fill="{G4}">v</text>')
            continue
        A.append(f'<text class="m" x="{x}" y="{y:.1f}" font-size="10" font-weight="700" fill="#ffffff">O'
                 '<animate attributeName="opacity" values="1;0;1;1" keyTimes="0;.02;.06;1" dur="4.5s" repeatCount="indefinite" calcMode="discrete"/></text>'
                 f'<text class="m" x="{x}" y="{y:.1f}" font-size="10" font-weight="700" fill="#ffffff" opacity="0">-'
                 '<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.02;.06;1" dur="4.5s" repeatCount="indefinite" calcMode="discrete"/></text>')
    A.append('</g>')
    # gato que camina por el borde de arriba
    body, eyes = cat_rows(CAT_WALK, 0, 0, cw, ch, [G4, G3])
    legs = []
    for j, frame in enumerate(CAT_LEGS):
        line = ''.join(CAT_RNG.choice(FUR) if c == '#' else ' ' for c in frame)
        vals = '1;0' if j == 0 else '0;1'
        legs.append(f'<text class="m" x="0" y="{7 * ch:.1f}" font-size="10" font-weight="700" fill="{G3}" opacity="{vals[0]}">{esc(line)}'
                    f'<animate attributeName="opacity" values="{vals}" dur=".5s" repeatCount="indefinite" calcMode="discrete"/></text>')
    eye = ''.join(f'<text class="m" x="{x}" y="{y:.1f}" font-size="10" font-weight="700" fill="#ffffff">O</text>' for x, y, _ in eyes)
    A.append(f'<g filter="url(#glow)">{body}{"".join(legs)}{eye}'
             '<animateTransform attributeName="transform" type="translate" values="-120 2;1320 2" dur="26s" begin="-9s" repeatCount="indefinite"/></g>')
    return ''.join(A)


def banner():
    W, H, CYC = 1200, 440, 14
    COLS, ROWS, CW, CH = 66, 54, 6, 7.4
    FX, FY = 772, 20
    A = []
    A.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    A.append('<title>Sergio García en estilo Matrix: su cara formada por caracteres verdes, dos gatos de código y un registro de lo que hace que se va actualizando</title>')
    A.append('<style>' + font_css((400, 700)) + '</style>')

    # cara a partir del avatar: brillo → carácter más denso y verde más claro
    im = Image.open(os.path.join(HERE, 'avatar.png')).convert('RGB')
    bg = im.getpixel((4, 4))
    small = im.resize((COLS, ROWS), Image.LANCZOS)
    cells = {}
    for r in range(ROWS):
        for c in range(COLS):
            p = small.getpixel((c, r))
            if sum((a - b) ** 2 for a, b in zip(p, bg)) ** .5 < 48:
                continue
            cells[(r, c)] = (0.2126 * p[0] + 0.7152 * p[1] + 0.0722 * p[2]) / 255
    srt = sorted(cells.values())
    th = [srt[int(len(srt) * q)] for q in (.18, .38, .58, .8)]
    ramp = [".:'", '-=+:', '*+xz7', '#%8&$', '@MW#B']
    levels = [G0, G1, G2, G3, G4]
    grid = {k: [[' '] * COLS for _ in range(ROWS)] for k in range(5)}
    for (r, c), L in cells.items():
        k = sum(L >= t for t in th)
        grid[k][r][c] = random.choice(ramp[k])

    A.append('<defs>' + glow_defs())
    A.append('<linearGradient id="soft" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".85" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    A.append(f'<mask id="reveal"><rect x="{FX - 10}" width="{COLS * CW + 20}" height="{ROWS * CH + 40}" fill="url(#soft)">'
             f'<animate attributeName="y" values="{FY - ROWS * CH - 40};{FY};{FY};{FY + ROWS * CH + 20}" keyTimes="0;.2;.88;1" dur="{CYC}s" repeatCount="indefinite"/></rect></mask>')
    A.append('<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".85"/></radialGradient>')
    A.append('<linearGradient id="leftfade" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".88"/><stop offset=".55" stop-color="#000" stop-opacity=".7"/><stop offset=".64" stop-color="#000" stop-opacity="0"/></linearGradient>')
    A.append('<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".35"/></pattern>')
    A.append(f'<clipPath id="all"><rect width="{W}" height="{H}" rx="18"/></clipPath>')
    log = [(True, 'automatización de procesos', 'instalado'),
           (True, 'agentes de IA con Claude Code', 'instalado'),
           (True, 'Supplier Radar · Supplier Scout', 'en línea'),
           (False, 'Crunch Heist · juego de Roblox', 'en pruebas'),
           (False, 'modpack de Minecraft', 'construyendo'),
           (False, 'Power BI · SQL', 'aprendiendo'),
           (True, 'gatos de la casa', 'supervisando')]
    for i in range(len(log)):
        t0 = 0.06 + i * 0.065
        A.append(f'<clipPath id="ty{i}"><rect x="56" y="{230 + i * 24}" height="22" width="0">'
                 f'<animate attributeName="width" values="0;0;640;640;0" keyTimes="0;{t0:.3f};{t0 + .06:.3f};.9;1" dur="{CYC}s" repeatCount="indefinite"/></rect></clipPath>')
    A.append('</defs>')

    A.append(f'<g clip-path="url(#all)"><rect width="{W}" height="{H}" fill="{BG}"/>')
    A.append(rain(W, H, 18, [chr(c) for c in range(0xFF66, 0xFF9E)] + list('0123456789Z:.=*+-<>')))
    A.append(f'<rect width="{W}" height="{H}" fill="url(#leftfade)"/>')

    # cara, con interferencias de vez en cuando
    A.append(f'<rect x="{FX - 14}" y="{FY - 6}" width="{COLS * CW + 28}" height="{ROWS * CH + 12}" fill="{BG}" opacity=".55"/>')
    A.append('<g><g mask="url(#reveal)" filter="url(#glow)">')
    for k in range(5):
        for r in range(ROWS):
            line = ''.join(grid[k][r])
            if line.strip():
                A.append(f'<text class="m" x="{FX}" y="{FY + (r + 1) * CH:.1f}" font-size="10" fill="{levels[k]}" '
                         f'font-weight="{700 if k >= 3 else 400}">{esc(line)}</text>')
    glyphs = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ$#%&*+=?'
    for (r, c) in random.sample(list(cells), 220):
        d = round(random.uniform(.8, 3), 2)
        A.append(f'<text class="m" x="{FX + c * CW}" y="{FY + (r + 1) * CH:.1f}" font-size="10" fill="#eafff0" opacity="0">{esc(random.choice(glyphs))}'
                 f'<animate attributeName="opacity" values="0;1;0" dur="{d}s" begin="{round(random.uniform(0, 4), 2)}s" repeatCount="indefinite"/></text>')
    A.append('</g>')
    A.append(f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;9 0;-6 0;3 0;0 0;0 0;-7 0;0 0;0 0" '
             f'keyTimes="0;.42;.425;.43;.435;.44;.7;.705;.71;1" dur="{CYC}s" repeatCount="indefinite"/></g>')
    A.append(f'<rect x="{FX - 10}" width="{COLS * CW + 20}" height="2" fill="#b7ffcf" filter="url(#glow)" opacity="0">'
             f'<animate attributeName="y" values="{FY - 20};{FY + ROWS * CH};{FY + ROWS * CH}" keyTimes="0;.2;1" dur="{CYC}s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.19;.21;1" dur="{CYC}s" repeatCount="indefinite"/></rect>')

    A.append(cats(CW, CH))

    # izquierda: identidad y registro
    A.append('<g class="m">')
    A.append(f'<text x="56" y="70" font-size="15" fill="{G2}">sergio@bogota<tspan fill="{G3}">:~$</tspan> ./actualizar_perfil.sh</text>')
    A.append(f'<text x="742" y="70" text-anchor="end" font-size="13" fill="#ffffff">[ sigue al conejo blanco ]'
             '<animate attributeName="opacity" values="1;.25;1" dur="2.2s" repeatCount="indefinite"/></text>')
    A.append(f'<g filter="url(#glow2)"><text x="52" y="136" font-size="60" font-weight="700" fill="{G4}" letter-spacing="1">SERGIO GARCÍA'
             '<animate attributeName="opacity" values="1;1;.4;1;.75;1;1" keyTimes="0;.6;.61;.62;.63;.64;1" dur="5s" repeatCount="indefinite"/></text></g>')
    A.append(f'<text x="56" y="170" font-size="17" fill="{G3}">Negocios Internacionales · IA · Automatización</text>')
    A.append(f'<text x="56" y="214" font-size="14" fill="{G1}">// <!--live-->{esc(LIVE_DEFAULT)}<!--/live--></text>')
    adv = 9  # avance de JetBrains Mono a 15 px
    for i, (done, name, st) in enumerate(log):
        y = 246 + i * 24
        col = G3 if done else G4
        mark = '[ OK ]' if done else '[    ]'
        dots = '.' * max(2, 34 - len(name))
        A.append(f'<g clip-path="url(#ty{i})"><text class="m" x="56" y="{y}" font-size="15">'
                 f'<tspan fill="{col}">{mark}</tspan><tspan fill="{G4}"> {esc(name)} </tspan><tspan fill="{G0}">{dots}</tspan>'
                 f'<tspan fill="{col}"> {st}</tspan></text>')
        if not done:
            frames = '|/-\\'
            for slot in (2, 3):
                for j, f in enumerate(frames):
                    vis = ['0'] * 4
                    vis[(j + (slot - 2) * 2) % 4] = '1'
                    A.append(f'<text class="m" x="{56 + slot * adv}" y="{y}" font-size="15" fill="{G4}" opacity="0">{esc(f)}'
                             f'<animate attributeName="opacity" values="{";".join(vis)}" dur=".6s" repeatCount="indefinite" calcMode="discrete"/></text>')
        A.append('</g>')
    A.append(f'<rect x="56" y="412" width="0" height="6" fill="{G2}" filter="url(#glow)">'
             f'<animate attributeName="width" values="0;0;300;300;0" keyTimes="0;.5;.8;.9;1" dur="{CYC}s" repeatCount="indefinite"/></rect>')
    A.append(f'<rect x="56" y="412" width="300" height="6" fill="none" stroke="{G0}"/>')
    A.append(f'<text x="372" y="419" font-size="13" fill="{G3}">Bogotá · abierto a rol remoto</text>')
    A.append('</g>')

    A.append(f'<rect width="{W}" height="{H}" fill="url(#scan)"/><rect width="{W}" height="{H}" fill="url(#vig)"/>')
    A.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="18" fill="none" stroke="{G2}" stroke-opacity=".35"/>')
    A.append('</g></svg>')
    return '\n'.join(A)


# =====================================================================
# TARJETAS DE PROYECTO
# =====================================================================
CARDS = [
    ('comercio-exterior-colombia', 'Comercio exterior', True, 'público',
     ['3,7 millones de registros del DANE en', 'SQL y Power BI: cuadra 13 de 13 con el', 'boletín. n8n con IA local que yo apruebo.'],
     'sql · duckdb · power-bi · n8n · 96 pruebas', 'ver código →'),
    ('olist-logistica-sql', 'Olist logística', True, 'público',
     ['99.441 pedidos de una tienda de Brasil:', 'dónde se demoran las entregas y cuánto', 'baja la nota con cada día de retraso.'],
     'sql · duckdb · power-bi · 58 pruebas', 'ver código →'),
    ('vuelos-colombia', 'Vuelos en Colombia', True, 'público',
     ['Rutas, temporadas y aerolíneas con los', 'datos de la Aerocivil. Sin Viva y Ultra,', 'Avianca y LATAM subieron al 77,9 %.'],
     'sql · duckdb · power-bi · 41 pruebas', 'ver código →'),
    ('taller3d-costos', 'Taller 3D: costos', True, 'público',
     ['Cuánto cuesta de verdad cada pieza y a', 'qué precio venderla. Cotiza en n8n y yo', 'apruebo. Datos inventados, método real.'],
     'sql · power-bi · n8n · 66 pruebas', 'ver código →'),
    ('supplier-radar', 'Supplier Radar', True, 'en línea',
     ['Mi sistema de proveedores de la práctica,', 'rehecho: lee hasta fotos del celular y', 'revisa que cada documento esté vigente.'],
     'apps-script · ocr · gmail · $0 licencias', 'ver demo →'),
    ('supplier-scout', 'Supplier Scout', True, 'en línea',
     ['Busca proveedores como lo hace compras:', 'nacionales (SECOP II), los tuyos y los', 'cercanos. 58 de 58 comprobados por NIT.'],
     'secop-ii · openstreetmap · 199 pruebas', 'ver demo →'),
    ('mesa-de-cotejo', 'Mesa de Cotejo', True, 'en línea',
     ['Reclamos por suplantación sin que se', 'venza ningún plazo de la Ley 2573.', '109 pruebas; las fechas, nunca con IA.'],
     'javascript · días hábiles · 3 idiomas', 'ver demo →'),
    ('agentes-ia', 'Agentes de IA', True, 'en uso',
     ['Agentes de diseño 3D y marketing con', 'Claude Code, conectados por MCP a Blender,', 'Bambu Studio y DaVinci Resolve.'],
     'claude-code · mcp · python · fastapi', 'ver caso →'),
    ('ojo-del-mundo', 'Ojo del mundo', True, 'público',
     ['Dibuja un mundo de Minecraft en 3D', 'desde sus archivos para que Claude lo', 'revise. Servidor MCP con 32 herramientas.'],
     'python · numpy · mcp · pruebas en ci', 'ver código →'),
    ('crunch-heist', 'Crunch Heist', False, 'en pruebas',
     ['Juego de Roblox con universo propio:', 'robos entre bases, tycoon y colección,', 'sin pay-to-win. Hecho con Claude Code.'],
     'roblox · luau · claude-code', ''),
]


def card(slug, title, done, status, desc, stack, cta):
    W, H = 600, 260
    mark = '[ OK ]' if done else '[ .. ]'
    texts = f'~/proyectos/{slug}{mark} {status}{title}{"".join(desc)}$ stack: {stack}{cta}01'
    A = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<title>{esc(title)}: {esc(" ".join(desc))}</title>',
         '<style>' + font_css((400, 700), texts) + '</style>',
         '<defs>' + glow_defs() + f'<clipPath id="c"><rect width="{W}" height="{H}" rx="14"/></clipPath>'
         '<linearGradient id="fade" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".9"/><stop offset=".7" stop-color="#000" stop-opacity=".75"/><stop offset="1" stop-color="#000" stop-opacity=".2"/></linearGradient></defs>',
         f'<g clip-path="url(#c)"><rect width="{W}" height="{H}" fill="{BG}"/>',
         rain(W, H, 22, list('01'), size=13, dim=.6),
         f'<rect width="{W}" height="{H}" fill="url(#fade)"/>',
         '<g class="m">',
         f'<rect width="{W}" height="36" fill="{G0}" fill-opacity=".35"/>',
         f'<text x="22" y="24" font-size="14" fill="{G2}">~/proyectos/{slug}</text>',
         f'<text x="{W - 22}" y="24" text-anchor="end" font-size="14" fill="{G3 if done else "#ffffff"}">{mark} {status}'
         + ('' if done else '<animate attributeName="opacity" values="1;.3;1" dur="1.4s" repeatCount="indefinite"/>') + '</text>',
         f'<g filter="url(#glow2)"><text x="22" y="90" font-size="34" font-weight="700" fill="{G4}">{esc(title)}</text></g>']
    for i, l in enumerate(desc):
        A.append(f'<text x="22" y="{128 + i * 24}" font-size="15.5" fill="#a7f3c0">{esc(l)}</text>')
    A.append(f'<text x="22" y="226" font-size="13.5" fill="{G1}">$ stack: <tspan fill="{G2}">{esc(stack)}</tspan></text>')
    if cta:
        A.append(f'<text x="{W - 22}" y="226" text-anchor="end" font-size="15" font-weight="700" fill="#ffffff">{esc(cta)}</text>')
    A.append('</g>')
    A.append(f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="{G2}" stroke-opacity=".45"/></g></svg>')
    return '\n'.join(A)


# =====================================================================
# PÍLDORAS DE CONTACTO Y DIVISOR
# =====================================================================
PILLS = [('portafolio', 'píldora roja', 'PORTAFOLIO →', '#ef4444', '#fca5a5'),
         ('linkedin', 'píldora azul', 'LINKEDIN →', '#3b82f6', '#93c5fd'),
         ('email', 'señal directa', 'EMAIL →', G2, G4)]


def pill(slug, small, big, c1, c2):
    W, H = 300, 72
    A = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<title>{esc(big.rstrip(" →"))}</title>',
         '<style>' + font_css((400, 700), small + big) + '</style>',
         '<defs>' + glow_defs() + '</defs>',
         f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="{(H - 2) / 2}" fill="{BG}" stroke="{c1}" stroke-opacity=".7" stroke-width="2"/>',
         f'<g transform="rotate(-35 46 36)" filter="url(#glow)"><rect x="22" y="26" width="48" height="20" rx="10" fill="{c1}"/>'
         f'<path d="M46 26h14a10 10 0 0 1 0 20h-14z" fill="{c2}"/><rect x="28" y="29" width="12" height="4" rx="2" fill="#fff" opacity=".5"/>'
         f'<animateTransform attributeName="transform" type="rotate" values="-35 46 36;-25 46 36;-35 46 36" dur="3s" repeatCount="indefinite"/></g>',
         f'<g class="m"><text x="92" y="30" font-size="13" fill="{c2}">{esc(small)}</text>'
         f'<text x="92" y="53" font-size="20" font-weight="700" fill="#ffffff">{esc(big)}</text></g></svg>']
    return '\n'.join(A)


def divider():
    W, H = 1200, 18
    s = ''.join(random.choice('01') for _ in range(200))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            '<style>' + font_css((400,), '01') + '</style>'
            '<defs><linearGradient id="e" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".15" stop-color="#fff"/>'
            '<stop offset=".85" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="m"><rect width="{W}" height="{H}" fill="url(#e)"/></mask>'
            '<linearGradient id="hl" x1="0" x2="1"><stop offset="0" stop-color="#b3ffcb" stop-opacity="0"/><stop offset=".5" stop-color="#b3ffcb"/><stop offset="1" stop-color="#b3ffcb" stop-opacity="0"/></linearGradient></defs>'
            f'<g mask="url(#m)"><text class="m" x="0" y="13" font-size="10" fill="{G1}" letter-spacing="0">{s}</text>'
            f'<rect y="8" width="180" height="2" fill="url(#hl)"><animate attributeName="x" values="-180;{W}" dur="3.5s" repeatCount="indefinite"/></rect></g></svg>')


def main():
    os.makedirs(ASSETS, exist_ok=True)
    files = {'matrix.svg': banner(), 'matrix-divider.svg': divider()}
    for c in CARDS:
        files[f'card-{c[0]}.svg'] = card(*c)
    for p in PILLS:
        files[f'pill-{p[0]}.svg'] = pill(*p)
    for name, content in files.items():
        with open(os.path.join(ASSETS, name), 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'{name:28s} {len(content.encode()) // 1024} KB')


if __name__ == '__main__':
    main()
