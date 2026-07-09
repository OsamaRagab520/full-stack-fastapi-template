import { Plus } from "lucide-react"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import { type UserPublic, UsersService } from "@/client"
import { FormDialog } from "@/components/Common/FormDialog"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

type FormData = {
  email: string
  full_name?: string
  password: string
  confirm_password: string
  is_superuser: boolean
  is_active: boolean
}

const AddUser = () => {
  const { t } = useTranslation()

  const formSchema = useMemo(
    () =>
      z
        .object({
          email: z.email({ message: t("validations.emailInvalid") }),
          full_name: z.string().optional(),
          password: z
            .string()
            .min(1, { message: t("validations.passwordRequired") })
            .min(8, { message: t("validations.passwordMinLength") }),
          confirm_password: z
            .string()
            .min(1, { message: t("validations.passwordConfirmRequired") }),
          is_superuser: z.boolean(),
          is_active: z.boolean(),
        })
        .refine((data) => data.password === data.confirm_password, {
          message: t("validations.passwordsDontMatch"),
          path: ["confirm_password"],
        }),
    [t],
  )

  return (
    <FormDialog<FormData, UserPublic>
      trigger={(open) => (
        <Button className="my-4" onClick={open}>
          <Plus className="me-2" />
          {t("users:admin.add")}
        </Button>
      )}
      title={t("users:addUser.dialogTitle")}
      description={t("users:addUser.description")}
      schema={formSchema}
      defaultValues={{
        email: "",
        full_name: "",
        password: "",
        confirm_password: "",
        is_superuser: false,
        is_active: false,
      }}
      mutationFn={({ confirm_password: _, ...body }) =>
        UsersService.createUser({ requestBody: body })
      }
      successMessage={t("users:addUser.createdToast")}
      invalidate={["users"]}
    >
      {(form) => (
        <>
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  {t("users:addUser.emailLabel")}{" "}
                  <span className="text-destructive">*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    placeholder={t("users:addUser.emailLabel")}
                    type="email"
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
            name="full_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("users:addUser.fullNameLabel")}</FormLabel>
                <FormControl>
                  <Input
                    placeholder={t("users:addUser.fullNameLabel")}
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
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  {t("users:addUser.setPassword")}{" "}
                  <span className="text-destructive">*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    placeholder={t("users:addUser.passwordLabel")}
                    type="password"
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
            name="confirm_password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  {t("users:addUser.confirmPasswordLabel")}{" "}
                  <span className="text-destructive">*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    placeholder={t("users:addUser.passwordLabel")}
                    type="password"
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
            name="is_superuser"
            render={({ field }) => (
              <FormItem className="flex items-center gap-3 space-y-0">
                <FormControl>
                  <Checkbox
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </FormControl>
                <FormLabel className="font-normal">
                  {t("users:addUser.isSuperuser")}
                </FormLabel>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="is_active"
            render={({ field }) => (
              <FormItem className="flex items-center gap-3 space-y-0">
                <FormControl>
                  <Checkbox
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </FormControl>
                <FormLabel className="font-normal">
                  {t("users:addUser.isActive")}
                </FormLabel>
              </FormItem>
            )}
          />
        </>
      )}
    </FormDialog>
  )
}

export default AddUser
