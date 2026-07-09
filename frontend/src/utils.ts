import { AxiosError } from "axios"
import type { ApiError } from "./client"
import i18n from "./i18n"

function extractErrorMessage(err: Error): string {
  if (err instanceof AxiosError) {
    return err.message
  }

  const body = (err as ApiError).body as
    | { detail?: string | { msg: string }[] }
    | null
    | undefined
  const errDetail = body?.detail
  if (Array.isArray(errDetail) && errDetail.length > 0) {
    return errDetail[0].msg
  }
  return (errDetail as string | undefined) || i18n.t("toast.fallback")
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
