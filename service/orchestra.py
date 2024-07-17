import asyncio
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import queue
import time
import json
import os

# Configuration
NODE_URLS = [
    # "http://region-31.seetacloud.com:37099",
    # "https://u11820-955b-de7d95e0.neimeng.seetacloud.com:6443",
    # "https://u11820-a131-14dac496.neimeng.seetacloud.com:6443",
    "https://u11820-8622-a630f78f.neimeng.seetacloud.com:6443",
    # "https://u11820-9715-5624ff7c.neimeng.seetacloud.com:6443",
    "http://region-31.seetacloud.com:59071"

]
TASK_QUEUE = queue.Queue()
TASK_TIMEOUT = 300  # 5 minutes
MAX_RETRIES = 3  # Maximum retries for a task
WORKER_COUNT = 5  # Number of worker tasks to run

# Global state to track node status
node_status = {url: "available" for url in NODE_URLS}
node_locks = {url: asyncio.Lock() for url in NODE_URLS}
# Asyncio lock for thread-safe access to the global list
status_lock = asyncio.Lock()


class DialogMessage(BaseModel):
    role: str
    content: str


class Task(BaseModel):
    message: DialogMessage
    task_id: str
    target: str


class NodeTask(BaseModel):
    message: DialogMessage
    functionality: str


async def list_node_statuses():
    async with status_lock:
        return node_status


class TaskProcessor:
    def __init__(self, task: Task):
        self.task = task
        self.results = {}
        self.attempt = 1
        self.target = '' if task is None else task.target
        self.retry_prompt = ''

    async def check_node_availability(self, node_url):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f'{node_url}/status')
                status = 'unreachable'
                if response.status_code == 200:
                    status = response.json().get('status', 'unknown')
                async with status_lock:
                    node_status[node_url] = status
            except httpx.RequestError as exc:
                async with status_lock:
                    node_status[node_url] = 'unreachable'
                print(f"An error occurred while requesting {exc.request.url!r}: {exc}")

    async def poll_node_statuses(self):
        while True:
            tasks = [self.check_node_availability(url) for url in NODE_URLS]
            await asyncio.gather(*tasks)
            await asyncio.sleep(1)

    async def send_to_node(self, node_task, timeout=120, retry_count=0):
        start_time = time.time()
        while time.time() - start_time < timeout:
            async with status_lock:
                available_nodes = [url for url, status in node_status.items() if status == 'available']

            if available_nodes:
                for url in available_nodes:
                    if node_locks[url].locked():
                        continue
                    async with node_locks[url]:
                        try:
                            async with httpx.AsyncClient() as client:
                                response = await client.post(f"{url}/chat", json=node_task.dict(), timeout=30)
                                if response.status_code == 503:
                                    async with status_lock:
                                        node_status[url] = 'busy'
                                    continue
                                print(f"Node {url} response: {response.text}")
                                response.raise_for_status()
                                return response.json()
                        except httpx.HTTPStatusError as exc:
                            raise HTTPException(status_code=exc.response.status_code,
                                                detail=f"Node {url} error: {exc.response.text}")
                        except Exception as e:
                            if retry_count < MAX_RETRIES:
                                print(f"Retrying node task due to error: {str(e), e} {retry_count}")
                                return await self.send_to_node(node_task, timeout, retry_count + 1)
                            else:
                                raise HTTPException(
                                    status_code=500, detail=f"Node {url} error: {str(e)}")
            await asyncio.sleep(3)

        raise HTTPException(status_code=503, detail="No available nodes within the timeout period")

    async def process_task(self):
        while self.attempt <= MAX_RETRIES:
            try:
                # Initialize NodeTasks 1-3
                node_tasks = [
                    NodeTask(message=self.task.message, functionality=f'analysis{f}') for f in ['_general', '_risk', '_sentiment']
                ]

                # Send NodeTasks 1-3 to nodes and gather results
                node_results = await asyncio.gather(
                    *[self.send_to_node(node_task) for node_task in node_tasks]
                )

                # Initialize NodeTask 4 with results of NodeTasks 1-3
                print(f"Aggregating results... {self.task.task_id}")
                aggregated_message = '\n[-ANALYZER RESULTS SEPARATION-]\n'.join(result['response']['content'] for result in node_results)
                node_task4 = NodeTask(message=DialogMessage(role="system", content=aggregated_message),
                                      functionality='aggregator')
                result4 = await self.send_to_node(node_task4)
                self.results['result4'] = result4['response']['content']

                # Initialize NodeTask 5 with result of NodeTask 4 and original message
                discriminator_message = f"[Summary]{result4['response']['content']} [RawNews]{self.task.message.content}"
                node_task5 = NodeTask(message=DialogMessage(role="system", content=discriminator_message),
                                      functionality='discriminator')
                result5 = await self.send_to_node(node_task5)
                self.results['result5'] = result5['response']['content']

                if "[Result]: Reject" in self.results['result5'] and self.attempt < MAX_RETRIES:
                    print("Result 5 indicates decline, retrying task...")
                    self.retry_prompt = '[Retry Prompt] '+self.results['result5']
                    self.attempt += 1
                else:
                    self.save_results(success=True)
                    break

                print("Result 4:", self.results['result4'])
                print("Result 5:", self.results['result5'])
            except Exception as e:
                print(f"Error processing task {self.task.task_id}: {str(e)}")
                self.save_results(success=False, error=str(e))
                break

    def save_results(self, success=True, error=None):
        result_filename = f"result_{self.target}.json"
        with open(result_filename, 'a') as f:
            # if file is empty, write the opening bracket
            if os.stat(result_filename).st_size == 0:
                f.write("[\n")
            f.write(json.dumps({
                "task_id": self.task.task_id,
                "status": "success" if success else "failed",
                "results": self.results if success else {"error": error}
            }, indent=4))
            f.write(",\n")
            # if task is the last task, write the closing bracket
            current, total = self.task.task_id.split('/')
            if current == total:
                f.write("]\n")


async def worker():
    while True:
        if not TASK_QUEUE.empty():
            task = TASK_QUEUE.get()
            task_processor = TaskProcessor(task)
            await task_processor.process_task()
        await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start polling the node statuses
    loop = asyncio.get_event_loop()
    poll_task = loop.create_task(TaskProcessor(None).poll_node_statuses())

    # Start worker tasks
    worker_tasks = [loop.create_task(worker()) for _ in range(WORKER_COUNT)]

    yield

    # Cleanup
    poll_task.cancel()
    await poll_task
    for worker_task in worker_tasks:
        worker_task.cancel()
        await worker_task


app = FastAPI(lifespan=lifespan)


@app.post("/process")
async def process(task: Task):
    # Add task to the queue
    TASK_QUEUE.put(task)

    if TASK_QUEUE.qsize() > 15:
        raise HTTPException(status_code=503, detail="Task queue is full")

    return {"message": "Task added to the queue"}


@app.get("/queue_size")
async def queue_size():
    return {"queue_size": TASK_QUEUE.qsize()}


@app.post("/add_node")
async def add_node(url: str):
    if url in NODE_URLS:
        return {"message": "Node already exists"}
    NODE_URLS.append(url)
    node_status[url] = "available"
    node_locks[url] = asyncio.Lock()
    return {"message": "Node added successfully"}

@app.get("/status_nodes")
async def status_nodes():
    return await list_node_statuses()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
