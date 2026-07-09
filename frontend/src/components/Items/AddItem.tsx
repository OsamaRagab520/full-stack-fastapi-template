import { Plus } from "lucide-react"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import { type ItemCreate, ItemsService } from "@/client"
import { FormDialog } from "@/components/Common/FormDialog"
import { Button } from "@/components/ui/button"
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

type FormData = { title: string; description?: string }

const AddItem = () => {
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
    <FormDialog<FormData, ItemCreate>
      trigger={(open) => (
        <Button className="my-4" onClick={open}>
          <Plus className="me-2" />
          {t("items:add")}
        </Button>
      )}
      title={t("items:addDialog.title")}
      description={t("items:addDialog.description")}
      schema={formSchema}
      defaultValues={{ title: "", description: "" }}
      mutationFn={(data) => ItemsService.createItem({ requestBody: data })}
      successMessage={t("items:createdToast")}
      invalidate={["items"]}
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
                    required
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

export default AddItem
