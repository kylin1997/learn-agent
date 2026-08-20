from LlmClient import LlmClient
import os,subprocess,json

SYSTEM = f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain."

# -- Tool definition: just bash --
TOOLS = [{
    "type": "function",
    "function": {
        "name": "bash",
        "description": "Run a shell command.",
        "parameters": {
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    },
}]

DANGEROUS = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]

class AgentLoop:
    def __init__(self,llm_client: LlmClient):
        self.llm_client = llm_client
    
    def run_bash(self, command: str) -> str:
        if any(d in command for d in DANGEROUS):
            return "Error: Dangerous command blocked"
        
        try:
            r = subprocess.run(command,shell=True,cwd=os.getcwd(),capture_output=True,text=True,timeout=120)
            out = (r.stdout + r.stderr).strip()
            return out[:50000] if out else "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Timeout (120s)"
        except (FileNotFoundError, OSError) as e:
            return f"Error: {e}"
    
    def agent_loop(self, messages: list, max_turns: int = 20):
        for _ in range(max_turns):
            # 调用重载版 think: 传入工具, 返回 (文本, 工具调用列表) 集合
            result = self.llm_client.think(messages, tools=TOOLS)
            # 防御: 调用失败返回 None 或空结果时终止循环
            if not result or not isinstance(result, tuple):
                print("❌ LLM 调用失败, 终止 agent 循环")
                return None
            text, tool_calls = result
            tool_calls = tool_calls or []
            messages.append({
                "role": "assistant",
                "content": text or "",
                **({"tool_calls": [{
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    } for tc in tool_calls]} if tool_calls else {})
            })

            # 没有工具调用 => 任务完成, 退出循环
            if not tool_calls:
                return text

            # 执行每个工具调用, 并把结果回填给模型
            for tc in tool_calls:
                if tc.function.name != "bash":
                    result = f"Error: unknown tool {tc.function.name}"
                else:
                    args = json.loads(tc.function.arguments or "{}")
                    command = args.get("command", "")
                    print(f"\n🔧 执行命令: {command}")
                    result = self.run_bash(command)
                    print(f"📄 输出: {result[:500]}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

if __name__ == "__main__":
    llm_client = LlmClient()

    agent_loop = AgentLoop(llm_client=llm_client)

    print("s01: Agent Loop")
    print("Enter a question, press Enter to send. Type q to quit.\n")

    history = []
    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break

        if query.strip().lower() in ("q", "exit", ""):
            break

        history.append({"role": "user", "content": query})
        agent_loop.agent_loop(history)
        
