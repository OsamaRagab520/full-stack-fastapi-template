import { Trash2 } from "lucide-react"
import { useTranslation } from "react-i18next"

import { ItemsService } from "@/client"
import { ConfirmDialog } from "@/components/Common/ConfirmDialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"

interface DeleteItemProps {
  id: string
  onSuccess: () => void
}

const DeleteItem = ({ id, onSuccess }: DeleteItemProps) => {
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
          {t("items:delete")}
        </DropdownMenuItem>
      )}
      title={t("items:delete")}
      description={t("items:deleteWarning")}
      confirmLabel={t("actions.delete")}
      mutationFn={() => ItemsService.deleteItem({ id })}
      successMessage={t("items:deletedToast")}
      invalidate="all"
      onSuccess={onSuccess}
    />
  )
}

export default DeleteItem
