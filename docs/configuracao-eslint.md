# Configuração do ESLint e SonarJS

Data: 01/11/2026. Esta fase configura e executa a análise estática; não realiza refatoração nem altera ou executa testes.

## Versões verificadas e escolha

Antes da configuração, foram executados `node --version`, `npm --version` e `npm ls --depth=0`, e lidos os manifestos das ferramentas instaladas.

| Componente | Versão encontrada | Decisão |
| --- | --- | --- |
| Node.js | 24.19.0 | Manter |
| npm | 11.17.0 | Manter |
| ESLint | 8.57.1 | Fixar em devDependencies |
| eslint-plugin-sonarjs | 0.21.0 | Fixar em devDependencies |
| Jest | 29.7.0 | Manter sem alterações |
| @babel/preset-env | 7.29.7 | Manter sem alterações |

O manifesto do ESLint 8.57.1 declara Node `^12.22.0 || ^14.17.0 || >=16.0.0`; o do SonarJS 0.21.0 declara Node `>=14` e peer dependency ESLint `^5.0.0 || ^6.0.0 || ^7.0.0 || ^8.0.0`. Portanto, o Node instalado satisfaz os requisitos declarados e o par de ferramentas é compatível. A execução local confirmou o funcionamento neste ambiente.

Foram mantidas as versões já instaladas, fixando-as para preservar o conjunto de regras desta atividade e o formato solicitado. O ESLint 8 está fora de manutenção desde 05/10/2024, conforme a documentação oficial. A escolha é de compatibilidade com a base da atividade, não uma recomendação de versão para um projeto novo. Uma atualização de versão principal fica fora desta fase.

## Formato e ambiente

O arquivo usado é `.eslintrc.json`, suportado nativamente pelo ESLint 8.57.1. Não é necessário adotar outro formato ou habilitar uma opção de compatibilidade. O JSON não contém comentários. A documentação do ESLint 8 descreve esse formato e a transição para flat config no ESLint 9: https://eslint.org/docs/v8.x/use/configure/configuration-files

O projeto tem `"type": "module"` no package.json e usa `export`. A configuração mantém `sourceType: "module"`, `ecmaVersion: "latest"` (sintaxe reconhecida pelo parser instalado), ambiente Node e globais ES2021. O ambiente Jest fica restrito a `tests/**/*.js` via overrides, evitando reconhecer globais de testes no código de produção. Nenhum teste foi alterado. `root: true` delimita a configuração ao projeto.

## Configuração aplicada

```json
{
  "root": true,
  "env": {
    "es2021": true,
    "node": true
  },
  "extends": [
    "eslint:recommended",
    "plugin:sonarjs/recommended"
  ],
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "plugins": ["sonarjs"],
  "rules": {
    "sonarjs/cognitive-complexity": ["error", 15],
    "sonarjs/no-identical-functions": "error",
    "sonarjs/no-duplicated-branches": "error"
  },
  "overrides": [
    {
      "files": ["tests/**/*.js"],
      "env": {"jest": true}
    }
  ]
}
```

Os dois presets recomendados já existiam e foram preservados. O limite de complexidade cognitiva foi ajustado de 5 para os 15 solicitados. A regra explícita `no-duplicated-branches`, também preexistente, foi mantida. Nenhuma regra foi desativada para ocultar problemas. O script já existente foi verificado e preservado:

```json
{
  "scripts": {
    "test": "jest",
    "lint": "eslint src/"
  }
}
```

## Comandos disponíveis

Na raiz do projeto:

```powershell
npm ci
npm run lint
npx --no-install eslint --version
npx --no-install eslint --print-config src/ReportGenerator.js
```

`npm ci` reproduz as dependências do package-lock.json. `npm run lint` analisa src/ sem aplicar correções. `--print-config` mostra a configuração efetiva do arquivo. O script `npm test` foi preservado, mas não foi executado nesta fase; suas limitações preexistentes estão documentadas em fase-1-preparacao.md.

Comando executado para fixar as ferramentas já instaladas e atualizar o manifesto e o lockfile:

```powershell
npm install --save-dev --save-exact eslint@8.57.1 eslint-plugin-sonarjs@0.21.0 --ignore-scripts --no-audit --no-fund
npm run lint
```

## Resultado da verificação

A instalação terminou com código 0. O lint carregou a configuração e analisou src/ sem erro de parser ou de carregamento de plugin. Reportou **2 erros e 0 avisos** em `src/ReportGenerator.js`:

| Local | Regra | Resultado |
| --- | --- | --- |
| 11:3, generateReport | sonarjs/cognitive-complexity | Complexidade 27, limite 15 |
| 43:14, generateReport | sonarjs/no-collapsible-if | Condicional que pode ser unificada com a condição interna |

Código de saída do lint: **1**, por violações no código existente; a configuração funciona. `sonarjs/no-identical-functions` está ativa como error, mas não encontrou ocorrências neste arquivo. Blocos repetidos dentro de uma função não significam necessariamente funções idênticas para essa regra.

A API do ESLint confirmou as duas regras explícitas, o limite 15, `no-undef` do preset ESLint e a preservação das 30 regras habilitadas pelo preset SonarJS recomendado desta versão. A verificação inicial da configuração efetiva foi ajustada para distinguir regras habilitadas daquelas que o próprio preset já define como off; nenhuma configuração foi relaxada nessa verificação.

Evidências:

- `evidencias/eslint-lint.txt`: saída real de npm run lint.
- `evidencias/eslint-lint.exitcode.txt`: código de saída 1.
- `evidencias/eslint-config-efetiva.json`: resumo da configuração efetiva verificada pela API.

`git diff --exit-code HEAD -- src tests` terminou com código 0, confirmando que código-fonte e testes permanecem iguais aos da base. Nenhuma correção automática, refatoração ou execução de testes ocorreu nesta fase.
