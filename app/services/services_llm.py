from typing import Generator
from groq import Groq  

client = Groq()

def generate_title(
    prompt: str
) -> str:
    """
    Generates a short and descriptive title summarizing the user's prompt.

    Args:
        prompt: The original user prompt.

    Returns:
        A single-sentence title string.
    """
    title_prompt = (
        "Give a short, 3-4 word title (no quotes, no asterisks) summarizing the following user prompt:\n\n"
        f"{prompt}\n\n"
    )

    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[{"role": "user", "content": title_prompt}],
        temperature=0,
        stream=False,
        reasoning_format="hidden",
    )

    return response.choices[0].message.content.strip().strip("")


def generate_response(
    prompt: str
) -> Generator[str, None, None]:
    """
    Generate a response with prompt using qwen3-32b model. 

    Args:
        prompt: the prompt to send the model.

    Returns:
        A generator yielding pieces of the response as strings,
        received incrementally from the streaming API.
    """
    response = client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        reasoning_format="hidden",
    )
    for chunk in response:
        yield chunk.choices[0].delta.content or ""