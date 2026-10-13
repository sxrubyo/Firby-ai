const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");

const { isSourceCheckout, resolveRepoDir } = require("../npm/repo_resolution");

function fakeExists(existing) {
  const values = new Set(existing.map((entry) => path.resolve(entry)));
  return (candidate) => values.has(path.resolve(candidate));
}

test("usa el checkout como fuente de verdad cuando tiene marcadores de proyecto", () => {
  const packageRoot = "/srv/firby";
  const existsSync = fakeExists([
    "/srv/firby/.git",
    "/srv/firby/firby_app.py",
    "/srv/firby/run.sh",
    "/srv/firby/instances",
  ]);

  assert.equal(isSourceCheckout(packageRoot, existsSync), true);
  assert.equal(
    resolveRepoDir({
      packageRoot,
      firbyHome: "/home/test/.firby",
      existsSync,
    }),
    packageRoot
  );
});

test("una instalación empaquetada conserva su workspace de usuario", () => {
  const packageRoot = "/usr/local/lib/node_modules/@innvisor/firby-ai";
  const existsSync = fakeExists([
    `${packageRoot}/firby_app.py`,
    `${packageRoot}/run.sh`,
  ]);

  assert.equal(isSourceCheckout(packageRoot, existsSync), false);
  assert.equal(
    resolveRepoDir({
      packageRoot,
      firbyHome: "/home/test/.firby",
      existsSync,
    }),
    "/home/test/.firby/repo"
  );
});

test("FIRBY_REPO_DIR tiene prioridad para operaciones controladas", () => {
  const packageRoot = "/srv/firby";
  const existsSync = fakeExists([
    "/srv/firby/.git",
    "/srv/firby/firby_app.py",
    "/srv/firby/run.sh",
    "/srv/firby/instances",
  ]);

  assert.equal(
    resolveRepoDir({
      packageRoot,
      firbyHome: "/home/test/.firby",
      configuredRepoDir: "/srv/firby-staging",
      existsSync,
    }),
    "/srv/firby-staging"
  );
});
