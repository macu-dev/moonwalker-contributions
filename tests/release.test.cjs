const test = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync, readdirSync } = require('node:fs');
const release = require('../scripts/release.cjs');
const { checkVersion } = require('../scripts/check-version.cjs');
const config = JSON.parse(readFileSync('release-please-config.json'));
const sha = 'a'.repeat(40), other = 'b'.repeat(40);
const notes = '## [1.2.3](https://example.com/compare) (2026-10-15)\n\n### Correcciones\n\n* Corregir etiquetas (#1)';
const changelog = `# Changelog\n\n${notes}\n\n## 1.2.2\n\nAnterior.\n`;
const draft = { id: 1, tag_name: 'v1.2.3', target_commitish: sha, draft: true, body: notes };

function fixture(item = draft) {
  const state = { item: { ...item }, refs: {}, calls: [], failPublish: false, failAlias: false, all: [] };
  const github = {
    paginate: async () => [state.item, ...state.all],
    rest: {
      repos: {
        listReleases() {},
        getRelease: async () => ({ data: { ...state.item } }),
        getContent: async args => {
          assert.equal(args.ref, sha);
          return { data: { content: Buffer.from(changelog).toString('base64') } };
        },
        updateRelease: async args => {
          if (state.failPublish) throw new Error('publication unavailable');
          assert.equal(args.target_commitish, sha);
          state.calls.push('publish');
          state.item.draft = false;
          state.refs['v1.2.3'] = sha;
        },
      },
      git: {
        getRef: async args => {
          const value = state.refs[args.ref.slice(5)];
          if (!value) throw Object.assign(new Error('Not found'), { status: 404 });
          return { data: { object: { sha: value, type: 'commit' } } };
        },
        createRef: async args => {
          if (state.failAlias) throw new Error('alias unavailable');
          state.calls.push('alias');
          state.refs[args.ref.slice(10)] = args.sha;
        },
        updateRef: async args => {
          state.calls.push('alias');
          state.refs[args.ref.slice(5)] = args.sha;
        },
      },
    },
  };
  return { state, github, candidate: release.selectRelease([item]) || release.selectRelease([item], item.tag_name) };
}

test('configuration and manifest conform to official Release Please schemas', () => {
  const Ajv = require('ajv');
  const ajv = new Ajv({ strict: false });
  require('ajv-formats')(ajv);
  for (const [name, file] of [['config', 'release-please-config.json'], ['manifest', '.release-please-manifest.json']]) {
    const validate = ajv.compile(require(`release-please/schemas/${name}.json`));
    assert.ok(validate(JSON.parse(readFileSync(file))), JSON.stringify(validate.errors));
  }
});

test('real Python strategy produces the configured bumps and updates both versions', async () => {
  require('release-please'); // Initialize upstream factories before loading a concrete strategy.
  const { Python } = require('release-please/build/src/strategies/python');
  const { DefaultVersioningStrategy } = require('release-please/build/src/versioning-strategies/default');
  const { Version } = require('release-please/build/src/version');
  const { TagName } = require('release-please/build/src/util/tag-name');
  const { parseConventionalCommits } = require('release-please/build/src/commit');
  const metadata = readFileSync('pyproject.toml', 'utf8');
  const source = readFileSync('src/moonwalk_contributions/__init__.py', 'utf8');
  const github = {
    repository: { owner: 'macu-dev', repo: 'moonwalker-contributions' },
    getFileContentsOnBranch: async path => {
      if (path !== 'pyproject.toml') throw new Error('Unexpected file');
      return { parsedContent: metadata };
    },
    findFilesByFilenameAndRef: async () => [],
  };
  const strategy = new Python({
    github, targetBranch: 'main', includeComponentInTag: false,
    changelogSections: config['changelog-sections'],
    versioningStrategy: new DefaultVersioningStrategy({
      bumpMinorPreMajor: config['bump-minor-pre-major'],
      bumpPatchForMinorPreMajor: config['bump-patch-for-minor-pre-major'],
    }),
  });
  for (const [base, message, expected] of [
    ['0.1.0', 'fix: corregir etiquetas', '0.1.1'],
    ['0.1.0', 'feat: nueva animación', '0.2.0'],
    ['0.1.0', 'feat!: cambiar entradas\n\nBREAKING CHANGE: renombrar entrada', '0.2.0'],
    ['1.2.3', 'fix!: eliminar opción\n\nBREAKING CHANGE: usar nueva opción', '2.0.0'],
    ['0.1.0', 'chore: update contribution animation', null],
  ]) {
    const commits = parseConventionalCommits([{ sha, message, files: ['src/moonwalk_contributions/cli.py'] }]);
    const result = await strategy.buildReleasePullRequest(commits, { tag: new TagName(Version.parse(base)), sha: other });
    if (!expected) { assert.equal(result, undefined); continue; }
    assert.equal(result.version.toString(), expected);
    assert.ok(release.validTitle(result.title.toString()));
    const updatedMetadata = result.updates.find(item => item.path === 'pyproject.toml').updater.updateContent(metadata);
    const updatedSource = result.updates.find(item => item.path === 'src/moonwalk_contributions/__init__.py').updater.updateContent(source);
    assert.equal(checkVersion(updatedMetadata, updatedSource, expected), expected);
    const updatedChangelog = result.updates.find(item => item.path === 'CHANGELOG.md').updater.updateContent(readFileSync('CHANGELOG.md', 'utf8'));
    const built = await strategy.buildRelease({
      title: result.title.toString(), body: result.body.toString(),
      headBranchName: result.headRefName, sha, number: 1, baseBranchName: 'main', labels: [], files: [],
    });
    assert.equal(release.changelogNotes(updatedChangelog, `v${expected}`), built.notes.trim());
  }
});

test('version checker rejects inconsistent metadata, CLI and release tag', () => {
  const metadata = 'version = "0.1.0"', source = '__version__ = "0.1.0"';
  assert.equal(checkVersion(metadata, source, '0.1.0\n', 'v0.1.0'), '0.1.0');
  assert.throws(() => checkVersion(metadata, source, '0.2.0'));
  assert.throws(() => checkVersion(metadata, '__version__ = "0.2.0"', '0.1.0'));
  assert.throws(() => checkVersion(metadata, source, '0.1.0', 'v0.2.0'));
});

test('titles accept conventional types, scopes, breaking markers and release PRs', () => {
  for (const title of ['feat: giro', 'fix(cli): etiquetas', 'feat!: cambio', 'chore(main): release 0.2.0']) {
    assert.ok(release.validTitle(title));
  }
  for (const title of ['Update stuff', 'feat: ', 'feat: cambio\nrun me', 'feat:']) assert.ok(!release.validTitle(title));
});

test('activation requires app configuration and recorded preflight; preparation can precede publication', () => {
  assert.throws(() => release.requireActivation({}));
  const env = { RELEASE_APP_ID: '1', RELEASE_APP_PRIVATE_KEY: 'test', RELEASE_PREFLIGHT_URL: 'https://github.com/org/repo/issues/1' };
  assert.doesNotThrow(() => release.requireActivation(env, false));
  assert.throws(() => release.requireActivation(env));
  assert.doesNotThrow(() => release.requireActivation({ ...env, RELEASE_AUTOMATION_ENABLED: 'true' }));
});

test('pending draft is selected for recovery; missing and ambiguous targets stop', () => {
  assert.equal(release.selectRelease([draft]).sha, sha);
  assert.equal(release.selectRelease([]), null);
  assert.throws(() => release.selectRelease([draft, { ...draft, id: 2 }]));
  assert.throws(() => release.selectRelease([draft], 'v1.2.2'));
  assert.throws(() => release.selectRelease([], 'v1.2.3'));
  assert.throws(() => release.selectRelease([{ ...draft, target_commitish: 'main' }]));
});

test('publication stays on the saved SHA when main advances, and is idempotent', async () => {
  const { github, state, candidate } = fixture();
  state.main = other;
  await release.publish(github, {}, candidate, sha);
  await release.publish(github, {}, candidate, sha);
  assert.deepEqual(state.calls, ['publish', 'alias']);
  assert.equal(state.refs['v1.2.3'], sha);
});

test('mismatched validation, changed draft and conflicting complete tag cannot publish', async () => {
  for (const change of ['validation', 'draft', 'tag', 'notes']) {
    const { github, state, candidate } = fixture();
    if (change === 'draft') state.item.target_commitish = other;
    if (change === 'tag') state.refs['v1.2.3'] = other;
    if (change === 'notes') state.item.body = 'unreviewed notes';
    await assert.rejects(release.publish(github, {}, candidate, change === 'validation' ? other : sha));
    assert.deepEqual(state.calls, []);
  }
});

test('failure before publication preserves the draft and can be recovered', async () => {
  const { github, state, candidate } = fixture();
  state.failPublish = true;
  await assert.rejects(release.publish(github, {}, candidate, sha));
  assert.equal(state.item.draft, true);
  assert.deepEqual(state.calls, []);
  state.failPublish = false;
  await release.publish(github, {}, candidate, sha);
  assert.deepEqual(state.calls, ['publish', 'alias']);
});

test('failure after publication repairs only the alias on retry', async () => {
  const { github, state, candidate } = fixture();
  state.failAlias = true;
  await assert.rejects(release.publish(github, {}, candidate, sha));
  assert.equal(state.item.draft, false);
  assert.deepEqual(state.calls, ['publish']);
  state.failAlias = false;
  await release.publish(github, {}, candidate, sha);
  assert.deepEqual(state.calls, ['publish', 'alias']);
});

test('recovering an old version cannot roll back its major alias', async () => {
  const { github, state, candidate } = fixture();
  state.all = [{ ...draft, id: 2, draft: false, tag_name: 'v1.3.0', target_commitish: other }];
  state.refs.v1 = other;
  await release.publish(github, {}, candidate, sha);
  assert.equal(state.refs.v1, other);
});

test('zero-major publication never creates a v0 alias', async () => {
  const { github, state } = fixture();
  await release.updateAlias(github, {}, { tag: 'v0.2.0', sha }, []);
  assert.deepEqual(state.calls, []);
});

test('authorization errors are not treated as an absent tag', async () => {
  const { github } = fixture();
  github.rest.git.getRef = async () => { throw Object.assign(new Error('Forbidden'), { status: 403 }); };
  await assert.rejects(release.tagSha(github, {}, 'v1'));
});

test('workflow YAML parses; recovery and normal publication share concurrency', () => {
  const yaml = require('yaml');
  for (const file of readdirSync('.github/workflows')) yaml.parse(readFileSync(`.github/workflows/${file}`, 'utf8'));
  const workflow = yaml.parse(readFileSync('.github/workflows/release-please.yml', 'utf8'));
  assert.equal(workflow.concurrency['cancel-in-progress'], false);
  assert.ok(workflow.on.workflow_dispatch.inputs.recover_tag);
  const title = yaml.parse(readFileSync('.github/workflows/pr-title.yml', 'utf8'));
  assert.equal(title.permissions.contents, 'read');
  assert.ok(title.jobs.title.steps.every(step => !step.uses.includes('checkout')));
  assert.ok(!title.jobs.title.steps[0].with.script.includes('${{'));
});
