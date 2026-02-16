from transformers import Pipeline, pipeline
import torch
import aiohttp
from loguru import logger


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(model_name: str, task: str, trust_remote_code: bool = False) -> Pipeline:
    pip = pipeline(
        task,
        model=model_name,
        dtype=torch.bfloat16,
        device=device,
        trust_remote_code=trust_remote_code,
    )
    return pip


async def generate_text(
    # pipe: Pipeline,
    prompt: str,
    temperature: float = 0.7,
    vllm_api_key: str = "",
) -> str:
    system_prompt = """ 
        You are a helpful assistant. use the context provided to answer the question,
        dont ever create info, if you dont know say i don't know,
        Context:
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    header = {"Authorization": f"Bearer {vllm_api_key}"}
    body = {"messages": messages, "temprature": temperature}

    try:
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                "http://localhost:8000/v1/chat/completions", json=body, headers=header
            )
            response.raise_for_status()
            prediction = await response.json()

    except Exception as e:
        logger.error(f"Failed to obtain predictions from vLLM - Error: {e}")
        return (
            "Failed to obtain predictions from vLLM - See server logs for more details"
        )

    try:
        output = prediction["choices"][0]["message"]["content"]
        logger.debug(f"Generated text: {output}")
        return output
    except KeyError as e:
        logger.error(f"Failed to parse predictions from vLLM - Error: {e}")
        return (
            "Failed to parse predictions from vLLM - See server logs for more details"
        )

    # FOR HF LOCAL MODEL INFERENCE - - - - - - -
    # prompt = pipe.tokenizer.apply_chat_template(
    #     messages, tokenize=False, add_generation_prompt=True
    # )

    # prediction = pipe(
    #     prompt,
    #     return_full_text=False,
    #     max_new_tokens=1024,
    #     temperature=temperature,
    #     do_sample=True,
    #     top_k=50,
    #     top_p=0.95,
    # )

    # output = prediction[0]["generated_text"]
    # return output
