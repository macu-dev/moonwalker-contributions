// Called only from trusted workflows. Octokit is supplied by actions/github-script.
const tagPattern = /^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$/;
const shaPattern = /^[a-f0-9]{40}$/;

function version(tag) {
  const match = tagPattern.exec(tag);
  if (!match) throw new Error(`Se requiere un tag completo vX.Y.Z: ${tag}`);
  return match.slice(1).map(Number);
}

function compare(a, b) {
  const left = version(a), right = version(b);
  for (let i = 0; i < 3; i++) if (left[i] !== right[i]) return left[i] - right[i];
  return 0;
}

function validTitle(title) {
  return /^(feat|fix|perf|refactor|docs|style|test|build|ci|chore|revert)(\([^\r\n()]+\))?!?: \S[^\r\n]*$/.test(title);
}

function requireActivation(env, publishing = true) {
  if (!env.RELEASE_APP_ID || !env.RELEASE_APP_PRIVATE_KEY) {
    throw new Error('Configurar RELEASE_APP_ID y RELEASE_APP_PRIVATE_KEY antes de usar releases.');
  }
  if ((publishing && env.RELEASE_AUTOMATION_ENABLED !== 'true') || !env.RELEASE_PREFLIGHT_URL?.startsWith('https://github.com/')) {
    throw new Error('Completar la verificación remota de RELEASING.md y configurar RELEASE_PREFLIGHT_URL y RELEASE_AUTOMATION_ENABLED.');
  }
}

async function releases(github, repo) {
  return github.paginate(github.rest.repos.listReleases, { ...repo, per_page: 100 });
}

function selectRelease(all, requestedTag = '') {
  const drafts = all.filter(item => item.draft);
  if (drafts.length > 1) throw new Error('Hay varios borradores: reconciliarlos antes de continuar.');
  if (requestedTag) {
    version(requestedTag);
    if (drafts.length && drafts[0].tag_name !== requestedTag) {
      throw new Error('Recuperar primero el borrador pendiente.');
    }
  }
  const item = requestedTag ? all.find(item => item.tag_name === requestedTag) : drafts[0];
  if (requestedTag && !item) throw new Error('La versión solicitada no existe. No se creará otra release.');
  if (!item) return null;
  version(item.tag_name);
  if (item.prerelease) throw new Error('Este flujo no publica canales de prerelease.');
  if (!shaPattern.test(item.target_commitish)) throw new Error('El objetivo debe ser un SHA completo, no una rama.');
  return { id: item.id, sha: item.target_commitish, tag: item.tag_name };
}

async function tagSha(github, repo, tag) {
  let object;
  try {
    object = (await github.rest.git.getRef({ ...repo, ref: `tags/${tag}` })).data.object;
  } catch (error) {
    if (error.status === 404) return null;
    throw error;
  }
  for (let depth = 0; object.type === 'tag' && depth < 8; depth++) {
    object = (await github.rest.git.getTag({ ...repo, tag_sha: object.sha })).data.object;
  }
  if (object.type !== 'commit') throw new Error('El tag no resuelve a un commit.');
  return object.sha;
}

async function checkTag(github, repo, candidate) {
  const existing = await tagSha(github, repo, candidate.tag);
  if (existing && existing !== candidate.sha) throw new Error('El tag completo apunta a otro SHA; no se reescribirá.');
  return existing;
}

function changelogNotes(changelog, tag) {
  const sections = changelog.split(/(?=^#{1,3} \[?(?:\d+\.\d+\.\d+|Unreleased))/m);
  const section = sections.find(text => text.match(/^#{1,3} \[?(\d+\.\d+\.\d+)/)?.[1] === tag.slice(1));
  if (!section) throw new Error('No hay una entrada de changelog para la versión.');
  return section.trim();
}

async function updateAlias(github, repo, candidate, all) {
  const major = version(candidate.tag)[0];
  if (major === 0) return;
  const sameMajor = all.filter(item => !item.draft && !item.prerelease && tagPattern.test(item.tag_name)
    && version(item.tag_name)[0] === major);
  const latest = sameMajor.sort((a, b) => compare(b.tag_name, a.tag_name))[0];
  // Refuse to move an alias back when recovering an older release.
  if (latest && compare(latest.tag_name, candidate.tag) > 0) return;
  const alias = `v${major}`;
  const current = await tagSha(github, repo, alias);
  if (current === candidate.sha) return;
  if (current) {
    const known = sameMajor.filter(item => item.tag_name !== candidate.tag);
    let recognized = false;
    for (const item of known) {
      if (await tagSha(github, repo, item.tag_name) === current) recognized = true;
    }
    if (!recognized) throw new Error('El alias apunta a un commit no reconocido; requiere reconciliación.');
    await github.rest.git.updateRef({ ...repo, ref: `tags/${alias}`, sha: candidate.sha, force: true });
  } else {
    await github.rest.git.createRef({ ...repo, ref: `refs/tags/${alias}`, sha: candidate.sha });
  }
}

async function publish(github, repo, candidate, validatedSha) {
  version(candidate.tag);
  if (!shaPattern.test(validatedSha) || candidate.sha !== validatedSha) throw new Error('SHA no validado.');
  const current = (await github.rest.repos.getRelease({ ...repo, release_id: candidate.id })).data;
  if (current.tag_name !== candidate.tag || current.target_commitish !== candidate.sha || current.prerelease) {
    throw new Error('El objetivo de la release cambió después de validarlo.');
  }
  await checkTag(github, repo, candidate);
  const file = (await github.rest.repos.getContent({ ...repo, path: 'CHANGELOG.md', ref: candidate.sha })).data;
  if (!file.content) throw new Error('No se pudo leer CHANGELOG.md.');
  const notes = changelogNotes(Buffer.from(file.content, 'base64').toString('utf8'), candidate.tag);
  if (notes !== (current.body || '').trim()) throw new Error('Las notas difieren del changelog validado.');
  if (current.draft) {
    await github.rest.repos.updateRelease({
      ...repo, release_id: candidate.id, target_commitish: candidate.sha, draft: false,
    });
  }
  if (await tagSha(github, repo, candidate.tag) !== candidate.sha) throw new Error('El tag publicado no coincide.');
  await updateAlias(github, repo, candidate, await releases(github, repo));
}

module.exports = { version, compare, validTitle, requireActivation, releases, selectRelease, tagSha, checkTag, changelogNotes, updateAlias, publish };
