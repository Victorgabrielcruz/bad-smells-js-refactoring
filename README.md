# Detecção de Bad Smells e Refatoração Segura

Este é o repositório-base para o trabalho prático sobre Bad Smells e Refatoração.

## 1. Contexto

O código em `src/ReportGenerator.js` funciona, mas foi escrito de forma mal cheirosa (com Bad Smells). Ele é difícil de ler, manter e testar.

A suíte de testes em `__tests__/ReportGenerator.test.js` é sua **rede de segurança**. Ela está completa, robusta e testa o _comportamento_ (o resultado final), não a implementação.

## 2. Seu Desafio

1.  **Analisar:** Rodar o ESLint (`npx eslint src/`) e identificar os Bad Smells apontados pela ferramenta (e manualmente).
2.  **Refatorar:** Criar uma cópia do arquivo (`src/ReportGenerator.refactored.js`) e refatorar o código para que ele fique limpo, legível e sem os smells detectados.
3.  **Validar:** Criar uma cópia do teste (`__tests__/ReportGenerator.refactored.test.js`), apontá-la para seu novo arquivo refatorado e garantir que **todos os testes continuem passando**.

**Regra Principal:** Você não deve alterar os testes (exceto para duplicá-los). A suíte de testes é a sua garantia de que a refatoração foi bem-sucedida.

## 3. Como Começar

1.  **Instale as dependências:**
    ```bash
    npm install
    ```
2.  **Execute os testes (Rede de Segurança):**

    ```bash
    npm test
    ```

    (Confirme que todos passam antes de começar).

3.  **Execute a Análise Estática (Detecção de Smells):**
    ```bash
    npx eslint src/
    ```
    (Analise os erros reportados pelo `eslint-plugin-sonarjs`).

## Entrega do trabalho

- [Relatório PDF em formatação ABNT (4 páginas)](output/pdf/relatorio-bad-smells-abnt.pdf)
- [Guia da entrega e reprodução](docs/entrega.md)
- [Processo de refatoração](docs/processo-refatoracao.md)
- [Validação final e limitações](docs/evidencias/validacao-final.md)

A implementação original e a suíte em `tests/` foram preservadas. A cópia refatorada está em `src/ReportGenerator.refactored.js` e a suíte copiada em `__tests__/ReportGenerator.refactored.test.js`.

Resultado registrado: lint da cópia sem diagnósticos; com ESM temporário, 8 testes aprovados e 2 reprovados, pela mesma falha de HTML ADMIN preexistente em cada suíte. O requisito de 100% de aprovação não foi atingido. Consulte o guia para os comandos e as evidências reais.
