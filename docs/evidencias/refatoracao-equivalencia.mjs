import assert from 'node:assert/strict';
import fs from 'node:fs';
import { ReportGenerator as Original } from '../../src/ReportGenerator.js';
import { ReportGenerator as Refactored } from '../../src/ReportGenerator.refactored.js';

const users = ['ADMIN', 'USER', 'GUEST', undefined].map(role => ({ name: 'Ana,<teste>', role }));
const formats = ['CSV', 'HTML', 'JSON', '', undefined];
const item = (value, priority) => ({ id: 1, name: 'Produto,<teste>', value, priority });
const itemSets = [
  [], [item(0)], [item(499)], [item(500)], [item(501)],
  [item(999)], [item(1000)], [item(1001)],
  [item(300, true), item(1200, false), item(500, false)],
  [item(-1), item(300, 'existing'), item(NaN), item(700)],
];
const db = {};
assert.deepEqual(Object.getOwnPropertyNames(Refactored.prototype), Object.getOwnPropertyNames(Original.prototype));
assert.equal(new Refactored(db).db, db);
let cases = 0;
for (const user of users) {
  for (const format of formats) {
    for (const items of itemSets) {
      const originalItems = structuredClone(items);
      const refactoredItems = structuredClone(items);
      const original = new Original(db);
      const refactored = new Refactored(db);
      for (let repeat = 0; repeat < 2; repeat++) {
        assert.equal(refactored.generateReport(format, user, refactoredItems), original.generateReport(format, user, originalItems));
        assert.deepEqual(refactoredItems, originalItems);
      }
      cases++;
    }
  }
}
const originalTest = fs.readFileSync(new URL('../../tests/ReportGenerator.test.js', import.meta.url), 'utf8');
const copiedTest = fs.readFileSync(new URL('../../__tests__/ReportGenerator.refactored.test.js', import.meta.url), 'utf8');
assert.equal(copiedTest, originalTest.replace('../src/ReportGenerator.js', '../src/ReportGenerator.refactored.js'));
console.log(`${cases} cenários comparativos aprovados, com duas chamadas sucessivas por cenário (400 comparações de saída e estado).`);
console.log('Cobertura: ADMIN/USER/papel desconhecido/ausente; CSV/HTML/formato desconhecido/vazio/ausente; limites 500 e 1000; prioridade preexistente; array vazio; valores negativos e NaN.');
console.log('Interface pública preservada; cópia do teste difere exclusivamente no caminho do import.');
