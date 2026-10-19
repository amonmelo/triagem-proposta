# DESIGN — triagem-proposta

**O desenho em uma frase:** o código decide, o modelo apresenta. As regras R1–R6 vivem em `triagem/regras.py` (Python puro, zero dependências); o Claude só entrega o JSON à linha de comando e mostra o card que volta. Mesma entrada, mesmo parecer — sempre.

## Onde entra a revisão humana, e por quê

A revisão entra onde o código não consegue *verificar* um fato, só desconfiar: CAR "Pendente" (R3), cadastro diferente de "Regular" (R4), divergência acima de 5% entre matrícula e CAR (R5) e campo ausente ou ilegível (R6). Recusa é outra coisa: área pequena (R1) e desmatamento após o corte (R2) são fatos objetivos — o código recusa sem cerimônia. Duas decisões que tomei nessa fronteira: quando RECUSADA e REVISÃO aparecem juntas, vale RECUSADA e o parecer lista todos os motivos; e dado quebrado (área negativa, número escrito como texto, alerta com data no futuro) não recusa "na letra" — vai para revisão humana, porque recusar proponente por erro de digitação é desperdiçar negócio.

## Como levaria para dados reais (SICAR, PRODES, Receita) e o que pode dar errado

Trocaria cada campo digitado por consulta: status do CAR no SICAR, alertas no PRODES/DETER cruzando o polígono, situação cadastral na Receita pelo CNPJ. O que pode dar errado — e como contorno: (1) a proposta não traz identificador confiável do imóvel no CAR, só matrícula — precisaria combinar com o time jurídico qual chave usar; (2) fontes externas caem ou mudam de formato — a consulta vira passo assíncrono com cache, retentativas e comprovante datado guardado; (3) a base do PRODES e o polígono do CAR divergem entre si — o parecer precisa registrar qual versão de base foi usada; (4) status da Receita muda com o tempo — o parecer diria "Regular *na consulta de 12/03*", nunca "é Regular". Sobre os status reais de CNPJ: manteria só "Regular" passando reto, como o comitê definiu (comparando sem diferenciar maiúsculas e espaços, como na R3 — "REGULAR" é o mesmo status); "Pendente de regularização" e "Suspensa" vão para revisão humana com prazo de regularização; "Inapta", "Baixada" e "Nula" eu levaria ao comitê como candidatas a recusa direta — empresa sem existência válida não sustenta financiamento —, mas isso é mudança de regra deles, não decisão minha.

## Quando o comitê muda uma regra

As regras já são constantes nomeadas num módulo próprio; mudar "100 ha" é uma linha. O fluxo: issue → PR que **primeiro ajusta os testes** para o novo limite (os bordais 100 ha, 01/01/2020 e 5% estão travados em teste) → muda a constante → CI verde → tag (ex.: `regras-v2`) e o campo `esquema` do parecer sobe de `/1` para `/2`. Publicar para o time é mesclar na main e atualizar a pasta da skill (`~/.claude/skills/` ou a skill distribuída do Desktop). Por um ciclo, as duas versões rodariam em paralelo comparando pareceres antes da troca definitiva.

## Como um analista não técnico passa a usar — e a confiar

Uso: abre o Claude, cola o JSON (ou anexa o arquivo) e pede "tria essa proposta"; o card que volta já é a tarefa no gerenciador de tarefas do time. A confiança vem de três hábitos, não de discurso: todo parecer cita a regra e o valor recebido (o analista confere na hora, sem abrir código); os testes e o CI provam que os limites são exatamente os do comitê; e uma amostra semanal de pareceres é conferida à mão contra as fontes. Se o analista discorda de um resultado, ele não edita a decisão — abre issue para o comitê mudar a regra.

## Como usei IA

O teste permite e recomenda — usei IA como par de programação: esqueleto do pacote, primeira bateria de testes de borda e uma segunda opinião sobre as ambiguidades do enunciado (o dia 01/01/2020, o 5% exato, o alerta ilegível). As decisões de desenho são minhas, e o comportamento está provado nos testes — que eu li, rodei e ajustei um a um. A tentação quando se usa IA é inflar: cortei do rascunho tudo o que o enunciado não pedia — com IA, o trabalho difícil é decidir o que não construir.
