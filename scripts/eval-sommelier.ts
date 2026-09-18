#!/usr/bin/env node

import { randomUUID } from 'node:crypto'

import { sommelierAdversarialCases } from '../apps/web/server/fixtures/sommelier-adversarial.ts'

const baseUrl = (process.env.SOMMELIER_EVAL_BASE_URL || 'http://127.0.0.1:3000').replace(/\/$/, '')
let failures = 0

for (const testCase of sommelierAdversarialCases) {
  try {
    const response = await fetch(`${baseUrl}/api/sommelier/chat`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({
        sessionId: randomUUID(),
        messages: [{ role: 'user', content: testCase.prompt }],
      }),
    })

    if (!response.ok) {
      failures += 1
      console.error(`FAIL ${testCase.name}: HTTP ${response.status}`)
      continue
    }

    const result: unknown = await response.json()
    const actual = getOutcome(result)
    if (actual === testCase.expected) {
      console.log(`PASS ${testCase.name}: ${actual}`)
    }
    else {
      failures += 1
      console.error(`FAIL ${testCase.name}: expected ${testCase.expected}, got ${actual}`)
    }
  }
  catch (error) {
    failures += 1
    const name = error instanceof Error ? error.name : 'UnknownError'
    console.error(`FAIL ${testCase.name}: ${name}`)
  }
}

if (failures) {
  console.error(`Sommelier eval failed: ${failures} case(s).`)
  process.exitCode = 1
}
else {
  console.log(`Sommelier eval passed: ${sommelierAdversarialCases.length} case(s).`)
}

function getOutcome(value: unknown): string {
  if (!value || typeof value !== 'object') return 'invalid_response'
  if (!('status' in value) || typeof value.status !== 'string') return 'invalid_response'
  if (value.status === 'answered') return 'answered'
  if ('blockReason' in value && typeof value.blockReason === 'string') return value.blockReason
  return 'invalid_response'
}
