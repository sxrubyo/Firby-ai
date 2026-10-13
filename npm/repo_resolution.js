const fs = require("fs");
const path = require("path");

function isSourceCheckout(packageRoot, existsSync = fs.existsSync) {
  const root = path.resolve(packageRoot);
  return Boolean(
    existsSync(path.join(root, ".git")) &&
    existsSync(path.join(root, "firby_app.py")) &&
    existsSync(path.join(root, "run.sh")) &&
    existsSync(path.join(root, "instances"))
  );
}

function resolveRepoDir({ packageRoot, firbyHome, configuredRepoDir = "", existsSync = fs.existsSync }) {
  const root = path.resolve(packageRoot);
  const configured = String(configuredRepoDir || "").trim();
  if (configured) {
    return path.resolve(configured);
  }
  if (isSourceCheckout(root, existsSync)) {
    return root;
  }
  return path.resolve(firbyHome, "repo");
}

module.exports = { isSourceCheckout, resolveRepoDir };
