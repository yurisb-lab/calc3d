#!/usr/bin/env python3
"""Gera os arquivos de marca do app a partir de "Lyke logo.svg".

    pip install cairosvg
    python3 tools/gerar-marca.py

Saída (na raiz do projeto):
  lyke-logo.svg      lockup completo (emblema + L.Y.K.E 3D + assinatura)
  lyke-marca.svg     só o emblema — o que cabe em tamanho pequeno
  icone-192.png      ícone PWA
  icone-512.png      ícone PWA
  icone-512-mask.png ícone maskable (Android recorta as bordas)
  icone-180.png      apple-touch-icon

O logo original é um traço do potrace: 165 <path> pretos num único <g>, sem cor
nenhuma além do preto. Este script separa esses paths em três bandas (emblema,
wordmark e assinatura) pela altura de cada um, porque cada peça é usada em um
lugar diferente do app.

Os SVGs saem com fill preto de propósito: no app eles entram como CSS
mask-image, onde só o alfa importa e a cor vem do tema (currentColor); no PDF
entram como <img>, onde o preto é justamente o que se quer.
"""

import os
import re

import cairosvg

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEM = os.path.join(RAIZ, 'Lyke logo.svg')

INK = '#0E1114'   # preto do logo
FG = '#FFFFFF'

# fronteiras entre as bandas, em unidades do viewBox original (1254x1254)
CORTE_EMBLEMA, CORTE_WORD = 729, 984


# ---------------------------------------------------------------- path data

TOK = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])|(-?\d*\.?\d+(?:[eE][-+]?\d+)?)')
NARG = {'M': 2, 'L': 2, 'T': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'A': 7, 'Z': 0}


def pontos(d):
    """Pontos absolutos tocados pelo path, pontos de controle inclusos.

    Dá uma bbox um pouco folgada, o que é irrelevante aqui: serve só para saber
    em que banda o path cai e para aparar o viewBox com uma margem de sobra.
    """
    toks = [(c or n) for c, n in TOK.findall(d)]
    i, cmd, x, y, sx, sy, pts = 0, None, 0.0, 0.0, 0.0, 0.0, []
    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in 'Zz':
                x, y = sx, sy
                continue
        if cmd is None:
            break
        up, rel, n = cmd.upper(), cmd.islower(), NARG[cmd.upper()]
        args = [float(v) for v in toks[i:i + n]]
        i += n
        if len(args) < n:
            break
        if up == 'H':
            nx, ny = (x + args[0] if rel else args[0]), y
        elif up == 'V':
            nx, ny = x, (y + args[0] if rel else args[0])
        elif up == 'A':
            nx, ny = (x + args[5], y + args[6]) if rel else (args[5], args[6])
        else:
            for k in range(0, n, 2):
                pts.append((x + args[k], y + args[k + 1]) if rel else (args[k], args[k + 1]))
            nx, ny = (x + args[n - 2], y + args[n - 1]) if rel else (args[n - 2], args[n - 1])
        pts.append((nx, ny))
        x, y = nx, ny
        if up == 'M':
            sx, sy = x, y
            cmd = 'l' if rel else 'L'   # um M solto continua como lineto
    return pts


def para_viewbox(pts):
    """do espaço do <g> (translate(0,1254) scale(.1,-.1)) para o do viewBox"""
    return [(0.1 * px, 1254 - 0.1 * py) for px, py in pts]


# ---------------------------------------------------------------- montagem

def ler_bandas():
    raw = open(ORIGEM, encoding='utf-8').read()
    paths = re.findall(r'<path d="(.*?)"\s*/>', raw, re.S)
    if not paths:
        raise SystemExit('nenhum <path> encontrado em ' + ORIGEM)

    bandas = {'emblema': [], 'word': [], 'assinatura': []}
    caixas = {k: [] for k in bandas}
    for d in paths:
        pts = para_viewbox(pontos(d))
        cy = sum(p[1] for p in pts) / len(pts)
        k = 'emblema' if cy < CORTE_EMBLEMA else ('word' if cy < CORTE_WORD else 'assinatura')
        bandas[k].append(d)
        caixas[k] += pts

    bbox = {}
    for k, pts in caixas.items():
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        bbox[k] = (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    return bandas, bbox


def uniao(bbox, chaves):
    cx = [bbox[k] for k in chaves]
    x0 = min(b[0] for b in cx)
    y0 = min(b[1] for b in cx)
    x1 = max(b[0] + b[2] for b in cx)
    y1 = max(b[1] + b[3] for b in cx)
    return (x0, y0, x1 - x0, y1 - y0)


def grupo(bandas, chaves, fill):
    """os paths pedidos, ainda no sistema de coordenadas do potrace"""
    corpo = ''.join('<path d="%s"/>' % d for k in chaves for d in bandas[k])
    return ('<g transform="translate(0,1254) scale(0.1,-0.1)" fill="%s" stroke="none">%s</g>'
            % (fill, corpo))


def arquivo_svg(bandas, bbox, chaves, titulo):
    x, y, w, h = uniao(bbox, chaves)
    m = 6
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%.1f %.1f %.1f %.1f" '
            'role="img" aria-label="%s">%s</svg>'
            % (x - m, y - m, w + 2 * m, h + 2 * m, titulo, grupo(bandas, chaves, '#000000')))


def encaixe(bandas, bbox, chaves, X, Y, W, H, fill=FG):
    """recorta a banda com um <svg> aninhado (que já corta o que sobra) e encaixa na caixa"""
    x, y, w, h = uniao(bbox, chaves)
    return ('<svg x="%g" y="%g" width="%g" height="%g" viewBox="%.1f %.1f %.1f %.1f" '
            'preserveAspectRatio="xMidYMid meet" overflow="hidden">%s</svg>'
            % (X, Y, W, H, x, y, w, h, grupo(bandas, chaves, fill)))


def icone(bandas, bbox, pecas, raio=None):
    """1000x1000; raio=None deixa o fundo sangrar até a borda (maskable / iOS)"""
    fundo = ('<rect width="1000" height="1000" fill="%s"/>' % INK if raio is None else
             '<rect width="1000" height="1000" rx="%g" ry="%g" fill="%s"/>' % (raio, raio, INK))
    corpo = ''.join(encaixe(bandas, bbox, *p) for p in pecas)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">%s%s</svg>'
            % (fundo, corpo))


def png(svg, nome, tam):
    destino = os.path.join(RAIZ, nome)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=destino,
                     output_width=tam, output_height=tam)
    print('  %-20s %d×%d' % (nome, tam, tam))


def main():
    bandas, bbox = ler_bandas()
    print('bandas:', {k: len(v) for k, v in bandas.items()})

    for nome, chaves, titulo in [
        ('lyke-logo.svg', ['emblema', 'word', 'assinatura'], 'L.Y.K.E 3D'),
        ('lyke-marca.svg', ['emblema'], 'L.Y.K.E 3D'),
    ]:
        svg = arquivo_svg(bandas, bbox, chaves, titulo)
        open(os.path.join(RAIZ, nome), 'w', encoding='utf-8').write(svg + '\n')
        print('  %-20s %d KB' % (nome, len(svg) // 1024))

    # ícone comum: emblema em cima, wordmark embaixo — ainda legível a 192px
    lockup = icone(bandas, bbox,
                   [(['emblema'], 305, 130, 390, 390),
                    (['word'], 150, 585, 700, 190)],
                   raio=220)
    png(lockup, 'icone-192.png', 192)
    png(lockup, 'icone-512.png', 512)

    # apple-touch-icon: sem cantos próprios, o iOS aplica a máscara dele
    png(icone(bandas, bbox,
              [(['emblema'], 305, 150, 390, 390),
               (['word'], 165, 600, 670, 180)]), 'icone-180.png', 180)

    # maskable: tudo dentro do círculo seguro de 80%, só o emblema
    png(icone(bandas, bbox, [(['emblema'], 285, 285, 430, 430)]), 'icone-512-mask.png', 512)


if __name__ == '__main__':
    main()
