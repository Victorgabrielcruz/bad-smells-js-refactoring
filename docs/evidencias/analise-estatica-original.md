# Análise estática do código original — antes da refatoração

## Escopo e execução

Foi executado `npx eslint src/` na raiz de `bad-smells-js-refactoring`, sem `--fix`, sem alterações em src/ ou tests/ e sem executar testes. O arquivo analisado é `src/ReportGenerator.js`, ainda igual à versão HEAD do repositório (`git diff --exit-code HEAD -- src tests`: saída 0).

Ambiente utilizado nesta fase: Node.js 24.19.0, npm 11.17.0, ESLint 8.57.1 e eslint-plugin-sonarjs 0.21.0, conforme configuração verificada na fase anterior. Presets: `eslint:recommended` e `plugin:sonarjs/recommended`; limite de complexidade cognitiva 15, severidade error. Nenhuma regra foi desativada nesta fase.

A saída completa da execução está em `analise-estatica-original.txt`. Uma segunda execução, com o formatador JSON, preservou os diagnósticos estruturados diretamente da ferramenta:

```powershell
npx eslint src/
npx eslint src/ --format json --output-file docs/evidencias/analise-estatica-original.eslint.json
```

As duas execuções terminaram com **código 1**: **2 erros, 0 avisos e 0 erros fatais**. O código 1 decorre das violações encontradas, não de falha na configuração.

Data/hora efetiva, códigos de saída e hashes SHA-256 antes/depois constam em `analise-estatica-original.execucao.json`. Os hashes do código-fonte coincidem:

```text
E3AAAF125FC846DE0BE4BE873DB63A6D17B020CAB8446E82DEBB3F26A0A386A8
```

## Diagnósticos reais

| Regra violada | Severidade | Arquivo | Função | Linha:coluna | Resultado |
| --- | --- | --- | --- | --- | --- |
| sonarjs/cognitive-complexity | error | src/ReportGenerator.js | generateReport | 11:3 | Complexidade cognitiva 27; máximo permitido 15; excedente 12 |
| sonarjs/no-collapsible-if | error | src/ReportGenerator.js | generateReport | 43:14 | Unificar esta condição com a condição interna |

Mensagens originais, sem tradução:

```text
Refactor this function to reduce its Cognitive Complexity from 27 to the 15 allowed.
Merge this if statement with the nested one.
```

A primeira localização aponta para a declaração do método, não para um único ramo causador da complexidade. A segunda aponta para `else if (user.role === 'USER')` na linha 43, que contém o `if (item.value <= 500)` na linha 45. A ferramenta não informou valor de complexidade para esse segundo diagnóstico. A identificação da função e o excedente de 12 são contexto e cálculo deste relatório; os valores 27 e 15 vêm da mensagem do ESLint.

## Comparação com a análise manual

Referência preservada: `../analise-manual.md`.

| Achado manual | Resultado estático | Relação e limite da comparação |
| --- | --- | --- |
| Long Method e responsabilidades misturadas, linhas 11–68 | cognitive-complexity em 11:3, valor 27 | Há convergência sobre a dificuldade do método. Complexidade cognitiva mede o fluxo de controle; não mede diretamente comprimento nem comprova responsabilidades misturadas. Esses dois aspectos continuam fundamentados na leitura manual. |
| Condicionais complexas, linhas 27–54, especialmente 43–52 | cognitive-complexity e no-collapsible-if em 43:14 | Coincidência direta com o aninhamento identificado manualmente. A ferramenta acrescenta uma localização precisa e a sugestão concreta de unificar os ifs das linhas 43 e 45. |
| Código CSV repetido, linhas 35–37 e 46–48; acumulação em 37, 41, 48 e 51 | Nenhum diagnóstico de duplicação | Achado somente manual nesta execução. no-identical-functions procura funções idênticas; os trechos citados estão dentro de um único método. A ausência de alerta não invalida a repetição observada. no-duplicated-branches também não emitiu diagnóstico. |
| Números mágicos 1000 e 500, linhas 30 e 45 | Nenhum diagnóstico | Achado somente manual. A configuração desta atividade não habilita uma regra específica para números mágicos. |

**Somente a ferramenta:** quantificou a complexidade em 27 frente ao limite 15 e formalizou a ocorrência específica de `no-collapsible-if`. Não surgiu uma categoria inteiramente nova de smell em relação à análise manual: essa ocorrência está dentro das condicionais já registradas.

**Somente a leitura manual:** duplicação de trechos e da totalização, números mágicos e avaliação de extensão/responsabilidades do método. O alerta de complexidade é evidência complementar, e não uma equivalência automática com Long Method.

`sonarjs/no-identical-functions` está configurada explicitamente como error, mas não reportou ocorrências. Não se deve registrar uma violação dessa regra apenas porque a análise manual encontrou blocos repetidos.

## Refatorações priorizadas — propostas, não executadas

| Prioridade | Local | Técnica proposta | Motivo e comportamento a preservar |
| --- | --- | --- | --- |
| 1 | generateReport, linhas 11–68 | Extract Function/Method e Decompose Conditional | Separar visibilidade, prioridade e geração de cabeçalho/linha/rodapé, tornando as regras compreensíveis e testáveis isoladamente. Ataca o método concentrador dos problemas e a complexidade 27. Preservar a mutação existente de item.priority e a saída textual. |
| 2 | Linhas 27–54, especialmente 43–45 | Consolidate Conditional Expression e, onde apropriado, guard clauses | Reduzir o aninhamento e tratar a ocorrência de no-collapsible-if. Uma conjunção com curto-circuito pode unir papel USER e limite de valor sem mudar essa seleção. A alteração isolada não garante reduzir a complexidade total até 15; isso precisa ser medido depois. |
| 3 | Linhas 35–51 | Extract Function/Method e Consolidate Duplicate Conditional Fragments | Centralizar a linha CSV e a acumulação para evitar divergências. Preservar diferenças de estilo HTML de ADMIN e USER; formatos não reconhecidos atualmente não acumulam valores. |
| 4 | Linhas 30 e 45 | Replace Magic Number with Symbolic Constant | Dar nomes de domínio aos limites de prioridade e visibilidade. Preservar estritamente `> 1000` e `<= 500`. |

Em eventual fase posterior de refatoração, validar os fluxos CSV/HTML, os papéis, os limites de valor e a prioridade preexistente. Os problemas de testes da base documentados em `../fase-1-preparacao.md` não foram corrigidos ou reavaliados nesta fase. Nenhuma refatoração ou mudança em testes foi feita.

## Print da execução — pendente

**Não foi capturado print nesta fase.** A saída real completa e o JSON nativo do ESLint foram preservados; nenhuma imagem foi criada ou apresentada como captura.

A skill de automação Windows disponível foi consultada antes da tentativa de uso e proíbe automatizar terminais: “Do not automate terminal applications such as Windows Terminal, Command Prompt, or Windows PowerShell.” Fonte local: `C:/Users/vgppl/.codex/plugins/cache/openai-bundled/computer-use/26.1023.51421/docs/guidance.md`, referenciada por `skills/computer-use/SKILL.md`. Por isso, não se usou automação de janela de terminal para produzir a captura. O print continua pendente de captura manual.

Para completá-lo, executar `npx eslint src/` na raiz do projeto em uma janela com largura suficiente para mostrar as mensagens, capturar a janela e salvar o print em docs/evidencias/. A captura deve exibir o comando, o arquivo, os dois diagnósticos e o resumo, sem substituir as evidências textuais.

## Arquivos desta fase

- `analise-estatica-original.txt`: saída textual completa de `npx eslint src/`.
- `analise-estatica-original.exitcode.txt`: código de saída da execução textual.
- `analise-estatica-original.eslint.json`: relatório estruturado nativo do ESLint, com mensagens, posições, contagens e código-fonte analisado.
- `analise-estatica-original.execucao.json`: comando, data/hora, códigos de saída e hashes antes/depois.
- `analise-estatica-original.md`: este relatório comparativo e lista priorizada.
