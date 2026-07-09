import { useEffect } from "react"
import { useTranslation } from "react-i18next"

/**
 * Keep `<html lang>` and `<html dir>` in sync with the active i18next language,
 * so RTL languages (e.g. ar) flip the layout via Tailwind logical properties.
 */
export function useLanguageDirection() {
  const { i18n } = useTranslation()

  useEffect(() => {
    const apply = (lng: string) => {
      document.documentElement.lang = lng
      document.documentElement.dir = i18n.dir(lng)
    }
    apply(i18n.language)
    i18n.on("languageChanged", apply)
    return () => {
      i18n.off("languageChanged", apply)
    }
  }, [i18n])
}
