import axios from "axios";

/**
 * Extracts a human-friendly error message from an API/Axios error or generic Error.
 * Maps status codes accurately:
 * - 400 -> backend detail or bad request message
 * - 401 -> "Invalid email or password" (or provided detail)
 * - 409 -> backend detail or conflict message
 * - 422 -> formatted validation error message
 * - 500+ -> "Server error. Please try again."
 * - Network / CORS error -> "Unable to connect to the backend."
 */
export function getApiErrorMessage(error: unknown, fallbackMessage: string): string {
  if (axios.isAxiosError(error)) {
    // Network errors, connection refused, CORS errors
    if (!error.response) {
      if (error.code === "ERR_NETWORK" || error.message?.includes("Network Error")) {
        return "Unable to connect to the backend.";
      }
      return error.message || "Unable to connect to the backend.";
    }

    const status = error.response.status;
    const data = error.response.data;

    // Parse backend detail if available
    let backendDetail = "";
    if (data) {
      if (typeof data === "string") {
        backendDetail = data;
      } else if (typeof data.detail === "string") {
        backendDetail = data.detail;
      } else if (Array.isArray(data.detail)) {
        // Pydantic 422 validation errors: array of { loc, msg, type }
        const details = data.detail
          .map((item: any) => {
            if (typeof item === "string") return item;
            const field = Array.isArray(item?.loc) ? item.loc[item.loc.length - 1] : "";
            const msg = item?.msg || JSON.stringify(item);
            return field ? `${field}: ${msg}` : msg;
          })
          .join(", ");
        backendDetail = details ? `Validation error (${details})` : "Validation error";
      } else if (data.message && typeof data.message === "string") {
        backendDetail = data.message;
      }
    }

    if (status === 400) {
      return backendDetail || fallbackMessage;
    }
    if (status === 401) {
      return backendDetail || "Invalid email or password";
    }
    if (status === 409) {
      return backendDetail || "Account or resource conflict. Please try again.";
    }
    if (status === 422) {
      return backendDetail || "Invalid form data. Please check your inputs.";
    }
    if (status >= 500) {
      return "Server error. Please try again.";
    }

    if (backendDetail) {
      return backendDetail;
    }
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallbackMessage;
}
