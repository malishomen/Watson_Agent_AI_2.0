#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor Task Sender - отправка задач в Cursor через file-based систему
"""
import time, json, os, glob, sys
from pathlib import Path

INBOX = Path(__file__).parent.parent / "inbox"
CURSOR_TASKS = Path(__file__).parent.parent / "cursor_tasks"
PROCESSED = Path(__file__).parent.parent / "data" / "processed_tasks.log"

def init_dirs():
    """Создает необходимые директории"""
    INBOX.mkdir(exist_ok=True)
    CURSOR_TASKS.mkdir(exist_ok=True)
    PROCESSED.parent.mkdir(exist_ok=True)

def log_processed(task_file: str):
    """Логирует обработанную задачу"""
    with open(PROCESSED, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {task_file}\n")

def create_cursor_instruction(task_data: dict, task_id: str) -> str:
    """
    Создает детальную инструкцию для Cursor AI
    """
    text = task_data.get("text", "")
    repo_path = task_data.get("repo_path", "")
    dry_run = task_data.get("dry_run", False)
    action = task_data.get("action", "generate")  # generate | apply_diff
    
    # Проверяем есть ли готовый diff от LLM
    has_llm_diff = "generated_diff" in task_data
    llm_analysis = task_data.get("llm_analysis", "")
    generated_diff = task_data.get("generated_diff", "")
    
    if has_llm_diff and action == "apply_diff":
        # РЕЖИМ: Применить готовый diff от DeepSeek + Qwen
        instruction = f"""# 🎯 ЗАДАЧА С ГОТОВЫМ DIFF ОТ WATSON LLM

## 📋 Задача: {task_id}

**Описание:**
{text}

**Репозиторий:**
`{repo_path}`

**Режим:** {'🧪 DRY-RUN (review diff)' if dry_run else '✅ APPLY (применить готовый diff)'}

---

## 🤖 LLM УЖЕ ОБРАБОТАЛ ЗАДАЧУ

### DeepSeek R1 Analysis:
```
{llm_analysis}
```

### Qwen 2.5 Coder Generated Diff:
```diff
{generated_diff}
```

---

## ⚡ ИНСТРУКЦИИ ДЛЯ CURSOR AI

Cursor, **НЕ генерируй код заново!** Готовый diff уже создан LLM моделями.

Твоя задача:

### 1. Review diff
- Прочитай diff выше
- Проверь что он корректен
- Определи какие файлы затронуты

### 2. {'Покажи summary (НЕ применяй)' if dry_run else 'Примени изменения'}
{'- Покажи какие файлы будут изменены' if dry_run else '- Используй search_replace для каждого изменения из diff'}
{'- Создай отчет для review' if dry_run else '- Примени все hunks из diff последовательно'}

### 3. Проверка
- Убедись что все изменения применены корректно
- Проверь синтаксис
{'- Создай summary для review' if dry_run else '- Запусти линтер если есть'}

### 4. Отчет
Создай файл `cursor_tasks/{task_id}_result.md`:

```markdown
# Результат: {task_id}

## Задача
{text}

## LLM Analysis (DeepSeek R1)
{llm_analysis[:200]}...

## Изменения (из Qwen diff)
{'- Reviewed diff: N файлов' if dry_run else '- Applied diff: N файлов'}

## Статус
{'✅ Diff reviewed, ready to apply' if dry_run else '✅ Diff applied successfully'}
```

---

## 🚨 ВАЖНО

- **НЕ ГЕНЕРИРУЙ** код заново - используй готовый diff!
- Работай в репозитории: `{repo_path}`
- {'ТОЛЬКО review, НЕ применяй' if dry_run else 'Применяй diff аккуратно, hunk за hunk'}
- Создай подробный отчет

**Начинай выполнение!** 🚀
"""
    else:
        # СТАРЫЙ РЕЖИМ: Cursor генерирует сам
        instruction = f"""# 🎯 АВТОМАТИЧЕСКАЯ ЗАДАЧА ОТ WATSON AGENT

## 📋 Задача: {task_id}

**Описание:**
{text}

**Репозиторий:**
`{repo_path}`

**Режим:** {'🧪 DRY-RUN (только показать diff)' if dry_run else '✅ APPLY (применить изменения)'}

---

## ⚡ ИНСТРУКЦИИ ДЛЯ ВЫПОЛНЕНИЯ

Cursor AI, выполни следующие шаги:

### 1. Анализ задачи
- Прочитай описание задачи выше
- Определи какие файлы нужно изменить
- Спланируй изменения

### 2. Поиск файлов
- Найди все релевантные файлы в репозитории
- Прочитай их содержимое
- Определи где нужны изменения

### 3. Внесение изменений
{'- Создай diff патч и ПОКАЖИ его (НЕ применяй!)' if dry_run else '- Внеси изменения в файлы'}
{'- Сохрани diff в файл для review' if dry_run else '- Сохрани все измененные файлы'}

### 4. Проверка
- Убедись что синтаксис корректен
- Проверь что импорты на месте
{'- Покажи summary изменений' if dry_run else '- Запусти линтер (если есть)'}

### 5. Отчет
Создай файл `cursor_tasks/{task_id}_result.md` с отчетом:
```markdown
# Результат задачи {task_id}

## Задача
{text}

## Выполнено
- [x] Файл 1: описание изменений
- [x] Файл 2: описание изменений

## Diff
```diff
... твой diff ...
```

## Статус
{'✅ Diff создан, готов к review' if dry_run else '✅ Изменения применены'}
```

---

## 🚨 ВАЖНО

- Работай **только** в указанном репозитории: `{repo_path}`
- {'**НЕ применяй** изменения, только покажи diff' if dry_run else 'Применяй изменения аккуратно'}
- Создавай **подробный отчет** о проделанной работе
- **НЕ останавливайся** на первой ошибке - анализируй и исправляй

---

**Начинай выполнение прямо сейчас!** 🚀
"""
    return instruction

def process_task(task_file: Path):
    """
    Обрабатывает задачу из inbox и создает инструкцию для Cursor
    """
    print(f"\n📥 Processing: {task_file.name}")
    
    try:
        with open(task_file, "r", encoding="utf-8") as f:
            task_data = json.load(f)
        
        task_id = task_file.stem  # task_1234
        
        # Проверяем есть ли готовый diff от LLM
        has_llm_diff = "generated_diff" in task_data
        action = task_data.get("action", "generate")
        
        if has_llm_diff:
            print(f"   🤖 Режим: LLM pre-processed")
            print(f"   📊 DeepSeek R1 analysis: available")
            print(f"   📝 Qwen 2.5 diff: {len(task_data.get('generated_diff', ''))} bytes")
            print(f"   ⚡ Action: {action}")
        else:
            print(f"   🎯 Режим: Cursor self-generation")
        
        # Создаем инструкцию для Cursor
        instruction = create_cursor_instruction(task_data, task_id)
        
        # Сохраняем в cursor_tasks/
        cursor_file = CURSOR_TASKS / f"{task_id}_instruction.md"
        with open(cursor_file, "w", encoding="utf-8") as f:
            f.write(instruction)
        
        print(f"   ✅ Создана инструкция: {cursor_file.name}")
        print(f"   📄 Откройте файл в Cursor и отправьте в Chat!")
        print(f"   📂 Путь: {cursor_file.absolute()}")
        
        # Логируем обработку
        log_processed(task_file.name)
        
        # Удаляем задачу из inbox
        task_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error processing {task_file.name}: {e}")
        return False

def main():
    """
    Основной цикл мониторинга inbox и создания задач для Cursor
    """
    init_dirs()
    
    print("")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("   📋 CURSOR TASK SENDER - ЗАПУЩЕН")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    print(f"👀 Watching: {INBOX.absolute()}")
    print(f"📤 Output:   {CURSOR_TASKS.absolute()}")
    print(f"📝 Log:      {PROCESSED.absolute()}")
    print("")
    print("💡 Когда задача появится в inbox:")
    print("   1. Создается instruction файл в cursor_tasks/")
    print("   2. Откройте файл в Cursor")
    print("   3. Отправьте весь текст в Cursor Chat (Ctrl+L)")
    print("   4. Cursor выполнит задачу автоматически!")
    print("")
    print("⏸️  Нажмите Ctrl+C для остановки")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    
    try:
        while True:
            tasks = sorted(INBOX.glob("*.task.json"))
            
            if tasks:
                print(f"\n🔔 Найдено задач: {len(tasks)}")
                
            for task_file in tasks:
                process_task(task_file)
                time.sleep(1)  # Небольшая пауза между задачами
            
            time.sleep(2)  # Polling interval
            
    except KeyboardInterrupt:
        print("\n\n✋ Остановлен пользователем")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        sys.exit(0)

if __name__ == "__main__":
    main()

