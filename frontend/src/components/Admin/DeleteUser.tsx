import { Trash2 } from "lucide-react"
import { useTranslation } from "react-i18next"

import { UsersService } from "@/client"
import { ConfirmDialog } from "@/components/Common/ConfirmDialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"

interface DeleteUserProps {
  id: string
  onSuccess: () => void
}

const DeleteUser = ({ id, onSuccess }: DeleteUserProps) => {
  const { t } = useTranslation()

  return (
    <ConfirmDialog
      trigger={(open) => (
        <DropdownMenuItem
          variant="destructive"
          onSelect={(e) => e.preventDefault()}
          onClick={open}
        >
          <Trash2 />
          {t("users:deleteUser.title")}
        </DropdownMenuItem>
      )}
      title={t("users:deleteUser.title")}
      description={t("users:deleteUser.warning")}
      confirmLabel={t("actions.delete")}
      mutationFn={() => UsersService.deleteUser({ userId: id })}
      successMessage={t("users:deleteUser.deletedToast")}
      invalidate="all"
      onSuccess={onSuccess}
    />
  )
}

export default DeleteUser
