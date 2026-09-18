export function sampleRandomItems<T>(
  items: readonly T[],
  count: number,
  random: () => number = Math.random,
): T[] {
  const shuffled = [...items]

  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(random() * (index + 1))
    const current = shuffled[index]
    const replacement = shuffled[swapIndex]

    if (current === undefined || replacement === undefined) {
      continue
    }

    shuffled[index] = replacement
    shuffled[swapIndex] = current
  }

  return shuffled.slice(0, Math.max(0, count))
}
