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

Nada é posicionado à mão: o lockup é empilhado em espaço unitário e o encaixe()
acha a maior escala que ainda mantém os quatro cantos de cada peça dentro do
círculo seguro. É esse círculo que o launcher usa quando recorta o ícone — sem
ele o "L." e o selo "3D", que ficam nas pontas do wordmark, saem cortados.
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


# ------------------------------------------------------------ zona segura

SEGURO_ANY = .44    # círculo de 88% — o quanto o launcher come, com respiro
SEGURO_MASK = .40   # 80%, o que a spec maskable garante

# lockup do ícone: largura de cada peça em espaço unitário (wordmark = 1) e o
# respiro entre elas, em altura de wordmark
LOCKUP = [('emblema', .60), ('word', 1.)]
RESPIRO = .30


def pilha(partes, lockup, respiro):
    """empilha as peças centradas e devolve (larg, alt, desloc_y) de cada uma

    tudo em espaço unitário, com a origem no centro do conjunto."""
    caixas = []
    for nome, larg in lockup:
        arte = partes[nome]
        caixas.append([nome, larg, larg * arte.height / arte.width])
    gap = respiro * caixas[-1][2]
    alt = sum(c[2] for c in caixas) + gap * (len(caixas) - 1)

    saida, y = [], -alt / 2
    for nome, w, h in caixas:
        saida.append((nome, w, h, y + h / 2))
        y += h + gap
    return saida


def encaixe(itens, raio, passos=400):
    """maior escala (e centro vertical) que mantém a pilha dentro do círculo

    o corte do launcher é redondo, então o que decide não é a largura da peça e
    sim o canto dela: quanto mais longe do centro vertical, menos largura sobra."""
    def cabe(s, dy):
        for _, w, h, cy in itens:
            a, b = w * s / 2, h * s / 2
            if a * a + (abs(cy * s + dy) + b) ** 2 > raio * raio:
                return False
        return True

    melhor = (0., 0.)
    for i in range(-passos, passos + 1):
        dy = raio * i / passos
        lo, hi = 0., 4.
        for _ in range(50):
            s = (lo + hi) / 2
            if cabe(s, dy):
                lo = s
            else:
                hi = s
        if lo > melhor[0]:
            melhor = (lo, dy)
    if not melhor[0]:
        raise SystemExit('nada cabe no círculo de raio %.2f' % raio)
    return melhor


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


def icone(partes, tam, raio, lockup, seguro, respiro=RESPIRO):
    """desenha o lockup na maior escala que ainda cabe no círculo seguro"""
    itens = pilha(partes, lockup, respiro)
    s, dy = encaixe(itens, seguro)
    im = placa(tam, round(raio * tam))
    for nome, w, h, cy in itens:
        encaixa(im, partes[nome], .5 * tam, (.5 + cy * s + dy) * tam,
                w * s * tam, h * s * tam)
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
    for tam in (192, 512):
        salva(icone(partes, tam, .22, LOCKUP, SEGURO_ANY), 'icone-%d.png' % tam)

    # apple-touch-icon: sem cantos próprios, o iOS aplica a máscara dele
    salva(icone(partes, 180, 0, LOCKUP, SEGURO_ANY), 'icone-180.png')

    # maskable: o Android corta até 80%, aí só o emblema sobrevive legível
    salva(icone(partes, 512, 0, [('emblema', 1.)], SEGURO_MASK), 'icone-512-mask.png')


if __name__ == '__main__':
    main()
