import { describe, expect, it } from 'vitest'
import { MAX_SCAN_FILE_SIZE, validateScanFile } from './scan-file'

describe('validateScanFile', () => {
  it('accepts supported images within the limit', () => {
    expect(validateScanFile({ type: 'image/jpeg', size: 1_024 })).toBeNull()
  })

  it('rejects unsupported formats', () => {
    expect(validateScanFile({ type: 'image/gif', size: 1_024 })).toContain('JPEG')
  })

  it('rejects images larger than the limit', () => {
    expect(validateScanFile({ type: 'image/png', size: MAX_SCAN_FILE_SIZE + 1 })).toContain('10 МБ')
  })
})
