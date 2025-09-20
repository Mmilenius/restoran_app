# convert_images.py - окремий файл в корені проєкту
import os
from PIL import Image
import glob


def convert_webp_to_jpg(webp_path, jpg_path):
    """Конвертація WebP в JPG"""
    try:
        with Image.open(webp_path) as img:
            # Конвертуємо в RGB якщо зображення має альфа-канал
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.save(jpg_path, 'JPEG', quality=85, optimize=True)
            print(f"Конвертовано: {webp_path} -> {jpg_path}")
            return True
    except Exception as e:
        print(f"Помилка конвертації {webp_path}: {e}")
        return False


def convert_all_webp_in_media():
    """Конвертує всі WebP файли в media/dishes/"""
    media_path = 'media/dishes/'

    if not os.path.exists(media_path):
        print(f"Папка {media_path} не існує")
        return

    # Знаходимо всі WebP файли
    webp_files = glob.glob(os.path.join(media_path, '*.webp'))

    if not webp_files:
        print("WebP файли не знайдено")
        return

    print(f"Знайдено {len(webp_files)} WebP файлів")

    converted = 0
    for webp_file in webp_files:
        # Створюємо назву JPG файлу
        jpg_file = webp_file.replace('.webp', '.jpg')

        if convert_webp_to_jpg(webp_file, jpg_file):
            converted += 1
            # Видаляємо оригінальний WebP файл (опційно)
            # os.remove(webp_file)

    print(f"Успішно конвертовано {converted} файлів")


if __name__ == '__main__':
    convert_all_webp_in_media()