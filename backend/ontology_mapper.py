import os
import anthropic
import json
from dotenv import load_dotenv

load_dotenv()

claude_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

PROMPT_TEMPLATE = '''
You are an expert data integration agent. Your job is to map API endpoints to ontology tables for automated data onboarding.

Given the following API specification and ontology schema, output ONLY a JSON object in the following format:

{{
  "endpoint_to_table": [
    {{"endpoint": "/api/users", "table": "users"}},
    ...
  ]
}}

If you are not sure about a mapping, do not include it. Only include mappings you are confident about.

API Spec:
{api_spec}

Ontology Schema:
{ontology_schema}
'''

def map_api_to_ontology(api_spec, ontology_schema):
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