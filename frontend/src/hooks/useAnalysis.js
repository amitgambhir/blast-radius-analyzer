import { useState, useCallback } from 'react'

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')


function buildApiUrl(path) {
  return API_BASE_URL ? `${API_BASE_URL}${path}` : path
}

export function useAnalysis() {
  const [status, setStatus] = useState('idle') // idle | streaming | complete | error
  const [passes, setPasses] = useState([])
  const [currentPass, setCurrentPass] = useState(null)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const startAnalysis = useCallback(async (formData) => {
    setStatus('streaming')
    setPasses([])
    setCurrentPass(null)
    setResult(null)
    setError(null)

    try {
      const response = await fetch(buildApiUrl('/api/analyze/stream'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        const text = await response.text()
        throw new Error(`API error ${response.status}: ${text}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          if (!raw) continue
          try {
            const event = JSON.parse(raw)
            handleEvent(event, setCurrentPass, setPasses, setResult, setStatus, setError)
          } catch {
            // skip malformed lines
          }
        }
      }
    } catch (err) {
      setError(err.message)
      setStatus('error')
    }
  }, [])

  const reset = useCallback(() => {
    setStatus('idle')
    setPasses([])
    setCurrentPass(null)
    setResult(null)
    setError(null)
  }, [])

  return { status, passes, currentPass, result, error, startAnalysis, reset }
}

function handleEvent(event, setCurrentPass, setPasses, setResult, setStatus, setError) {
  switch (event.type) {
    case 'progress':
      setCurrentPass({ pass: event.pass, total: event.total, message: event.message })
      break
    case 'pass_complete':
      setPasses(prev => [...prev, { pass: event.pass, name: event.name, summary: event.summary }])
      setCurrentPass(null)
      break
    case 'result':
      setResult(event.data)
      break
    case 'complete':
      setStatus('complete')
      break
    case 'error':
      setError(event.message)
      setStatus('error')
      break
    default:
      break
  }
}
