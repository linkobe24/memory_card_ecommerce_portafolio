import { TokenResponse, RefreshTokenRequest } from "@/types/user.types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public response?: any
  ) {
    super(message);
    this.name = "APIError";
  }
}

function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("refresh_token");
}

function saveTokens(accessToken: string, refresToken: string) {
  if (typeof window === "undefined") return null;
  localStorage.setItem("access_token", accessToken);
  localStorage.setItem("refresh_token", refresToken);
}

function clearTokens() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
}

// refresh token automatico
async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_URL}/api/auth/refresh`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!response.ok) {
      clearTokens();
      return null;
    }

    const data: TokenResponse = await response.json();
    saveTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch (error) {
    clearTokens();
    return null;
  }
}

// fetch wrapper con interceptores
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  const accessToken = getAccessToken();

  // Request interceptor: normaliza headers y agrega JSON + bearer token
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  let response = await fetch(url, { ...options, headers });

  // Response interceptor: si 401, intenta refresh y reintenta
  if (response.status === 401) {
    const newAccessToken = await refreshAccessToken();
    if (newAccessToken) {
      // reintentar request con nuevo token
      headers.set("Authorization", `Bearer ${newAccessToken}`);
      response = await fetch(url, {
        ...options,
        headers,
      });
    } else {
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw new APIError("Sesión expirada", 401);
    }
  }

  // Response interceptor: mapea errores de API a APIError
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.detail || "Error en la solicitud",
      response.status,
      errorData
    );
  }

  return response.json();
}

export const apiClient = {
  get: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: "GET" }),

  post: <T>(endpoint: string, data?: any) =>
    apiRequest<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data?: any) =>
    apiRequest<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string) =>
    apiRequest<T>(endpoint, { method: "DELETE" }),

  // helper para login (guardar tokens)
  loging: async (email: string, password: string): Promise<TokenResponse> => {
    const data = await apiRequest<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    saveTokens(data.access_token, data.refresh_token);
    return data;
  },

  // helper para logout (limpia tokens)
  logout: () => {
    clearTokens();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  },
};
