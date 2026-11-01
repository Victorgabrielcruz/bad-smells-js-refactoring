# Entrega - Detecção de Bad Smells e Refatoração Segura

## Arquivos principais

- Relatório revisado visualmente, 4 páginas: `output/pdf/relatorio-bad-smells-refatoracao-segura.pdf`.
- Implementação refatorada: `src/ReportGenerator.refactored.js`.
- Suíte copiada: `__tests__/ReportGenerator.refactored.test.js`.
- Configuração: `.eslintrc.json`, `package.json` e `package-lock.json`.
- Análise manual: `docs/analise-manual.md`.
- Processo e trechos antes/depois: `docs/processo-refatoracao.md`.
- Validação: `docs/evidencias/validacao-final.md`, com logs e relatórios JSON reais no mesmo diretório.

Fork: https://github.com/Victorgabrielcruz/bad-smells-js-refactoring

## Como reproduzir

```powershell
npm ci
npx eslint src/ReportGenerator.refactored.js
npm run lint
```

O lint apenas da cópia retorna 0. `npm run lint` analisa também o original preservado e retorna 1 pelos dois alertas preexistentes.

`npm test` sem ajuste temporário não carrega ESM na configuração original. Para executar as duas suítes sem alterar configuração ou expectativas:

```powershell
$savedOptions = $env:NODE_OPTIONS
try {
    $env:NODE_OPTIONS = (($savedOptions + ' --experimental-vm-modules').Trim())
    npm test -- --runInBand
} finally {
    $env:NODE_OPTIONS = $savedOptions
}
```

Resultado real registrado: 8 testes aprovados e 2 reprovados; a mesma divergência de `<tr >` versus `<tr>` em HTML ADMIN, uma em cada suíte, já presente na base. O requisito do enunciado de 100% de aprovação não foi atingido. Não se afirma equivalência para todas as entradas possíveis. A verificação suplementar de 200 cenários pode ser repetida com `node docs/evidencias/refatoracao-equivalencia.mjs`.

## Imagem do ESLint e proveniência

`docs/evidencias/eslint-antes-captura-editor.png` é uma captura real feita nesta entrega da saída anterior preservada em `analise-estatica-original.txt`, aberta no Visual Studio Code. O texto não foi reescrito para a imagem. A versão `-recorte.png`, usada no PDF, apenas enquadra a área do documento e remove áreas vazias e abas não pertinentes. Não é uma imagem sintética nem captura histórica da janela do terminal. Se for exigido especificamente um print do terminal no instante anterior à refatoração, essa captura histórica continua indisponível; os resultados anteriores completos estão preservados em texto/JSON.

Os registros antigos que dizem que o print estava pendente refletem o estado daquelas fases; a captura do arquivo de evidência foi feita somente na preparação da entrega.

## Revisão e integridade

O PDF foi renderizado com Poppler e suas quatro páginas foram inspecionadas visualmente: capa, três smells e captura, trechos antes/depois, tabela de validação e conclusão. A capa usa os dados acadêmicos fornecidos pelo aluno. O script de geração está em `docs/relatorio/gerar_relatorio.py` e utiliza ReportLab, Pillow e pypdf. As imagens temporárias de revisão em `tmp/` não integram a entrega.

Os originais estão preservados: `src/ReportGenerator.js` e `tests/ReportGenerator.test.js` (caminho real da base). O teste copiado difere somente no import. Verificações e hashes estão em `docs/evidencias/validacao-final-resumo.json`.

`node_modules/`, arquivos de ambiente, credenciais, anexos locais e arquivos temporários não devem entrar no commit. O lockfile é incluído para reprodução das dependências. Os dados de identificação acadêmica no relatório foram fornecidos e solicitados pelo aluno para a entrega.
