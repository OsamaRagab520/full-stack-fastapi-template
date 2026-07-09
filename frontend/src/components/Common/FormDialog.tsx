import { zodResolver } from "@hookform/resolvers/zod"
import type { QueryKey } from "@tanstack/react-query"
import type { ReactNode } from "react"
import { useState } from "react"
import {
  type DefaultValues,
  type FieldValues,
  type Resolver,
  type UseFormReturn,
  useForm,
} from "react-hook-form"
import { useTranslation } from "react-i18next"
import type { ZodType } from "zod"

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
import { Form } from "@/components/ui/form"
import { LoadingButton } from "@/components/ui/loading-button"
import { useEntityMutation } from "@/hooks/useEntityMutation"

interface FormDialogProps<TFieldValues extends FieldValues, TData> {
  /**
   * Renders the element that opens the dialog. Receives `open`, so it works
   * both as a plain button (`<DialogTrigger>`-style) and as a
   * `DropdownMenuItem` (which opens from `onClick` while preventing the menu's
   * own `onSelect` close).
   */
  trigger: (open: () => void) => ReactNode
  title: string
  description: string
  /** Validation schema; also the standard `onBlur` / `criteriaMode: "all"` form config lives here. */
  schema: ZodType<TFieldValues>
  defaultValues: DefaultValues<TFieldValues>
  /** Submit-button label; defaults to `actions.save`. */
  submitLabel?: string
  /** Maps the validated form values to the request. Reshape to the API type here. */
  mutationFn: (data: TFieldValues) => Promise<TData>
  successMessage: string
  invalidate?: QueryKey | "all"
  /** Runs after the success toast (e.g. close the parent menu). */
  onSuccess?: () => void
  /** Renders the fields; receives the form so callers wire `FormField`s to `form.control`. */
  children: (form: UseFormReturn<TFieldValues>) => ReactNode
}

/**
 * A create/update dialog. Owns the open state, the react-hook-form wiring (the
 * shared `onBlur` / `criteriaMode` config + zod resolver), the dialog + form
 * shell, the Cancel/Save footer, and the success-toast / error / invalidation
 * policy (via `useEntityMutation`) — closing and resetting on success. Each
 * call site supplies only its schema, defaults, fields, trigger, and request.
 */
export function FormDialog<TFieldValues extends FieldValues, TData = unknown>({
  trigger,
  title,
  description,
  schema,
  defaultValues,
  submitLabel,
  mutationFn,
  successMessage,
  invalidate,
  onSuccess,
  children,
}: FormDialogProps<TFieldValues, TData>) {
  const { t } = useTranslation()
  const [isOpen, setIsOpen] = useState(false)

  const form = useForm<TFieldValues>({
    // zodResolver can't line up its input/output generics against an abstract
    // `ZodType<TFieldValues>`; one cast contains that here so call sites stay
    // fully typed (they pass a concrete `z.object(...)`).
    resolver: zodResolver(schema as never) as Resolver<TFieldValues>,
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues,
  })

  const mutation = useEntityMutation<TData, TFieldValues>({
    mutationFn,
    successMessage,
    invalidate,
    onSuccess: () => {
      setIsOpen(false)
      form.reset()
      onSuccess?.()
    },
  })

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      {trigger(() => setIsOpen(true))}
      <DialogContent className="sm:max-w-md">
        <Form {...form}>
          <form onSubmit={form.handleSubmit((data) => mutation.mutate(data))}>
            <DialogHeader>
              <DialogTitle>{title}</DialogTitle>
              <DialogDescription>{description}</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">{children(form)}</div>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline" disabled={mutation.isPending}>
                  {t("actions.cancel")}
                </Button>
              </DialogClose>
              <LoadingButton type="submit" loading={mutation.isPending}>
                {submitLabel ?? t("actions.save")}
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
