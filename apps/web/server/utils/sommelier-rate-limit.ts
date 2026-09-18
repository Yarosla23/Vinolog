interface SessionWindow {
  count: number
  resetsAt: number
}

const WINDOW_MS = 10 * 60 * 1000
const windows = new Map<string, SessionWindow>()

export function consumeSommelierRequest(sessionId: string, limit: number): boolean {
  const now = Date.now()

  if (windows.size > 1_000) {
    for (const [id, window] of windows) {
      if (window.resetsAt <= now) windows.delete(id)
    }
  }

  const current = windows.get(sessionId)

  if (!current || current.resetsAt <= now) {
    windows.set(sessionId, { count: 1, resetsAt: now + WINDOW_MS })
    return true
  }

  if (current.count >= limit) {
    return false
  }

  current.count += 1
  return true
}
