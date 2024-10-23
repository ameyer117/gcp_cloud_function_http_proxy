# HTTP Request Proxy on Google Cloud Functions

This project implements an HTTP request proxy using Google Cloud Functions. It allows you to send HTTP requests to any URL with customizable methods, headers, body, and parameters. The function acts as a proxy, forwarding your request and returning the response. This is very useful for troubleshooting network problems and serverless VPC connectors.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Deployment](#deployment)
- [Usage](#usage)
  - [Health Check Endpoint](#health-check-endpoint)
  - [Proxy Endpoint](#proxy-endpoint)
- [Testing](#testing)
- [CORS Handling](#cors-handling)
- [Notes](#notes)
- [License](#license)

## Features

- Proxy HTTP requests with customizable methods, headers, body, and parameters.
- Supports common HTTP methods: `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, `HEAD`, `OPTIONS`.
- Returns detailed response information including status code, headers, body, and elapsed time.
- Includes a health check endpoint.
- Handles Cross-Origin Resource Sharing (CORS) preflight requests.
- Skips SSL Verification for simplicity (adjust as needed for security).

## Prerequisites

- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) installed and configured.
- A Google Cloud Platform project with billing enabled.
- Python 3.11 or higher.
- [Git](https://git-scm.com/downloads) installed.

## Setup Instructions

1. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

## Deployment

Deploy the function to Google Cloud Functions using the following steps:

1. **Set the Default Project**

   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

   > Replace `YOUR_PROJECT_ID` with your Google Cloud project ID.

2. **Deploy the Function**

   ```bash
   gcloud functions deploy http-request-proxy \
       --runtime python310 \
       --trigger-http \
       --allow-unauthenticated \
       --entry-point main
   ```

   - `http-request-proxy`: The name you want to give your Cloud Function.
   - `--runtime python310`: Specifies the Python runtime environment.
   - `--trigger-http`: Indicates that the function is triggered by HTTP requests.
   - `--allow-unauthenticated`: Allows public access to the function.
   - `--entry-point main`: The name of the function in `main.py`.

3. **Wait for Deployment to Complete**

   The deployment process may take a few minutes. Once completed, note the URL provided by the Google Cloud CLI.

## Usage

### Health Check Endpoint

Check if the function is running properly by accessing the `/health` endpoint.

```bash
curl -X GET https://YOUR_CLOUD_FUNCTION_URL/health
```

**Expected Response:**

```json
{"status": "healthy"}
```

### Proxy Endpoint

Send HTTP requests via the proxy by making a `POST` request to the `/proxy` endpoint with a JSON payload.

#### Request Model

- **url** `(str)`: The target URL to which the request will be proxied.
- **method** `(str)`: The HTTP method (e.g., `GET`, `POST`).
- **headers** `(dict, optional)`: Custom HTTP headers.
- **body** `(dict or any, optional)`: The request body for methods like `POST` or `PUT`.
- **params** `(dict, optional)`: Query parameters.
- **timeout** `(int, optional)`: Request timeout in seconds (default is `30`).
- **verify** `(bool, optional)`: Verify SSL certificates (default is `False`).

#### Example Request

```bash
curl -X POST https://YOUR_CLOUD_FUNCTION_URL/proxy \
     -H "Content-Type: application/json" \
     -d '{
           "url": "https://httpbin.org/post",
           "method": "POST",
           "headers": {
               "Content-Type": "application/json"
           },
           "body": {
               "message": "Hello, World!"
           }
         }'
```

#### Example Response

```json
{
  "status_code": 200,
  "headers": {
    "Date": "Wed, 01 Nov 2023 12:00:00 GMT",
    "Content-Type": "application/json",
    "Content-Length": "500",
    "Connection": "keep-alive",
    "...": "..."
  },
  "body": {
    "args": {},
    "data": "{\"message\": \"Hello, World!\"}",
    "files": {},
    "form": {},
    "headers": {
      "Content-Length": "27",
      "Content-Type": "application/json",
      "...": "..."
    },
    "json": {
      "message": "Hello, World!"
    },
    "origin": "0.0.0.0",
    "url": "https://httpbin.org/post"
  },
  "elapsed_seconds": 0.456
}
```

## Testing

You can test the function locally before deploying by using the Functions Framework.

1. **Install the Functions Framework**

   ```bash
   pip install functions-framework
   ```

2. **Run the Function Locally**

   ```bash
   functions-framework --target=main --debug
   ```

3. **Send Requests to the Local Function**

   Use `curl` or any HTTP client to send requests to `http://localhost:8080`.

   **Example:**

   ```bash
   curl -X POST http://localhost:8080/proxy \
        -H "Content-Type: application/json" \
        -d '{
              "url": "https://httpbin.org/get",
              "method": "GET"
            }'
   ```

## CORS Handling

The function includes basic CORS handling:

- **Preflight Requests**: OPTIONS requests are handled to allow all methods and headers.
- **CORS Headers**: `Access-Control-Allow-Origin` is set to `*` to allow requests from any origin.

> **Note:** Adjust the CORS settings as needed for your application to restrict origins, methods, or headers.

## Notes

- **Error Handling**: The function returns JSON responses with error details in case of failures.
- **Synchronous vs. Asynchronous**: The function uses synchronous HTTP requests via `httpx.Client` for simplicity. Adjust to asynchronous if needed.
- **Security Considerations**: Be cautious when proxying requests to ensure that the function is not misused for malicious purposes. Implement authentication and input validation as necessary.
- **Logging**: Add logging as needed to monitor the function's behavior.

## License

This project is licensed under the [MIT License](LICENSE).

---

Feel free to customize the README further to suit your project's specific needs.