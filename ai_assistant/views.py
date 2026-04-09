import json
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# 1. НАЛАШТУВАННЯ API КЛЮЧА
# ВСТАВ СВІЙ ЗГЕНЕРОВАНИЙ КЛЮЧ СЮДИ В ЛАПКИ:
GEMINI_API_KEY = "ТВІЙ_API_КЛЮЧ_ТУТ"

genai.configure(api_key=GEMINI_API_KEY)

# 2. СИСТЕМНА ІНСТРУКЦІЯ ДЛЯ ШІ
# Тут ми задаємо йому "роль", щоб він не відповідав як звичайний бот
RESTAURANT_CONTEXT = """
Ти - привітний віртуальний помічник ресторану "Гуцульський двір" (м. Яремче). 
Твоя мета - допомагати гостям. 
Ось що ти знаєш про нас:
- Ми готуємо автентичну українську та гуцульську кухню (банош, бограч, деруни, шашлик).
- Ми маємо Основний зал, Літню терасу (альтанки) та VIP-зону.
- Графік роботи: Пн-Пт (10:00 - 22:00), Сб-Нд (11:00 - 23:00).
- Адреса: вул. Карпатська, 12, м. Яремче.
- Телефон: +38 (099) 123 45 67.
- Забронювати стіл можна на сторінці Бронювання.

Правила відповідей:
1. Відповідай українською мовою.
2. Будь ввічливим, коротким і по суті.
3. Не придумуй того, чого немає в меню (якщо питають про суші чи піцу - кажи, що ми спеціалізуємося на українській кухні).
4. Завжди запрошуй гостей до нас.
"""

# Ініціалізуємо модель Gemini 1.5 Flash (найкраще співвідношення швидкості та якості для чатів)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=RESTAURANT_CONTEXT
)


@csrf_exempt
def ask_ai_assistant(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            if not user_message:
                return JsonResponse({'success': False, 'error': 'Порожнє повідомлення'})

            # Відправляємо запит до Gemini
            # Якщо потрібно зберігати історію діалогу, тут використовується model.start_chat()
            # Але для простого Q&A використовуємо generate_content()
            response = model.generate_content(user_message)

            # Отримуємо текст відповіді
            ai_reply = response.text

            return JsonResponse({'success': True, 'reply': ai_reply})

        except Exception as e:
            import traceback
            print("Gemini API Error:", traceback.format_exc())
            return JsonResponse({
                'success': False,
                'error': f"Вибачте, сталася технічна помилка. Подробиці для розробника: {str(e)}"
            })

    return JsonResponse({'success': False, 'error': 'Only POST methods are allowed'})