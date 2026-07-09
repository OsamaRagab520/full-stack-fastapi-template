import { useTranslation } from "react-i18next"

import { UsersService } from "@/client"
import { ConfirmDialog } from "@/components/Common/ConfirmDialog"
import { Button } from "@/components/ui/button"
import useAuth from "@/hooks/useAuth"

const DeleteConfirmation = () => {
  const { t } = useTranslation()
  const { logout } = useAuth()

  return (
    <ConfirmDialog
      trigger={(open) => (
        <Button variant="destructive" className="mt-3" onClick={open}>
          {t("users:deleteAccount.title")}
        </Button>
      )}
      title={t("users:deleteConfirmation.title")}
      description={t("users:deleteConfirmation.warning")}
      confirmLabel={t("actions.delete")}
      mutationFn={() => UsersService.deleteUserMe()}
      successMessage={t("users:deleteConfirmation.deletedToast")}
      invalidate={["currentUser"]}
      onSuccess={logout}
    />
  )
}

export default DeleteConfirmation
