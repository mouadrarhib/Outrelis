import { http } from '../../../lib/http'
import type { OnboardingState, StartingPath } from '../onboarding.types'

export async function getOnboardingState(signal?: AbortSignal) {
  return (await http.get<OnboardingState>('/onboarding', { signal })).data
}

export async function saveStartingPath(startingPath: StartingPath, signal?: AbortSignal) {
  return (await http.put<OnboardingState>(
    '/onboarding/starting-path',
    { starting_path: startingPath },
    { signal },
  )).data
}
