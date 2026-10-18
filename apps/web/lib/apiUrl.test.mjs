import assert from "node:assert/strict";
import test from "node:test";

import { buildApiUrl, resolveApiBaseUrl } from "./apiUrl.ts";

const requestPath = "/sales/13/void";
const scenarios = [
  {
    name: "LAN",
    location: { hostname: "192.168.100.220", protocol: "http:" },
    expected: "http://192.168.100.220:8010/api/v1/sales/13/void",
    expectedLogin: "http://192.168.100.220:8010/api/v1/auth/login",
  },
  {
    name: "Tailscale",
    location: { hostname: "100.121.163.126", protocol: "http:" },
    expected: "http://100.121.163.126:8010/api/v1/sales/13/void",
    expectedLogin: "http://100.121.163.126:8010/api/v1/auth/login",
  },
  {
    name: "localhost",
    location: { hostname: "localhost", protocol: "http:" },
    expected: "http://localhost:8010/api/v1/sales/13/void",
    expectedLogin: "http://localhost:8010/api/v1/auth/login",
  },
  {
    name: "IPv4 loopback",
    location: { hostname: "127.0.0.1", protocol: "http:" },
    expected: "http://127.0.0.1:8010/api/v1/sales/13/void",
    expectedLogin: "http://127.0.0.1:8010/api/v1/auth/login",
  },
  {
    name: "IPv6 loopback",
    location: { hostname: "::1", protocol: "http:" },
    expected: "http://[::1]:8010/api/v1/sales/13/void",
    expectedLogin: "http://[::1]:8010/api/v1/auth/login",
  },
  {
  name: "SolsActive HTTPS",
  location: {
    hostname: "aqua.solsactive.com",
    protocol: "https:",
  },
  expected: "https://aqua.solsactive.com/api/v1/sales/13/void",
  expectedLogin: "https://aqua.solsactive.com/api/v1/auth/login",
  },
];

for (const scenario of scenarios) {
  test(`resolves ${scenario.name} from the browser host`, () => {
    assert.equal(buildApiUrl(requestPath, scenario.location), scenario.expected);
    assert.equal(
      buildApiUrl("/auth/login", scenario.location),
      scenario.expectedLogin,
    );
    globalThis.window = { location: scenario.location };
    try {
      assert.equal(buildApiUrl(requestPath), scenario.expected);
      assert.equal(buildApiUrl("/auth/login"), scenario.expectedLogin);
    } finally {
      delete globalThis.window;
    }
  });
}

test("normalizes request paths without a leading slash", () => {
  assert.equal(
    buildApiUrl("health", { hostname: "localhost", protocol: "http:" }),
    "http://localhost:8010/api/v1/health",
  );
});

test("uses the configured fallback only outside the browser", () => {
  const expected = (
    process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8010/api/v1"
  ).replace(/\/+$/, "");

  assert.equal(resolveApiBaseUrl(), expected);
  assert.equal(buildApiUrl("/auth/login"), `${expected}/auth/login`);
});
