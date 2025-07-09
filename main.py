import asyncio
from call_system import CallSystem

if __name__ == "__main__":
    system = CallSystem()
    asyncio.run(system.run()) 