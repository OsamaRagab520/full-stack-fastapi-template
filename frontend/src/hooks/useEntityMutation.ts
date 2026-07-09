import {
  type QueryKey,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query"

import { handleError } from "@/utils"
import useCustomToast from "./useCustomToast"

interface UseEntityMutationOptions<TData, TVariables> {
  mutationFn: (variables: TVariables) => Promise<TData>
  /** Toast shown when the mutation succeeds. */
  successMessage: string
  /**
   * Which queries to refetch once the mutation settles: a `QueryKey` refetches
   * just that key, `"all"` refetches every query, and omitting it skips
   * invalidation entirely.
   */
  invalidate?: QueryKey | "all"
  /** Caller cleanup after the success toast (close the dialog, reset the form, …). */
  onSuccess?: (data: TData) => void
}

/**
 * Wraps `useMutation` with the success-toast / error-handling / cache-invalidation
 * policy shared by every create/update/delete dialog, so each call site only
 * supplies what actually varies: the request, the success message, and any cleanup.
 */
export function useEntityMutation<TData = unknown, TVariables = void>({
  mutationFn,
  successMessage,
  invalidate,
  onSuccess,
}: UseEntityMutationOptions<TData, TVariables>) {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  return useMutation({
    mutationFn,
    onSuccess: (data) => {
      showSuccessToast(successMessage)
      onSuccess?.(data)
    },
    onError: (err) => handleError(err, showErrorToast),
    onSettled: invalidate
      ? () =>
          queryClient.invalidateQueries(
            invalidate === "all" ? undefined : { queryKey: invalidate },
          )
      : undefined,
  })
}
