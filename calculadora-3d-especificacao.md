# Calculadora de Preço de Venda — Impressão 3D

**Documento de especificação — v1**
Base de pesquisa: agosto/2026. Valores de taxas e tarifas são **padrões editáveis**, não verdades fixas.

---

## 1. O problema

Quase todo mundo que vende peça 3D calcula só o filamento e acha que está lucrando. O filamento costuma ser o **menor** dos custos. Numa peça típica de 82 g e 9 h de impressão, o filamento é R$ 9,74 de um custo real de R$ 29,03 — ou seja, **um terço**. Quem cobra "filamento × 2" está pagando para trabalhar.

O objetivo do app: você digita **gramas + horas** (que o fatiador já te dá) e ele devolve o preço certo, já considerando tudo.

---

## 2. O que precisa entrar na conta

A pesquisa em fontes brasileiras e internacionais converge em **7 blocos**. Nenhum deles é opcional se a venda for comercial.

### 2.1 Material (filamento)
- Peso da peça em gramas (o fatiador informa).
- Preço do rolo e peso do rolo → preço por grama.
- **Desperdício**: purga, brim, raft, suportes, torre de purga em multicolor. A referência de mercado é **5% a 10%** sobre o peso. Em impressão multicolor com AMS, a torre de purga pode pesar mais que a própria peça — nesse caso, pegue o valor real do fatiador.

### 2.2 Energia elétrica
- Potência média da impressora em watts. Impressoras FDM de mesa ficam entre **100 W e 250 W**; máquinas fechadas ou com câmara aquecida vão de 200 W a 400 W.
- Tarifa do kWh da sua conta (com impostos, não a tarifa "seca" da ANEEL).
- É o menor custo de todos, mas entra porque em produção contínua acumula.

### 2.3 Máquina (depreciação + manutenção)
- A impressora se desgasta e um dia será trocada. Cada peça devolve um pedacinho do valor dela.
- Vida útil de referência: **3.000 a 10.000 horas** de impressão. Um valor conservador e comum é 4.000–5.000 h.
- Some também bico, correia, hotend, mesa, ventoinhas — manutenção anual diluída por hora.
- **Cuidado**: não copie o custo/hora de outra pessoa. Ele depende da SUA máquina, do SEU uso e da SUA vida útil.

### 2.4 Mão de obra
- Fatiar, preparar a mesa, tirar a peça, remover suporte, lixar, pintar, montar, embalar, responder cliente.
- Conte **só os minutos em que sua mão está na peça** — a impressora trabalha sozinha, não precisa de você.
- Em peças pequenas, este item costuma ser **o maior custo isolado**. Ignorar isso é trabalhar de graça.

### 2.5 Insumos e acabamento
- Embalagem, caixa, etiqueta, sacola.
- Cola, tinta, primer, lixa.
- Ferragens: ímã, argola de chaveiro, parafuso, fita, LED, pilha.
- Cada item tem **preço unitário e quantidade por peça** — 4 parafusos de R$ 0,30 entram como R$ 1,20 na peça, não R$ 0,30.
- O app traz um **catálogo rápido** dos insumos mais comuns (argola, saquinho, cartão de brinde, tag, ímã, parafuso, rolamento, LED, feltro, cola, tinta) com preço de partida editável. Tocar duas vezes no mesmo item soma quantidade em vez de duplicar a linha.

### 2.6 Reserva para falhas
- Peça que soltou da mesa às 3 da manhã, rolo embolado, arquivo com problema.
- Referência: **5% a 15%**, conforme o risco do trabalho.
- **A conta certa é dividir, não somar.** Se 10% falha, cada peça boa precisa carregar a peça morta: `custo ÷ 0,90`, e não `custo × 1,10`. Dá diferença real no fim do mês.

### 2.7 Taxas do canal e margem
- Comissão de marketplace, taxa fixa por item, taxa de maquininha/Pix, imposto.
- **Elas incidem sobre o preço final, não sobre o custo** — por isso precisam entrar por divisão (ver seção 3.3).
- Margem de lucro: o que sobra pra você depois de tudo. Referência de mercado brasileiro: **50% a 150% de markup**, sendo margem menor em peças simples e concorridas, maior em peça exclusiva ou personalizada.

---

## 3. As fórmulas

### 3.1 Custo de produção

```
preço_por_grama   = preço_do_rolo ÷ peso_do_rolo_em_gramas
custo_material    = gramas_da_peça × (1 + desperdício%) × preço_por_grama

custo_energia     = (potência_W ÷ 1000) × horas_de_impressão × tarifa_kWh

custo_hora_máquina = (valor_da_impressora ÷ vida_útil_horas)
                     + (manutenção_anual ÷ horas_por_ano)
custo_máquina     = custo_hora_máquina × horas_de_impressão

custo_mão_de_obra = (minutos_de_preparo ÷ 60 × valor_hora)      ← por lote
                    + (minutos_de_acabamento ÷ 60 × valor_hora)  ← por peça

custo_insumos     = soma de (preço_unitário × quantidade) de cada insumo

subtotal          = material + energia + máquina + mão_de_obra + insumos

CUSTO_REAL        = subtotal ÷ (1 − taxa_de_falha%)
```

### 3.2 Preço direto (WhatsApp, PIX, venda na mão)

Aqui existe uma pegadinha clássica. **Markup e margem não são a mesma coisa.**

```
Por markup (multiplicar):   preço = custo × (1 + markup%)
Por margem (dividir):       preço = custo ÷ (1 − margem%)
```

Sobre um custo de R$ 29,03:
- **50% de markup** → R$ 43,55 (que na verdade é 33% de margem)
- **50% de margem** → R$ 58,06

O app vai deixar você escolher o modo e **mostrar o outro número junto**, para não confundir os dois.

### 3.3 Preço com taxas (marketplace, maquininha, imposto)

Precificação "de trás para frente": você parte da margem que quer receber **limpa** e o app descobre o preço de etiqueta.

```
PREÇO_FINAL = (CUSTO_REAL + taxa_fixa + frete_por_sua_conta)
              ÷ (1 − comissão% − imposto% − margem%)
```

**Trava obrigatória**: se `comissão + imposto + margem ≥ 100%`, não existe preço possível. O app precisa avisar em vez de mostrar número absurdo ou infinito.

### 3.4 Conferência (o painel que mais importa)

Depois de calcular, o app mostra o caminho inverso do dinheiro — é isso que dá confiança no número:

```
Preço de etiqueta          R$ 82,58
− Comissão (20%)          −R$ 16,52
− Taxa fixa               −R$  4,00
= Você recebe              R$ 62,06
− Custo real              −R$ 29,03
= LUCRO LÍQUIDO            R$ 33,03   (40,0%)
```

---

## 4. Exemplo completo para validar o app

Use estes números para conferir se a conta está batendo depois de pronto.

| Item | Entrada | Cálculo | Valor |
|---|---|---|---|
| Filamento | 82 g, rolo R$ 110/1000 g, 8% desperdício | 88,56 g × R$ 0,11 | R$ 9,74 |
| Energia | 150 W, 9 h, R$ 0,75/kWh | 1,35 kWh × 0,75 | R$ 1,01 |
| Máquina | R$ 2.500 ÷ 4.000 h | R$ 0,625/h × 9 h | R$ 5,63 |
| Mão de obra | 20 min a R$ 25/h | 0,333 h × 25 | R$ 8,33 |
| Insumos | embalagem + argola | — | R$ 2,00 |
| **Subtotal** | | | **R$ 26,71** |
| Falhas 8% | 26,71 ÷ 0,92 | | **R$ 29,03** |

**Preço final com 40% de margem:**

| Canal | Conta | Preço |
|---|---|---|
| Direto / PIX | 29,03 ÷ 0,60 | **R$ 48,38** |
| Marketplace 20% + R$ 4 fixo | (29,03 + 4) ÷ 0,40 | **R$ 82,58** |

A mesma peça vale R$ 48 na sua mão e R$ 83 no marketplace. **Esse é o motivo do app existir** — vender no marketplace pelo preço da venda direta é prejuízo silencioso.

---

## 5. Estrutura do app

Quatro abas na base da tela (padrão de app, o polegar alcança).

### Aba 1 — Calcular (tela inicial)
O caminho rápido. Só isto aparece de cara:

1. Seletor de **impressora** (o que você cadastrou)
2. Seletor de **filamento**
3. **Gramas** (do fatiador)
4. **Horas e minutos** de impressão
5. **Quantidade de peças**
6. Botão grande: **Calcular preço**

Tudo o mais (desperdício, mão de obra, insumos, falhas) fica em blocos recolhíveis com valores já preenchidos pelos Ajustes. Quem quiser afinar, abre. Quem não quiser, não vê.

**Toggle importante:** "Os valores do fatiador são para → [1 peça] [a mesa toda]". Se for a mesa toda, o app divide pela quantidade.

**Resultado:** card fixo com o preço sugerido em destaque, a decomposição do custo, o painel de conferência e o comparativo entre canais lado a lado.

**"Como esse custo foi montado":** bloco recolhível que mostra a fórmula de cada camada com os números do momento — `82,0 g + 8% desperdício × R$ 0,11/g`, `(150 W ÷ 1000) × 2,50 h × R$ 0,75/kWh`, `R$ 0,63/h × 2,50 h`, `R$ 13,99 ÷ 0,92`. Serve para conferir de onde veio cada centavo e para explicar o preço ao cliente sem decorar conta.

### Aba 2 — Impressoras
Cadastro: apelido, potência (W), valor de compra, vida útil em horas, manutenção anual estimada. O app calcula e mostra o **custo/hora** automaticamente — aberto em **depreciação + manutenção**, para a conta não virar um número mágico — e permite sobrescrever manualmente.

### Aba 3 — Filamentos
Cadastro: apelido, material (PLA/PETG/ABS/TPU/outro), cor, preço do rolo, peso do rolo. Mostra o **preço por grama** calculado.

### Aba 4 — Ajustes
Tarifa do kWh, valor da sua hora, desperdício padrão, taxa de falha padrão, margem padrão, e a lista de **canais de venda** (nome, comissão %, taxa fixa R$, imposto %).

### Extra — Histórico
Orçamentos salvos com nome do cliente/peça, data e preço. Permite reabrir, duplicar e recalcular. Mais botão **Exportar / Importar JSON** para backup e para levar os dados de um aparelho pro outro.

---

## 6. Canais de venda — padrões sugeridos

⚠️ **Taxas de marketplace mudam com frequência.** Estes são pontos de partida editáveis, com base na pesquisa de agosto/2026. Confirme sempre no painel oficial do canal antes de precificar.

| Canal | Comissão | Taxa fixa | Observação |
|---|---|---|---|
| Direto / PIX | 0% | R$ 0 | O melhor cenário |
| Maquininha (crédito) | 3% a 5% | R$ 0 | Varia por operadora e parcelamento |
| Shopee | ~14% a 20% | R$ 4 a R$ 26 | Escalonada por faixa de preço; o teto de R$ 100 foi removido em 2026 |
| Mercado Livre | 10% a 19% | variável | Desde março/2026 há tarifa por peso e faixa de preço |
| Elo7 | ~12% | — | Público mais alinhado a peça artesanal/personalizada |

**Detalhe traiçoeiro da Shopee**: as faixas criam um degrau. Um produto a R$ 79,99 pode pagar menos taxa em reais do que um a R$ 80,00. Se der tempo, vale um aviso no app quando o preço calculado cair a poucos reais acima de um limite de faixa.

---

## 7. Interface e responsividade

### Direção visual proposta
Nada de "SaaS genérico". A referência é o mundo da própria impressora: mesa de impressão, camadas, leitura de painel.

- **Paleta**: base clara fria tipo vidro de mesa de impressão (`#EDF0F3`), grafite do chassi (`#151A21`), laranja de bico quente para o número principal (`#FF6B2C`), verde-azulado para lucro positivo (`#0F9D8F`), âmbar para alertas (`#E4B429`).
- **Tipografia**: números em fonte **monoespaçada** (o valor precisa parecer medido, não estimado); títulos em uma sans com caráter técnico; corpo em fonte de sistema para carregar rápido. Fontes via CDN com fallback de sistema.
- **Elemento assinatura**: a **barra de camadas**. O custo aparece empilhado horizontalmente como as camadas de uma impressão — material, energia, máquina, mão de obra, falhas, taxa, lucro — cada faixa com sua cor e largura proporcional. Você bate o olho e vê onde o dinheiro está indo. É o gráfico mais honesto possível para este produto e ninguém mais usa.

### Alvos de tela

| Dispositivo | Largura CSS | Layout |
|---|---|---|
| iPhone 14 Plus | 428 × 926 | 1 coluna, abas na base |
| Galaxy S23 Ultra | ~412 × 915 | 1 coluna, abas na base |
| Tablet | 768–1023 | 2 colunas |
| Desktop | ≥ 1024 | Formulário à esquerda, resultado fixo (sticky) à direita |

### Regras técnicas obrigatórias
- `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` e `env(safe-area-inset-bottom)` no rodapé — senão as abas ficam embaixo da barra de gestos do iPhone.
- `100dvh` em vez de `100vh` — o Chrome do Android muda de altura quando a barra de endereço some.
- Inputs com `font-size: 16px` no mínimo, ou o iOS dá zoom sozinho ao tocar no campo.
- `inputmode="decimal"` nos campos numéricos — abre o teclado numérico direto.
- Áreas de toque com no mínimo 48 px de altura.
- **Aceitar vírgula E ponto** como separador decimal. Brasileiro digita `0,75`; o `parseFloat` do JavaScript lê isso como `0`. Erro clássico e silencioso.
- Foco visível no teclado e `prefers-reduced-motion` respeitado.
- CSS `@media print` para gerar o orçamento em PDF pelo próprio navegador, sem biblioteca nenhuma.

---

## 8. Técnica e publicação

- **Um único arquivo `index.html`**, com CSS e JavaScript dentro. Vanilla JS, sem framework, sem build.
- **Armazenamento**: `localStorage` para impressoras, filamentos, ajustes e histórico — envolvido em `try/catch` com queda para memória, para o app não quebrar em ambiente que bloqueia storage.
- **Backup**: exportar e importar um arquivo `.json`.
- **Funciona offline** depois do primeiro carregamento (útil em feira e evento).

### Publicar no GitHub (sem terminal)
1. Criar um repositório novo, público, por exemplo `calculadora-3d`.
2. **Add file → Upload files**, arrastar o `index.html`, **Commit changes**.
3. **Settings → Pages → Source: Deploy from a branch → main / (root) → Save**.
4. Em 1–2 minutos o link fica no ar: `https://SEUUSUARIO.github.io/calculadora-3d/`.
5. Para atualizar, é só subir o `index.html` novo por cima.

No celular, abrir o link e usar "Adicionar à tela de início" — vira um ícone e abre como app.

---

## 9. Fora do escopo da v1

Ideias boas, mas que atrapalham se entrarem agora:

- Leitura automática do arquivo `.gcode` para preencher gramas e horas
- Resina / SLA (mililitros em vez de gramas)
- Multicolor com torre de purga calculada
- Custo fixo mensal rateado (aluguel, internet) por volume de peças
- Cálculo de frete por CEP
- Catálogo de produtos com preço já fechado
- Nuvem / login

---

## 10. Decisões tomadas (v1)

| Pergunta | Resposta | Efeito no app |
|---|---|---|
| Onde vende? | Só direto (WhatsApp/PIX) | Comparador de canais **fora**. Sobrou um único campo opcional de taxa de recebimento em Ajustes, padrão 0%. A seção 6 fica como referência para o dia em que abrir marketplace. |
| Como imprime? | Depende do pedido | Toggle "1 peça / mesa toda" **entra**. Mão de obra separada em preparo por lote e acabamento por peça. |
| O que importa na v1 | PDF, histórico, cálculo simples | Tela principal com 6 campos; o resto recolhido em "Ajuste fino". |

Resina, leitura de `.gcode` e custo fixo mensal ficam para depois.

---

## Fontes consultadas

Precifi3D, CalculaSTL, Tamo Tudo 3D, CaniveteMEI, PrintCal, National 3D, Galpão das Máquinas, Snapmaker, Firgelli, PrintNexus, 3DPCC, 3D Costify, Ecommerce na Prática, Anymarket, Irroba, Calcularte, YAV.

---

# Adendo — v2 (agosto/2026)

A v1 era um app de cálculo. A v2 vira um app de **controle**: o preço que você
escolheu fica salvo, o produto tem foto e categoria, e tudo aparece igual nos
2 ou 3 aparelhos que você usa.

## 11. O que entrou

### 11.1 Sincronização na nuvem (Firebase)
Estava em "fora do escopo" na v1 pelo motivo certo: nuvem antes de a conta
estar correta é distração. Com a conta pronta, ela virou a peça que faltava —
não adianta cadastrar produto no celular e não achar no computador.

- **Firebase Auth (e‑mail/senha)** + **Firestore**, carregados por CDN só
  quando você configura. Sem configuração, o app não faz nenhuma requisição e
  segue 100% local, como antes.
- A configuração do projeto vem **embutida no `index.html`**: em cada aparelho
  novo basta **entrar com o mesmo e‑mail e senha**. É o login que amarra os
  dados, e não há nada para colar.
- Dá para sair da nuvem a qualquer momento (e voltar) sem perder nada, e para
  apontar o app para outro projeto do Firebase.
- Sincronização em tempo real por `onSnapshot`, um documento por item. Duas
  pessoas editando coisas diferentes não se atropelam.
- Cache offline do Firestore ligado: sem internet o app continua funcionando e
  envia sozinho quando a conexão volta.
- Passo a passo e regras de segurança no arquivo `FIREBASE.md`.

### 11.2 Preço escolhido
O app sugeria um preço e você perdia esse número ao fechar a tela. Agora:

- Campo **"Preço que eu vou cobrar"**, com atalhos de arredondamento
  (R$ 48,90 / R$ 50) calculados a partir do sugerido.
- A conferência recalcula lucro e margem **reais** com o seu preço, e mostra
  quanto você está cobrando a mais ou a menos que o sugerido.
- O preço escolhido fica salvo no produto e no orçamento.

### 11.3 Catálogo de produtos
- Cadastro com **até 3 fotos** por produto (câmera ou galeria), comprimidas no
  próprio navegador para caber na nuvem e no aparelho.
- **Categorias** editáveis (nome + cor), com filtro por categoria e busca.
- **Link do modelo / STL** (MakerWorld, Printables, Thingiverse, Cults…) —
  para reimprimir sem caçar o arquivo e para conferir a licença.
- Guarda os parâmetros do cálculo: gramas, horas, impressora, filamento,
  margem, desperdício, falhas, mão de obra e insumos. Um toque em **Abrir na
  calculadora** e o produto volta exatamente como estava.

### 11.4 Compras e notas fiscais
- Registro de compra com data, valor, tipo, loja, **nº da nota/pedido**, link
  do pedido e **foto do comprovante**.
- Total do mês e total do filtro no topo, busca e exportação em **CSV** para
  fechar o mês na planilha.
- Atalho **"Registrar uma compra deste rolo"** dentro do cadastro de filamento:
  o formulário (data, rolos, valor, loja) abre na própria ficha do rolo, diz o
  que vai acontecer antes de confirmar e só leva para a tela de Compras se o
  usuário quiser anexar a nota.

### 11.5 Link de compra do filamento
Cadastro de filamento ganhou **marca/loja** e **link de compra** — quando o
rolo acabar, é um toque para recomprar o mesmo e conferir se o preço mudou.

### 11.6 Explicações no lugar onde a dúvida aparece
Botão `?` ao lado dos campos que confundem — margem × markup, desperdício,
reserva de falhas, preparo × acabamento, tarifa de kWh, custo/hora da máquina,
1 peça × mesa toda. Passe o mouse no computador, toque no celular.

## 12. Estrutura do app na v2

Seis abas: **Calcular · Produtos · Compras · Salvos · Cadastros · Ajustes**.
Impressoras e filamentos ficam juntos em *Cadastros*; a sincronização mora em
*Ajustes*.

## 13. Técnica

- Continua **um único `index.html`**, vanilla JS, sem build.
- Fotos em **IndexedDB** no aparelho (o `localStorage` não aguentaria) e num
  documento por foto no Firestore. `localStorage` segue guardando o resto.
- Firebase carregado por `import()` dinâmico, com fallback de versão. Se o
  navegador não suportar módulos ES, o app avisa e segue no modo local.
- Backup `.json` agora inclui categorias, produtos, compras e as fotos.

## 14. Continua fora do escopo

Leitura de `.gcode`, resina/SLA, torre de purga calculada, custo fixo mensal
rateado, frete por CEP e comparador de marketplaces.

---

# Adendo — v3 (agosto/2026)

A v2 fechou a conta e o controle. A v3 fecha a **venda**: o orçamento deixa de
ser uma peça solta e vira um pedido — com cliente, várias peças, desconto,
frete, envio pelo WhatsApp e acompanhamento até o dinheiro entrar. E o app,
que já prometia funcionar offline, passa a cumprir isso de fato.

## 15. O que entrou

### 15.1 PWA completo — abre e instala sem depender da rede
A v2 prometia "funciona offline depois do primeiro carregamento" e "adicionar à
tela de início", mas isso dependia do cache HTTP do navegador.

- `manifest.webmanifest` com ícones (192, 512 e maskable), `display:standalone`,
  cores de tema e `apple-touch-icon` para o iOS.
- **Service worker** (`sw.js`): a casca do app fica em cache e abre sem rede. A
  página usa *network-first* de propósito — o app é um arquivo só, e um HTML
  velho preso no cache seria uma versão inteira congelada no aparelho. O cache
  é a rede de segurança do modo offline, nunca a fonte preferida.
- Nada de origem externa passa pelo service worker: as fontes do Google e o
  Firebase (que usa conexões longas e streaming) vão direto para a rede.
- As **fontes não seguram mais a tela**: a folha do Google Fonts é carregada
  sem bloquear o render e entra quando chega. Numa feira sem sinal, o app abre
  na hora com a pilha de fallback em vez de esperar o tempo de conexão.
- Botão **Instalar o app** em *Ajustes*, guardando o `beforeinstallprompt` — o
  Chrome só oferece a instalação uma vez, e o evento morre se ninguém o
  guardar. No iOS, onde esse evento não existe, aparece a instrução do Safari.

### 15.2 Orçamento com cliente e várias peças
Pedido real é "3 chaveiros + 1 vaso", não uma peça só.

- **Cliente** (nome e WhatsApp) e **observações** no orçamento.
- Várias linhas no mesmo orçamento: calcule uma peça, toque em **+ Adicionar
  esta peça ao orçamento**, calcule a próxima. Cada item guarda o cálculo
  inteiro — dá para **editar** um item, que volta para a calculadora do jeito
  que estava, e salvar a alteração no lugar.
- **Desconto** em R$ ou %, **frete/entrega** e **total do pedido**, com lucro
  estimado do pedido inteiro. O frete aparece como repasse, fora do lucro.
- Enquanto ninguém adiciona nada, o orçamento **espelha a peça que está na
  calculadora**. Quem só quer o preço de uma peça não precisa saber que existe
  uma lista — o caminho rápido continua de um toque.
- O rascunho do orçamento fica **só neste aparelho**: um pedido meio montado
  pulando de celular para celular no meio de uma venda confundiria mais do que
  ajudaria.

### 15.3 Enviar pelo WhatsApp
O público vende por WhatsApp; até aqui o único jeito de mandar o preço era
gerar o PDF e caçar o arquivo.

- **Enviar no WhatsApp**: monta o texto formatado (itens, quantidade, unitário,
  subtotal, desconto, frete, total, prazo de produção e validade) e abre a
  conversa direto no número do cliente. O número brasileiro é aceito digitado
  de qualquer jeito; sem número, o WhatsApp abre a lista de contatos.
- **Copiar orçamento** para colar em qualquer lugar, com fallback para
  navegadores sem a API de área de transferência.
- **Compartilhar** via `navigator.share` onde o aparelho oferece.
- O **PDF** passou a aceitar as várias linhas, o bloco do cliente, desconto e
  frete — a tabela já tinha a estrutura, ganhou as linhas.

### 15.4 Salvos virou gestão de pedidos
Antes a aba só abria e excluía. Agora um orçamento salvo é um pedido em
andamento:

- **Status**: orçado → aprovado → imprimindo → entregue → pago.
- **Data de entrega** por pedido.
- **Busca** por peça, cliente ou observação, e **filtro por status** com
  contagem.
- **Em aberto** e **recebido este mês** no topo — o mês do recebido conta a
  data em que o pedido foi marcado como pago.
- **Duplicar** (o cliente que sempre pede a mesma coisa), **abrir de volta**
  no orçamento e mandar o WhatsApp direto do pedido salvo.

## 16. Compatibilidade

Pedidos salvos na v2 eram uma peça só e sem status. Eles continuam abrindo:
viram um pedido de um item, com status *orçado*, sem precisar reescrever nada
no armazenamento.

## 17. Continua fora do escopo

O de sempre — leitura de `.gcode`, resina/SLA, torre de purga calculada, custo
fixo mensal rateado, frete por CEP e comparador de marketplaces — mais:
anexar o PDF no `navigator.share` (exigiria uma biblioteca de PDF embarcada, e
o app gera o orçamento pela impressão do próprio navegador) e cadastro de
clientes com histórico próprio.

---

# Adendo — v4 (agosto/2026)

A v3 fechou a venda. A v4 fecha o **dinheiro**: o app já guardava receita
(pedidos) e despesa (compras) e nunca cruzava as duas, já sabia o lucro de cada
peça e nunca dizia qual valia a pena imprimir, já sabia o peso do rolo e nunca
o quanto ainda sobrava dentro dele. Nenhuma das quatro entregas abaixo pede um
dado novo do usuário que ele não tivesse motivo para dar.

## 18. O que entrou

### 18.1 Painel do mês
Aba nova, entre *Salvos* e *Cadastros*, com um seletor de mês (a faixa vai do
mês mais antigo com movimento até o corrente). São **duas bases de apuração**,
cada uma dita na tela para ninguém somar laranja com banana:

- **Dinheiro** — pedidos marcados como *Pago*, pelo mês do pagamento.
- **Produção** — pedidos que passaram de *orçado*, pelo mês em que foram
  criados. É o que aproxima as horas que a máquina de fato rodou.

Os blocos:

- **Resultado do mês**: recebido → frete repassado → venda das peças → taxas de
  recebimento → custo de produção → **lucro** e margem, com uma barra de
  composição. A taxa de recebimento, que fica escondida dentro do lucro de cada
  item, é aberta aqui.
- **Caixa do mês**: entrou (pedidos pagos) − saiu (compras registradas) =
  saldo. É de propósito diferente do lucro, e a tela explica por quê: um rolo
  de R$ 110 sai do caixa hoje e vira custo aos poucos, a cada peça impressa.
- **Produção do mês**: horas impressas, filamento em kg, peças, pedidos, lucro
  por hora de máquina e ticket médio. Com o rateio ligado, mostra também como
  as horas do mês se comparam com as horas configuradas em *Ajustes* — é o
  sinal para calibrar o palpite.
- **O que deu mais lucro**: os itens dos pedidos pagos agrupados por produto (ou
  por nome), ordenados por lucro, com o lucro por hora ao lado.
- **Em aberto agora**: o que ainda não entrou, por status. Vale para todos os
  meses, não só o selecionado.
- **Rolos acabando**: ligado ao link de recompra do cadastro (§11.5).

### 18.2 Lucro por hora de máquina
O recurso escasso não é dinheiro, é hora de impressora: duas peças com o mesmo
lucro não valem o mesmo se uma leva 2 h e a outra 20 h.

- Indicador **Lucro / hora** na Conferência, ao lado de preço por grama e por
  hora (os quatro viraram uma grade 2×2).
- No **catálogo de produtos**, cada card mostra o lucro por hora de máquina, e
  a lista pode ser ordenada por *A–Z*, *Lucro / h* ou *Lucro*. Produto salvo com
  os números da mesa cheia tem as horas divididas pela quantidade antes da
  conta.
- Na ficha do produto, mais uma linha em *Preço*.

### 18.3 Estoque do rolo
O cadastro de filamento já tinha o peso do rolo; faltava saber quanto ainda tem
dentro dele.

- Campos **Estoque** (g restantes) e **Avisar em** (g), com barra de nível e
  botão **Repor estoque**, que devolve o peso cadastrado sem registrar compra
  nenhuma.
- Campo vazio quer dizer *não controlo este rolo*, que é diferente de 0 g, que
  quer dizer *rolo acabado*. Por isso o estoque é texto, como o custo/hora
  manual da impressora.
- **Baixa automática ao salvar o orçamento**, já contando o desperdício que o
  próprio item assumiu no cálculo. O pedido guarda que a baixa foi aplicada, e
  duplicar não desconta de novo.
- **Avisos ligados ao link de recompra** (§11.5): na calculadora, quando o rolo
  selecionado está acabando, acabado ou não dá para o pedido; abaixo do botão
  de salvar, com o que saiu de cada rolo; e no Painel do mês.

### 18.4 Custo fixo mensal rateado
Estava em "fora do escopo" desde a v1 (§9, §14, §17) e era o maior erro de
precisão que sobrou: aluguel, internet, assinatura do fatiador, energia da
máquina parada, contador.

- Dois campos em *Ajustes*: **custo fixo (R$/mês)** e **horas impressas por
  mês**. O rateio vira R$/h e cada peça paga a fatia do tempo que ocupou a mesa.
- Entra como camada própria (*Custo fixo*) na pilha do preço e na memória de
  cálculo, ao lado de filamento, energia, máquina, mão de obra e insumos.
- Ambos nascem em **0**: quem nunca abrir *Ajustes* continua com o preço de
  antes, e o rateio só passa a valer quando o usuário informa os dois números.
- A caixa de apoio mostra o R$/h resultante, quanto uma peça de 9 h paga e a
  **média real de horas por mês** dos pedidos do próprio usuário — o número com
  que ele calibra o palpite em vez de chutar.

## 19. Compatibilidade

- Filamentos antigos sobem sem estoque (campo vazio) e com aviso em 150 g.
- Pedidos salvos antes da v4 são marcados como *baixa já aplicada*, para que um
  "duplicar" antigo não desconte o rolo retroativamente.
- Ajustes antigos ganham `fixed:0` e `fixedHours:0` — nenhum preço muda sozinho.
- Os campos novos sincronizam junto com os documentos que já iam para a nuvem;
  nada mudou no formato do backup `.json` além dos campos a mais.

## 20. Continua fora do escopo

Leitura de `.gcode`, resina/SLA, torre de purga calculada, frete por CEP,
comparador de marketplaces, anexar o PDF no `navigator.share` e cadastro de
clientes com histórico próprio. O rateio do custo fixo **saiu** desta lista.

---

# Adendo — v5 (agosto/2026)

A v4 fechou o dinheiro. A v5 ataca as três coisas que ainda separavam o app do
jeito como o negócio realmente funciona: o número era **digitado à mão** do
fatiador para o celular, a peça só podia ter **uma cor**, e o preço era sempre
de **uma unidade** — quando quase toda venda que vale a pena é por lote.

## 21. O que entrou

### 21.1 Importar G-code / 3MF
Prusa, Orca, Bambu e Cura escrevem gramas, tempo, tipos e cores em **texto puro**
no cabeçalho (Cura) ou no rodapé (os demais) do arquivo fatiado. Ler isso tira o
maior atrito do app e o único erro que o cálculo não consegue perceber: o de
digitação.

- Zona de arrastar-e-soltar no topo de *Do fatiador*; o arquivo pode cair em
  **qualquer lugar** da tela de calcular, e um toque abre o seletor de arquivos.
- Formatos: `.gcode`, `.gco`, `.g`, `.gcode.gz` e `.3mf` já fatiado. O `.3mf` é
  um ZIP: o diretório central é lido na mão e o conteúdo inflado pelo
  `DecompressionStream` do próprio navegador — **sem biblioteca**.
  - Bambu e Orca guardam o resultado em `Metadata/slice_info.config`, com uma
    linha por filamento (gramas, cor, material) e o tempo previsto da mesa.
  - 3MF que é só projeto (não foi fatiado) recebe um recado dizendo isso, em vez
    de um erro genérico.
- Arquivo de 100 MB não é lido inteiro: só os **400 KB de cada ponta**, que é
  onde os cabeçalhos ficam.
- Quando o arquivo traz apenas o comprimento (o caso do Cura), o peso sai de
  `volume × densidade`, com a densidade do material — e a tela diz que foi
  calculado, não lido.
- **O desperdício é zerado na importação.** O arquivo já contou brim, suporte e
  purga; manter a porcentagem por cima cobraria o mesmo material duas vezes.
- Os valores são sempre da **mesa toda** — o escopo muda sozinho e o resumo pede
  para conferir a quantidade de peças.
- O nome da peça, quando está vazio, sai do nome do arquivo.

### 21.2 Multicolor / AMS
Com AMS, CFS ou MMU a torre de purga costuma **pesar mais que a peça**, e o
desperdício deixa de ser uma porcentagem do tamanho: é o volume de cada troca.

- Chave *1 filamento / Multicolor* logo abaixo da impressora. No modo
  multicolor, uma **linha por cor**: filamento cadastrado + gramas.
- **Torre de purga em gramas absolutas**, não em %. Ela é rateada entre as cores
  na mesma proporção em que cada uma entra na peça, porque o que sai na purga é
  filamento de todas elas misturado.
- A memória de cálculo abre **uma linha por rolo** e mostra quanto a purga
  representa do peso total.
- O **estoque dá baixa em todos os rolos** usados, cada um com o que lhe cabe;
  os avisos de rolo acabando passam a valer por rolo.
- O orçamento e o PDF descrevem a peça como `PLA + PETG` quando ela mistura
  materiais.
- Produto salvo guarda as cores e a purga, e volta com elas ao abrir na
  calculadora.

### 21.3 Preço por faixa de quantidade
O preparo é por lote: fatiar, limpar a mesa, trocar o filamento e ligar custa o
mesmo para 1 ou para 50 peças. Diluído, o preço unitário cai com o volume — e
essa queda é **matemática do próprio cálculo**, não um desconto inventado.

- Tabela no painel de resultado, ao lado da conferência: preço unitário, total,
  lucro e o quanto cai em relação à primeira faixa.
- As faixas são editáveis (padrão `1, 10, 50`, até seis) e ficam nos *Ajustes*,
  sincronizadas como o resto.
- **Copiar** manda a tabela pronta para o WhatsApp, com a frase que explica por
  que o preço cai.
- Com preço escolhido na mão, as faixas mantêm o **multiplicador** que o usuário
  decidiu sobre o custo, não a margem teórica que ele não quis.
- Com preparo em 0 min todas as faixas dão o mesmo preço, e a tela diz por quê —
  é o empurrão para preencher o campo que quase todo mundo deixa em branco.

## 22. Compatibilidade

- Pedidos e produtos salvos antes da v5 continuam com um filamento só: a baixa
  de estoque cai no caminho antigo (gramas líquidas + desperdício) quando o item
  não traz a lista por rolo.
- Ajustes antigos ganham `tiers:'1, 10, 50'`; nenhum preço muda sozinho.
- O modo multicolor nasce desligado e não altera nenhum cálculo de quem não usa.
- Navegador sem `DecompressionStream` continua lendo `.gcode` normal; o `.3mf` e
  o `.gz` avisam que não dá e pedem o G-code.

## 23. Continua fora do escopo

Resina/SLA, `.bgcode` binário do Prusa, ler a miniatura embutida no G-code para
virar foto do produto, frete por CEP, comparador de marketplaces, anexar o PDF
no `navigator.share` e cadastro de clientes com histórico próprio. A leitura de
`.gcode` e a torre de purga **saíram** desta lista.
