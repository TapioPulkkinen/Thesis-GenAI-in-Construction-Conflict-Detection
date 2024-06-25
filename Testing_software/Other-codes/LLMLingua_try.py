from test_prompts_and_texts import TestPromptsAndText
from llmlingua import PromptCompressor
from time import perf_counter

def compressPromt(model="quantized", dev_map = "cuda", model_conf=None):
    if model_conf is None:
        model_conf = {"revision": "main"}
    print("starting to initialize...")
    start = perf_counter()
    if model == "quantized":
        llm_lingua = PromptCompressor("TheBloke/Llama-2-7b-Chat-GPTQ", device_map=dev_map, model_config=model_conf)
    else:
        dev_map = "cpu"
        model_conf = {}
        llm_lingua = PromptCompressor("NousResearch/Llama-2-7b-hf", device_map=dev_map, model_config=model_conf)
    end = perf_counter()
    print(f"Time taken for initializing was {end-start}\n")
    print("Starting to compress prompt...")
    start2 = perf_counter()
    compressed_prompt = llm_lingua.compress_prompt(context=TestPromptsAndText.t_text,
                                                   instruction=TestPromptsAndText.t_prompt)
    print(f"\nHere is the compressed prompt: \n{compressed_prompt}")
    end2 = perf_counter()
    print(f"Time taken for compressing was {end2 - start2}")

if __name__ == "__main__":
    compressPromt()
    