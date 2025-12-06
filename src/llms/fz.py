from openai import OpenAI
import os
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DEEPSEEK_3_1_MODEL_NAME = "DeepSeek-3.1"
DEEPSEEK_3_1_MODEL_ID = os.environ.get(
    "DEEPSEEK_3_1_MODEL_ID") or ""
ARK_BASE_URL = os.environ.get(
    "ARK_BASE_URL") or "https://ark-cn-beijing.bytedance.net/api/v3"


FZ_API_KEY = os.environ.get("ARK_API_KEY") or ""
K2_MODEL_ID = os.environ.get("K2_MODEL_ID") or ""
K2_MODEL_NAME = "K2"


OPEN_AI_API_KEY = os.environ.get("OPEN_AI_API_KEY") or ""
OPEN_AI_BASE_URL = os.environ.get(
    "OPEN_AI_BASE_URL") or "https://api.gptsapi.net/v1"

# openai client
openai_client = OpenAI(
    base_url="OPEN_AI_BASE_URL",
    api_key=OPEN_AI_API_KEY
)

fz_k2_chat_model = ChatOpenAI(
    model=K2_MODEL_ID,
    api_key=SecretStr(FZ_API_KEY),
    base_url=ARK_BASE_URL,
    model_kwargs={"max_tokens": 32000}
)


fz_deepseek_3_1_chat_model = ChatOpenAI(
    model=DEEPSEEK_3_1_MODEL_ID,
    api_key=SecretStr(FZ_API_KEY),
    base_url=ARK_BASE_URL,
)
