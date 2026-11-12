# Fram — Photo Studio

Windows-приложение для просмотра и базового редактирования изображений.

## Возможности
- Просмотр популярных форматов: PNG, JPEG, BMP, GIF, WEBP, TIFF, ICO и других форматов Pillow.
- Открытие RAW через rawpy (поддержка зависит от модели камеры).
- Просмотр GIF покадрово и экспорт кадров в GIF.
- Яркость, контраст, насыщенность, резкость, фильтры, поворот, обрезка, изменение размера и текст.
- Сохранение в PNG, JPEG, WEBP, BMP и TIFF.

Важно: не существует гарантии поддержки буквально всех форматов. RAW требует rawpy, а AVIF/HEIC и некоторые варианты TIFF зависят от доступных декодеров.

## Запуск из исходников
Требуется Python 3.11+:
```powershell
py -m pip install -r requirements.txt
py main.py
```

## Сборка
На Windows запусти `build_windows.bat`. Для установщика используется Inno Setup 6 и сценарий `fram.iss`.

## Сборка через GitHub
Открой Actions → Build Fram for Windows → Run workflow. После успешной сборки скачай артефакт **Fram-Setup** — в нём будет `Fram-Setup.exe`.
