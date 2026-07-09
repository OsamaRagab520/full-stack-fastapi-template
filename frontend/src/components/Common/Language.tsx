import { Languages } from "lucide-react"
import { useTranslation } from "react-i18next"

import { UsersService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"
import i18n, { type AppLanguage, LANGUAGES } from "@/i18n"
import { tokenStore } from "@/lib/tokenStore"

async function changeLanguage(code: AppLanguage) {
  await i18n.changeLanguage(code)
  // Persist to the user profile when authenticated (drives localized emails).
  if (tokenStore.isAuthenticated()) {
    void UsersService.updateUserMe({ requestBody: { locale: code } }).catch(
      () => {},
    )
  }
}

export const SidebarLanguage = () => {
  const { isMobile } = useSidebar()
  const { t } = useTranslation()

  return (
    <SidebarMenuItem>
      <DropdownMenu modal={false}>
        <DropdownMenuTrigger asChild>
          <SidebarMenuButton
            tooltip={t("language.title")}
            data-testid="language-button"
          >
            <Languages className="size-4 text-muted-foreground" />
            <span>{t("language.title")}</span>
            <span className="sr-only">{t("language.change")}</span>
          </SidebarMenuButton>
        </DropdownMenuTrigger>
        <DropdownMenuContent
          side={isMobile ? "top" : "right"}
          align="end"
          className="w-(--radix-dropdown-menu-trigger-width) min-w-56"
        >
          {LANGUAGES.map((l) => (
            <DropdownMenuItem
              key={l.code}
              data-testid={`language-${l.code}`}
              onClick={() => void changeLanguage(l.code)}
            >
              {l.label}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </SidebarMenuItem>
  )
}

export const Language = () => {
  const { t } = useTranslation()

  return (
    <div className="flex items-center justify-center">
      <DropdownMenu modal={false}>
        <DropdownMenuTrigger asChild>
          <Button data-testid="language-button" variant="outline" size="icon">
            <Languages className="h-[1.2rem] w-[1.2rem]" />
            <span className="sr-only">{t("language.change")}</span>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          {LANGUAGES.map((l) => (
            <DropdownMenuItem
              key={l.code}
              onClick={() => void changeLanguage(l.code)}
            >
              {l.label}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
