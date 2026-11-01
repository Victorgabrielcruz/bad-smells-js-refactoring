# Processo de refatoração

Data: 01/11/2026. Esta fase aplica somente a refatoração em uma cópia, duplica a suíte sem alterar expectativas e registra as validações reais.

## Preservação da base e interface

- `src/ReportGenerator.js` foi preservado. A cópia de trabalho é `src/ReportGenerator.refactored.js`, criada inicialmente por cópia do original.
- O repositório contém `tests/ReportGenerator.test.js`, e não `__tests__/ReportGenerator.test.js`. O teste original real foi preservado no local existente. Não foi inventado ou movido um teste original em `__tests__/`.
- A suíte copiada está no caminho solicitado, `__tests__/ReportGenerator.refactored.test.js`. A única diferença de conteúdo em relação ao teste original é o caminho do import:

```diff
-import { ReportGenerator } from '../src/ReportGenerator.js';
+import { ReportGenerator } from '../src/ReportGenerator.refactored.js';
```

- Permanecem o export nomeado `ReportGenerator`, o construtor com argumento `database`, a propriedade `db` e o método público `generateReport(reportType, user, items)`. Os auxiliares são funções internas ao módulo, sem novos métodos públicos ou exports.
- Não foram alterados package.json, configuração do Jest ou regras do ESLint nesta fase. Não foi usado `eslint-disable`, nem mudança de severidade ou limite.
- `git diff --exit-code HEAD -- src/ReportGenerator.js tests/ReportGenerator.test.js` retornou 0 ao final, comprovando a preservação dos originais.

## Linha de base e impedimentos preexistentes

Antes de refatorar, foi executado `npm test -- --runInBand`. O script atual (`jest`) falhou ao carregar ESM: `Cannot use import statement outside a module`; 0 testes foram executados.

Em seguida, foi usado o suporte ESM do Jest por meio de `NODE_OPTIONS=--experimental-vm-modules`, apenas no processo de validação, restaurando-se o valor anterior depois de cada execução. Com essa opção, a suíte original executou **5 testes: 4 passaram e 1 falhou**.

A falha já existia: `Admin User > deve gerar um relatório HTML completo para Admin (com prioridade)`, na linha 50. O teste espera `<tr><td>1...`, enquanto a implementação original produz `<tr ><td>1...` para ADMIN sem prioridade. Corrigir esse espaço mudaria o texto retornado, contrariando a exigência de preservar o comportamento observável. Por isso, a refatoração mantém essa saída e registra a falha, sem alterar a expectativa nem enfraquecer a suíte.

## Etapa 1 — extração de funções e constantes

### Extract Function / Extract Method

O método original, linhas 11–68, concentrava cabeçalho, seleção, prioridade, formatação, soma e rodapé. Primeiro foram extraídos cabeçalho e rodapé, mantendo sua construção textual e a ordem das operações.

Antes, dentro de `generateReport`:

```js
if (reportType === 'CSV') {
  report += 'ID,NOME,VALOR,USUARIO\n';
} else if (reportType === 'HTML') {
  report += '<html><body>\n';
  report += '<h1>Relatório</h1>\n';
  report += `<h2>Usuário: ${user.name}</h2>\n`;
  report += '<table>\n';
  report += '<tr><th>ID</th><th>Nome</th><th>Valor</th></tr>\n';
}
```

Depois, no resultado final, linhas 15 e 30:

```js
let report = createHeader(reportType, user);
// Processamento dos itens.
report += createFooter(reportType, total);
```

`createHeader` (36–49) e `createFooter` (51–63) contêm os blocos extraídos. As funções mantêm retorno vazio para formatos desconhecidos. Não foram criadas classes de renderização ou hierarquias de formatos.

### Replace Magic Number with Symbolic Constant

Antes, linhas 30 e 45 do original:

```js
if (item.value > 1000) {
  item.priority = true;
}
// Dentro do ramo USER:
if (item.value <= 500) {
  // Renderização.
}
```

Depois, constantes nas linhas 1–2 e uso nas funções de regra:

```js
const ADMIN_PRIORITY_THRESHOLD = 1000;
const USER_MAX_VISIBLE_VALUE = 500;
```

```js
function applyAdminPriority(user, item) {
  if (user.role === 'ADMIN' && item.value > ADMIN_PRIORITY_THRESHOLD) {
    item.priority = true;
  }
}
```

Os valores e operadores foram preservados: 1000 não ativa a prioridade; 500 é visível para USER. A inicialização `total = 0` permaneceu, pois não é um limite de negócio sem nome.

**Validação após a primeira mudança significativa:** `npm test -- --runInBand`, com ESM temporário: **8 aprovados e 2 reprovados em 10 testes**. Cada suíte apresentou a mesma falha preexistente de HTML ADMIN; nenhum outro teste passou a falhar. Evidência: `evidencias/refatoracao-02-extracoes.txt`.

## Etapa 2 — decomposição das condicionais e remoção de duplicação

### Decompose Conditional e Replace Nested Conditional with Guard Clauses

Antes, linhas 43–52 do original:

```js
} else if (user.role === 'USER') {
  if (item.value <= 500) {
    if (reportType === 'CSV') {
      report += `${item.id},${item.name},${item.value},${user.name}\n`;
      total += item.value;
    } else if (reportType === 'HTML') {
      report += `<tr><td>${item.id}</td><td>${item.name}</td><td>${item.value}</td></tr>\n`;
      total += item.value;
    }
  }
}
```

Depois, a regra de visibilidade está nomeada e o laço descarta itens não visíveis antes da renderização:

```js
function isVisibleTo(user, item) {
  return user.role === 'ADMIN' ||
    (user.role === 'USER' && item.value <= USER_MAX_VISIBLE_VALUE);
}
```

```js
for (const item of items) {
  if (!isVisibleTo(user, item)) {
    continue;
  }

  applyAdminPriority(user, item);
  if (reportType === 'CSV' || reportType === 'HTML') {
    report += createRow(reportType, user, item);
    total += item.value;
  }
}
```

O predicado preserva o curto-circuito: ADMIN não depende do limite de USER. A prioridade continua sendo aplicada antes de verificar o formato, inclusive quando ele é desconhecido, como no original. Usuários de papel desconhecido não geram linhas.

### Extract Function e Consolidate Duplicate Conditional Fragments

Antes, a mesma linha CSV aparecia nos ramos ADMIN (36–37) e USER (47–48), e a soma estava em quatro ramos:

```js
report += `${item.id},${item.name},${item.value},${user.name}\n`;
total += item.value;
```

Depois, há uma única geração CSV em `createRow` (76–87):

```js
if (reportType === 'CSV') {
  return `${item.id},${item.name},${item.value},${user.name}\n`;
}
```

A soma fica em um único ponto do laço, após a geração da linha para um formato reconhecido. Formatos desconhecidos continuam sem totalização nem saída.

A composição HTML também foi centralizada, preservando deliberadamente a diferença textual do ADMIN:

```js
let openingTag = '<tr>';
if (user.role === 'ADMIN') {
  const style = item.priority ? 'style="font-weight:bold;"' : '';
  openingTag = `<tr ${style}>`;
}
return `${openingTag}<td>${item.id}</td><td>${item.name}</td><td>${item.value}</td></tr>\n`;
```

A prioridade já existente no item continua sendo respeitada para ADMIN e não gera estilo no caminho USER. Não foram introduzidas normalização de HTML, validação de entradas ou mudanças de regras de negócio.

O `generateReport` final ocupa as linhas **14–33**, contra **11–68** do original. Agora ele coordena as etapas, e os auxiliares descrevem cada responsabilidade.

**Validação após a segunda mudança significativa:** `npm test -- --runInBand`, com ESM temporário: **8 aprovados e 2 reprovados em 10 testes**. São novamente as duas instâncias da mesma falha preexistente, uma em cada suíte. Evidência: `evidencias/refatoracao-03-condicionais-duplicacao.txt`.

## Resultados reais

| Momento | Comando | Aprovados | Reprovados | Saída |
| --- | --- | --- | --- | --- |
| Base, sem opção ESM | npm test -- --runInBand | 0 executados | Falha de carregamento | 1 |
| Base, com ESM temporário | npm test -- --runInBand | 4 | 1 | 1 |
| Extrações e constantes, com ESM temporário | npm test -- --runInBand | 8 | 2 | 1 |
| Condicionais e duplicação, com ESM temporário | npm test -- --runInBand | 8 | 2 | 1 |
| Lint somente da cópia refatorada | npx eslint src/ReportGenerator.refactored.js | 0 diagnósticos | 0 diagnósticos | 0 |
| Comparação suplementar com o original | node docs/evidencias/refatoracao-equivalencia.mjs | 200 cenários | 0 | 0 |

Não há 100% de aprovação da suíte: a falha da base continua existindo e não foi reclassificada como sucesso. Não foi identificada regressão nova nos testes executados.

O lint da cópia refatorada terminou sem erros ou avisos, mantendo as regras configuradas. O original permanece intocado com os achados registrados nas fases anteriores; não se afirma que `npm run lint` em todo src/ ficou limpo.

### Comparação suplementar de comportamento

Para verificar lacunas da suíte original sem alterá-la, foi salvo um script de comparação direta em `evidencias/refatoracao-equivalencia.mjs`. Ele executa original e cópia com entradas clonadas e compara o texto retornado e o estado final dos itens com assertions estritas.

Foram aprovados **200 cenários**, com duas chamadas sucessivas por cenário: **400 comparações de saída e estado**. Abrangem ADMIN, USER, papel desconhecido/ausente; CSV, HTML, formato desconhecido/vazio/ausente; arrays vazios; fronteiras 499/500/501 e 999/1000/1001; prioridade preexistente; valores negativos e NaN. Isso é evidência para os casos executados, não prova de equivalência para todo objeto JavaScript possível.

O mesmo script confirmou a superfície pública do protótipo, a identidade de `db` e a igualdade integral do teste copiado após a única substituição do import.

### Como reproduzir os testes em PowerShell

```powershell
$savedOptions = $env:NODE_OPTIONS
try {
    $env:NODE_OPTIONS = (($savedOptions + ' --experimental-vm-modules').Trim())
    npm test -- --runInBand
} finally {
    $env:NODE_OPTIONS = $savedOptions
}

npx eslint src/ReportGenerator.refactored.js
node docs/evidencias/refatoracao-equivalencia.mjs
```

O comando de teste continua retornando 1 pela falha preexistente descrita. A opção temporária ESM não altera o script npm, a suíte ou a configuração do projeto.

## Evidências e integridade

Os arquivos `evidencias/refatoracao-00-test-sem-esm.txt`, `refatoracao-01-base.txt`, `refatoracao-02-extracoes.txt` e `refatoracao-03-condicionais-duplicacao.txt` preservam as saídas reais. Cada execução tem um arquivo `.exitcode.txt` correspondente. A verificação de lint está em `refatoracao-eslint.txt` e `refatoracao-eslint.exitcode.txt`; saída e código da comparação estão em `refatoracao-equivalencia.txt` e `refatoracao-equivalencia.exitcode.txt`.

Hashes SHA-256 dos arquivos originais preservados:

```text
src/ReportGenerator.js
E3AAAF125FC846DE0BE4BE873DB63A6D17B020CAB8446E82DEBB3F26A0A386A8

tests/ReportGenerator.test.js
FFFA6AA1599B399AF1D52ABD192370C7D80158E08C3EE02F4C95B18BC0AE97DA
```

Não houve alteração dos originais, correção da falha da base, mudança das expectativas, supressão de regras, commit ou push nesta fase.
