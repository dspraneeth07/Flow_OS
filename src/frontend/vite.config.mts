import react from "@vitejs/plugin-react-swc";
import * as dotenv from "dotenv";
import path from "path";
import { defineConfig, loadEnv } from "vite";
import istanbul from "vite-plugin-istanbul";
import svgr from "vite-plugin-svgr";
import tsconfigPaths from "vite-tsconfig-paths";
import {
  API_ROUTES,
  BASENAME,
  PORT,
  PROXY_TARGET,
} from "./src/customization/config-constants";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  const envFlowOSResult = dotenv.config({
    path: path.resolve(__dirname, "../../.env"),
  });

  const envFlowOS = envFlowOSResult.parsed || {};

  const apiRoutes = API_ROUTES || ["^/api/v1/", "^/api/v2/", "/health"];

  const target =
    env.VITE_PROXY_TARGET || PROXY_TARGET || "http://localhost:7860";

  const port = Number(env.VITE_PORT) || PORT || 3000;

  const proxyTargets = apiRoutes.reduce((proxyObj, route) => {
    proxyObj[route] = {
      target: target,
      changeOrigin: true,
      secure: false,
      ws: true,
    };
    return proxyObj;
  }, {});

  return {
    base: BASENAME || "",
    build: {
      outDir: "build",
    },
    define: {
      "import.meta.env.BACKEND_URL": JSON.stringify(
        envFlowOS.BACKEND_URL ?? "http://localhost:7860",
      ),
      "import.meta.env.ACCESS_TOKEN_EXPIRE_SECONDS": JSON.stringify(
        envFlowOS.ACCESS_TOKEN_EXPIRE_SECONDS ?? 60,
      ),
      "import.meta.env.CI": JSON.stringify(envFlowOS.CI ?? false),
      "import.meta.env.FLOWOS_AUTO_LOGIN": JSON.stringify(
        envFlowOS.FLOWOS_AUTO_LOGIN ?? true,
      ),
      "import.meta.env.FLOWOS_MCP_COMPOSER_ENABLED": JSON.stringify(
        envFlowOS.FLOWOS_MCP_COMPOSER_ENABLED ?? "true",
      ),
      // Compile-time hard kill switch for the palette Bundle-header
      // Reload action.  The actual user-facing gate is the runtime
      // ``enable_extension_reload`` flag served from ``/config`` (mirrors
      // ``FLOWOS_ENABLE_EXTENSION_RELOAD``), so a packaged frontend
      // built once can still light up the button when an operator opts
      // the backend in via ``--env-file`` or ``flowos_core extension dev``.
      // Default ``true`` here means the bundle SHIPS the UI; corporate
      // Mode B/C builds that want to drop the code entirely can set
      // ``FLOWOS_EXTENSION_RELOAD_ENABLED=false`` in ``.env`` to dead-code-
      // eliminate the Reload UI at build time.
      "import.meta.env.FLOWOS_EXTENSION_RELOAD_ENABLED": JSON.stringify(
        envFlowOS.FLOWOS_EXTENSION_RELOAD_ENABLED ?? "true",
      ),
      "import.meta.env.FLOWOS_WXO_UTM_SOURCE": JSON.stringify(
        envFlowOS.FLOWOS_WXO_UTM_SOURCE ?? "flowos",
      ),
    },
    plugins: [
      react(),
      svgr(),
      tsconfigPaths(),
      istanbul({
        include: "src/**/*",
        extension: [".ts", ".tsx", ".js", ".jsx"],
        requireEnv: false,
      }),
    ],
    server: {
      port: port,
      proxy: {
        ...proxyTargets,
      },
    },
  };
});
