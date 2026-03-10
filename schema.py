from typing import TypedDict

class GenerationOptions(TypedDict):
    temperature: float
    num_predict: int
    stop: list[str]
    num_ctx: int

class ClientRequest(TypedDict):
    model: str
    prompt: str
    raw: bool
    options: GenerationOptions
    keep_alive: int
    
class ResponseChunk(TypedDict):
    model: str
    created_at: str
    response: str
    done: bool
    
class FinalChunk(ResponseChunk):
    done_reason: str
    total_duration: int
    load_duration: int
    prompt_eval_count: int
    prompt_eval_duration: int
    eval_count: int
    eval_duration: int