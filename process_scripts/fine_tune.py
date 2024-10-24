import torch, os, multiprocessing
from datasets import load_dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    set_seed
)
from trl import SFTTrainer, SFTConfig

compute_dtype = torch.bfloat16
attn_implementation = 'flash_attention_2'

def fine_tune(model_name, batch_size=1, gradient_accumulation_steps=32, LoRA = True):

  tokenizer = AutoTokenizer.from_pretrained(model_name)
  tokenizer.pad_token = "<|finetune_right_pad_id|>"
  tokenizer.pad_token_id = 128004
  tokenizer.padding_side = 'right'

  ds = load_dataset('json', data_files='ru_turbo_saiga.jsonl')

  def process(row):
    messages = row["messages"]
    conversation = ""
    for message in messages:
        role = message["role"]
        content = message["content"]
        if role == "user":
            conversation += f"User: {content}\n"
        elif role == "bot":
            conversation += f"Bot: {content}\n"

    row["text"] = conversation + tokenizer.eos_token
    return row


  ds = ds.map(
      process,
      num_proc= multiprocessing.cpu_count(),
      load_from_cache_file=False,
  )

  model = AutoModelForCausalLM.from_pretrained(
              model_name, device_map={"": 0}, attn_implementation=attn_implementation
    )
  model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={'use_reentrant':True})

  peft_config = LoraConfig(
          lora_alpha=16,
          lora_dropout=0.05,
          r=16,
          bias="none",
          task_type="CAUSAL_LM",
          target_modules= ['k_proj', 'q_proj', 'v_proj', 'o_proj', "gate_proj", "down_proj", "up_proj"]
  )

  output_dir = "LoRA/"

  training_arguments = SFTConfig(
          output_dir=output_dir,
          eval_strategy="steps",
          do_eval=True,
          optim="adamw_8bit",
          per_device_train_batch_size=batch_size,
          gradient_accumulation_steps=gradient_accumulation_steps,
          per_device_eval_batch_size=batch_size,
          log_level="debug",
          save_strategy="epoch",
          logging_steps=25,
          learning_rate=5e-6,
          bf16 = True,
          eval_steps=25,
          num_train_epochs=1,
          warmup_ratio=0.1,
          lr_scheduler_type="linear",
          dataset_text_field="text",
          max_seq_length=1024,
  )
  train_test_split = ds['train'].train_test_split(test_size=0.1)

  train_dataset = train_test_split['train']
  eval_dataset = train_test_split['test']

  trainer = SFTTrainer(
          model=model,
          train_dataset = train_dataset,
          eval_dataset = eval_dataset,
          peft_config=peft_config,
          tokenizer=tokenizer,
          args=training_arguments,
  )

  gpu_stats = torch.cuda.get_device_properties(0)
  start_gpu_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
  max_memory = round(gpu_stats.total_memory / 1024 / 1024 / 1024, 3)
  trainer_ = trainer.train()


  used_memory = round(torch.cuda.max_memory_reserved() / 1024 / 1024 / 1024, 3)
  used_memory_for_trainer= round(used_memory - start_gpu_memory, 3)
  used_percentage = round(used_memory         /max_memory*100, 3)
  trainer_percentage = round(used_memory_for_trainer/max_memory*100, 3)
  print(f"{round(trainer_.metrics['train_runtime']/60, 2)} minutes used for training.")

fine_tune("meta-llama/Llama-3.2-3B", batch_size=1, gradient_accumulation_steps=32, LoRA = True)