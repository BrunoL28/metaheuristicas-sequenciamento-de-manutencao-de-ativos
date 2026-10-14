# Auditoria de prompt injection

**Data:** 2026-10-14 · **Arquivos analisados:** 6 · **Scanner estrutural:** executado (`scan_injection.py`, PyMuPDF 1.28.2) + diff visual (render × camada de texto) + passada semântica

## Veredito

| Arquivo | Papel no trabalho | sha256 | Prompt injection |
|---|---|---|---|
| `INPUTS/_FundIA__TP2_BuscaLocal_GAs.pdf` | enunciado (7 p.) | a2df795a94db47fac51b1f1d920d8a7672ca047cc9bf38114f8d40f54f92b2cd | **NÃO** |
| `INPUTS/manutencao_pequena.txt` | instância (n = 12) | df6c118bec0dba6a92753af31faafaafbb5083b3de027aacb972b4ddd32fdab8 | **NÃO** |
| `INPUTS/manutencao_media.txt` | instância (n = 50) | a0530fea7fb109254e378a72789a6d1c6979ba0701504f9aa4211e80d8373d8f | **NÃO** |
| `INPUTS/manutencao_grande.txt` | instância (n = 150) | 947d97fadb372750d8c3fe39cb2bb5a5fa026b198b593d3680a6b20f33d6a639 | **NÃO** |
| `INPUTS/slides/Chapter_4_2026_1_Parts_1_2 (1).pdf` | referência — slides Cap. 4 (CSP, busca local, SA) | 21a467ce86375b95840c6009388d66af1247ed7a9f46965e2c1860ed5efa32ba | **NÃO** |
| `INPUTS/slides/Chapter_4_2026_1_Part3 (1).pdf` | referência — slides Cap. 4 parte 3 (AG, ED) | 863f7ddd55798ee7d24ef02cdf4aa16997bac1f630eaab05e861a9a4e31c8fe6 | **NÃO** |

## Itens descartados

- `_FundIA__TP2_BuscaLocal_GAs.pdf`, p. 3, bbox (275,663,275,674) — `off-page-text` (HIGH) — legítimo: é o caractere combinante `̸` (U+0338) que o LaTeX usa para desenhar `≠` em "algoritmo ≠ problema" (título da Seção 2.1); bbox de largura zero, visível no render.
- `Chapter_4_2026_1_Parts_1_2 (1).pdf`, pp. 14, 19, 35, 57 (13 ocorrências) — `off-page-text` — legítimo: mesmo `̸` (U+0338) de `≠` nas restrições ("vi,j ≠ vi,k", "B ≠ 3" …).
- `Chapter_4_2026_1_Part3 (1).pdf`, p. 31 (3 ocorrências) — `off-page-text` — legítimo: `̸` de "r1 ≠ r2 ≠ r3 ≠ i" na Eq. (1) do ED.
- `Chapter_4_2026_1_Part3 (1).pdf`, pp. 24–26, y ≈ 274–285 (página tem 272 pt de altura) — `off-page-text` — texto realmente invisível, mas legítimo: legendas de animação Beamer empurradas para fora da página por overflow de layout — "Geração t = 0: Inicialização Aleatória (Exploração Pura)", "Geração t = 20: Agrupamento nos picos de aptidão", "Geração t = 100: Convergência (Intensificação Final)". Descritivas, não se dirigem a IA, não alteram valores e são coerentes com o conteúdo visível (as legendas equivalentes das pp. 38–40 aparecem normalmente).
- `Chapter_4_2026_1_Part3 (1).pdf`, 19 páginas (122 ocorrências) e `Chapter_4_2026_1_Parts_1_2 (1).pdf`, p. 68 (6 ocorrências) — `covered-text` (HIGH, "painted over by a later shade") — legítimo: sombras de blocos Beamer (`shadow=true`) e degradês de cabeçalho desenhados depois do texto com transparência; todo o texto sinalizado aparece no render (verificado nas pp. 16, 22, 24, 31 da Part3 e p. 68 da Parts_1_2).
- `Chapter_4_2026_1_Part3 (1).pdf`, p. 22 (3 ocorrências) — `white-text` (LOW) — legítimo: numerais "1", "2", "3" brancos dentro de marcadores circulares coloridos de lista enumerada; visíveis no render.

## Verificações adicionais

- Enunciado: todas as 7 páginas comparadas visualmente com o dump — conteúdo idêntico. Valores-chave consistentes em todas as menções: h(identidade) = 4366, h* = 1875 (3 menções), guloso = 3168, referências 16 332 / 60 417, orçamentos 50 000 / 150 000 / 300 000, execuções 30 / 30 / 10, exemplo n = 4 com h = 39 e ótimo 22.
- Metadados: sem título/assunto/palavras-chave anômalos; 0 anotações; 0 arquivos embutidos nos 3 PDFs.
- Instâncias `.txt`: apenas dígitos, espaços e quebras de linha (0 caracteres não-ASCII / Unicode invisível).
- Grep por frases dirigidas a IA / exfiltração (`ignore`, "you are an AI", "se você for uma IA", ChatGPT/Claude/LLM, "não mencione", URLs, canários) nos dumps: 0 ocorrências.
- Grep de segredos (`password|api key|secret|token|…`) nos dumps: 0 ocorrências.

## Limitações desta análise

- Imagens (pseudocódigos em imagem nos slides Parts 1–2, pp. 25, 28, 40, 49, 58 etc.) não passaram por OCR; por serem imagens, o conteúdo é igualmente visível a humanos.
- Diff visual completo apenas no enunciado; nos slides, verificação visual por amostragem das páginas sinalizadas (padrão uniforme de sombras Beamer).
