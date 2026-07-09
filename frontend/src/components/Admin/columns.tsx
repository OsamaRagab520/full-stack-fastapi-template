import type { ColumnDef } from "@tanstack/react-table"
import type { TFunction } from "i18next"

import type { UserPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { UserActionsMenu } from "./UserActionsMenu"

export type UserTableData = UserPublic & {
  isCurrentUser: boolean
}

export const getColumns = (t: TFunction): ColumnDef<UserTableData>[] => [
  {
    accessorKey: "full_name",
    header: t("users:admin.columns.fullName"),
    cell: ({ row }) => {
      const fullName = row.original.full_name
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn("font-medium", !fullName && "text-muted-foreground")}
          >
            {fullName || t("na")}
          </span>
          {row.original.isCurrentUser && (
            <Badge variant="outline" className="text-xs">
              {t("actions.you")}
            </Badge>
          )}
        </div>
      )
    },
  },
  {
    accessorKey: "email",
    header: t("users:admin.columns.email"),
    cell: ({ row }) => (
      <span className="text-muted-foreground">{row.original.email}</span>
    ),
  },
  {
    accessorKey: "is_superuser",
    header: t("users:admin.columns.role"),
    cell: ({ row }) => (
      <Badge variant={row.original.is_superuser ? "default" : "secondary"}>
        {row.original.is_superuser
          ? t("users:admin.roleSuperuser")
          : t("users:admin.roleUser")}
      </Badge>
    ),
  },
  {
    accessorKey: "is_active",
    header: t("users:admin.columns.status"),
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "size-2 rounded-full",
            row.original.is_active ? "bg-green-500" : "bg-gray-400",
          )}
        />
        <span className={row.original.is_active ? "" : "text-muted-foreground"}>
          {row.original.is_active
            ? t("users:admin.statusActive")
            : t("users:admin.statusInactive")}
        </span>
      </div>
    ),
  },
  {
    id: "actions",
    header: () => (
      <span className="sr-only">{t("users:admin.columns.actions")}</span>
    ),
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu user={row.original} />
      </div>
    ),
  },
]
