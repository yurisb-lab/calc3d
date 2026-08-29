#!/usr/bin/env python3
"""Gera os arquivos de marca do app a partir de logo_lyke.png.

    pip install pillow
    python3 tools/gerar-marca.py

Saída (na raiz do projeto):
  lyke-logo.png      lockup completo (emblema + L.Y.K.E 3D + assinatura), aparado
  lyke-marca.png     só o emblema, quadrado — o que cabe em tamanho pequeno
  icone-192.png      ícone PWA
  icone-512.png      ícone PWA
  icone-512-mask.png ícone maskable (o Android recorta as bordas)
  icone-180.png      apple-touch-icon

O logo é colorido e desenhado para fundo claro: o azul-marinho do bico, do aro
interno e de um dos arcos some em cima de preto. Por isso todo ícone aqui sai
sobre uma placa branca, que é o contexto nativo da marca — e é também o motivo
de a topbar e a assinatura dos Ajustes usarem uma placa branca no app.

O corte em três bandas (emblema, wordmark e assinatura) é feito pelas faixas de
pixels transparentes que separam as partes; cada banda vai para um lugar
diferente, porque a assinatura em corpo 8 não sobrevive a 192px.
"""

import os

from PIL import Image, ImageDraw

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGEM = os.path.join(RAIZ, 'logo_lyke.png')

PLACA = (255, 255, 255, 255)   # o logo pede fundo claro
ALFA = 20                      # abaixo disso o pixel conta como vazio


# ---------------------------------------------------------------- recortes

def opacos(im):
    return im.getchannel('A').point(lambda v: 255 if v > ALFA else 0)


def bbox(im):
    b = opacos(im).getbbox()
    if not b:
        raise SystemExit('imagem vazia: ' + ORIGEM)
    return b


def bandas(im):
    """separa emblema / wordmark / assinatura pelas linhas totalmente vazias"""
    x0, y0, x1, y1 = bbox(im)
    m = opacos(im).crop((0, 0, im.width, im.height)).load()
    cheias = []
    for y in range(y0, y1):
        cheias.append(any(m[x, y] for x in range(x0, x1)))

    faixas, ini = [], None
    for i, c in enumerate(cheias):
        if c and ini is None:
            ini = i
        elif not c and ini is not None:
            if i - ini > 3:
                faixas.append((y0 + ini, y0 + i))
            ini = None
    if ini is not None:
        faixas.append((y0 + ini, y1))
    if len(faixas) != 3:
        raise SystemExit('esperava 3 bandas no logo, achei %d: %s' % (len(faixas), faixas))

    nomes = ['emblema', 'word', 'assinatura']
    out = {}
    for nome, (a, b) in zip(nomes, faixas):
        faixa = im.crop((0, a, im.width, b))
        fx = opacos(faixa).getbbox()
        out[nome] = faixa.crop(fx)
    return out


# ---------------------------------------------------------------- montagem

def encaixa(base, arte, cx, cy, larg, alt):
    """redimensiona a arte para caber na caixa e cola centralizada"""
    s = min(larg / arte.width, alt / arte.height)
    w, h = max(1, round(arte.width * s)), max(1, round(arte.height * s))
    base.alpha_composite(arte.resize((w, h), Image.LANCZOS),
                         (round(cx - w / 2), round(cy - h / 2)))


def placa(tam, raio):
    """quadrado branco com cantos arredondados (raio=0 → sangra até a borda)"""
    im = Image.new('RGBA', (tam, tam), (0, 0, 0, 0))
    if raio <= 0:
        im.paste(PLACA, (0, 0, tam, tam))
        return im
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, tam - 1, tam - 1), radius=raio, fill=PLACA)
    return im


def icone(partes, tam, raio, pecas):
    """pecas: (banda, cx, cy, larg, alt) em fração do lado, para escalar junto"""
    im = placa(tam, round(raio * tam))
    for banda, cx, cy, w, h in pecas:
        encaixa(im, partes[banda], cx * tam, cy * tam, w * tam, h * tam)
    return im


def salva(im, nome):
    destino = os.path.join(RAIZ, nome)
    im.save(destino, optimize=True)
    print('  %-20s %d×%d' % (nome, im.width, im.height))


def main():
    src = Image.open(ORIGEM).convert('RGBA')
    print('origem %s  %d×%d' % (os.path.basename(ORIGEM), src.width, src.height))
    partes = bandas(src)
    for k, v in partes.items():
        print('  banda %-11s %d×%d' % (k, v.width, v.height))

    # lockup completo aparado e emblema solto, para uso dentro do app e no PDF
    x0, y0, x1, y1 = bbox(src)
    salva(src.crop((x0, y0, x1, y1)), 'lyke-logo.png')

    emb = partes['emblema']
    lado = max(emb.width, emb.height)
    quad = Image.new('RGBA', (lado, lado), (0, 0, 0, 0))
    quad.alpha_composite(emb, ((lado - emb.width) // 2, (lado - emb.height) // 2))
    salva(quad, 'lyke-marca.png')

    # ícone comum: emblema em cima, wordmark embaixo — ainda legível a 192px
    comum = [('emblema', .5, .35, .46, .46), ('word', .5, .70, .74, .17)]
    for tam in (192, 512):
        salva(icone(partes, tam, .22, comum), 'icone-%d.png' % tam)

    # apple-touch-icon: sem cantos próprios, o iOS aplica a máscara dele
    salva(icone(partes, 180, 0, [('emblema', .5, .37, .46, .46),
                                 ('word', .5, .71, .70, .16)]), 'icone-180.png')

    # maskable: tudo dentro do círculo seguro de 80%, só o emblema
    salva(icone(partes, 512, 0, [('emblema', .5, .5, .56, .56)]), 'icone-512-mask.png')


if __name__ == '__main__':
    main()
