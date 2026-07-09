import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { createFileRoute, redirect } from "@tanstack/react-router"
import type { PaginationState } from "@tanstack/react-table"
import { useState } from "react"

import { type UserPublic, UsersService } from "@/client"
import AddUser from "@/components/Admin/AddUser"
import { columns, type UserTableData } from "@/components/Admin/columns"
import { DataTable } from "@/components/Common/DataTable"
import PendingUsers from "@/components/Pending/PendingUsers"
import useAuth from "@/hooks/useAuth"

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
        title: "Admin - FastAPI Template",
      },
    ],
  }),
})

function Admin() {
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
          <h1 className="text-2xl font-bold tracking-tight">Users</h1>
          <p className="text-muted-foreground">
            Manage user accounts and permissions
          </p>
        </div>
        <AddUser />
      </div>

      {isLoading ? (
        <PendingUsers />
      ) : isError ? (
        <p className="text-muted-foreground">
          Unable to load users. Please try again.
        </p>
      ) : (
        <DataTable
          columns={columns}
          data={tableData}
          rowCount={data?.count ?? 0}
          pagination={pagination}
          onPaginationChange={setPagination}
        />
      )}
    </div>
  )
}
