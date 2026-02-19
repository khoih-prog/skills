import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
<<<<<<< HEAD
const skillRoot = path.resolve(__dirname, '..');
=======
const repoRoot = path.resolve(__dirname, '..');
const skillRoot = path.join(repoRoot, 'consensus-interact');
>>>>>>> 912d99e075cb64bbc5df2e17a32d3fd12a566428

function read(relPath) {
  return fs.readFileSync(path.join(skillRoot, relPath), 'utf8');
}

<<<<<<< HEAD
test('local skill copy has expected core files', () => {
=======
test('skill repo has expected core files', () => {
>>>>>>> 912d99e075cb64bbc5df2e17a32d3fd12a566428
  const required = [
    'SKILL.md',
    'README.md',
    'JOBS.md',
    'HEARTBEAT.md',
    'AI-SELF-IMPROVEMENT.md',
    path.join('references', 'api.md'),
    path.join('scripts', 'consensus_quickstart.sh')
  ];

  for (const rel of required) {
    const full = path.join(skillRoot, rel);
    assert.equal(fs.existsSync(full), true, `missing ${rel}`);
  }
});

<<<<<<< HEAD
test('README references local docs (not stale /public paths)', () => {
=======
test('README references local repo docs (not stale /public paths)', () => {
>>>>>>> 912d99e075cb64bbc5df2e17a32d3fd12a566428
  const readme = read('README.md');
  assert.ok(!readme.includes('/public/'), 'README still references /public paths');
  assert.match(readme, /SKILL\.md/);
  assert.match(readme, /JOBS\.md/);
  assert.match(readme, /AI-SELF-IMPROVEMENT\.md/);
});

test('quickstart uses supported default consensus policy key', () => {
  const script = read(path.join('scripts', 'consensus_quickstart.sh'));
  assert.ok(!script.includes('"type": "SINGLE_WINNER"'), 'deprecated policy SINGLE_WINNER found');
  assert.ok(script.includes('"type": "FIRST_SUBMISSION_WINS"'), 'missing FIRST_SUBMISSION_WINS default policy');
});
