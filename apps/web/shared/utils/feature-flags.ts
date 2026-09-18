export function isFeatureEnabled(value: unknown): boolean {
  return value !== false && String(value).toLowerCase() !== 'false'
}
