/* Service worker da Calculadora 3D.
   Objetivo: abrir sem rede e poder ser instalado na tela inicial.

   Regra de ouro: a página NUNCA é servida do cache quando há rede. O app é um
   arquivo só, então um HTML velho preso no cache seria uma versão inteira
   congelada no aparelho do usuário. Por isso navegação e index.html usam
   network-first — o cache é só a rede de segurança do modo offline.

   Nada de origem externa passa por aqui: as fontes do Google e, principalmente,
   o Firebase (que usa fetch de longa duração e streaming) precisam ir direto
   para a rede, sem interferência. */

var VERSION = 'calc3d-v4';
var SHELL = ['./', './index.html', './manifest.webmanifest',
             './icone-192.png', './icone-512.png', './icone-512-mask.png', './icone-180.png',
             './lyke-marca.png', './lyke-logo.png'];

self.addEventListener('install', function(e){
  e.waitUntil(
    caches.open(VERSION)
      /* addAll é tudo-ou-nada: um ícone ausente derrubaria a instalação inteira */
      .then(function(c){ return Promise.all(SHELL.map(function(u){ return c.add(u).catch(function(){}); })); })
      .then(function(){ return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function(e){
  e.waitUntil(
    caches.keys()
      .then(function(ks){ return Promise.all(ks.map(function(k){ return k === VERSION ? null : caches.delete(k); })); })
      .then(function(){ return self.clients.claim(); })
  );
});

function putCopy(req, res){
  if(res && res.ok && res.type === 'basic'){
    var copy = res.clone();
    caches.open(VERSION).then(function(c){ c.put(req, copy); }).catch(function(){});
  }
  return res;
}

self.addEventListener('fetch', function(e){
  var req = e.request;
  if(req.method !== 'GET') return;

  var url;
  try { url = new URL(req.url); } catch(err){ return; }
  if(url.origin !== self.location.origin) return;   /* fontes e Firebase vão direto */

  var isPage = req.mode === 'navigate' || /\/(index\.html)?$/.test(url.pathname);

  if(isPage){
    /* rede primeiro: uma versão nova do app sempre ganha da cópia guardada */
    e.respondWith(
      fetch(req)
        .then(function(res){ return putCopy(req, res); })
        .catch(function(){
          return caches.match(req).then(function(hit){
            return hit || caches.match('./index.html') || caches.match('./');
          });
        })
    );
    return;
  }

  /* demais arquivos do próprio app (ícones, manifest): cache primeiro, com
     atualização silenciosa em segundo plano */
  e.respondWith(
    caches.match(req).then(function(hit){
      var net = fetch(req).then(function(res){ return putCopy(req, res); }).catch(function(){ return hit; });
      return hit || net;
    })
  );
});
