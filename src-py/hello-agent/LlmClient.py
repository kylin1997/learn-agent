import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List,Dict

# 加载 .env 文件中的环境变量
load_dotenv()

class LlmClient:
    """
    用于调用任何兼容OpenAI接口的服务，并默认使用流式响应。
    """
    def __init__(self,model:str = None,apiKey:str = None,baseUrl:str=None,timeout:int = None):
        """
        初始化
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        
        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)
    
    def think(self,messages:List[Dict[str,str]],temperature:float =0,top_p:float =1.0) -> str:
        """
        调用大语言模型进行思考，并返回其响应。
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                temperature=temperature,
                top_p=top_p,
                stream=True
            )
            # 处理流式响应
            print("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            
            print()
            return "".join(collected_content)
        
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None

# --- 客户端使用示例 ---
if __name__ == '__main__':
    try:
        llmClient = LlmClient()

        exampleMessages = [
            {"role":"system","content":"You are a helpful assistant that writes Python code."},
            {"role": "user", "content": "写一个快速排序算法"}
        ]

        print("--- 调用LLM ---")
        responeseText = llmClient.think(exampleMessages)

    except ValueError as e:
        print(e)