import type { QueryKey } from "@tanstack/react-query"
import type { ReactNode } from "react"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { LoadingButton } from "@/components/ui/loading-button"
import { useEntityMutation } from "@/hooks/useEntityMutation"

interface ConfirmDialogProps<TData> {
  /**
   * Renders the element that opens the dialog. Receives `open`, so it works
   * both as a plain button and as a `DropdownMenuItem` (which must call `open`
   * from its `onClick` while preventing the menu's own `onSelect` close).
   */
  trigger: (open: () => void) => ReactNode
  title: string
  description: string
  /** Label for the confirm button (already translated). */
  confirmLabel: string
  /** Confirm-button style; defaults to `destructive` (the common case). */
  confirmVariant?: React.ComponentProps<typeof Button>["variant"]
  /** The action to run on confirm. */
  mutationFn: () => Promise<TData>
  successMessage: string
  invalidate?: QueryKey | "all"
  /** Runs after the success toast (e.g. close the parent menu, log out, …). */
  onSuccess?: () => void
}

/**
 * A confirm-then-mutate dialog. Owns the open state, the dialog shell, the
 * Cancel/confirm footer, and the success-toast / error / invalidation policy
 * (via `useEntityMutation`), so each call site only supplies the copy, the
 * action, and where to invalidate.
 */
export function ConfirmDialog<TData = unknown>({
  trigger,
  title,
  description,
  confirmLabel,
  confirmVariant = "destructive",
  mutationFn,
  successMessage,
  invalidate,
  onSuccess,
}: ConfirmDialogProps<TData>) {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)

  const mutation = useEntityMutation<TData, void>({
    mutationFn,
    successMessage,
    invalidate,
    onSuccess: () => {
      setIsOpen(false)
      onSuccess?.()
    },
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      {trigger(() => setIsOpen(true))}
      <DialogContent className="sm:max-w-md">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            mutation.mutate()
          }}
        >
          <DialogHeader>
            <DialogTitle>{title}</DialogTitle>
            <DialogDescription>{description}</DialogDescription>
          </DialogHeader>

          <DialogFooter className="mt-4">
            <DialogClose asChild>
              <Button variant="outline" disabled={mutation.isPending}>
                {t("actions.cancel")}
              </Button>
            </DialogClose>
            <LoadingButton
              variant={confirmVariant}
              type="submit"
              loading={mutation.isPending}
            >
              {confirmLabel}
            </LoadingButton>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
