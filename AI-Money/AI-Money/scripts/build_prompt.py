
import json
import yaml
import os
from jinja2 import Environment, FileSystemLoader


CONFIG_FILE_NAME = "config.json"

def load_config(config_path):
    """Загружает конфигурацию из JSON файла."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ОШИБКА: Файл конфигурации не найден по пути: {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"ОШИБКА: Не удалось распарсить JSON в файле: {config_path}")
        return None

def load_file_content(file_path):
    """Универсальная функция для загрузки текстового содержимого из файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ОШИБКА: Файл не найден: {file_path}")
        return None
    except Exception as e:
        print(f"ОШИБКА при чтении файла {file_path}: {e}")
        return None

def load_yaml_data(file_path):
    """Загружает данные из YAML файла."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"ОШИБКА: YAML файл не найден: {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"ОШИБКА при парсинге YAML файла {file_path}: {e}")
        return None

def load_jsonl_data(file_path):
    """Загружает данные из JSONL файла (каждая строка - JSON объект)."""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # Пропускаем пустые строки
                    data.append(json.loads(line))
        return data
    except FileNotFoundError:
        print(f"ОШИБКА: JSONL файл не найден: {file_path}")
        return None
    except Exception as e:
        print(f"ОШИБКА при чтении JSONL файла {file_path}: {e}")
        return None

def main():
    """Главная функция для сборки промпта."""
    # Определяем путь к корневой директории проекта (где лежит config.json)
    # os.path.dirname(__file__) дает путь к папке scripts
    # os.path.join(..) поднимает нас на уровень вверх, в корень
    project_root = os.path.join(os.path.dirname(__file__), '..')
    config_file_path = os.path.join(project_root, CONFIG_FILE_NAME)

    print(f"Запуск сборки промпта. Корень проекта: {project_root}")

    # 1. Загружаем конфигурацию
    config = load_config(config_file_path)
    if not config:
        return # Выходим, если конфиг не загрузился

    # 2. Загружаем все необходимые компоненты на основе путей из конфига
    # Абсолютные пути к файлам
    system_message_file = os.path.join(project_root, config.get("system_message_file"))
    variables_file = os.path.join(project_root, config.get("variables_file"))
    examples_file = os.path.join(project_root, config.get("examples_file"))
    template_file = os.path.join(project_root, config.get("template_file"))
    output_file = os.path.join(project_root, config.get("output_file"))

    print(f"Загрузка компонентов...")
    
    system_message = load_file_content(system_message_file)
    variables = load_yaml_data(variables_file)
    examples = load_jsonl_data(examples_file)
    
    if not all([system_message is not None, variables is not None, examples is not None]):
        print("ОШИБКА: Не удалось загрузить один из компонентов промпта. Сборка прервана.")
        return

    # 3. Настраиваем Jinja2
    # FileSystemLoader говорит Jinja2, где искать шаблоны (в нашем случае в корне проекта)
    # lstrip_blocks=True и trim_blocks=True убирают лишние пустые строки в сгенерированном тексте
    env = Environment(loader=FileSystemLoader(project_root), lstrip_blocks=True, trim_blocks=True)
    template = env.get_template(config.get("template_file"))

    # 4. Рендерим шаблон, подставляя в него данные
    print("Сборка финального промпта из шаблона...")
    final_prompt = template.render(
        system_message=system_message,
        variables=variables,
        examples=examples
    )

    # 5. Сохраняем результат в файл
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_prompt)
        print(f"✅ УСПЕХ: Собранный промпт сохранён в {output_file}")
    except Exception as e:
        print(f"ОШИБКА при сохранении финального промпта в файл {output_file}: {e}")

if __name__ == "__main__":
    main()
