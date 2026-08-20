import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL_ID = "Qwen/Qwen1.5-0.5B-Chat"


def setup_device():
    """设置运行设备，优先使用GPU"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    return device


def load_tokenizer(model_id):
    """加载分词器"""
    return AutoTokenizer.from_pretrained(model_id)


def load_model(model_id, device):
    """加载模型并移动到指定设备，设置为评估模式"""
    model = AutoModelForCausalLM.from_pretrained(model_id).to(device)
    model.eval()
    return model


def build_messages():
    """构建对话消息"""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好，请介绍你自己。"}
    ]


def encode_messages(tokenizer, messages, device):
    """使用聊天模板格式化并编码消息"""
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)
    print("编码后的输入文本:")
    print(model_inputs)
    return model_inputs


def generate_response(model, model_inputs, max_new_tokens=512):
    """使用模型生成回答，返回截取掉输入部分的Token ID"""
    generated_ids = model.generate(
        model_inputs.input_ids,
        max_new_tokens=max_new_tokens
    )
    return [
        output_ids[len(input_ids):]
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]


def decode_response(tokenizer, generated_ids):
    """解码生成的Token ID为文本"""
    return tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]


def main():
    device = setup_device()

    tokenizer = load_tokenizer(MODEL_ID)
    model = load_model(MODEL_ID, device)
    print("模型和分词器加载完成！")

    messages = build_messages()
    model_inputs = encode_messages(tokenizer, messages, device)

    generated_ids = generate_response(model, model_inputs)
    response = decode_response(tokenizer, generated_ids)

    print("\n模型的回答:")
    print(response)


if __name__ == "__main__":
    main()