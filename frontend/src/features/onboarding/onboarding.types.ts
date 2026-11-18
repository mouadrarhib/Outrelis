export type StartingPath = 'find_first_leads' | 'grow_pipeline'

export interface OnboardingState {
  starting_path: StartingPath | null
  completed: boolean
  completed_at: string | null
  updated_at: string | null
}
