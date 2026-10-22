# DESIGN: triagem-proposta

O código decide, o modelo apresenta. As regras R1 a R6 moram em `triagem/regras.py`, Python puro e sem dependências. O Claude só entrega o JSON à linha de comando e mostra o card que volta. Mesma entrada, mesmo parecer, sempre.

## Onde entra a revisão humana

Entra onde o código não consegue verificar um fato, só desconfiar: CAR "Pendente" (R3), cadastro diferente de "Regular" (R4), divergência acima de 5% entre matrícula e CAR (R5) e campo ausente ou ilegível (R6). Já área pequena (R1) e desmatamento depois do corte (R2) são fatos objetivos, e o código recusa sem cerimônia.

Duas decisões minhas nessa fronteira. Quando RECUSADA e REVISÃO aparecem juntas, vale RECUSADA e o parecer lista todos os motivos. E dado quebrado (área negativa, número escrito como texto, alerta com data no futuro) vai para revisão, não para recusa: recusar um proponente por erro de digitação é jogar negócio fora.

**Revisão no Asana.** O time usa o Asana e hoje não há prazo para a revisão. O card já sai em Markdown, pronto para a descrição da tarefa; `--quadro` simula isso em arquivo, e em produção o mesmo bloco iria pela API. Como sugestão minha, não regra deles: prazo de 2 dias úteis como data de entrega, responsável atribuído pelo projeto e cada pendência virando subtarefa. Duas semanas de uso mostram se 2 dias é folga ou aperto.

## Dados reais (SICAR, PRODES, Receita)

Cada campo digitado vira uma consulta: status do CAR no SICAR, alertas no PRODES/DETER cruzando o polígono, situação cadastral na Receita pelo CNPJ. O que pode dar errado:

1. A proposta pode trazer só a matrícula, sem identificador confiável do CAR. Teria de combinar com o jurídico qual chave usar.
2. Fontes externas caem ou mudam de formato. A consulta vira passo assíncrono, com cache, retentativas e comprovante datado.
3. PRODES e polígono do CAR divergem entre si. O parecer registra qual versão da base foi usada.
4. A Receita muda com o tempo. O parecer diz "Regular na consulta de 12/03", nunca "é Regular".

**Data de corte da R2.** No teste vale a data do alerta no JSON (a Beatriz confirmou). Com dado real, separo data do alerta, data de publicação da base e ano de referência. O PRODES é anual: "desmatamento de 2020" não diz se foi antes ou depois de 01/01/2020. O DETER traz data por alerta e aplica o corte exato. Se a fonte só tem o ano, 2020 é ambíguo e vai para revisão, citando a base usada.

**Status de CNPJ.** Só "Regular" passa, sem diferenciar maiúsculas. "Pendente de regularização" e "Suspensa" vão para revisão, com prazo. "Inapta", "Baixada" e "Nula" eu levaria ao comitê como candidatas a recusa direta, porque empresa sem existência válida não sustenta financiamento. Mas mudar regra é decisão deles, não minha.

## Quando o comitê muda uma regra

Os limites são constantes nomeadas, então mudar "100 ha" é uma linha. O fluxo: issue, depois um PR que primeiro ajusta os testes ao novo limite (100 ha, 01/01/2020 e 5% estão travados em teste), depois a constante, CI verde, tag como `regras-v2` e o campo `esquema` do parecer sobe de `/1` para `/2`. Para o time, mescla na main e atualiza a pasta da skill. Por um ciclo, as duas versões rodam em paralelo e comparo os pareceres antes da troca.

## Como o analista passa a usar e a confiar

Abre o Claude, anexa o JSON e pede "tria essa proposta". A confiança vem de três hábitos. Todo parecer cita a regra e o valor recebido, então o analista confere sem abrir código. Os testes e o CI provam que os limites são os do comitê. E uma amostra semanal de pareceres é conferida à mão contra as fontes. Se o analista discorda de um resultado, não edita a decisão: abre issue para o comitê mudar a regra.

## Como usei IA

Como par de programação: esqueleto do pacote, primeira bateria de testes de borda e uma segunda opinião sobre as ambiguidades do enunciado (o dia 01/01/2020, o 5% exato, o alerta ilegível). As decisões são minhas, e o comportamento está provado em testes que li, rodei e ajustei um a um. Cortei do rascunho tudo que o enunciado não pedia, porque com IA o trabalho difícil é decidir o que não construir.
