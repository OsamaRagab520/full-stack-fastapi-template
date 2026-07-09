import { AxiosError } from "axios"
import { ApiError, type ValidationError } from "./client"
import i18n from "./i18n"

// FastAPI error bodies are `{ detail: string }` for domain errors and
// `{ detail: ValidationError[] }` for 422s. `ApiError.body` is typed `unknown`,
// so narrow it here instead of trusting a cast that silently rots on client
// regeneration.
function extractErrorMessage(err: Error): string {
  if (err instanceof AxiosError) {
    return err.message
  }
  if (err instanceof ApiError && isDetailBody(err.body)) {
    const { detail } = err.body
    if (typeof detail === "string") {
      return detail
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return (detail[0] as ValidationError).msg
    }
  }
  return i18n.t("toast.fallback")
}

function isDetailBody(body: unknown): body is { detail?: unknown } {
  return typeof body === "object" && body !== null && "detail" in body
}

export const handleError = (
  err: Error,
  showErrorToast: (msg: string) => void,
): void => {
  showErrorToast(extractErrorMessage(err))
}

export const getInitials = (name: string): string => {
  return name
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase()
}
