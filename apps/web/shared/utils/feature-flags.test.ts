import { describe, expect, it } from 'vitest'
import { isFeatureEnabled } from './feature-flags'

describe('isFeatureEnabled', () => {
  it.each([false, 'false', 'FALSE'])('disables a feature for %s', (value) => {
    expect(isFeatureEnabled(value)).toBe(false)
  })

  it.each([true, 'true', undefined])('keeps a feature enabled for %s', (value) => {
    expect(isFeatureEnabled(value)).toBe(true)
  })
})
