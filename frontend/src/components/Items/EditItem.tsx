import { Pencil } from "lucide-react"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import { type ItemPublic, ItemsService } from "@/client"
import { FormDialog } from "@/components/Common/FormDialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

type FormData = { title: string; description?: string }

interface EditItemProps {
  item: ItemPublic
  onSuccess: () => void
}

const EditItem = ({ item, onSuccess }: EditItemProps) => {
  const { t } = useTranslation()

  const formSchema = useMemo(
    () =>
      z.object({
        title: z.string().min(1, { message: t("validations.titleRequired") }),
        description: z.string().optional(),
      }),
    [t],
  )

  return (
    <FormDialog<FormData, ItemPublic>
      trigger={(open) => (
        <DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={open}>
          <Pencil />
          {t("actions.edit")}
        </DropdownMenuItem>
      )}
      title={t("items:editDialog.title")}
      description={t("items:editDialog.description")}
      schema={formSchema}
      defaultValues={{
        title: item.title,
        description: item.description ?? undefined,
      }}
      mutationFn={(data) =>
        ItemsService.updateItem({ id: item.id, requestBody: data })
      }
      successMessage={t("items:updatedToast")}
      invalidate={["items"]}
      onSuccess={onSuccess}
    >
      {(form) => (
        <>
          <FormField
            control={form.control}
            name="title"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  {t("items:titleLabel")}{" "}
                  <span className="text-destructive">*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    placeholder={t("items:titlePlaceholder")}
                    type="text"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("items:descriptionLabel")}</FormLabel>
                <FormControl>
                  <Input
                    placeholder={t("items:descriptionPlaceholder")}
                    type="text"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </>
      )}
    </FormDialog>
  )
}

export default EditItem
