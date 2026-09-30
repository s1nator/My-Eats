const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "";

function errorMessage(payload, fallback) {
  if (typeof payload?.detail === "string") {
    return payload.detail;
  }
  if (typeof payload?.detail?.message === "string") {
    return payload.detail.message;
  }
  return fallback;
}

async function request(path, options = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });
  const payload = response.status === 204 ? null : await response.json();

  if (!response.ok) {
    throw new Error(errorMessage(payload, "Не удалось выполнить запрос"));
  }

  return payload;
}

function queryString(params) {
  const query = new URLSearchParams();

  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, String(value));
    }
  }

  const value = query.toString();
  return value ? `?${value}` : "";
}

export function getMenu(params = {}) {
  return request(`/api/v1/menu${queryString(params)}`);
}

export function createOrder(payload) {
  return request("/api/v1/orders", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getOrders(status) {
  return request(`/api/v1/orders${queryString({ status })}`);
}

export function changeOrderStatus(orderId, status) {
  return request(`/api/v1/orders/${orderId}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function cancelOrder(orderId) {
  return request(`/api/v1/orders/${orderId}`, {
    method: "DELETE",
  });
}
