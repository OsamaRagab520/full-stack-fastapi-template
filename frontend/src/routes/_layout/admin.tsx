import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import type { PaginationState } from "@tanstack/react-table"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { type UserPublic, UsersService } from "@/client"
import AddUser from "@/components/Admin/AddUser"
import { getColumns, type UserTableData } from "@/components/Admin/columns"
import { DataTable } from "@/components/Common/DataTable"
import PendingUsers from "@/components/Pending/PendingUsers"
import useAuth from "@/hooks/useAuth"
import i18n from "@/i18n"

function getUsersQueryOptions({ pageIndex, pageSize }: PaginationState) {
  return {
    queryFn: () =>
      UsersService.readUsers({ skip: pageIndex * pageSize, limit: pageSize }),
    queryKey: ["users", { pageIndex, pageSize }],
    placeholderData: keepPreviousData,
  }
}

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  beforeLoad: async () => {
    const user = await UsersService.readUserMe()
    if (!user.is_superuser) {
      throw redirect({
        to: "/",
      })
    }
  },
  head: () => ({
    meta: [
      {
        title: i18n.t("users:admin.metaTitle"),
      },
    ],
  }),
})

function Admin() {
  const { t } = useTranslation()
  const { user: currentUser } = useAuth()
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  })
  const { data, isLoading, isError } = useQuery(
    getUsersQueryOptions(pagination),
  )

  const tableData: UserTableData[] =
    data?.data.map((user: UserPublic) => ({
      ...user,
      isCurrentUser: currentUser?.id === user.id,
    })) ?? []

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            {t("users:admin.heading")}
          </h1>
          <p className="text-muted-foreground">{t("users:admin.subtitle")}</p>
        </div>
        <AddUser />
      </div>

      {isLoading ? (
        <PendingUsers />
      ) : isError ? (
        <p className="text-muted-foreground">{t("users:admin.loadError")}</p>
      ) : (
        <DataTable
          columns={getColumns(t)}
          data={tableData}
          rowCount={data?.count ?? 0}
          pagination={pagination}
          onPaginationChange={setPagination}
        />
      )}
    </div>
  )
}
