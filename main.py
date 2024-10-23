# main.py
import json
import functions_framework
from pydantic import BaseModel
import httpx
from typing import Optional, Dict, Any

class RequestModel(BaseModel):
    url: str
    method: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, str]] = None
    timeout: Optional[int] = 30
    verify: Optional[bool] = False

class ResponseModel(BaseModel):
    status_code: int
    headers: Dict[str, str]
    body: Any
    elapsed_seconds: float

@functions_framework.http
def main(request):
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        # Allows all methods and headers for simplicity
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*',
        }
        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Content-Type': 'application/json'
    }

    path = request.path
    if path == '/health':
        return (json.dumps({"status": "healthy"}), 200, headers)

    elif path == '/proxy' or path == '/':
        try:
            # Get JSON data from request
            request_data = request.get_json()
            if not request_data:
                return ('Bad Request: No JSON payload provided', 400, headers)
            # Validate and parse request data
            request_model = RequestModel(**request_data)

            method = request_model.method.upper()
            if method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
                return ('Unsupported HTTP method', 400, headers)

            with httpx.Client(verify=request_model.verify) as client:
                response = client.request(
                    method=method,
                    url=request_model.url,
                    headers=request_model.headers,
                    json=request_model.body if method not in ["GET", "HEAD"] else None,
                    params=request_model.params,
                    timeout=request_model.timeout
                )

                # Convert headers to dict as some may be non-string
                headers_dict = dict(response.headers)
                headers_str = {k: str(v) for k, v in headers_dict.items()}

                response_model = ResponseModel(
                    status_code=response.status_code,
                    headers=headers_str,
                    body=response.json() if 'application/json' in response.headers.get("content-type", "") else response.text,
                    elapsed_seconds=response.elapsed.total_seconds()
                )
                return (response_model.json(), response_model.status_code, headers)

        except httpx.RequestError as e:
            error_message = f"Request failed: {str(e)}"
            return (json.dumps({"detail": error_message}), 500, headers)
        except Exception as e:
            error_message = str(e)
            return (json.dumps({"detail": error_message}), 500, headers)
    else:
        return ('Not Found', 404, headers)
