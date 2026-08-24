// Vite's `?react` suffix turns an SVG into a React component (vite-plugin-svgr).
// Jest has no such loader, so every `*.svg?react` import maps here.
const React = require("react");

const SvgMock = React.forwardRef((props, ref) =>
  React.createElement("svg", { ref, "data-testid": "svg-mock", ...props }),
);
SvgMock.displayName = "SvgMock";

module.exports = SvgMock;
module.exports.default = SvgMock;
module.exports.ReactComponent = SvgMock;
module.exports.__esModule = true;
