# Validação final da refatoração

Data: 01/11/2026. Esta fase executou validações e criou evidências; não alterou implementação, testes, dependências ou configuração de regras.

## Comparação antes e depois

A coluna original foi obtida por nova execução sobre `src/ReportGenerator.js`, preservado. Seus diagnósticos também foram comparados automaticamente aos resultados históricos em `analise-estatica-original.eslint.json` e coincidem em regra, severidade, linha, coluna e mensagem.

| Verificação | Antes — original | Depois — refatorado |
| --- | --- | --- |
| ESLint | 2 erros; 0 avisos; saída 1 | 0 erros; 0 avisos; saída 0 |
| sonarjs/cognitive-complexity | Violação em 11:3: complexidade 27, limite 15 | Nenhuma violação com limite 15 |
| Complexidade exata disponível | generateReport: 27 | Valor exato não emitido pelo lint; não ultrapassa o limite 15 segundo a regra |
| sonarjs/no-collapsible-if | Violação em 43:14 | Nenhuma violação |
| sonarjs/no-identical-functions | Nenhum diagnóstico | Nenhum diagnóstico |
| npm test sem opção ESM | Suíte não carrega; 0 testes executados | Suíte não carrega; 0 testes executados |
| Testes com ESM temporário | 4 aprovados; 1 reprovado | 4 aprovados; 1 reprovado |
| HTML ADMIN sem prioridade | Produz `<tr >`; teste espera `<tr>` | Mesmo comportamento e mesma falha |
| Preservação do original | Código e teste com diff vazio em relação ao HEAD | Cópias em novos arquivos; teste difere apenas no import |

**Resultado global com ESM:** 2 suítes reprovadas, 10 testes executados, 8 aprovados e 2 reprovados; saída 1. Não há aprovação completa. A falha duplicada é preexistente e não constitui regressão introduzida pela refatoração nos cenários verificados.

## Comandos executados e evidências

```powershell
npx eslint src/ReportGenerator.refactored.js
npx eslint src/ReportGenerator.js
npx eslint src/ReportGenerator.js src/ReportGenerator.refactored.js --format json --output-file docs/evidencias/validacao-final-eslint.json
npm test
```

- `validacao-final-eslint-refatorado.txt` e `.exitcode.txt`: saída vazia do lint bem-sucedido e código 0. Ausência de texto é o resultado real, não evidência de ausência de execução; o JSON conjunto também registra o arquivo com zero mensagens.
- `validacao-final-eslint-original.txt` e `.exitcode.txt`: os dois erros preservados no original, código 1.
- `validacao-final-eslint.json`: relatório nativo do ESLint para os dois arquivos.
- `validacao-final-test-padrao.txt` e `.exitcode.txt`: execução literal de `npm test`, com erro de carregamento de ESM nas duas suítes e código 1.
- `validacao-final-execucao.json`: data/hora, versões, códigos de saída e hash da configuração antes/depois.

Para executar efetivamente as duas suítes, foi necessária uma segunda execução com suporte ESM temporário, sem mudar o package.json ou a configuração do Jest:

```powershell
$savedOptions = $env:NODE_OPTIONS
try {
    $env:NODE_OPTIONS = (($savedOptions + ' --experimental-vm-modules').Trim())
    npm test -- --runInBand --json --outputFile=docs/evidencias/validacao-final-jest.json
} finally {
    $env:NODE_OPTIONS = $savedOptions
}
```

- `validacao-final-test-esm.txt` e `.exitcode.txt`: saída completa e código 1.
- `validacao-final-jest.json`: resultado estruturado por suíte e por teste.

## Mesma configuração e rigor preservado

Ambiente verificado: Node.js 24.19.0, npm 11.17.0, ESLint 8.57.1 e SonarJS 0.21.0. Os dois arquivos foram analisados na mesma execução JSON e com a mesma configuração efetiva, comparada por igualdade profunda via API do ESLint.

Foram mantidos `eslint:recommended`, `plugin:sonarjs/recommended`, `sonarjs/cognitive-complexity: ["error", 15]` e `sonarjs/no-identical-functions: "error"`. O hash de `.eslintrc.json` antes e depois desta fase é idêntico. Não houve supressões, mudanças de limites, severidades ou expectativas.

A configuração efetiva completa está em `validacao-final-config-efetiva.json`; a igualdade dos perfis e a comparação com os diagnósticos históricos estão em `validacao-final-resumo.json`.

A ferramenta não apresenta a complexidade exata de funções que não violam o limite. Portanto, não foi inventado um valor para a cópia refatorada. O resultado verificado é ausência de violação acima de 15, e não complexidade zero.

## Integridade do código e dos testes

Comando executado pelo script de verificação:

```powershell
git diff --exit-code HEAD -- src/ReportGenerator.js tests/ReportGenerator.test.js
```

Resultado: saída 0, diff vazio salvo em `validacao-final-originais.diff`. O caminho real da suíte original é `tests/ReportGenerator.test.js`; não existe um teste original em `__tests__/` nesta base.

Além do diff, os hashes SHA-256 dos arquivos atuais coincidem exatamente com os registrados antes da refatoração:

```text
src/ReportGenerator.js
E3AAAF125FC846DE0BE4BE873DB63A6D17B020CAB8446E82DEBB3F26A0A386A8

tests/ReportGenerator.test.js
FFFA6AA1599B399AF1D52ABD192370C7D80158E08C3EE02F4C95B18BC0AE97DA
```

Foi feita uma verificação adicional contra o conteúdo do HEAD. A primeira tentativa de comparação byte a byte falhou porque o Git armazena LF e o checkout Windows usa CRLF. A saída real dessa tentativa foi preservada em `validacao-final-integridade-tentativa1.txt` e seu código 1 no arquivo correspondente. O verificador foi corrigido apenas para tratar essa conversão conhecida de finais de linha; não houve alteração nos originais. A comparação de conteúdo normalizada contra HEAD passou, assim como a igualdade byte a byte com os hashes históricos do checkout.

O script também confirmou igualdade integral entre `__tests__/ReportGenerator.refactored.test.js` e o teste original após uma única substituição:

```diff
-import { ReportGenerator } from '../src/ReportGenerator.js';
+import { ReportGenerator } from '../src/ReportGenerator.refactored.js';
```

Esse resumo da diferença está em `validacao-final-teste-copiado.diff`. A confirmação por assertion de igualdade integral, os hashes e os resultados estão em `validacao-final-resumo.json` e `validacao-final-integridade.txt`; a execução corrigida terminou com código 0. O verificador reproduzível é `validacao-final-verificar.mjs`.

## Problemas preservados e limitações

**Original preservado:** mantém complexidade cognitiva 27 e a condicional aninhada diagnosticada pelo SonarJS. Permanecem também os achados manuais de concentração de responsabilidades, duplicação e literais de negócio identificados em `../analise-manual.md`. Nenhum deles foi corrigido no arquivo original, conforme exigido.

**Refatorado:** não apresenta os dois alertas estáticos com a configuração atual. A inspeção do código confirma funções auxiliares para cabeçalho, rodapé, seleção, prioridade e linha; soma centralizada; constantes 500 e 1000 nomeadas. A ausência de alertas não significa ausência de todo smell possível. O comportamento de mutar `item.priority` e o espaço em `<tr >` continuam existentes por preservação do comportamento observável.

**Falha funcional ainda presente nas duas versões:** o teste HTML ADMIN na linha 50 espera `<tr>`, mas recebe `<tr >`. Isso já foi constatado na base antes das mudanças e foi novamente confirmado nesta fase. Corrigir o espaço mudaria a saída textual original; não foi feito como suposta correção de regressão. Não houve alteração de expectativas.

**Execução padrão ainda limitada:** `npm test` sem o suporte ESM temporário não consegue carregar as suítes. Esta validação não modificou scripts nem configuração para corrigir essa limitação da base.

**Escopo da equivalência:** foi reexecutado `node docs/evidencias/refatoracao-equivalencia.mjs`, com código 0. Seus 200 cenários, cada um com duas chamadas sucessivas, passaram nas 400 comparações de saída e estado dos itens. A evidência atual está em `validacao-final-equivalencia.txt` e `.exitcode.txt`. O script inclui limites de valor, prioridades preexistentes, papéis e formatos desconhecidos e itens vazios. Não é uma prova para todas as entradas JavaScript possíveis.

Nenhuma regressão nova foi identificada nas verificações executadas; por isso, não foi necessária alteração da implementação refatorada nesta fase.
