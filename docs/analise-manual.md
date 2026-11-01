# Análise manual de Bad Smells — ReportGenerator

## Escopo

Inspeção manual de `src/ReportGenerator.js`, realizada em 01/11/2026. As linhas abaixo correspondem ao arquivo original, sem alterações. Não foram executados análise estática, testes ou refatorações nesta fase. Os achados se baseiam na leitura do código, sem métricas produzidas por ferramentas.

## 1. Long Method — método longo e responsabilidades misturadas

- **Local:** `src/ReportGenerator.js`, função `generateReport(reportType, user, items)`, linhas **11–68**.
- **Evidência:** o mesmo método monta cabeçalho (16–24), percorre e seleciona itens, altera sua prioridade, formata linhas e soma valores (27–55), monta rodapé (58–65) e finaliza o texto (67).

```js
// Linhas 28–33
if (user.role === 'ADMIN') {
  // Admins veem todos os itens
  if (item.value > 1000) {
    // Lógica bônus para admins
    item.priority = true;
  }
```

```js
// Linhas 61–64, ainda no mesmo método
} else if (reportType === 'HTML') {
  report += '</table>\n';
  report += `<h3>Total: ${total}</h3>\n`;
  report += '</body></html>\n';
```

- **Impacto na manutenção e nos testes:** uma mudança de regra de visibilidade, prioridade ou apresentação exige navegar pelo mesmo fluxo extenso. Para verificar uma regra isolada pela interface atual, os testes precisam preparar usuário, itens e formato e examinar o relatório completo. A mutação de `item.priority` também exige verificar o estado dos itens após a chamada. O problema é a concentração dessas tarefas, além da extensão do método.
- **Técnica sugerida:** **Extract Function / Extract Method** para separar seleção de itens, aplicação da regra de prioridade e geração de cabeçalho, linha e rodapé. Preservar explicitamente o comportamento observável atual, inclusive a mutação dos itens, antes de considerar mudanças de contrato.

## 2. Condicionais complexas — decisões aninhadas e repetidas

- **Local:** `src/ReportGenerator.js`, função `generateReport`, linhas **27–54**, especialmente **43–52**. A decisão por formato também aparece nas linhas **16–24** e **58–65**.
- **Evidência:** no corpo do laço, o formato é decidido dentro da seleção por papel e do limite de valor.

```js
// Linhas 43–51
} else if (user.role === 'USER') {
  // Users comuns só veem itens de valor baixo
  if (item.value <= 500) {
    if (reportType === 'CSV') {
      report += `${item.id},${item.name},${item.value},${user.name}\n`;
      total += item.value;
    } else if (reportType === 'HTML') {
      report += `<tr><td>${item.id}</td><td>${item.name}</td><td>${item.value}</td></tr>\n`;
      total += item.value;
```

- **Impacto na manutenção e nos testes:** as decisões sobre papel, valor e formato estão entrelaçadas. Alterar um formato exige conferir caminhos de ADMIN e USER, além de cabeçalho e rodapé. Os testes precisam cobrir combinações de papel, formato e limites de valor para detectar diferenças entre os caminhos.
- **Técnica sugerida:** **Decompose Conditional**, extraindo um predicado de visibilidade, e **Replace Nested Conditional with Guard Clauses** para reduzir o aninhamento. Separar a renderização por formato; se a variação justificar, aplicar **Replace Conditional with Polymorphism** com renderizadores CSV e HTML.

## 3. Duplicate Code — geração CSV e acumulação repetidas

- **Local:** `src/ReportGenerator.js`, função `generateReport`, linhas **35–37** e **46–48**; a acumulação também se repete nas linhas **41** e **51**.
- **Evidência:** a linha CSV e a soma são idênticas nos caminhos de ADMIN e USER.

```js
// Linhas 35–37 — ADMIN
if (reportType === 'CSV') {
  report += `${item.id},${item.name},${item.value},${user.name}\n`;
  total += item.value;
```

```js
// Linhas 46–48 — USER, após o filtro por valor
if (reportType === 'CSV') {
  report += `${item.id},${item.name},${item.value},${user.name}\n`;
  total += item.value;
```

- **Impacto na manutenção e nos testes:** uma mudança na representação CSV precisa ser repetida em dois pontos e pode deixar os papéis com saídas inconsistentes. A soma em quatro ramos facilita esquecer a totalização em uma alteração futura. Os testes precisam conferir a mesma regra nos diferentes ramos para detectar essa divergência.
- **Técnica sugerida:** **Extract Function / Extract Method** para a linha CSV e **Slide Statements / Consolidate Duplicate Conditional Fragments** para centralizar a acumulação após a seleção e a renderização válidas. A extração deve preservar o tratamento atual de formatos não reconhecidos: eles não acumulam valores. O HTML de ADMIN e USER não é uma duplicação exata, pois o primeiro pode incluir estilo de prioridade.

## 4. Magic Numbers — limites de negócio literais

- **Local:** `src/ReportGenerator.js`, função `generateReport`, linhas **30** e **45**.
- **Evidência:** os limites de prioridade e de visibilidade aparecem diretamente nas condições.

```js
// Linhas 30–32
if (item.value > 1000) {
  // Lógica bônus para admins
  item.priority = true;
}
```

```js
// Linhas 43–45
} else if (user.role === 'USER') {
  // Users comuns só veem itens de valor baixo
  if (item.value <= 500) {
```

- **Impacto na manutenção e nos testes:** os comentários ajudam a entender a regra, mas os números não têm nomes que expressem seu significado no domínio. Alterar limites exige localizar e interpretar os literais; os testes também podem repetir esses valores sem explicitar sua finalidade. É necessário cobrir as fronteiras: valor igual a 1000 não ativa a prioridade, enquanto valor igual a 500 é visível para USER.
- **Técnica sugerida:** **Replace Magic Number with Symbolic Constant**, com nomes como `ADMIN_PRIORITY_THRESHOLD` e `USER_MAX_VISIBLE_VALUE`, preservando os operadores `>` e `<=`. Não há evidência suficiente para classificar a inicialização `total = 0` como número mágico: ela representa o elemento neutro da soma.

## Prioridade recomendada

**Prioridade 1: decompor `generateReport` (Long Method).** Ele concentra os demais problemas e mistura regras de negócio, apresentação e efeito colateral nos itens. Extrair pequenas funções com responsabilidades claras torna as regras mais fáceis de testar isoladamente e prepara a simplificação das condicionais e a remoção da duplicação.

Em uma fase posterior autorizada, convém proteger o comportamento atual com testes de caracterização antes de refatorar: CSV e HTML para ADMIN e USER, limites de 500 e 1000, prioridade preexistente e mutação dos itens. Esta é apenas uma recomendação; nenhuma dessas ações foi executada nesta fase.
