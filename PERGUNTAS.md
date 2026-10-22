# Perguntas técnicas (seção 8)

Respondo com o que eu fiz. Onde foi trabalho de equipe, digo qual foi a minha parte.

## 1. GitHub em equipe

Na equipe do meu trabalho atual o fluxo é no GitLab, não no GitHub, mas é a mesma coisa: branch por demanda, merge request revisado antes de entrar, e o código passa por dev, homologação e produção em MRs separados. Quem decide o que sobe para produção é o líder técnico e o time de infra. A minha parte é abrir o MR com diff pequeno, responder a revisão e dar rebase na main antes do merge, porque conflito resolvido ali é bem mais barato do que no meio do merge. Também uso git worktree quando preciso tocar em duas demandas ao mesmo tempo.

Antes disso, por pouco mais de dois anos, fui líder da equipe de sistemas numa empresa de software. Lá eu não cuidava de branch, cuidava de pessoas, SLA e escala de suporte. No GitHub, sozinho, uso Actions para rodar teste a cada push, como neste repositório.

## 2. Google Cloud

Uso o BigQuery em produção. Carreguei mais de 72 milhões de registros públicos de CNPJ lá, tratando os dados inconsistentes, e fiz uma tela de NPS que lê do BigQuery no sistema do trabalho. Isso foi eu, sozinho. A conta e as permissões são do time de infra, então a parte de criar projeto, papel e orçamento não é minha, e não vou dizer que é. O que eu faço do meu lado: chave só de leitura para o que só lê, nada de credencial no repositório e olhar o custo da consulta antes de rodar em tabela grande, porque no BigQuery você paga pelo que varre.

## 3. Apps Script / Google Sheets

Já automatizei planilha, mas o meu uso mais forte de Google hoje é pela API e pelo MCP, não dentro do Apps Script. No `agentic-dev-platform` (meu projeto aberto, github.com/amonmelo/agentic-dev-platform) tem um servidor MCP que fala com Asana, Slack e Google, e qualquer ação que escreve passa por aprovação humana antes. A lógica de gatilho, leitura e escrita é a mesma do Apps Script, só muda onde ela roda.

## 4. APIs REST

Integrei CRM e ERP por REST e webhook no trabalho (Ploomes, Meetime, o ERP) e fiz uma API para parceiros, com autenticação Basic e uma credencial por parceiro, documentada para o time que ia integrar. Asana e Slack uso pelo MCP, como acima. No meu projeto pessoal falo com Microsoft Graph por OAuth: quando vem 401, renovo o token e repito a chamada uma vez, e só então falho. Erro de rede e 5xx eu repito, erro de regra eu não repito. Também aprendi a guardar o pedido e a resposta quando dá erro, porque é o que prova depois o que foi enviado.

## 5. LLM, agentes, skills e MCP

Esta é a minha área hoje. Montei sozinho, a partir de demandas reais do trabalho, uma plataforma no Claude Code com skills, agentes e hooks que leva a demanda do card até o merge request. O que funcionou:

- **Um agente cético.** Um subagente tenta refutar cada achado antes de virar código. Na dúvida, refuta.
- **Hook feito de métrica.** Medi que o comprovante de teste era pulado em 26 de 39 rodadas. Isso virou um portão de entrega, e deixou de depender de o agente lembrar.
- **Prova antes de aprovar.** Nada passa com mock ou cenário que não rodou.

O que deu errado: no meu robô pessoal de candidaturas, ele registrava vaga como enviada sem a conta estar logada. Descobri que 192 "enviadas" nunca existiram. Corrigi fazendo o robô conferir o resultado real (login e página de confirmação) antes de gravar, e com uma trava no banco para dois agentes não fazerem a mesma candidatura. É o mesmo princípio deste teste: o que decide é código, e o modelo só apresenta.

## 6. Docker

Uso no dia a dia, no trabalho e nos meus servidores. No trabalho, o deploy vai para Kubernetes via Rancher, e já peguei um incidente de produção que era armazenamento (PVC e arquivos estáticos). A análise de causa raiz foi minha, e a mudança de infra ficou com o time de plataforma. Sobre segredo: não vai na imagem nem no repositório. Entra por variável de ambiente ou secret na hora de subir, e o `.dockerignore` evita que arquivo sensível vá junto no build.

## 7. Django

Trabalhei com Django no sistema de inteligência comercial da empresa: cerca de 143 commits meus em poucos meses, com PostgreSQL, Oracle e BigQuery. Fiz telas, exportação em CSV e XLSX, filtros em cascata, sincronização agendada com o ERP (com timeout e registro de falha) e a API para parceiros. Também uso Flask, FastAPI e Bottle, e escolho pelo tamanho do problema: Django quando admin e ORM economizam tempo, uma API enxuta em FastAPI quando só preciso do endpoint.
