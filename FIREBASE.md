# Sincronizar aparelhos e contas (Firebase)

A configuração do Firebase **já vem dentro do app** (no topo do bloco de
sincronização, em `index.html`). Em cada aparelho novo você só precisa
**fazer login**. Nada de colar código.

Os dados são **da empresa, não de cada conta**: todas as contas deste projeto
gravam e leem a mesma pasta (`orgs/empresa`). Você e sua esposa podem ter cada
um o seu e‑mail e a sua senha — os dois veem o mesmo catálogo, os mesmos
clientes e os mesmos orçamentos. Não há código para trocar nem convite para
aceitar: **quem tem conta neste projeto vê os dados**. Por isso o passo 5 aqui
embaixo, fechar o cadastro, deixa de ser recomendação e vira parte do
serviço.

Projeto usado: **`lyke3dcalc`**.

O app funciona sem nuvem também — se a internet cair, ele continua calculando e
salvando, e envia sozinho quando a conexão voltar.

---

## O que já está pronto

- Firebase Auth (e‑mail/senha) + Firestore, carregados por CDN.
- Fotos guardadas dentro do próprio Firestore (não usamos o Firebase Storage,
  que hoje exige plano pago) e em cache no aparelho.
- Plano **gratuito (Spark)** dá conta com folga.

## O que falta fazer no console, uma vez só

Abra <https://console.firebase.google.com> no projeto `lyke3dcalc`.

### 1. Ligar o login por e‑mail
**Criação › Authentication › Sign-in method** → ative **E‑mail/senha** e salve.

### 2. Criar o banco
**Criação › Firestore Database › Criar banco de dados**, região
**`southamerica-east1` (São Paulo)**.

### 3. Publicar as regras de segurança — **obrigatório**

Em **Firestore Database › Regras**, apague o que estiver lá, cole isto e clique
em **Publicar**:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // a empresa é uma só: toda conta deste projeto usa os mesmos dados
    match /orgs/empresa/{document=**} {
      allow read, write: if request.auth != null;
    }
    // vitrines: o link público que o cliente abre sem ter conta nenhuma.
    // Só entra aqui o que VOCÊ mandou publicar, e só você pode escrever.
    match /pub/{code}/{document=**} {
      allow read: if true;
      allow write: if request.auth != null;
    }
    // pasta antiga, de quando cada conta guardava tudo separado
    match /users/{uid}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

Estas regras mandam ninguém sem conta chegar perto do banco, e toda conta do
projeto compartilhar a pasta da empresa. Quem já usava a versão anterior
precisa publicar estas regras **antes** de abrir o app atualizado — senão o
app avisa que "o Firestore recusou o acesso".

A pasta `pub` é a **única** aberta para a internet, e é assim de propósito: o
link público precisa abrir no celular de quem não tem conta. O código da
vitrine tem 10 letras sorteadas — quem não recebeu o link não acha a página —,
e **nada** de custo, margem, gramas, tempo ou impressora é gravado ali: só nome,
descrição, fotos, vídeos e o seu preço de venda dos produtos que você marcou.
Tirou o link do ar, o documento é apagado e o endereço deixa de existir.

Sem esta parte das regras, o app avisa na hora de publicar que "o Firestore
recusou a publicação".

Sem isso, ou o Firestore bloqueia tudo (o app avisa "o Firestore recusou o
acesso"), ou o banco fica aberto para qualquer pessoa da internet.

### 4. Liberar o endereço do app
**Authentication › Settings › Domínios autorizados** → adicione o domínio onde
o app está publicado, por exemplo `yurisb-lab.github.io`. O `localhost` já vem
liberado.

Sem esse passo o login falha com `auth/unauthorized-domain`.

### 5. Fechar o cadastro — **obrigatório**

A chave do Firebase é pública por natureza (vai no código de qualquer app web) e
o repositório é aberto. Como agora **toda conta do projeto vê os dados da
empresa**, a lista de contas é a lista de quem enxerga: com o cadastro aberto,
um estranho poderia criar uma conta e entrar junto.

Crie as suas duas contas e então vá em **Authentication › Settings › User
actions** e **desmarque "Enable create (sign-up)"**. Vocês continuam entrando
normalmente; só param os cadastros novos.

Precisou de mais uma conta depois? Crie direto no console, em
**Authentication › Users › Adicionar usuário** — sem reabrir o cadastro.

Extra, se quiser apertar mais: no Google Cloud Console, em **APIs e serviços ›
Credenciais**, restrinja a chave por **referenciador HTTP** aos seus domínios.

---

## Usar em cada aparelho, e nas duas contas

1. Abra o app.
2. **Ajustes › Sincronização entre aparelhos**.
3. **Criar conta** na primeira vez; **Entrar** depois — no seu celular, no
   computador e na conta da sua esposa.

Pronto. O que um mudar aparece para o outro em segundos, e o painel mostra
**Contas que usam estes dados**, para vocês conferirem que as duas estão
ligadas.

Se cada conta já tinha dados da versão antiga: a primeira que entrar leva os
dela para a empresa; o que estava na outra continua guardado na pasta antiga
dela e pode ser trazido com **Backup › Exportar** e **Backup › Importar**.

### O link público (vitrine)

Em **Negócio › Link público** você escolhe produtos do catálogo e recebe um
endereço para mandar no WhatsApp — algo como
`https://yurisb-lab.github.io/calc3d/p.html?v=k7m2pq9xrb`. Quem abrir vê as
fotos, os vídeos, a descrição e o preço, marca a quantidade que quer e devolve
o pedido pronto no seu WhatsApp.

- A vitrine é a página `p.html`, que fica ao lado do app. Ela não pede login,
  não usa o SDK do Firebase (lê o Firestore direto, para abrir rápido no 4G) e
  não instala nada no celular do cliente.
- **Publicar** exige estar conectado à nuvem: é a sua conta que grava em `pub`.
- **Tirar do ar** apaga o documento e as fotos publicadas; o endereço passa a
  mostrar "este link não está mais no ar".
- Mudou a foto, o preço ou a descrição de um produto? Toque em **Atualizar
  link** — a vitrine não acompanha o catálogo sozinha, para você não publicar
  sem querer um preço que ainda estava sendo mexido.

### Sair da nuvem
No mesmo painel, **"Usar só neste aparelho, sem nuvem"**. Nada é apagado, e o
botão **Voltar a usar a nuvem** desfaz.

### Usar outro projeto do Firebase
No modo local, abra **"Usar outro projeto do Firebase"** e cole o
`firebaseConfig` do outro projeto.

---

## Como os dados ficam guardados

```
orgs/empresa/
  members/{uid}          contas que usam o app (só o e‑mail, para o painel)
  meta/settings          ajustes (tarifa, valor da hora, taxas, dados do orçamento)
  printers/{id}          impressoras
  filaments/{id}         filamentos (com marca e link de compra)
  categories/{id}        categorias do catálogo
  products/{id}          produtos (nome, categoria, link do STL, seu preço, parâmetros)
  buys/{id}              compras e notas fiscais
  jobs/{id}              orçamentos salvos
  photos/{id}            fotos: miniatura + imagem, em JPEG comprimido
  links/{id}             links públicos (quais produtos, título, WhatsApp)

pub/{codigo}             a vitrine publicada, aberta para qualquer pessoa
  photos/{id}            cópia pública só das fotos dos produtos publicados
```

Cada foto é um documento separado, comprimido para caber com folga no limite de
1 MB por documento do Firestore, e fica em cache no aparelho (IndexedDB) para
abrir rápido e funcionar sem internet.

## Perguntas rápidas

**Vai passar do plano gratuito?** É muito difícil. O Spark dá 50 mil leituras e
20 mil escritas por dia e 1 GiB de armazenamento. Um catálogo de algumas
centenas de produtos com fotos usa uma fração disso.

**E os dados que eu já tinha na nuvem, da versão anterior?** Na primeira
entrada, se a pasta da empresa ainda estiver vazia, o app copia sozinho o que
estava em `users/{uid}` para lá. A pasta antiga não é apagada.

**E se eu já tinha dados no aparelho antes de conectar?** Se a nuvem estiver
vazia, o app sobe tudo automaticamente. Se a nuvem já tiver dados, ela manda na
primeira conexão — e os dados locais ficam guardados; use **Enviar dados deste
aparelho** em Ajustes › Sincronização para juntá‑los.

**Se eu mexer num cadastro nos dois aparelhos ao mesmo tempo?** Ganha a versão
mais nova, cadastro por cadastro. Depois da primeira conexão a nuvem não
substitui mais a lista inteira: o que você acabou de digitar e o que ainda nem
subiu continuam valendo, e o aparelho reenvia o que ficou.

**Como troco o projeto do Firebase de vez?** Edite `BUILTIN_CFG` no topo do
bloco de sincronização, dentro do `index.html`.
