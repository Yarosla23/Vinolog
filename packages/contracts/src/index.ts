export const scanStatuses = ['matched', 'uncertain', 'not_found'] as const

export type ScanStatus = (typeof scanStatuses)[number]

export interface WineCard {
  slug: string
  name: string
  producer: string
  year: number | null
  category: string | null
  color: string | null
  region: string | null
  grapeVarieties: readonly string[]
  description: string | null
  servingTemperature: string | null
  imageUrl: string | null
}

export interface ScanCandidate {
  slug: string
  score: number
}

export interface ScanConfidence {
  kind: 'similarity' | 'calibrated_probability'
  top1Score: number
  margin: number
  calibratedProbability?: number
}

export interface ScanTiming {
  totalMs: number
  stages: Readonly<Record<string, number>>
}

export interface ScanVersion {
  model: string
  catalog: string
  configuration: string
}

export interface ScanResponse {
  status: ScanStatus
  wine: WineCard | null
  candidates: readonly ScanCandidate[]
  confidence: ScanConfidence
  timing: ScanTiming
  alternatives: readonly WineCard[]
  version: ScanVersion
  guidance?: string
  isMock: boolean
}

export interface SavedPairing {
  id: string
  wine: Pick<WineCard, 'slug' | 'name' | 'producer'>
  dish: string
  preference: 'softer' | 'richer'
  verdict: string
  savedAt: string
}
