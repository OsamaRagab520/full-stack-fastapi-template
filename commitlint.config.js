// Commit message linting — Conventional Commits.
// Enforced via pre-commit (commit-msg stage); see .pre-commit-config.yaml.
//
// Format:  <type>(<scope>): <subject>
// Example: fix(auth): make TokenPayload.sub required
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Allowed types. `feat` and `fix` are the only ones that drive a semver bump.
    'type-enum': [
      2,
      'always',
      [
        'feat', // a new feature or endpoint            (MINOR)
        'fix', // a bug fix                              (PATCH)
        'refactor', // neither fixes a bug nor adds a feature
        'perf', // a performance improvement
        'test', // adding or correcting tests only
        'docs', // documentation only (README, AGENTS.md, comments)
        'build', // build system or deps (pyproject.toml, uv.lock, Dockerfile)
        'ci', // CI config (.github/workflows, pre-commit)
        'style', // formatting / lint fixes, no logic change
        'chore', // tooling and housekeeping
        'revert', // reverts a previous commit
      ],
    ],
    // Allowed scopes. Omit the scope for changes that span the whole repo.
    'scope-enum': [
      2,
      'always',
      [
        // backend domains
        'auth',
        'users',
        'items',
        'emails',
        'core',
        // cross-cutting
        'deps',
        'ci',
        'docker',
        'frontend',
        'docs',
      ],
    ],
    // Imperative, lowercase subject, no trailing period; header <= 72 chars.
    'header-max-length': [2, 'always', 72],
  },
};
