const FeatureFlags = {
  Nesting: 1 << 0,
  MediaQueries: 1 << 1,
  LogicalProperties: 1 << 2,
  DirSelector: 1 << 3,
  LightDark: 1 << 4,
};

function toBuffer(code) {
  if (Buffer.isBuffer(code)) return code;
  if (typeof code === "string") return Buffer.from(code);
  return Buffer.from([]);
}

function transform(options = {}) {
  const code = toBuffer(options.code ?? "");
  return {
    code,
    map: options.inputSourceMap ?? null,
    warnings: [],
  };
}

function passthrough(value) {
  return value;
}

module.exports = {
  Features: FeatureFlags,
  transform,
  browserslistToTargets: () => ({}),
  composeVisitors: () => passthrough,
};
