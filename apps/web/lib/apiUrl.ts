const API_PORT = "8010";
const API_V1_PATH = "/api/v1";
const FALLBACK_API_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? `http://localhost:${API_PORT}${API_V1_PATH}`
).replace(/\/+$/, "");

export type ApiLocation = {
  hostname: string;
  protocol: string;
};

export function resolveApiBaseUrl(location?: ApiLocation): string {
  if (!location) {
    return FALLBACK_API_URL;
  }

  if (location.hostname === "aqua.solsactive.com") {
    return `${location.protocol}//${location.hostname}${API_V1_PATH}`;
  }

  const hostname = formatHostname(location.hostname);
  return `${location.protocol}//${hostname}:${API_PORT}${API_V1_PATH}`;
}

export function buildApiUrl(path: string, location?: ApiLocation): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const baseUrl = location
    ? resolveApiBaseUrl(location)
    : getApiBaseUrl();
  return `${baseUrl}${normalizedPath}`;
}

export function getApiBaseUrl(): string {
  return resolveApiBaseUrl(
    typeof window === "undefined" ? undefined : window.location,
  );
}

function formatHostname(hostname: string): string {
  if (
    hostname.startsWith("[") ||
    hostname === "localhost" ||
    !hostname.includes(":")
  ) {
    return hostname;
  }
  return `[${hostname}]`;
}
