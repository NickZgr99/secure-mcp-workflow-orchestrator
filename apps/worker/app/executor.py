import asyncio
import httpx
import json
import logging
import traceback
from datetime import datetime
from uuid import UUID

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.app.db.session import AsyncSessionLocal
from apps.api.app.db.models import Run, Workflow, RunSnapshot
from apps.api.app.cache.redis_client import get_redis
from shared.shared.schemas.workflow import WorkflowDefinition, Step

logger = logging.getLogger(__name__)

class WorkflowExecutor:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.redis = None
        self.db = None

    async def execute(self):
        self.redis = await get_redis()
        async with AsyncSessionLocal() as session:
            self.db = session
            try:
                await self._run_workflow()
            except Exception as e:
                logger.error(f"Error executing run {self.run_id}: {e}")
                traceback.print_exc()
                await self._fail_run(str(e))

    async def _run_workflow(self):
        # Load Run and Workflow from DB
        stmt = select(Run).where(Run.id == UUID(self.run_id))
        result = await self.db.execute(stmt)
        run = result.scalar_one_or_none()
        
        if not run:
            logger.error(f"Run {self.run_id} not found")
            return

        workflow_stmt = select(Workflow).where(Workflow.id == run.workflow_id)
        wf_result = await self.db.execute(workflow_stmt)
        workflow = wf_result.scalar_one_or_none()
        
        if not workflow:
            logger.error(f"Workflow {run.workflow_id} not found")
            return

        definition = WorkflowDefinition(**workflow.definition_json)
        
        # Update status to RUNNING
        run.status = "RUNNING"
        run.started_at = datetime.utcnow()
        await self.db.commit()
        await self._update_redis_state("RUNNING")

        context = {}
        
        for index, step in enumerate(definition.steps):
            # Skip if already executed (in case of resume logic, though simple loop for now)
            if index < run.current_step_index:
                continue

            run.current_step_index = index
            await self.db.commit()
            
            logger.info(f"Executing step {index}: {step.type}")
            
            try:
                result = await self._execute_step(step, context)
                context[f"step_{index}"] = {"type": step.type, "result": result}
                
                # Persist snapshot if needed
                if step.type == "persist_snapshot":
                    await self._save_snapshot(index, context)

            except Exception as e:
                logger.error(f"Step {index} failed: {e}")
                await self._fail_run(f"Step {index} failed: {str(e)}")
                return

        # Mark SUCCEEDED
        run.status = "SUCCEEDED"
        run.finished_at = datetime.utcnow()
        await self.db.commit()
        await self._update_redis_state("SUCCEEDED", context)
        logger.info(f"Run {self.run_id} succeeded")

    async def _execute_step(self, step: Step, context: dict):
        if step.type == "http":
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=step.method,
                    url=step.url,
                    headers=step.headers,
                    json=step.json_body,
                    timeout=step.timeout_seconds
                )
                response.raise_for_status()
                return response.json()
        
        elif step.type == "mcp_tool":
            # Stub for MCP tool
            return {"status": "mock_success", "tool": step.tool_name, "output": "Mock output"}
        
        elif step.type == "persist_snapshot":
            return {"status": "snapshot_taken"}
            
        return {}

    async def _save_snapshot(self, index: int, context: dict):
        snapshot = RunSnapshot(
            run_id=UUID(self.run_id),
            step_index=index,
            snapshot_json=context
        )
        self.db.add(snapshot)
        await self.db.commit()

    async def _fail_run(self, error_msg: str):
        stmt = select(Run).where(Run.id == UUID(self.run_id))
        result = await self.db.execute(stmt)
        run = result.scalar_one_or_none()
        if run:
            run.status = "FAILED"
            run.error_message = error_msg
            run.finished_at = datetime.utcnow()
            await self.db.commit()
        await self._update_redis_state("FAILED", error=error_msg)

    async def _update_redis_state(self, status: str, context: dict = None, error: str = None):
        key = f"run:{self.run_id}:state"
        current_state = await self.redis.get(key)
        if current_state:
            state = json.loads(current_state)
            state["status"] = status
            state["last_updated_at"] = str(datetime.utcnow())
            if context:
                state["context"] = context
            if error:
                state["error"] = error
            await self.redis.set(key, json.dumps(state), ex=86400)
