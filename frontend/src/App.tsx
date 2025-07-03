import React, { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [response, setResponse] = useState<string>('')
  const [error, setError] = useState<string>('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim()) return

    setIsLoading(true)
    setError('')
    setResponse('')
    
    try {
      const response = await fetch('/api/parse-doc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setResponse(JSON.stringify(data, null, 2))
    } catch (error) {
      console.error('Integration failed:', error)
      setError(error instanceof Error ? error.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Open Integration Agent</h1>
        <p>AI-Powered Data Integration</p>
      </header>
      <main>
        <div className="home">
          <div className="container">
            <h2>Start Your Integration</h2>
            <p>Paste the URL of any API documentation page to begin.</p>
            
            <form onSubmit={handleSubmit} className="url-form">
              <div className="input-group">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://docs.stripe.com/api"
                  required
                  disabled={isLoading}
                />
                <button type="submit" disabled={isLoading || !url.trim()}>
                  {isLoading ? 'Starting...' : 'Start Integration'}
                </button>
              </div>
            </form>

            {error && (
              <div className="error">
                <h3>Error:</h3>
                <p>{error}</p>
              </div>
            )}

            {response && (
              <div className="response">
                <h3>Backend Response:</h3>
                <pre>{response}</pre>
              </div>
            )}

            <div className="examples">
              <h3>Example API Documentation URLs:</h3>
              <ul>
                <li>Stripe: https://docs.stripe.com/api</li>
                <li>Shopify: https://shopify.dev/docs/api</li>
                <li>HubSpot: https://developers.hubspot.com/docs/api/overview</li>
                <li>QuickBooks: https://developer.intuit.com/app/developer/qbo/docs/develop</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App 