import os
import json
import subprocess
import tempfile
import re
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_api_spec(api_spec: Dict) -> Dict:
    """Analyze API specification to determine patterns and requirements."""
    
    analysis = {
        'auth_type': 'unknown',
        'pagination_type': 'unknown',
        'base_url': api_spec.get('base_url', ''),
        'has_rate_limiting': False,
        'data_structure': 'unknown'
    }
    
    # Analyze authentication
    auth_info = api_spec.get('authentication', {})
    if auth_info.get('type') == 'bearer':
        analysis['auth_type'] = 'bearer'
    elif auth_info.get('type') == 'api_key':
        analysis['auth_type'] = 'api_key'
    elif auth_info.get('type') == 'oauth':
        analysis['auth_type'] = 'oauth'
    
    # Analyze endpoints for pagination patterns
    endpoints = api_spec.get('endpoints', [])
    for endpoint in endpoints:
        path = endpoint.get('path', '').lower()
        if any(param in path for param in ['cursor', 'after', 'before']):
            analysis['pagination_type'] = 'cursor'
        elif any(param in path for param in ['page', 'offset', 'limit']):
            analysis['pagination_type'] = 'page'
    
    # Determine data structure patterns
    if any('stripe' in endpoint.get('path', '').lower() for endpoint in endpoints):
        analysis['data_structure'] = 'stripe'
        analysis['pagination_type'] = 'cursor'  # Stripe uses cursor-based pagination
    
    return analysis

def generate_deterministic_sdk(api_spec: Dict, mapping: Dict, acho_token: str) -> str:
    """Generate deterministic SDK code based on API analysis and templates."""
    
    analysis = analyze_api_spec(api_spec)
    
    # Build the SDK code using string concatenation to avoid template formatting issues
    sdk_code = f'''const fs = require('fs');
const axios = require('axios');
const {{ Acho }} = require('@acho-inc/acho-js');

async function ingestData() {{
    const acho = new Acho({{
        apiToken: '{acho_token}'
    }});
    
    const baseUrl = '{api_spec.get('api_specifications', {}).get('base_url', '')}';
    const mapping = {json.dumps(mapping)};
    
    // Authentication headers
    {generate_auth_headers(api_spec)}
    
    const results = [];
    
    try {{
        // Create or get resource endpoint
        let resId;
        if (mapping.endpoint_to_table.length > 0 && mapping.endpoint_to_table[0].resource_id) {{
            resId = mapping.endpoint_to_table[0].resource_id;
        }} else {{
            const resourceResp = await acho.ResourceEndpoints.create({{
                name: 'API Integration - ' + new Date().toISOString()
            }});
            resId = resourceResp.resId;
        }}
        
        console.log('Resource ID:', resId);
        
        // Process each mapped endpoint
        for (const mapItem of mapping.endpoint_to_table) {{
            try {{
                const endpoint = mapItem.endpoint;
                const tableName = mapItem.table;
                
                console.log(`Processing ${{endpoint}} -> ${{tableName}}`);
                
                {generate_endpoint_processing(analysis, api_spec)}
                
            }} catch (error) {{
                console.error(`Error processing ${{mapItem.endpoint}}:`, error.message);
                results.push({{
                    endpoint: mapItem.endpoint,
                    table: mapItem.table,
                    status: 'error',
                    error: error.message
                }});
            }}
        }}
        
        // Generate summary
        const summary = {{
            resource_id: resId,
            results: results,
            total_endpoints: mapping.endpoint_to_table.length,
            successful_ingestions: results.filter(r => r.status === 'success').length,
            total_records_ingested: results.reduce((sum, r) => sum + (r.records_ingested || 0), 0)
        }};
        
        console.log('\\n=== INGESTION SUMMARY ===');
        console.log(JSON.stringify(summary, null, 2));
        
        return summary;
        
    }} catch (error) {{
        console.error('Integration failed:', error.message);
        return {{ error: error.message }};
    }}
}}

// Run the ingestion
ingestData().catch(console.error);'''
    
    return sdk_code

def generate_auth_headers(api_spec: Dict) -> str:
    """Generate authentication headers as JavaScript code for the SDK."""
    auth_info = api_spec.get('authentication', {})
    # Stripe: emit a JS block
    if 'stripe' in api_spec.get('url', '').lower() or 'stripe' in api_spec.get('title', '').lower():
        return (
            "let authHeaders = {};\n"
            "if (process.env.STRIPE_SK) {\n"
            "  authHeaders['Authorization'] = 'Basic ' + Buffer.from(process.env.STRIPE_SK + ':').toString('base64');\n"
            "} else {\n"
            "  authHeaders['Authorization'] = 'Basic YOUR_STRIPE_KEY';\n"
            "}"
        )
    # Default: emit a JS object
    headers = {}
    if auth_info.get('type') == 'bearer':
        headers['Authorization'] = f"Bearer {auth_info.get('token', 'YOUR_TOKEN')}"
    elif auth_info.get('type') == 'api_key':
        headers[auth_info.get('header_name', 'X-API-Key')] = auth_info.get('api_key', 'YOUR_API_KEY')
    return f"const authHeaders = {json.dumps(headers)};"

def generate_auth_headers_for_nodejs(api_spec: Dict, stripe_key: str) -> str:
    """Generate authentication headers for Node.js SDK with Stripe API key."""
    
    auth_info = api_spec.get('authentication', {})
    headers = {}
    
    # Check if this is Stripe API and use the Stripe API key
    if 'stripe' in api_spec.get('url', '').lower() or 'stripe' in api_spec.get('title', '').lower():
        if stripe_key:
            # In Node.js, we'll use Buffer for base64 encoding
            headers['Authorization'] = f"Basic Buffer.from('{stripe_key}:').toString('base64')"
        else:
            headers['Authorization'] = "Basic YOUR_STRIPE_KEY"
    elif auth_info.get('type') == 'bearer':
        headers['Authorization'] = f"Bearer {auth_info.get('token', 'YOUR_TOKEN')}"
    elif auth_info.get('type') == 'api_key':
        headers[auth_info.get('header_name', 'X-API-Key')] = auth_info.get('api_key', 'YOUR_API_KEY')
    
    return json.dumps(headers)

def generate_endpoint_processing(analysis: Dict, api_spec: Dict) -> str:
    """Generate endpoint processing code based on API analysis."""
    
    if analysis['pagination_type'] == 'cursor':
        return generate_cursor_pagination_code()
    elif analysis['pagination_type'] == 'page':
        return generate_page_pagination_code()
    else:
        return generate_simple_pagination_code()

def generate_cursor_pagination_code() -> str:
    """Generate code for cursor-based pagination (like Stripe)."""
    
    return '''
                // Fetch data from API with cursor-based pagination
                let allData = [];
                let hasMore = true;
                let startingAfter = null;
                
                while (hasMore) {
                    const url = `${baseUrl}${endpoint}`;
                    const params = {};
                    
                    if (startingAfter) {
                        params.starting_after = startingAfter;
                    }
                    
                    const response = await axios.get(url, {
                        headers: authHeaders,
                        params: params,
                        timeout: 30000
                    });
                    
                    let data = response.data;
                    
                    // Handle data extraction
                    if (typeof data === 'object' && data !== null) {
                        if (Array.isArray(data)) {
                            data = data;
                        } else if (data.data && Array.isArray(data.data)) {
                            data = data.data;
                        } else if (data.results && Array.isArray(data.results)) {
                            data = data.results;
                        } else if (data.items && Array.isArray(data.items)) {
                            data = data.items;
                        } else {
                            data = [data];
                        }
                    } else {
                        data = [];
                    }
                    
                    allData = allData.concat(data);
                    
                    // Check for more data
                    if (data.length > 0 && response.data.has_more) {
                        startingAfter = data[data.length - 1].id;
                    } else {
                        hasMore = false;
                    }
                    
                    // Rate limiting
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
                
                if (allData.length > 0) {
                    // Clean data for ingestion
                    const cleanedData = allData.map(item => {
                        const cleaned = {};
                        for (const [key, value] of Object.entries(item)) {
                            if (typeof value === 'object' && value !== null) {
                                cleaned[key] = JSON.stringify(value);
                            } else {
                                cleaned[key] = value;
                            }
                        }
                        return cleaned;
                    });
                    
                    // Create write stream and ingest data
                    const writableStream = await acho.ResourceEndpoints.createWriteStream({
                        resId: resId,
                        tableId: tableName,
                        dataType: 'json'
                    });
                    
                    await new Promise((resolve, reject) => {
                        cleanedData.forEach((row) => {
                            writableStream.write(JSON.stringify(row) + '\\n');
                        });
                        writableStream.end();
                        
                        writableStream.on('response', (res) => {
                            if (res.statusCode === 200) {
                                resolve('done');
                            } else {
                                reject(new Error(`HTTP ${res.statusCode}`));
                            }
                        });
                        
                        writableStream.on('error', (error) => {
                            reject(error);
                        });
                    });
                    
                    results.push({
                        endpoint: endpoint,
                        table: tableName,
                        status: 'success',
                        records_ingested: cleanedData.length
                    });
                    
                    console.log(`Successfully ingested ${cleanedData.length} records from ${endpoint}`);
                } else {
                    results.push({
                        endpoint: endpoint,
                        table: tableName,
                        status: 'no_data',
                        records_ingested: 0
                    });
                    console.log(`No data found for ${endpoint}`);
                }'''

def generate_page_pagination_code() -> str:
    """Generate code for page-based pagination."""
    
    return '''
                // Fetch data from API with page-based pagination
                let allData = [];
                let page = 1;
                let hasMore = true;
                
                while (hasMore) {
                    const url = `${baseUrl}${endpoint}`;
                    const params = { page: page };
                    
                    const response = await axios.get(url, {
                        headers: authHeaders,
                        params: params,
                        timeout: 30000
                    });
                    
                    let data = response.data;
                    
                    // Handle data extraction
                    if (typeof data === 'object' && data !== null) {
                        if (Array.isArray(data)) {
                            data = data;
                        } else if (data.data && Array.isArray(data.data)) {
                            data = data.data;
                        } else if (data.results && Array.isArray(data.results)) {
                            data = data.results;
                        } else if (data.items && Array.isArray(data.items)) {
                            data = data.items;
                        } else {
                            data = [data];
                        }
                    } else {
                        data = [];
                    }
                    
                    allData = allData.concat(data);
                    
                    // Check for more data
                    if (data.length > 0) {
                        page++;
                        // Rate limiting
                        await new Promise(resolve => setTimeout(resolve, 100));
                    } else {
                        hasMore = false;
                    }
                }
                
                if (allData.length > 0) {
                    // Clean data for ingestion
                    const cleanedData = allData.map(item => {
                        const cleaned = {};
                        for (const [key, value] of Object.entries(item)) {
                            if (typeof value === 'object' && value !== null) {
                                cleaned[key] = JSON.stringify(value);
                            } else {
                                cleaned[key] = value;
                            }
                        }
                        return cleaned;
                    });
                    
                    // Create write stream and ingest data
                    const writableStream = await acho.ResourceEndpoints.createWriteStream({
                        resId: resId,
                        tableId: tableName,
                        dataType: 'json'
                    });
                    
                    await new Promise((resolve, reject) => {
                        cleanedData.forEach((row) => {
                            writableStream.write(JSON.stringify(row) + '\\n');
                        });
                        writableStream.end();
                        
                        writableStream.on('response', (res) => {
                            if (res.statusCode === 200) {
                                resolve('done');
                            } else {
                                reject(new Error(`HTTP ${res.statusCode}`));
                            }
                        });
                        
                        writableStream.on('error', (error) => {
                            reject(error);
                        });
                    });
                    
                    results.push({
                        endpoint: endpoint,
                        table: tableName,
                        status: 'success',
                        records_ingested: cleanedData.length
                    });
                    
                    console.log(`Successfully ingested ${cleanedData.length} records from ${endpoint}`);
                } else {
                    results.push({
                        endpoint: endpoint,
                        table: tableName,
                        status: 'no_data',
                        records_ingested: 0
                    });
                    console.log(`No data found for ${endpoint}`);
                }'''

def generate_simple_pagination_code() -> str:
    """Generate code for simple API calls without pagination."""
    
    return '''
                // Fetch data from API (simple call)
                const url = `${baseUrl}${endpoint}`;
                console.log('DEBUG: Requesting URL:', url);
                const response = await axios.get(url, {
                    headers: authHeaders,
                    timeout: 30000
                });
                
                let data = response.data;
                
                // Handle data extraction
                if (typeof data === 'object' && data !== null) {
                    if (Array.isArray(data)) {
                        data = data;
                    } else if (data.data && Array.isArray(data.data)) {
                        data = data.data;
                    } else if (data.results && Array.isArray(data.results)) {
                        data = data.results;
                    } else if (data.items && Array.isArray(data.items)) {
                        data = data.items;
                    } else {
                        data = [data];
                    }
                } else {
                    data = [];
                }
                
                if (data.length > 0) {
                    // Clean data for ingestion
                    const cleanedData = data.map(item => {
                        const cleaned = {};
                        for (const [key, value] of Object.entries(item)) {
                            if (typeof value === 'object' && value !== null) {
                                cleaned[key] = JSON.stringify(value);
                            } else {
                                cleaned[key] = value;
                            }
                        }
                        return cleaned;
                    });
                    
                    // Create write stream and ingest data
                    const writableStream = await acho.ResourceEndpoints.createWriteStream({
                        resId: resId,
                        tableId: tableName,
                        dataType: 'json'
                    });
                    
                    await new Promise((resolve, reject) => {
                        cleanedData.forEach((row) => {
                            writableStream.write(JSON.stringify(row) + '\\n');
                        });
                        writableStream.end();
                        
                        writableStream.on('response', (res) => {
                            if (res.statusCode === 200) {
                                resolve('done');
                            } else {
                                reject(new Error(`HTTP ${res.statusCode}`));
                            }
                        });
                        
                        writableStream.on('error', (error) => {
                            reject(error);
                        });
                    });
                    
                    results.push({
                        endpoint: endpoint,
                        table: tableName,
                        status: 'success',
                        records_ingested: cleanedData.length
                    });
                    
                    console.log(`Successfully ingested ${cleanedData.length} records from ${endpoint}`);
                } else {
                    results.push({
                        endpoint: endpoint,
                        table: tableName,
                        status: 'no_data',
                        records_ingested: 0
                    });
                    console.log(`No data found for ${endpoint}`);
                }'''

def generate_ingestion_sdk(api_spec: Dict, mapping: Dict, acho_token: str) -> str:
    """Generate deterministic SDK code for data ingestion."""
    return generate_deterministic_sdk(api_spec, mapping, acho_token)

def generate_fallback_sdk(api_spec: Dict, mapping: Dict, acho_token: str) -> str:
    """Fallback SDK generation - now uses the same deterministic approach."""
    return generate_deterministic_sdk(api_spec, mapping, acho_token)

def execute_ingestion_sdk(api_spec: Dict, mapping: Dict, acho_token: str) -> Dict:
    """Execute the generated SDK code to ingest data into Acho."""
    
    try:
        # Generate the SDK code using deterministic templates
        sdk_code = generate_ingestion_sdk(api_spec, mapping, acho_token)
        
        if not sdk_code:
            return {"error": "Failed to generate SDK code"}
        
        # Create temporary file for the script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(sdk_code)
            script_path = f.name
        
        # Ensure environment variables are loaded
        load_dotenv()
        
        # Execute the script with environment variables
        env_vars = os.environ.copy()
        env_vars["NODE_PATH"] = os.path.join(os.path.dirname(__file__), "node_modules")
        
        # Ensure Stripe API key is passed if available
        if 'stripe' in api_spec.get('url', '').lower() or 'stripe' in api_spec.get('title', '').lower():
            stripe_key = os.getenv('STRIPE_SK')
            if stripe_key:
                env_vars['STRIPE_SK'] = stripe_key
                print(f"Passing STRIPE_SK to Node.js process")
        
        result = subprocess.run(
            ['node', script_path],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes timeout
            cwd=os.path.dirname(__file__),
            env=env_vars
        )
        
        # Clean up
        os.unlink(script_path)
        
        if result.returncode != 0:
            return {
                "error": f"SDK execution failed: {result.stderr}",
                "stdout": result.stdout
            }
        
        # Parse the output to find the summary
        lines = result.stdout.split('\n')
        summary_started = False
        summary_lines = []
        
        for line in lines:
            if '=== INGESTION SUMMARY ===' in line:
                summary_started = True
                continue
            elif summary_started:
                if line.strip():
                    summary_lines.append(line.strip())
        
        if summary_lines:
            try:
                # Join the summary lines and parse as JSON
                summary_json = ''.join(summary_lines)
                return json.loads(summary_json)
            except json.JSONDecodeError:
                pass
        
        # If we can't parse the summary, return a clean "no data" response
        # Check if the output indicates no data was found
        if 'No data found for' in result.stdout:
            return {
                "message": "No data found in the API",
                "status": "no_data",
                "details": "The API endpoints were successfully queried but no data was found."
            }
        
        return {
            "error": "Could not parse SDK output",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
    except Exception as e:
        return {"error": f"SDK execution failed: {str(e)}"}

def main():
    """Main function for testing the data ingestion agent."""
    # This would be called by the main orchestration agent
    pass

if __name__ == "__main__":
    main() 