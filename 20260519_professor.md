
# 👨‍🏫 Guia do Professor — Aula OAuth (2026-05-19)

## Objetivos pedagógicos
- Apresentar OAuth 2.0 como evolução do login por senha local (gancho com a aula 2026-05-12).
- Mostrar o **Authorization Code Flow** passo a passo, com o aluno entendendo *que dado trafega em cada etapa*.
- Discutir a separação `client_id` (público) × `client_secret` (privado).
- Provocar a reflexão: *"se em produção cada app tem suas próprias chaves, por que nesta aula eu compartilhei uma chave única?"* → gancho para **PKCE** e para a pesquisa da seção 6.

---

## 1. Antes da aula: registrar o OAuth Client no Google

1. Acesse https://console.cloud.google.com/ logado com `crebollo@gmail.com`.
2. Crie um novo projeto: **"Curso SSI 2026"**.
3. **APIs & Services → OAuth consent screen**
   - User type: **External**
   - App name: `Curso SSI`
   - Support email: `crebollo@gmail.com`
   - Developer contact: `crebollo@gmail.com`
   - Scopes: adicionar `openid`, `.../auth/userinfo.email`, `.../auth/userinfo.profile`
   - **Test users:** adicionar o e-mail Google de cada aluno. (Se não publicar o app, só os e-mails listados conseguem entrar — isso evita que o app caia em moderação do Google e é suficiente para 20 alunos.)
4. **APIs & Services → Credentials → Create Credentials → OAuth Client ID**
   - Application type: **Web application**
   - Name: `Curso SSI Web`
   - **Authorized redirect URIs** — cadastrar as 10 URLs das duplas:
     ```
     https://curso.chr.eti.br/time01/callback
     https://curso.chr.eti.br/time02/callback
     https://curso.chr.eti.br/time03/callback
     https://curso.chr.eti.br/time04/callback
     https://curso.chr.eti.br/time05/callback
     https://curso.chr.eti.br/time06/callback
     https://curso.chr.eti.br/time07/callback
     https://curso.chr.eti.br/time08/callback
     https://curso.chr.eti.br/time09/callback
     https://curso.chr.eti.br/time10/callback
     ```
5. Anote o `client_id` e o `client_secret` — você vai distribuir para as duplas no início da aula (no quadro, num arquivo no Moodle/Classroom, ou via Slack/Discord da turma).

> ⚠️ **Importante:** se uma dupla esquecer de configurar o `REDIRECT_URI` exatamente como cadastrado (com a barra final ou sem), o Google devolve `redirect_uri_mismatch`. É o erro mais comum em laboratório.

---

## 2. Infra dos alunos (lembrete)

- 10 duplas: `time01` até `time10`.
- Cada uma roda Flask em `https://curso.chr.eti.br/timeNN`.
- Cada subdomínio precisa estar configurado no reverse proxy (nginx ou similar) para fazer proxy para a porta Flask de cada aluno (ex.: porta 5001 para time01, 5002 para time02, ...). Vale alinhar isso antes da aula ou pedir para eles usarem ports diferentes.
- Como o app é servido em `/timeNN/`, o `REDIRECT_URI` deve incluir esse prefixo. O Flask, internamente, vê apenas `/callback` (porque o proxy remove o prefixo). Se o proxy NÃO remover o prefixo, as rotas no Flask precisam ser `@app.route("/timeNN/callback")` etc.

---

## 3. Roteiro sugerido da aula (50 min)

| Tempo | Atividade |
|-------|-----------|
| 0–5   | Revisão rápida da aula passada (hash, MD5 vs SHA-256). |
| 5–15  | Explicar OAuth no quadro, desenhando o triângulo Usuário ↔ App ↔ Google. |
| 15–20 | Distribuir `client_id` e `client_secret`. Explicar a diferença. |
| 20–40 | Laboratório: cada dupla sobe o `app.py`. |
| 40–50 | Discussão: *"por que eu não deveria ter compartilhado o `client_secret`? Como uma app mobile faz sem ter `client_secret`?"* → introduzir **PKCE** rapidamente como teaser da pesquisa. |

---

## 4. Pontos de discussão em sala

1. **Por que não pedir a senha do Google direto na nossa app?**
   - Phishing: usuário não saberia diferenciar a "nossa" tela de login da do Google.
   - Escopos: com OAuth eu só peço o que preciso (e-mail, foto). Com senha eu teria acesso a tudo.
   - Revogação: o usuário pode revogar a permissão no painel do Google sem trocar a senha.

2. **O que é o `state` e por que existe?**
   - Token aleatório que a app gera antes de redirecionar. Quando o Google devolve, a app confere que é o mesmo. Evita **CSRF na fase de callback** (atacante forçando o usuário a logar com a conta do atacante).

3. **Por que `client_secret` é segredo, mas estamos compartilhando?**
   - Provocação proposital. Em aplicações reais cada cliente tem o seu. Em apps **mobile/SPA**, *nem se usa client_secret* — usa-se **PKCE** (Proof Key for Code Exchange). Esse é o gancho para a pesquisa da seção 6 do material do aluno.

4. **Onde fica o token? E se vazar?**
   - Na nossa app fica na sessão do Flask (cookie assinado, lado servidor). Se o token vazar, atacante pode agir como o usuário até o token expirar (geralmente 1h no Google).

---

## 5. Troubleshooting comum

| Sintoma | Causa provável |
|---------|----------------|
| `Error 400: redirect_uri_mismatch` | A `REDIRECT_URI` no código não bate **exatamente** com a cadastrada no Google Cloud Console. Cuidado com `http` vs `https`, barra final, e prefixo `/timeNN`. |
| `Error 403: access_denied` | E-mail do aluno não está na lista de Test Users do OAuth consent screen. |
| `invalid_client` na troca do code | `client_secret` foi colado errado (espaço no final é comum). |
| Página fica em loop entre `/` e `/login` | `app.secret_key` mudou entre requests (acontece se Flask reinicia em modo debug). Mantenha a chave fixa. |
| `state` inválido | A sessão não persistiu entre as duas requests. Quase sempre é problema de cookie/proxy. Verifique se o reverse proxy está repassando cookies. |

---

## 6. Variantes / extensões (se sobrar tempo)

- Mostrar como **revogar** a permissão no painel do Google (https://myaccount.google.com/permissions) e o que acontece quando o usuário volta no site.
- Decodificar o **`id_token`** (JWT) que vem junto na resposta do Google e mostrar que dá pra extrair os dados do usuário **sem chamar `userinfo`**. Bom gancho para JWT na próxima aula.
- Adicionar uma rota `/admin` que só funciona se o e-mail logado pertence a um whitelist. Mostra como OAuth é **autenticação** (quem é) — autorização (o que pode) ainda é responsabilidade da app.

---

## 7. Entrega das duplas — checklist de correção

- [ ] `app.py` enviado por e-mail com assunto `2026-05-19`
- [ ] Nome completo da dupla no corpo do e-mail
- [ ] `CLIENT_SECRET` **removido** do arquivo enviado (se não removeu, ponto de discussão na devolutiva)
- [ ] Pesquisa das 3 perguntas (PKCE, OAuth vs OIDC, vazamento de client_secret)
- [ ] Print mostrando o login funcionando com o nome/foto do aluno
