import { Pencil } from "lucide-react"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import { type UserPublic, UsersService } from "@/client"
import { FormDialog } from "@/components/Common/FormDialog"
import { Checkbox } from "@/components/ui/checkbox"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
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
  password?: string
  confirm_password?: string
  is_superuser?: boolean
  is_active?: boolean
}

interface EditUserProps {
  user: UserPublic
  onSuccess: () => void
}

const EditUser = ({ user, onSuccess }: EditUserProps) => {
  const { t } = useTranslation()

  const formSchema = useMemo(
    () =>
      z
        .object({
          email: z.email({ message: t("validations.emailInvalid") }),
          full_name: z.string().optional(),
          password: z
            .string()
            .min(8, { message: t("validations.passwordMinLength") })
            .optional()
            .or(z.literal("")),
          confirm_password: z.string().optional(),
          is_superuser: z.boolean().optional(),
          is_active: z.boolean().optional(),
        })
        .refine(
          (data) => !data.password || data.password === data.confirm_password,
          {
            message: t("validations.passwordsDontMatch"),
            path: ["confirm_password"],
          },
        ),
    [t],
  )

  return (
    <FormDialog<FormData, UserPublic>
      trigger={(open) => (
        <DropdownMenuItem onSelect={(e) => e.preventDefault()} onClick={open}>
          <Pencil />
          {t("actions.edit")}
        </DropdownMenuItem>
      )}
      title={t("users:editUser.dialogTitle")}
      description={t("users:editUser.description")}
      schema={formSchema}
      defaultValues={{
        email: user.email,
        full_name: user.full_name ?? undefined,
        is_superuser: user.is_superuser,
        is_active: user.is_active,
      }}
      mutationFn={({ confirm_password: _, ...body }) => {
        // Don't send an unchanged (empty) password.
        if (!body.password) {
          body.password = undefined
        }
        return UsersService.updateUser({ userId: user.id, requestBody: body })
      }}
      successMessage={t("users:editUser.updatedToast")}
      invalidate={["users"]}
      onSuccess={onSuccess}
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
                <FormLabel>{t("users:addUser.setPassword")}</FormLabel>
                <FormControl>
                  <Input
                    placeholder={t("users:addUser.passwordLabel")}
                    type="password"
                    {...field}
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
                <FormLabel>{t("users:addUser.confirmPasswordLabel")}</FormLabel>
                <FormControl>
                  <Input
                    placeholder={t("users:addUser.passwordLabel")}
                    type="password"
                    {...field}
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

export default EditUser
