import asyncio
from ollama import AsyncClient
from loguru import logger
from .schema import TopicalGuardResponse

GUARDRAIL_SYSTEM_PROMPT = (
    "Your role is to assess whether a user query is about an allowed topic.\n"
    "Allowed topics:\n"
    "1. API Development\n"
    "2. FastAPI\n"
    "3. Building Generative AI systems\n"
    "If the topic is allowed, respond with only 'True'.\n"
    "If the topic is not allowed, respond with only 'False'.\n"
    "Never output anything other than 'True' or 'False'."
)


class InputGuardrail:
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-oss:20b-cloud",
        host: str = "https://ollama.com",
        timeout: float = 5.0,
        fail_open: bool = True,
    ):
        self.aclient = AsyncClient(
            host=host,
            headers={"Authorization": "Bearer " + api_key},
        )
        self.model = model
        self.timeout = timeout
        self.fail_open = fail_open

    async def is_topic_allowed(self, user_query: str) -> TopicalGuardResponse:
        try:
            response = await asyncio.wait_for(
                self.aclient.chat(
                    self.model,
                    messages=[
                        {"role": "system", "content": GUARDRAIL_SYSTEM_PROMPT},
                        {"role": "user", "content": user_query},
                    ],
                    think="medium",
                ),
                timeout=self.timeout,
            )
            result = response["message"]["content"].strip()
            classification = result.lower() in ("true", "yes", "allowed")
            logger.info(
                f"Guardrail result: query={user_query!r}, raw={result!r}, allowed={classification}"
            )
            return TopicalGuardResponse(classification=classification)

        except asyncio.TimeoutError:
            logger.warning(
                f"Guardrail timed out after {self.timeout}s — {'allowing' if self.fail_open else 'blocking'} request"
            )
            return TopicalGuardResponse(classification=self.fail_open)

        except Exception as e:
            logger.error(
                f"Guardrail error: {e} — {'allowing' if self.fail_open else 'blocking'} request"
            )
            return TopicalGuardResponse(classification=self.fail_open)
