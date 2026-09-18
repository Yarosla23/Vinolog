import { describe, expect, it } from 'vitest'

import {
  createSommelierModel,
  isSommelierProviderId,
  SommelierConfigurationError,
} from './sommelier-provider'

describe('sommelier provider config', () => {
  it('accepts only supported provider ids', () => {
    expect(isSommelierProviderId('openai')).toBe(true)
    expect(isSommelierProviderId('anthropic')).toBe(true)
    expect(isSommelierProviderId('google')).toBe(true)
    expect(isSommelierProviderId('unknown')).toBe(false)
  })

  it('rejects a live provider without its server key', () => {
    expect(() => createSommelierModel({
      provider: 'openai',
      model: '',
      apiKey: '',
    })).toThrow(SommelierConfigurationError)
  })

  it.each(['openai', 'anthropic', 'google'] as const)(
    'uses the shared key for the %s adapter',
    (provider) => {
      const result = createSommelierModel({ provider, model: '', apiKey: 'test-key' })

      expect(result.id).toBe(provider)
      expect(result.model).toBeDefined()
    },
  )

  it('uses the current Google model by default', () => {
    const result = createSommelierModel({ provider: 'google', model: '', apiKey: 'test-key' })

    expect(result.modelId).toBe('gemini-3.1-flash-lite')
  })
})
