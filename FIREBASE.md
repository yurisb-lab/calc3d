# Sincronizar entre 2 ou 3 aparelhos (Firebase)

A configuração do Firebase **já vem dentro do app** (no topo do bloco de
sincronização, em `index.html`). Em cada aparelho novo você só precisa
**fazer login com o mesmo e‑mail e a mesma senha**. Nada de colar código.

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
    // cada conta só enxerga e só escreve na própria pasta
    match /users/{uid}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

Sem isso, ou o Firestore bloqueia tudo (o app avisa "o Firestore recusou o
acesso"), ou o banco fica aberto para qualquer pessoa da internet.

### 4. Liberar o endereço do app
**Authentication › Settings › Domínios autorizados** → adicione o domínio onde
o app está publicado, por exemplo `yurisb-lab.github.io`. O `localhost` já vem
liberado.

Sem esse passo o login falha com `auth/unauthorized-domain`.

### 5. Fechar o cadastro depois de criar suas contas — recomendado

A chave do Firebase é pública por natureza (vai no código de qualquer app web),
e o repositório é aberto. As regras do passo 3 garantem que **ninguém enxerga os
seus dados** — cada conta só acessa a própria pasta. Mas, enquanto o cadastro
estiver aberto, um estranho poderia criar uma conta no projeto e consumir a sua
cota à toa.

Depois de criar a sua conta e entrar em todos os aparelhos, vá em
**Authentication › Settings › User actions** e **desmarque "Enable create
(sign-up)"**. Você continua entrando normalmente; só param os cadastros novos.
Se precisar de mais um aparelho depois, é só marcar de novo por um minuto.

Extra, se quiser apertar mais: no Google Cloud Console, em **APIs e serviços ›
Credenciais**, restrinja a chave por **referenciador HTTP** aos seus domínios.

---

## Usar em cada aparelho

1. Abra o app.
2. **Ajustes › Sincronização entre aparelhos**.
3. **Criar conta** no primeiro aparelho; **Entrar** nos outros, com o mesmo
   e‑mail e senha.

Pronto. O que você mudar num aparelho aparece nos outros em segundos.

### Sair da nuvem
No mesmo painel, **"Usar só neste aparelho, sem nuvem"**. Nada é apagado, e o
botão **Voltar a usar a nuvem** desfaz.

### Usar outro projeto do Firebase
No modo local, abra **"Usar outro projeto do Firebase"** e cole o
`firebaseConfig` do outro projeto.

---

## Como os dados ficam guardados

```
users/{seu-id}/
  meta/settings          ajustes (tarifa, valor da hora, taxas, dados do orçamento)
  printers/{id}          impressoras
  filaments/{id}         filamentos (com marca e link de compra)
  categories/{id}        categorias do catálogo
  products/{id}          produtos (nome, categoria, link do STL, seu preço, parâmetros)
  buys/{id}              compras e notas fiscais
  jobs/{id}              orçamentos salvos
  photos/{id}            fotos: miniatura + imagem, em JPEG comprimido
```

Cada foto é um documento separado, comprimido para caber com folga no limite de
1 MB por documento do Firestore, e fica em cache no aparelho (IndexedDB) para
abrir rápido e funcionar sem internet.

## Perguntas rápidas

**Vai passar do plano gratuito?** É muito difícil. O Spark dá 50 mil leituras e
20 mil escritas por dia e 1 GiB de armazenamento. Um catálogo de algumas
centenas de produtos com fotos usa uma fração disso.

**E se eu já tinha dados no aparelho antes de conectar?** Se a nuvem estiver
vazia, o app sobe tudo automaticamente. Se a nuvem já tiver dados, ela manda — e
os dados locais ficam guardados; use **Enviar dados deste aparelho** em Ajustes
› Sincronização para juntá‑los.

**Como troco o projeto do Firebase de vez?** Edite `BUILTIN_CFG` no topo do
bloco de sincronização, dentro do `index.html`.
