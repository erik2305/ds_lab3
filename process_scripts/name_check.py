from transformers import AutoTokenizer
import transformers
import torch
import time
import json

model = "LoRA/checkpoint-2122"

base_content = """
Ты - помощник для сравнения полей с именами. Тебе даны три поля: "FullName(rus)", "FirstName+LastName" и склеенное поле из "FirstName", 
"SecondName" и "LastName". Твоя задача - проверить, совпадают ли эти поля. Имя считается совпадающим, даже если отсутствует "SecondName", 
но "FirstName" и "LastName" совпадают. Ответь "Да", если имена совпадают, и "Нет", если нет.
"""

messages = [
    {
        "role": "system",
        "content": base_content
    },
    {
        "role": "user",
        "content": ""
    }
]

tokenizer = AutoTokenizer.from_pretrained(model)
pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    torch_dtype=torch.float16,
    device_map="auto",
)

with open('bp_bd_sirena_merge.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

id_log_file = "ids_with_no_match.txt"


with open(id_log_file, "a", encoding="utf-8") as log_file:
    for passenger_id, passenger_data in data.items():
        fullname_rus = passenger_data["PassengerDetails"]["FullName(rus)"]
        first_name = passenger_data["PassengerDetails"]["FirstName"]
        second_name = passenger_data["PassengerDetails"].get("SecondName", "")
        last_name = passenger_data["PassengerDetails"]["LastName"]
        
        merged_name = f"{first_name} {second_name} {last_name}"
        first_last_name = f"{last_name} {first_name}"  

        user_message = f"""
        Поле "FullName(rus)": {fullname_rus}
        Поле "FirstName+LastName": {first_last_name}
        Поле, склеенное из "FirstName", "SecondName", "LastName": {merged_name}
        """
        messages[1]["content"] = user_message
        start_time = time.time()

        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        outputs = pipeline(prompt, max_new_tokens=250, do_sample=True, temperature=0.1, top_k=30, top_p=0.9)
        output_text = outputs[0]['generated_text'].strip()
        
        print(f"Ответ модели: {output_text}")
        print("--- %s секунд на ответ ---" % (time.time() - start_time))

        if output_text.lower() == "нет":
            log_file.write(f"{passenger_id}\n")
            log_file.flush()  
            print(f"ID {passenger_id} добавлен в файл.")

        
        messages[0]["content"] = base_content
