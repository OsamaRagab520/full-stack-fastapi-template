import i18n from "i18next"
import LanguageDetector from "i18next-browser-languagedetector"
import { initReactI18next } from "react-i18next"

import arAuth from "./locales/ar/auth.json"
import arCommon from "./locales/ar/common.json"
import arItems from "./locales/ar/items.json"
import arUsers from "./locales/ar/users.json"
import enAuth from "./locales/en/auth.json"
import enCommon from "./locales/en/common.json"
import enItems from "./locales/en/items.json"
import enUsers from "./locales/en/users.json"

export const DEFAULT_LANGUAGE = "en"
export const SUPPORTED_LANGUAGES = ["en", "ar"] as const
export type AppLanguage = (typeof SUPPORTED_LANGUAGES)[number]

/** Language metadata for the switcher (label + direction). */
export const LANGUAGES: { code: AppLanguage; label: string }[] = [
  { code: "en", label: "English" },
  { code: "ar", label: "العربية" },
]

void i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { common: enCommon, auth: enAuth, items: enItems, users: enUsers },
      ar: { common: arCommon, auth: arAuth, items: arItems, users: arUsers },
    },
    fallbackLng: DEFAULT_LANGUAGE,
    supportedLngs: [...SUPPORTED_LANGUAGES],
    ns: ["common", "auth", "items", "users"],
    defaultNS: "common",
    detection: {
      order: ["cookie", "navigator"],
      lookupCookie: "lang",
      caches: ["cookie"],
      cookieMinutes: 525600, // 1 year
    },
    interpolation: { escapeValue: false },
  })

export default i18n
