import fs from 'node:fs';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import { execFileSync, spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
const require = createRequire(new URL('../../package.json', import.meta.url));
const { ESLint } = require('eslint');
const readJson = path => JSON.parse(fs.readFileSync(path, 'utf8').replace(/^\uFEFF/, ''));
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const originals = ['src/ReportGenerator.js', 'tests/ReportGenerator.test.js'];
const diff = spawnSync('git', ['diff', '--exit-code', 'HEAD', '--', ...originals], { encoding: 'utf8' });
fs.writeFileSync('docs/evidencias/validacao-final-originais.diff', diff.stdout);
assert.equal(diff.status, 0);
const integrity = originals.map(path => {
  const current = fs.readFileSync(path);
  const base = execFileSync('git', ['show', `HEAD:${path}`]);
  assert.equal(current.toString('utf8').replace(/\r\n/g, '\n'), base.toString('utf8').replace(/\r\n/g, '\n'));
  const historicalHashes = {
    'src/ReportGenerator.js': 'e3aaaf125fc846de0be4be873db63a6d17b020cab8446e82debb3f26a0a386a8',
    'tests/ReportGenerator.test.js': 'fffa6aa1599b399af1d52abd192370c7d80158e08c3ee02f4c95b18bc0ae97da',
  };
  assert.equal(hash(current), historicalHashes[path]);
  return { path, sha256: hash(current), headSha256: hash(base), identicalToHistoricalWorkingTreeBytes: true, identicalToHeadAfterCrLfNormalization: true };
});
const originalTest = fs.readFileSync(originals[1], 'utf8');
const copiedTest = fs.readFileSync('__tests__/ReportGenerator.refactored.test.js', 'utf8');
assert.equal(copiedTest, originalTest.replace('../src/ReportGenerator.js', '../src/ReportGenerator.refactored.js'));
fs.writeFileSync('docs/evidencias/validacao-final-teste-copiado.diff', "-import { ReportGenerator } from '../src/ReportGenerator.js';\n+import { ReportGenerator } from '../src/ReportGenerator.refactored.js';\n");
const eslint = new ESLint();
const originalConfig = await eslint.calculateConfigForFile('src/ReportGenerator.js');
const refactoredConfig = await eslint.calculateConfigForFile('src/ReportGenerator.refactored.js');
assert.deepEqual(originalConfig, refactoredConfig);
fs.writeFileSync('docs/evidencias/validacao-final-config-efetiva.json', JSON.stringify(originalConfig, null, 2) + '\n');
const current = readJson('docs/evidencias/validacao-final-eslint.json');
const historical = readJson('docs/evidencias/analise-estatica-original.eslint.json');
const originalLint = current.find(r => r.filePath.endsWith('ReportGenerator.js'));
const refactoredLint = current.find(r => r.filePath.endsWith('ReportGenerator.refactored.js'));
const signatures = result => result.messages.map(({ ruleId, severity, line, column, message }) => ({ ruleId, severity, line, column, message }));
assert.deepEqual(signatures(originalLint), signatures(historical[0]));
const jest = readJson('docs/evidencias/validacao-final-jest.json');
const testSummary = jest.testResults.map(suite => ({ file: suite.name, passed: suite.assertionResults.filter(t => t.status === 'passed').length, failed: suite.assertionResults.filter(t => t.status === 'failed').length, failures: suite.assertionResults.filter(t => t.status === 'failed').map(t => ({ name: t.fullName, messages: t.failureMessages })) }));
const summary = { integrity, originalsGitDiffExitCode: diff.status, copiedTestOnlyImportChanged: true, originalTestActualPath: originals[1], copiedTestPath: '__tests__/ReportGenerator.refactored.test.js', identicalEffectiveEslintConfig: true, eslint: require('eslint/package.json').version, sonarjs: require('eslint-plugin-sonarjs/package.json').version, cognitiveComplexityRule: originalConfig.rules['sonarjs/cognitive-complexity'], noIdenticalFunctionsRule: originalConfig.rules['sonarjs/no-identical-functions'], historicalOriginalDiagnosticsUnchanged: true, originalLint: { errors: originalLint.errorCount, warnings: originalLint.warningCount, messages: signatures(originalLint) }, refactoredLint: { errors: refactoredLint.errorCount, warnings: refactoredLint.warningCount, messages: signatures(refactoredLint) }, tests: testSummary };
fs.writeFileSync('docs/evidencias/validacao-final-resumo.json', JSON.stringify(summary, null, 2) + '\n');
console.log('Originais com diff vazio em relação ao HEAD (saída 0); hashes idênticos à fase anterior. HEAD usa LF e checkout usa CRLF.');
console.log('Teste copiado: diferença exclusiva no caminho do import.');
console.log('Configuração efetiva do ESLint idêntica para os dois arquivos; alertas do original iguais aos históricos.');
for (const s of testSummary) console.log(`${s.file}: ${s.passed} aprovados; ${s.failed} reprovados.`);
