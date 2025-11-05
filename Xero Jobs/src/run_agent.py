import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def main():
    stream = await client.chat.completions.create(
        model="gpt-5",
        messages=[
            {"role": "user", "content": "Say 'double bubble bath' ten times fast."},
        ],
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            print(delta.content, end="", flush=True)

    print("\n\n[Stream complete]")

asyncio.run(main())
