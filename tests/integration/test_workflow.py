import pytest
import uuid
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_workflow_execution(client: AsyncClient):
    # 1. Create Workflow
    workflow_data = {
        "name": "Test Workflow",
        "definition": {
            "version": "1.0",
            "steps": [
                {
                    "type": "http",
                    "method": "GET",
                    "url": "https://httpbin.org/get",
                    "timeout_seconds": 5
                }
            ]
        }
    }
    response = await client.post("/workflows/", json=workflow_data)
    assert response.status_code == 200
    workflow_id = response.json()["id"]

    # 2. Create Webhook Endpoint
    endpoint_data = {
        "path": "test-hook",
        "secret": "my-secret"
    }
    response = await client.post(f"/workflows/{workflow_id}/webhook-endpoints", json=endpoint_data)
    assert response.status_code == 200
    
    # 3. Trigger Webhook
    headers = {"x-webhook-secret": "my-secret"}
    response = await client.post("/webhooks/test-hook", headers=headers)
    assert response.status_code == 200
    run_id = response.json()["run_id"]
    
    # 4. Check Run Status (Initial)
    response = await client.get(f"/runs/{run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "QUEUED"
    assert data["workflow_id"] == workflow_id

    # Note: To test the actual execution, the Worker needs to be running.
    # In a real integration test, we'd spin up the worker or mock the event bus consumption.
    # For now, we verify the API side correctly enqueues the run.
