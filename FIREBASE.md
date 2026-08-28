# Sincronizar entre 2 ou 3 aparelhos (Firebase)

O app funciona sozinho, sem nuvem — os dados ficam no próprio aparelho. Este
guia liga a **sincronização**: você cadastra tudo no celular e aparece no
computador, e vice‑versa, em segundos.

Use o **plano gratuito (Spark)**. Não precisa cartão. As fotos são guardadas
dentro do próprio Firestore (não usamos o Firebase Storage, que hoje exige
plano pago).

---

## 1. Criar o projeto

1. Abra <https://console.firebase.google.com> e clique em **Criar um projeto**.
2. Dê um nome (ex.: `calculadora-3d`). Pode desativar o Google Analytics.

## 2. Criar o banco

1. No menu, **Criação › Firestore Database › Criar banco de dados**.
2. Escolha a região **`southamerica-east1` (São Paulo)** — é a mais perto.
3. Pode começar em modo de teste; no passo 5 você troca pelas regras certas.

## 3. Ligar o login por e‑mail

1. **Criação › Authentication › Primeiros passos**.
2. Na aba **Sign-in method**, ative **E‑mail/senha** e salve.

> É o login que amarra os aparelhos. Todos entram com **o mesmo e‑mail e a
> mesma senha** e enxergam os mesmos dados.

## 4. Pegar a configuração

1. Engrenagem **Configurações do projeto › Seus apps**.
2. Clique no ícone **`</>`** (Web), dê um apelido e registre.
3. Copie o bloco `firebaseConfig` que aparece — ele se parece com isto:

   ```js
   const firebaseConfig = {
     apiKey: "AIza...",
     authDomain: "calculadora-3d.firebaseapp.com",
     projectId: "calculadora-3d",
     storageBucket: "calculadora-3d.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abc123"
   };
   ```

4. No app, vá em **Ajustes › Sincronização entre aparelhos**, cole esse bloco
   inteiro no campo e toque em **Conectar**.
5. Toque em **Criar conta**, com o e‑mail e a senha que você vai usar em todos
   os aparelhos.

Essa configuração **não é segredo** — ela vai no código de qualquer app web.
Quem protege os dados são as regras do passo 5 e a sua senha.

## 5. Publicar as regras de segurança (obrigatório)

Em **Firestore Database › Regras**, apague o que estiver lá, cole isto e
clique em **Publicar**:

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

Sem isso, ou o Firestore bloqueia tudo (o app mostra "o Firestore recusou o
acesso"), ou o banco fica aberto para qualquer pessoa da internet.

## 6. Liberar o endereço onde o app está publicado

Se você abre o app pelo GitHub Pages, vá em **Authentication › Settings ›
Domínios autorizados** e adicione o domínio, por exemplo
`seuusuario.github.io`. `localhost` já vem liberado.

Sem esse passo o login falha com `auth/unauthorized-domain`.

## 7. Repetir nos outros aparelhos

Em cada celular ou computador: abra o app, **Ajustes › Sincronização**, cole a
**mesma** configuração, toque em **Conectar** e depois em **Entrar** com o
mesmo e‑mail e senha. Pronto.

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

Cada foto é um documento separado, comprimido para caber com folga no limite
de 1 MB por documento do Firestore, e fica em cache no aparelho (IndexedDB)
para abrir rápido e funcionar sem internet.

## Perguntas rápidas

**Vai passar do plano gratuito?** É muito difícil. O plano Spark dá 50 mil
leituras e 20 mil escritas por dia e 1 GiB de armazenamento. Um catálogo de
algumas centenas de produtos com fotos usa uma fração disso.

**Funciona sem internet?** Sim. O app continua calculando e salvando; quando a
conexão volta, o Firestore envia o que ficou pendente sozinho.

**E se eu já tinha dados no aparelho antes de conectar?** Se a nuvem estiver
vazia, o app sobe tudo automaticamente. Se a nuvem já tiver dados, ela manda —
e os dados locais ficam guardados; use **Enviar dados deste aparelho** em
Ajustes › Sincronização para juntá‑los.

**Quero parar de usar a nuvem.** Em Ajustes › Sincronização, toque em
**Remover configuração**. O app volta ao modo local e nada é apagado.
