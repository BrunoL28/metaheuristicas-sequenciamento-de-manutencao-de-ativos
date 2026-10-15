#!/usr/bin/env bash
# Monta o pacote de entrega em entrega/tp2-fundia-<data>.zip.
#
# Entram só os arquivos versionados de uma lista fixa (código, testes,
# instâncias, configurações, resultados e relatório, com o PDF compilado).
# README_ENTREGA.md vira o README.md do pacote. O script falha se houver
# mudanças não commitadas nesses caminhos, se o PDF não estiver versionado ou
# se algum arquivo de fora da lista aparecer no pacote.
set -euo pipefail

cd "$(dirname "$0")/.."

CAMINHOS=(src tests configs results relatorio Makefile pyproject.toml uv.lock 'INPUTS/manutencao_*.txt')
PROIBIDOS='CLAUDE\.md|AGENTS\.md|NEXT_UP\.md|CONTEXT\.md|IMPLEMENTATION_PLAN\.md|\.agents|archive/|INPUTS/slides|/tmp/'

if [ -n "$(git status --porcelain -- "${CAMINHOS[@]}" README_ENTREGA.md)" ]; then
    echo "Há mudanças não commitadas nos arquivos de entrega; faça o commit antes." >&2
    git status --short -- "${CAMINHOS[@]}" README_ENTREGA.md >&2
    exit 1
fi
if ! git ls-files --error-unmatch relatorio/main.pdf >/dev/null 2>&1; then
    echo "relatorio/main.pdf não está versionado; rode make report e faça o commit." >&2
    exit 1
fi

nome="tp2-fundia-$(date +%F)"
temporario=$(mktemp -d)
trap 'rm -rf "$temporario"' EXIT
destino="$temporario/$nome"
mkdir -p "$destino"

git ls-files -z -- "${CAMINHOS[@]}" | grep -zv "\.gitkeep$" | xargs -0 cp --parents -t "$destino"
cp README_ENTREGA.md "$destino/README.md"

if (cd "$temporario" && find "$nome" -type f) | grep -E "$PROIBIDOS"; then
    echo "Arquivos que não deveriam estar no pacote (acima)." >&2
    exit 1
fi

mkdir -p entrega
saida="$PWD/entrega/$nome.zip"
rm -f "$saida"
(cd "$temporario" && zip -qr "$saida" "$nome")
echo "Pacote: entrega/$nome.zip ($(du -h "$saida" | cut -f1), $(unzip -Z1 "$saida" | grep -vc '/$') arquivos)"
