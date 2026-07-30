import assert from "node:assert/strict";
import test from "node:test";

import {
  canShowAdminAnalytics,
  getAnalyticsPreset,
  getAnalyticsViewState,
} from "./adminAnalytics.ts";

test("admin sees analytics while operator keeps the simple operational panel", () => {
  assert.equal(canShowAdminAnalytics("admin_auditor"), true);
  assert.equal(canShowAdminAnalytics("operator"), false);
  assert.equal(canShowAdminAnalytics(null), false);
});

test("analytics presets prepare today, last seven days and current month", () => {
  const today = new Date(2026, 6, 29, 12, 0, 0);
  assert.deepEqual(getAnalyticsPreset("today", today), {
    start_date: "2026-07-29",
    end_date: "2026-07-29",
  });
  assert.deepEqual(getAnalyticsPreset("last7", today), {
    start_date: "2026-07-23",
    end_date: "2026-07-29",
  });
  assert.deepEqual(getAnalyticsPreset("month", today), {
    start_date: "2026-07-01",
    end_date: "2026-07-29",
  });
});

test("analytics view states cover loading, error, empty and ready", () => {
  assert.equal(
    getAnalyticsViewState({ error: "", hasData: false, isLoading: true }),
    "loading",
  );
  assert.equal(
    getAnalyticsViewState({
      error: "No disponible",
      hasData: false,
      isLoading: false,
    }),
    "error",
  );
  assert.equal(
    getAnalyticsViewState({ error: "", hasData: false, isLoading: false }),
    "empty",
  );
  assert.equal(
    getAnalyticsViewState({ error: "", hasData: true, isLoading: false }),
    "ready",
  );
});
