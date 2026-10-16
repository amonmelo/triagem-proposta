---
name: triagem-proposta
description: Triagem determinística de propostas de recuperação de pastagens degradadas (regras R1–R6). Aplica as regras em código Python e devolve parecer SEGUE, RECUSADA ou REVISÃO HUMANA com motivos, pendências e card em Markdown. Use quando o usuário trouxer o JSON de uma proposta (anexado ou colado) ou pedir um parecer de triagem.
---

# Triagem de propostas

Sua função aqui é OPERAR A FERRAMENTA, nunca decidir as regras: o parecer vem
sempre do script. O código é o pacote `triagem/` dentro desta pasta.

## Passo a passo

1. Localize esta pasta (a que contém este SKILL.md).
2. Obtenha a proposta em JSON: se veio anexada, use o arquivo direto; se foi
   colada no chat, salve primeiro em um arquivo temporário `.json` (UTF-8).
3. Rode, a partir desta pasta:

   ```
   python -m triagem <arquivo.json> --card
   ```

   (se o `python -m` não achar o pacote, use `python run.py <arquivo.json> --card`.)

4. Apresente o card EXATAMENTE como o script devolveu — não reescreva, não
   resuma, não mude o parecer.
5. Se o usuário pedir o detalhe (regra por regra), rode de novo com `--json`
   e mostre o parecer completo.
6. Várias propostas: rode uma por uma, ou aponte a pasta com os JSONs
   (`python -m triagem pasta/ --card`) e apresente um card por proposta.

## Regras de ouro

- NUNCA invente nem ajuste parecer: se o script disse RECUSADA, é RECUSADA.
- Se o script falhar (JSON inválido, campo quebrado), mostre a mensagem de
  erro dele e peça a correção — não tente "adivinhar" a triagem.
- O script é determinístico: mesma entrada, mesma saída. Não "melhore" as
  mensagens que ele devolve.
