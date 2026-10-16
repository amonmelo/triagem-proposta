# PERGUNTAS — respostas da seção 8

> **⚠️ Nota para mim antes de entregar (depois apagar este aviso):**
> o teste pede resposta com base no que eu **fiz**, não em teoria — e diz que admitir "não tenho experiência" vale mais que resposta genérica. A banca conversa sobre essas respostas na apresentação de 30 min, então: revisar cada `[CONFIRMAR]`, trocar pelos fatos com os meus números, e escrever com as minhas palavras. Nada aqui cita nomes internos de empregador — é projeto pessoal mesmo.

## 1. GitHub em equipe: branches, revisão, conflitos, permissões e versões

O repositório deste teste mostra como trabalho sozinho: commits pequenos com mensagem que explica o porquê, testes rodando no CI a cada push, e a main sempre verde.

Em equipe, `[CONFIRMAR — contar a situação real, com nome do contexto, tamanho do time e por quanto tempo]`. O desenho que costuma funcionar e que já usei:

- **Branches:** uma branch curta por tarefa (`feature/...`, `fix/...`), vida de poucos dias, merge cedo para não acumular divergência. Trunk-based na prática: a main é a verdade e ninguém commita direto nela.
- **Revisão de código:** PR pequeno (< ~300 linhas quando dá), revisado por pelo menos uma pessoa antes do merge; o CI reprova o merge que quebra teste. Revisão olha comportamento e legibilidade, não formalidade.
- **Conflitos:** resolvidos localmente com rebase na main antes do merge — e quando o mesmo arquivo mudou em duas frentes, a conversa acontece na issue antes, não no merge.
- **Permissões e versões:** main protegida (só entra por PR); quem cuida das permissões e das tags/release `[CONFIRMAR: era eu? um tech lead? como era o processo de publicar uma versão?]`.

## 2. Google Cloud

`[CONFIRMAR — responder só com o que for verdade. Se não usei Google Cloud em produção, dizer isso direto e mostrar que entendo os cuidados, por exemplo:]`

Não coloquei Google Cloud em produção; a infra que mantenho roda `[CONFIRMAR: VPS Linux com Docker / outra]`. O que eu trataria com cuidado em qualquer nuvem, e com Google Cloud em particular: service account com papel mínimo por função (nunca chave de admin no código), segredos no Secret Manager em vez de variável de ambiente versionada, e orçamento com alerta configurado no primeiro dia — custo descontrolado é o modo mais rápido de perder confiança no projeto.

## 3. Apps Script / Google Sheets

`[CONFIRMAR — se não fiz automação com Apps Script, ser direto e conectar com o mais próximo:]`

Não tenho automação em produção com Apps Script. O que faço hoje cobre o mesmo tipo de problema com Python: `[CONFIRMAR — exemplo real, ex.: ler/atualizar planilhas via API, robôs que leem fonte externa e escrevem num relatório, alertas automáticos]`. O padrão é o mesmo do Apps Script: gatilho, leitura da fonte, escrita no destino e notificação quando algo falha.

## 4. APIs REST (Asana, Slack, Gmail, Pipedrive…)

Já integrei várias — no meu projeto pessoal de automação eu falo diariamente com `[CONFIRMAR — listar as que rodam de verdade, ex.: Microsoft Graph (e-mail), portais de ATS, API do Telegram]`. O que aprendi na prática:

- **Autenticação:** OAuth com token de acesso e refresh; quando o 401 chega, o fluxo renova o token e repete a chamada uma vez antes de falhar de verdade. Credencial nunca no repositório — fica em cofre local/banco de credenciais próprio.
- **Limite de chamadas:** espalho as chamadas no tempo em vez de estourar o rate limit, e quando o 429 vem, backoff exponencial com teto. `[CONFIRMAR um número real: quantas chamadas/dia, qual janela]`
- **Erros:** retentativa só para erros transitórios (5xx/rede), com operação idempotente para não duplicar efeito; erro permanente cai num log com o request/response guardado para auditoria — já me salvou mais de uma vez provar o que foi enviado e quando.

## 5. LLM: agente/automação com Claude, skills e MCP

Sim — mantenho hoje uma automação multiagente que usa Claude via skills e MCP para `[descrever em uma frase o que a automação faz — CONFIRMAR como quer apresentar]`. O que funcionou de verdade:

- **Tirar a decisão de dentro do modelo.** O maior erro que cometi foi confiar regra de negócio ao prompt: o modelo "acha" às vezes, e "às vezes" não serve. Agora regra determinística é código com teste (este teste prático é exatamente esse princípio); o modelo orquestra e apresenta.
- **Skills com passo a passo curto e script por trás.** O SKILL.md manda o agente executar o script e mostrar o resultado — não reescrever.
- **Limites duros contra espiral.** Máximo de tentativas por campo/passo; na terceira falha, para e escala para humano. Loop infinito de agente é caro e constrangedor.

O que deu errado e como corrigi: `[CONFIRMAR — escolher 1–2 histórias reais, ex.: modelo improvisando decisão → mover para código; sessão longa degradando → resumo/reinício; custo de round-trip → agrupar chamadas]`.

## 6. Docker

Já usei para subir serviço em contêiner em servidor próprio: `[CONFIRMAR — o que roda em contêiner hoje, como é o compose, volumes, restart policy]`. Senhas e chaves eu trato assim: nada de segredo na imagem ou no repositório — entra em runtime por variável de ambiente/secret, a imagem roda sem privilégio, e `.dockerignore` para nenhum arquivo sensível vazar no build. `[CONFIRMAR se roda build próprio ou imagem pronta]`

## 7. Django

`[CONFIRMAR — responder com a verdade. Se não trabalhei com Django, dizer direto, sem enrolar:]` Não construí projeto em produção com Django. Conheço a estrutura (apps, ORM, admin, migrations) `[ajustar ao que realmente conhece]`, e a parte que eu uso no dia a dia — modelar dados, migração de schema e API — já fiz `[CONFIRMAR: com qual ferramenta? Flask? FastAPI? scripts + banco?]`.
