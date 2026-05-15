Concurrency in Python for AI Engineering (Async Mental Model)

This document explains Python async concurrency from a practical AI engineering perspective. The focus is not theoretical completeness but building a usable mental model for systems such as LLM orchestration, retrieval pipelines, and API-heavy services.

1. Concurrency Model (Mental Model)

Python async is based on a single-threaded event loop.

At any instant, only one piece of Python code executes. However, execution can switch between tasks when a task is waiting on I/O (network, disk, DB).

This is fundamentally different from:

Multithreading: multiple threads scheduled by the OS, potentially parallel
Multiprocessing: multiple processes executing in true parallel on multiple cores

In async Python:

There is no CPU parallelism by default
Concurrency is achieved via interleaving execution during waiting periods
Concurrency vs Parallelism
Concurrency: multiple tasks make progress over time (interleaved execution)
Parallelism: multiple tasks execute at the same time (multi-core execution)

Python async provides concurrency, not parallelism.

Why async exists (I/O waiting problem)

AI systems are dominated by I/O latency:

LLM API calls
Vector database queries
HTTP requests
File I/O

Without async, a single slow request blocks the entire program.

Async solves this by allowing the program to switch tasks while waiting.

Non-blocking execution

Non-blocking means:

A task voluntarily yields control when waiting
The event loop can run other tasks during this time

No task is forcibly interrupted. Cooperation is required.

Mental model: one worker, many tasks, worker switches only when a task says “I am waiting”.

2. async/await Basics (Language Layer)

Async in Python is built on coroutines.

A coroutine is a function that can pause and resume execution.

async def (Coroutine Definition)
async def fetch_data():
    return 42
Meaning
This defines a coroutine function
Calling it does NOT execute it
It returns a coroutine object

Execution happens only when:

awaited, or
scheduled as a Task
await (Suspension Point)

await is the keyword that:

pauses the current coroutine
yields control back to the event loop
resumes when the awaited operation completes

Example:

import asyncio

async def fetch_data():
    await asyncio.sleep(1)
    return "data"

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
Key idea

When execution hits await:

coroutine pauses
event loop switches to other work
resumes later at same point
Coroutines vs normal functions
Normal function: runs immediately to completion
Coroutine: pauses and resumes via await
Chaining async calls
import asyncio

async def step1():
    await asyncio.sleep(1)
    return "A"

async def step2(prev):
    await asyncio.sleep(1)
    return prev + "B"

async def main():
    a = await step1()
    b = await step2(a)
    print(b)

asyncio.run(main())
Execution property

This is sequential async execution, not concurrency.

Total time ≈ 2 seconds.

Line-level interpretation
async def step1()

Defines a coroutine. No execution yet.

await asyncio.sleep(1)
asyncio.sleep(1) → non-blocking timer
await → suspends coroutine and returns control to event loop

During this time:

coroutine is paused
other tasks can run
return "A"

Resumes coroutine and returns result to caller.

step2(prev)

Same behavior, but dependent on input from step1.

async def main()

Orchestrator coroutine. Nothing runs until scheduled.

a = await step1()

Execution flow:

step1 is scheduled
main pauses
event loop runs step1
step1 returns "A"
execution resumes in main
b = await step2(a)

Same pattern, sequential dependency.

No concurrency occurs.

asyncio.run(main())

Keyword: asyncio.run

This:

creates event loop
runs main coroutine
closes loop after completion

Nothing executes without it.

Key insight

This code uses async syntax but does not exploit concurrency.

3. Event Loop + Task Scheduling (Core Engine)

The event loop is the scheduler.

It continuously:

selects ready tasks
runs them until await
stores paused state
switches to other tasks
Tasks vs Coroutines

Coroutine

function definition (worker("A"))
inert until scheduled

Task

scheduled coroutine
actively managed by event loop
Cooperative scheduling

There is no preemption.

A coroutine must explicitly yield via await.

Example (true concurrency)
import asyncio

async def worker(name):
    print(f"{name} started")
    await asyncio.sleep(2)
    print(f"{name} finished")

async def main():
    t1 = asyncio.create_task(worker("A"))
    t2 = asyncio.create_task(worker("B"))

    await t1
    await t2

asyncio.run(main())
asyncio.create_task

Keyword: create_task

Meaning:

schedules coroutine immediately on event loop
converts coroutine into a Task
allows it to run independently
Execution flow
both tasks start immediately
both hit sleep
both pause concurrently
both resume after ~2 seconds

Total runtime ≈ 2 seconds (not 4)

Key line explanations
async def worker(name)

Defines coroutine blueprint.

print(f"{name} started")

Runs immediately when coroutine starts.

await asyncio.sleep(2)

Non-blocking pause:

yields execution
allows other tasks to run
print(f"{name} finished")

Runs after resumption.

await t1, await t2

Keyword: await Task

Meaning:

wait for completion of scheduled task
does NOT start task
only synchronizes with result
Execution timeline
t=0s
A started
B started

t=0–2s
A sleeping
B sleeping

t=2s
A finished
B finished
4. Running Concurrency (Practical AI Engineering)

This is the most important usage pattern: fan-out / fan-in

Fan-out: launch multiple independent async operations
Fan-in: collect results
asyncio.gather

Keyword: gather

Meaning:

schedules multiple coroutines concurrently
waits for all to complete
returns results as a list (order preserved)
Example: parallel LLM calls
import asyncio

async def call_llm(prompt):
    await asyncio.sleep(1)
    return f"response to {prompt}"

async def main():
    prompts = ["hello", "world", "ai", "systems"]

    results = await asyncio.gather(
        *(call_llm(p) for p in prompts)
    )

    print(results)

asyncio.run(main())
Execution model

At t=0:

all 4 coroutines are scheduled

During execution:

all are waiting simultaneously

At t≈1s:

all complete

Total time ≈ 1 second (not 4)

Key behavior of gather
executes tasks concurrently
preserves input order
returns list of results
AI engineering interpretation

This pattern maps directly to:

parallel LLM calls
vector DB queries
multi-document retrieval
batch inference pipelines
Alternative: create_task

Used when explicit task control is required:

cancellation
monitoring
dynamic orchestration
5. Blocking vs Non-blocking + Thread Escape Hatch

Async only works for I/O-bound work.

Problem: CPU blocking

CPU-heavy operations block the event loop:

numpy-heavy computation
local embeddings
synchronous libraries
time.sleep()
Example blocking function
import time

def cpu_task():
    time.sleep(2)
    return "done"

This blocks everything if run inside async code.

run_in_executor

Keyword: run_in_executor

Meaning:

offloads blocking work to a thread or process pool
keeps event loop responsive
Example
import asyncio
import time

def blocking_io():
    time.sleep(2)
    return "blocking result"

async def main():
    loop = asyncio.get_running_loop()

    result = await loop.run_in_executor(None, blocking_io)
    print(result)

asyncio.run(main())
Practical rule in AI systems
async → I/O orchestration
threads → blocking libraries
processes → CPU-heavy workloads
Final Mental Model

The async event loop is not a parallel execution engine.

It is a scheduler for waiting tasks.

Execution only progresses when:

a task is ready, or
a task is waiting

Everything else is just syntax around this scheduling model.