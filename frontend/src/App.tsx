import React, { useState } from 'react'
import './App.css'

function App() {
  const [url, setUrl] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [response, setResponse] = useState<string>('')
  const [error, setError] = useState<string>('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setIsLoading(true);
    setError('');
    setResponse('');
    
    try {
      // 1. Parse doc
      const parseRes = await fetch('/api/parse-doc', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() })
      });
      if (!parseRes.ok) throw new Error('Failed to parse doc');
      const apiSpec = await parseRes.json();

      // 2. Map ontology
      const mapRes = await fetch('/api/map-ontology', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_spec: apiSpec })
      });
      if (!mapRes.ok) throw new Error('Failed to map ontology');
      const mapping = await mapRes.json();

      // 3. Ingest data
      const ingestRes = await fetch('/api/ingest-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_spec: apiSpec, mapping })
      });
      if (!ingestRes.ok) throw new Error('Failed to ingest data');
      const ingestResult = await ingestRes.json();

      // Handle different response formats
      if (ingestResult.status === 'no_data') {
        setResponse(`✅ ${ingestResult.message}\n\n${ingestResult.details}`);
      } else if (ingestResult.error) {
        setError(ingestResult.error);
      } else {
        setResponse(JSON.stringify(ingestResult, null, 2));
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setIsLoading(false);
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
                <h3>Integration Result:</h3>
                {response.includes('✅') ? (
                  <div className="success-message">
                    <p>{response}</p>
                  </div>
                ) : (
                  <pre>{response}</pre>
                )}
              </div>
            )}

            <div className="examples">
              <h3>Example API Documentation URLs:</h3>
              <ul>
                <li>Petstore: https://petstore.swagger.io/</li>
                <li>JSONPlaceholder: https://jsonplaceholder.typicode.com/</li>
                <li>HubSpot Objects: https://developers.hubspot.com/docs/api/crm/objects</li>
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