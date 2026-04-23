import os
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"),
    api_key=os.getenv("NVIDIA_API_KEY")
)

def get_llm_response(prompt: str, model: str = "openai/gpt-oss-120b", max_retries: int = 7):
    """
    Calls the LLM and returns the response content along with token usage.
    Implements Exponential Backoff to avoid 40 RPM trial limits.
    """
    base_delay = 2.0  # Bắt đầu chờ 2 giây
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=1024,
            )
            
            content = response.choices[0].message.content
            usage = response.usage
            
            return {
                "content": content,
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"[ERROR] Max retries reached. Final error: {e}")
                raise e
            
            # Tính toán thời gian chờ: 2, 4, 8, 16, 32, 64 giây
            delay = base_delay * (2 ** attempt)
            print(f"[WARNING] Encountered API error (possibly Rate Limit). Retrying in {delay} seconds... (Attempt {attempt + 1}/{max_retries}) | Error: {e}")
            time.sleep(delay)
