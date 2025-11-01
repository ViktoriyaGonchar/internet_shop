"""Главный файл для запуска интернет-магазина SHOP SHIPS.

Этот файл является точкой входа в приложение и предоставляет
выбор между публичной частью (магазином) и CRM (админ-панелью).
"""

from data_manager import DataManager
from ui import PublicUI, CRMUI


def main() -> None:
    """Главная функция приложения."""
    print("\n" + "="*50)
    print("🚢 SHOP SHIPS - ИНТЕРНЕТ-МАГАЗИН")
    print("="*50)
    print("\nВыберите режим работы:")
    print("1. Публичная часть (покупатель)")
    print("2. CRM (администратор)")
    print("0. Выход")
    print("="*50)
    
    while True:
        choice = input("\nВаш выбор: ").strip()
        
        if choice == "1":
            # Публичная часть
            data_manager = DataManager()
            ui = PublicUI(data_manager)
            ui.show_menu()
            break
        elif choice == "2":
            # CRM
            data_manager = DataManager()
            ui = CRMUI(data_manager)
            ui.show_menu()
            break
        elif choice == "0":
            print("\n👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена пользователем.")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        import traceback
        traceback.print_exc()

