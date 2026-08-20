from ddgs import DDGS


def search(query: str, max_results: int = 5, max_retries: int = 2, timeout: int = 10) -> str:
    """搜索并将结果格式化为字符串返回，支持重试和超时设置"""
    for attempt in range(max_retries):
        try:
            with DDGS(timeout=timeout) as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                break
        except Exception as e:
            if attempt == max_retries - 1:
                return f"搜索失败（已重试{max_retries}次）: {type(e).__name__}"
            continue

    if not results:
        return "未找到相关结果。"

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['title']}\n   {r['href']}\n   {r['body']}")
    return "\n\n".join(lines)