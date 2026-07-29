import assert from "node:assert/strict";
import test from "node:test";

import {
  getLoginErrorMessage,
  readLoginCredentials,
} from "./loginForm.ts";

test("reads the submitted form values used by browser autofill", () => {
  const formData = new FormData();
  formData.set("username", "  admin  ");
  formData.set("password", " password with spaces ");

  assert.deepEqual(readLoginCredentials(formData), {
    username: "admin",
    password: " password with spaces ",
  });
});

test("reports invalid credentials without leaving a loading-only state", () => {
  assert.equal(
    getLoginErrorMessage(Object.assign(new Error("Credenciales invalidas."), {
      status: 401,
    })),
    "Usuario o contraseña incorrectos.",
  );
});

test("reports connectivity failures with the pilot escalation message", () => {
  assert.equal(
    getLoginErrorMessage(Object.assign(new Error("AbortError"), { status: 0 })),
    "No se pudo iniciar sesión. Verifica la conexión o avisa a George.",
  );
});
