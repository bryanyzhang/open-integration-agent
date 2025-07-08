import os
import anthropic
import json
import subprocess
import tempfile
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

def get_mock_ontology_schema() -> Dict:
    """Return a mock ontology schema for testing when Acho SDK is not available."""
    return {
        "tables": [
            {
                "name": "customers",
                "resource_id": "res_customers",
                "resource_name": "Customer Data",
                "fields": [
                    {"name": "id", "type": "STRING"},
                    {"name": "name", "type": "STRING"},
                    {"name": "email", "type": "STRING"},
                    {"name": "created_at", "type": "TIMESTAMP"}
                ]
            },
            {
                "name": "orders",
                "resource_id": "res_orders",
                "resource_name": "Order Data",
                "fields": [
                    {"name": "id", "type": "STRING"},
                    {"name": "customer_id", "type": "STRING"},
                    {"name": "amount", "type": "NUMBER"},
                    {"name": "status", "type": "STRING"},
                    {"name": "created_at", "type": "TIMESTAMP"}
                ]
            },
            {
                "name": "products",
                "resource_id": "res_products",
                "resource_name": "Product Data",
                "fields": [
                    {"name": "id", "type": "STRING"},
                    {"name": "name", "type": "STRING"},
                    {"name": "price", "type": "NUMBER"},
                    {"name": "description", "type": "STRING"}
                ]
            },
            {
                "name": "payments",
                "resource_id": "res_payments",
                "resource_name": "Payment Data",
                "fields": [
                    {"name": "id", "type": "STRING"},
                    {"name": "order_id", "type": "STRING"},
                    {"name": "amount", "type": "NUMBER"},
                    {"name": "status", "type": "STRING"},
                    {"name": "payment_method", "type": "STRING"}
                ]
            }
        ]
    }

def fetch_acho_ontology_schema(acho_token: str) -> Dict:
    """Fetch the real Acho ontology schema using the Acho SDK businessObject.exportOntology function."""
    script_content = f'''
const {{ Acho }} = require('@acho-inc/acho-js');

async function fetchSchema() {{
    try {{
        // Correct initialization as per documentation
        const acho = new Acho({{ apiToken: '{acho_token}', endpoint: 'https://kube.acho.io' }});
        const businessObject = acho.businessObject();
        const ontology = await businessObject.exportOntology();
        if (!ontology) {{
            console.log(JSON.stringify({{ error: 'Failed to export ontology from Acho' }}));
            return;
        }}
        
        // Transform the ontology to the expected format for mapping
        const ontology_schema = {{ tables: [] }};
        
        // Handle different possible ontology structures
        if (Array.isArray(ontology)) {{
            // If ontology is directly an array of tables
            console.log(`Processing ${{ontology.length}} tables...`);
            for (const table of ontology) {{
                if (table.tableName) {{
                    const transformedTable = {{
                        name: table.tableName,
                        resource_id: table.tableName, // Use tableName as resource_id
                        resource_name: table.tableDisplayName || table.tableName,
                        fields: []
                    }};
                    
                    if (table.tableColumns && Array.isArray(table.tableColumns)) {{
                        for (const columnName of table.tableColumns) {{
                            const fieldType = table.columnDataTypes && table.columnDataTypes[columnName] ? 
                                            table.columnDataTypes[columnName] : 'STRING';
                            transformedTable.fields.push({{
                                name: columnName,
                                type: fieldType
                            }});
                        }}
                    }}
                    
                    ontology_schema.tables.push(transformedTable);
                }}
            }}
        }} else if (ontology.resources && Array.isArray(ontology.resources)) {{
            // If ontology has resources structure
            for (const resource of ontology.resources) {{
                if (resource.tables) {{
                    for (const table of resource.tables) {{
                        ontology_schema.tables.push({{
                            name: table.name,
                            resource_id: resource.id,
                            resource_name: resource.name,
                            fields: table.fields ? table.fields.map(field => ({{
                                name: field.name,
                                type: field.type || 'STRING'
                            }})) : []
                        }});
                    }}
                }}
            }}
        }} else if (ontology.tables && Array.isArray(ontology.tables)) {{
            // If ontology has tables structure
            for (const table of ontology.tables) {{
                ontology_schema.tables.push({{
                    name: table.name || table.tableName,
                    resource_id: table.resource_id || table.tableName,
                    resource_name: table.resource_name || table.tableDisplayName || table.name || table.tableName,
                    fields: table.fields ? table.fields.map(field => ({{
                        name: field.name,
                        type: field.type || 'STRING'
                    }})) : []
                }});
            }}
        }}
        
        console.log(`Transformed ${{ontology_schema.tables.length}} tables successfully`);
        console.log(JSON.stringify(ontology_schema));
    }} catch (error) {{
        console.log(JSON.stringify({{ error: error.message }}));
    }}
}}

fetchSchema().catch(console.error);
'''
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(script_content)
            script_path = f.name
        result = subprocess.run(
            ['node', script_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.path.dirname(__file__),
            env={**os.environ, "NODE_PATH": os.path.join(os.path.dirname(__file__), "node_modules")}
        )
        os.unlink(script_path)
        if result.returncode != 0:
            return {"error": f"Failed to fetch Acho schema: {result.stderr}"}
        
        # Parse the JSON output from the Node.js script
        lines = result.stdout.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    parsed = json.loads(line)
                    if 'tables' in parsed:
                        return parsed
                    elif 'error' in parsed:
                        return parsed
                except json.JSONDecodeError:
                    continue
        
        return {"error": "Could not parse Acho schema response"}
    except Exception as e:
        return {"error": f"Failed to fetch Acho schema: {str(e)}"}

PROMPT_TEMPLATE = '''
You are an expert data integration agent. Your job is to map API endpoints to existing Acho ontology tables for automated data onboarding.

Given the following API specification and the Acho ontology schema, output ONLY a JSON object in the following format:

{{
  "endpoint_to_table": [
    {{"endpoint": "/api/users", "table": "users", "resource_id": "res_123", "resource_name": "My Resource"}},
    ...
  ]
}}

Mapping Rules:
1. Match API endpoints to Acho tables based on name similarity and data type
2. Only include mappings you are confident about
3. Include the resource_id and resource_name for each mapping
4. If an API endpoint doesn't have a good match in the Acho schema, don't include it
5. Consider both exact name matches and semantic similarity (e.g., "customers" matches "customer")
6. For Stripe API, common mappings include:
   - /v1/customers → customers table
   - /v1/charges → payments table
   - /v1/products → products table
   - /v1/orders → orders table

API Spec:
{api_spec}

Acho Ontology Schema:
{ontology_schema}
'''

def map_api_to_ontology(api_spec: Dict, acho_token: str) -> Dict:
    """Map API endpoints to the Acho ontology schema."""
    # First try to fetch the real Acho schema
    ontology_schema = fetch_acho_ontology_schema(acho_token)

    # If that fails, use mock schema for testing
    if "error" in ontology_schema:
        print(f"Warning: Using mock ontology schema due to Acho SDK error: {ontology_schema['error']}")
        print("This allows you to test Agent 2 functionality while resolving Acho SDK issues.")
        ontology_schema = get_mock_ontology_schema()

    if not ontology_schema.get("tables"):
        return {"error": "No tables found in Acho schema"}

    prompt = PROMPT_TEMPLATE.format(
        api_spec=json.dumps(api_spec, indent=2),
        ontology_schema=json.dumps(ontology_schema, indent=2)
    )

    try:
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            temperature=0,
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}]
        )
        content = ''.join(getattr(part, 'text', str(part)) for part in response.content).strip() if hasattr(response, 'content') and response.content else None
        if not content:
            return {"error": "Could not extract text from Claude response"}
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                try:
                    return json.loads(json_str)
                except Exception:
                    return {"error": "Failed to parse extracted JSON from Claude response"}
            else:
                return {"error": "Could not extract JSON from Claude response"}
    except Exception as e:
        return {"error": f"Claude analysis failed: {str(e)}"} 