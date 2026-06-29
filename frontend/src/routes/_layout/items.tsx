import { keepPreviousData, useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import type { PaginationState } from "@tanstack/react-table"
import { Search } from "lucide-react"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { ItemsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import AddItem from "@/components/Items/AddItem"
import { getColumns } from "@/components/Items/columns"
import PendingItems from "@/components/Pending/PendingItems"
import i18n from "@/i18n"

function getItemsQueryOptions({ pageIndex, pageSize }: PaginationState) {
  return {
    queryFn: () =>
      ItemsService.readItems({ skip: pageIndex * pageSize, limit: pageSize }),
    queryKey: ["items", { pageIndex, pageSize }],
    placeholderData: keepPreviousData,
  }
}

export const Route = createFileRoute("/_layout/items")({
  component: Items,
  head: () => ({
    meta: [
      {
        title: i18n.t("items:metaTitle"),
      },
    ],
  }),
})

function Items() {
  const { t } = useTranslation()
  const [pagination, setPagination] = useState<PaginationState>({
    pageIndex: 0,
    pageSize: 10,
  })
  const { data, isLoading, isError } = useQuery(
    getItemsQueryOptions(pagination),
  )

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            {t("items:heading")}
          </h1>
          <p className="text-muted-foreground">{t("items:subtitle")}</p>
        </div>
        <AddItem />
      </div>

      {isLoading ? (
        <PendingItems />
      ) : isError ? (
        <p className="text-muted-foreground">{t("items:loadError")}</p>
      ) : data && data.count === 0 ? (
        <div className="flex flex-col items-center justify-center text-center py-12">
          <div className="rounded-full bg-muted p-4 mb-4">
            <Search className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold">{t("items:empty")}</h3>
          <p className="text-muted-foreground">{t("items:emptyHint")}</p>
        </div>
      ) : (
        <DataTable
          columns={getColumns(t)}
          data={data?.data ?? []}
          rowCount={data?.count ?? 0}
          pagination={pagination}
          onPaginationChange={setPagination}
        />
      )}
    </div>
  )
}
