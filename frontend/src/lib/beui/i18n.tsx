/* oxlint-disable react/only-export-components -- source-owned beUI module exports its provider and hooks together. */
import { createContext, useCallback, useContext, useMemo } from 'react'
import type { ReactNode } from 'react'

export type Messages = Record<string, string>
export type LocaleMessages = Record<string, Partial<Messages>>

type LocaleContextValue = { locale?: string; messages: LocaleMessages }
const NO_MESSAGES: LocaleMessages = {}
const LocaleContext = createContext<LocaleContextValue>({ messages: NO_MESSAGES })

export interface LocaleProviderProps {
  locale: string
  messages?: LocaleMessages
  children: ReactNode
}

export function LocaleProvider({ locale, messages = NO_MESSAGES, children }: LocaleProviderProps) {
  const value = useMemo(() => ({ locale, messages }), [locale, messages])
  return <LocaleContext.Provider value={value}>{children}</LocaleContext.Provider>
}

export function useMessages<T extends Messages>(namespace: string, defaults: T, labels?: Partial<T>) {
  const { messages } = useContext(LocaleContext)
  const provided = messages[namespace]
  const labelsKey = labels ? JSON.stringify(labels) : ''
  const stableLabels = useMemo(
    () => labelsKey ? JSON.parse(labelsKey) as Partial<T> : undefined,
    [labelsKey],
  )

  return useCallback(
    (key: keyof T & string) => stableLabels?.[key] ?? provided?.[key] ?? defaults[key],
    [defaults, provided, stableLabels],
  )
}
