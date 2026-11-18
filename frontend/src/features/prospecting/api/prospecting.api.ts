import { http } from '../../../lib/http'
import type { ProspectingSetup, ProspectingSetupInput } from '../prospecting.types'

export async function getProspectingSetup(signal?: AbortSignal) {
  return (await http.get<ProspectingSetup>('/prospecting/setup', { signal })).data
}

export async function saveProspectingSetup(data: ProspectingSetupInput, signal?: AbortSignal) {
  return (await http.put<ProspectingSetup>('/prospecting/setup', data, { signal })).data
}
