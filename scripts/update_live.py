"""Actualiza la línea «último push» del banner con el repo público más reciente.

Lo corre .github/workflows/banner-en-vivo.yml una vez al día. Solo usa la
biblioteca estándar. Si la API falla, deja el banner como está.
"""
import datetime, json, os, re, sys, urllib.request

USER = 'Dsergio909'
SVG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'matrix.svg')
MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']


def latest_repo():
    req = urllib.request.Request(f'https://api.github.com/users/{USER}/repos?sort=pushed&per_page=20',
                                 headers={'Accept': 'application/vnd.github+json', 'User-Agent': USER})
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req, timeout=30) as r:
        repos = json.load(r)
    for repo in repos:
        # el propio repo del perfil no cuenta: lo empuja este mismo flujo
        if repo['name'].lower() == USER.lower() or repo['fork'] or repo['private']:
            continue
        return repo
    return None


def main():
    try:
        repo = latest_repo()
    except Exception as e:  # sin red o límite de la API: no se toca nada
        print(f'API no disponible: {e}')
        return 0
    if not repo:
        return 0
    d = datetime.datetime.fromisoformat(repo['pushed_at'].replace('Z', '+00:00'))
    line = f'último push: {repo["name"].lower()} · {d.day} {MESES[d.month - 1]} {d.year}'
    line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    svg = open(SVG, encoding='utf-8').read()
    new = re.sub(r'(<!--live-->).*?(<!--/live-->)', lambda m: m.group(1) + line + m.group(2), svg, count=1, flags=re.S)
    if new != svg:
        open(SVG, 'w', encoding='utf-8').write(new)
        print(f'actualizado: {line}')
    else:
        print('sin cambios')
    return 0


if __name__ == '__main__':
    sys.exit(main())
