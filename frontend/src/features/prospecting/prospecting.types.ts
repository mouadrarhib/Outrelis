export type OfferProfile = {
  id: string
  service_name: string
  outreach_language: string
  is_default: boolean
  created_at: string
  updated_at: string
}

export type SearchDraftLocation = {
  id: string
  location_query: string
  position: number
}

export type SearchDraft = {
  id: string
  offer_profile_id: string
  business_category: string
  result_limit_per_location: number | null
  locations: SearchDraftLocation[]
  created_at: string
  updated_at: string
}

export type ProspectingSetup = {
  configured: boolean
  offer_profile: OfferProfile | null
  search_draft: SearchDraft | null
}

export type ProspectingSetupInput = {
  service_name: string
  outreach_language: string
  business_category: string
  locations: string[]
  result_limit_per_location: number | null
}
