# Fase 1 — Preparação do ambiente e linha de base

Data: 01/11/2026, America/Sao_Paulo.

## Ambiente e repositório

- Projeto local: `C:\Users\vgppl\Documents\bad-smells-js-refactoring`.
- Origem: https://github.com/CleitonSilvaT/bad-smells-js-refactoring
- Fork criado: https://github.com/Victorgabrielcruz/bad-smells-js-refactoring
- Commit inicial: `39d39f9ad52c6c508239cfe0b968187ad086e654`.
- Node.js: `v24.19.0`; npm: `11.17.0`; Jest instalado: `29.7.0`.
- Foram pesquisadas as pastas existentes Documents, Desktop, Downloads, source, repos e projects, sem localizar uma cópia desse repositório. O projeto `Documents/test-smelly` corresponde a outra atividade e foi preservado.
- README.md e package.json foram lidos antes da instalação.
- O README menciona `__tests__/`, mas a suíte real está em `tests/ReportGenerator.test.js`. Nenhum arquivo foi movido.

## Comandos e resultados

```powershell
git clone https://github.com/Victorgabrielcruz/bad-smells-js-refactoring.git C:/Users/vgppl/Documents/bad-smells-js-refactoring
cd C:/Users/vgppl/Documents/bad-smells-js-refactoring
node --version
npm --version
npm install
npm test
```

O fork foi criado pela API autenticada do GitHub antes do clone. Nenhuma credencial foi salva nos registros.

`npm install`: código de saída 0; 423 pacotes adicionados, 424 auditados. Foi criado `package-lock.json`. A instalação reportou dependências descontinuadas e 28 vulnerabilidades (4 baixas e 24 moderadas). Não foi executado `npm audit fix`, para não modificar as dependências além da preparação solicitada.

### Primeira execução sem ajustes

`npm test`: código de saída 1; uma suíte não conseguiu iniciar e nenhum teste foi executado. Erro: `SyntaxError: Cannot use import statement outside a module`.

O projeto usa `type: module`, import/export e `jest.transform: {}`, mas o script original chama somente `jest`. Para investigar, habilitou-se o suporte ESM apenas no ambiente temporário do processo, conforme a documentação oficial do Jest 29.7: https://jestjs.io/docs/29.7/ecmascript-modules

### Execução de diagnóstico com ESM

```powershell
$previousNodeOptions = $env:NODE_OPTIONS
try {
    $env:NODE_OPTIONS = (($previousNodeOptions + ' --experimental-vm-modules').Trim())
    npm test
} finally {
    if ($null -eq $previousNodeOptions) {
        Remove-Item Env:NODE_OPTIONS -ErrorAction SilentlyContinue
    } else {
        $env:NODE_OPTIONS = $previousNodeOptions
    }
}
```

Resultado real: **5 testes executados; 4 aprovados; 1 reprovado; 0 ignorados**. Uma suíte reprovada. Código de saída 1. Taxa de aprovação: 80%.

Falha: `Admin User > deve gerar um relatório HTML completo para Admin (com prioridade)`.

- Esperado pelo teste em `tests/ReportGenerator.test.js:50`: `<tr><td>1</td><td>Produto A</td><td>300</td></tr>`.
- Recebido do código original: `<tr ><td>1</td><td>Produto A</td><td>300</td></tr>`.
- Causa localizada em `src/ReportGenerator.js:39-40`: quando `style` é vazio, a interpolação `<tr ${style}>` mantém um espaço antes de `>`. A comparação textual do teste detecta essa diferença.

Trata-se de uma falha preexistente do projeto base, anterior a qualquer refatoração. Nenhuma expectativa do teste nem código de produção foi alterado.

## Evidências

- `evidencias/fase-1-npm-install.txt`: saída da instalação.
- `evidencias/fase-1-npm-install.exitcode.txt`: código de saída da instalação.
- `evidencias/fase-1-npm-test-inicial.txt`: primeira execução sem ajustes.
- `evidencias/fase-1-npm-test-inicial.exitcode.txt`: código da primeira execução.
- `evidencias/fase-1-npm-test-esm.txt`: execução com suporte ESM e diagnóstico da falha funcional.
- `evidencias/fase-1-npm-test-esm.exitcode.txt`: código da execução ESM.

Foi executado `git diff --exit-code HEAD -- src tests package.json README.md .eslintrc.json`, com resultado 0, confirmando que os arquivos originais permanecem intactos. Somente a documentação/evidências e o lockfile foram adicionados localmente. Não foi realizado commit ou push nesta fase.

## Situação e pendências

Ambiente instalado e fork clonado, mas a condição de 100% dos testes aprovados **não foi atingida**. Antes de iniciar a refatoração, é necessário resolver a execução ESM e tratar a divergência preexistente de HTML em uma etapa explícita de correção da base, preservando o registro inicial e os testes originais. A fase 2 não foi iniciada.

Nenhuma autenticação ou ação manual de fork/clone está pendente para o usuário.
