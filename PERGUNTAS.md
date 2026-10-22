# PERGUNTAS — respostas da seção 8

## 1. GitHub em equipe: branches, revisão, conflitos, permissões e versões

Já trabalhei em equipe com GitHub, e o repositório deste teste mostra como eu costumo fazer: commits pequenos com mensagem que explica o porquê, testes rodando no CI a cada push e a main sempre verde.

- **Branches:** uma branch curta por tarefa (`feature/...`, `fix/...`), vida de poucos dias, merge cedo para não acumular divergência. A main é a verdade e ninguém commita direto nela.
- **Revisão de código:** PR pequeno (menos de ~300 linhas quando dá), revisado por pelo menos uma pessoa antes do merge; o CI reprova o merge que quebra teste. A revisão olha comportamento e legibilidade, não formalidade.
- **Conflitos:** resolvidos localmente com rebase na main antes do merge. Quando o mesmo arquivo mudou em duas frentes, a conversa acontece antes, na issue, e não na hora do merge.
- **Permissões e versões:** main protegida (só entra por PR) e versões marcadas com tag (`v1.2.0`), para saber exatamente o que está em produção e voltar atrás se precisar.

## 2. Google Cloud

Já coloquei serviço no Google Cloud em produção. O que eu cuido em qualquer nuvem: service account com papel mínimo por função (nunca chave de admin no código), segredos no Secret Manager em vez de variável de ambiente versionada e orçamento com alerta configurado no primeiro dia, porque custo descontrolado é o modo mais rápido de perder a confiança no projeto.

## 3. Apps Script / Google Sheets

Já automatizei planilhas com Apps Script. O padrão que sigo é sempre o mesmo: gatilho (horário ou edição), leitura da fonte, escrita no destino e aviso quando algo falha, para ninguém descobrir o erro só quando o número está errado. Fora do Apps Script, faço o mesmo tipo de automação em Python, lendo e escrevendo planilhas por API.

## 4. APIs REST (Asana, Slack, Gmail, Pipedrive…)

Já integrei várias. No meu projeto pessoal de automação eu falo todos os dias com a API do Microsoft Graph (e-mail), com o Telegram e com portais de recrutamento. O que aprendi na prática:

- **Autenticação:** OAuth com token de acesso e refresh. Quando o 401 chega, o fluxo renova o token e repete a chamada uma vez antes de falhar de verdade. Credencial nunca fica no repositório; fica em cofre local, no banco.
- **Limite de chamadas:** espalho as chamadas no tempo em vez de estourar o rate limit, e quando o 429 vem, faço backoff exponencial com teto.
- **Erros:** retentativa só para erros transitórios (5xx e rede), com operação idempotente para não duplicar efeito. Erro permanente cai num log com o pedido e a resposta guardados, o que já me salvou mais de uma vez na hora de provar o que foi enviado e quando.

## 5. LLM: agente/automação com Claude, skills e MCP

Sim. Mantenho hoje uma automação com vários agentes que usa Claude via skills e MCP para buscar vagas, qualificar, preencher candidaturas e acompanhar as respostas por e-mail. O que funcionou de verdade:

- **Tirar a decisão de dentro do modelo.** O maior erro que cometi foi confiar regra de negócio ao prompt: o modelo "acha" às vezes, e "às vezes" não serve. Hoje regra determinística é código com teste (este teste prático é exatamente esse princípio); o modelo orquestra e apresenta.
- **Skills com passo a passo curto e script por trás.** O SKILL.md manda o agente executar o script e mostrar o resultado, não reescrever.
- **Reserva antes de agir.** Com vários agentes, cada um reserva o recurso (a vaga, a caixa de e-mail) antes de tocar nele. Sem isso, dois agentes faziam a mesma candidatura duas vezes; agora uma trava no banco impede.
- **Limites duros contra espiral.** Máximo de tentativas por passo; na segunda falha o agente contorna ou registra e segue. Loop infinito de agente é caro e constrangedor.

O que deu errado e como corrigi: (1) o modelo improvisava uma decisão que deveria ser regra, então a decisão virou código com teste e o modelo ficou só com a apresentação; (2) um robô registrava "enviado" sem a conta estar logada, e várias candidaturas nunca existiram. Passei a conferir o resultado real (o login e a página de confirmação) antes de gravar o status, em vez de confiar que a ação deu certo.

## 6. Docker

Uso Docker em servidor para subir serviços em contêiner. Segredos eu trato assim: nada de segredo na imagem ou no repositório. Entram em runtime por variável de ambiente ou secret, a imagem roda sem privilégio de root, e um `.dockerignore` evita que arquivo sensível vá junto no build. Com `restart: unless-stopped` e volumes nomeados para o que precisa sobreviver a uma troca de contêiner.

## 7. Django

Já fiz projeto com Django. Conheço a estrutura (apps, ORM, admin, migrations) e uso no dia a dia a parte de modelar dados, migrar schema e expor API. Onde preciso de algo mais leve, uso Python com FastAPI e Postgres, e a escolha depende do tamanho: Django quando o admin e o ORM economizam tempo, FastAPI quando é só uma API enxuta.
