const { readFileSync } = require('node:fs');
const { execFileSync } = require('node:child_process');

function checkVersion(metadata, source, cliVersion, tag = '') {
  const version = metadata.match(/^version\s*=\s*"([^"]+)"/m)?.[1];
  const exported = source.match(/^__version__\s*=\s*"([^"]+)"/m)?.[1];
  if (!version || version !== exported || version !== cliVersion.trim()) {
    throw new Error('Las versiones de pyproject.toml, __version__ y CLI no coinciden.');
  }
  if (tag && tag !== `v${version}`) throw new Error('El tag no coincide con la versión del paquete.');
  return version;
}

if (require.main === module) {
  console.log(checkVersion(
    readFileSync('pyproject.toml', 'utf8'),
    readFileSync('src/moonwalk_contributions/__init__.py', 'utf8'),
    execFileSync('moonwalk-contributions', ['--version'], { encoding: 'utf8' }),
    process.env.RELEASE_TAG || '',
  ));
}
module.exports = { checkVersion };
