# Локальные сэмплы прайсов

Сюда клади скачанные `.gz` / распакованные `.xml` (например PriceFull Шуферсаль).

**Файлы прайсов в Git не коммитим** — они большие и часто обновляются.
Папка `data/samples/` указана в корневом `.gitignore`; этот README — исключение.

Пример после скачивания с https://prices.shufersal.co.il/ :

```bash
# из корня репозитория
ls data/samples/
gunzip -k data/samples/PriceFull....xml.gz   # -k сохранить .gz
head -n 40 data/samples/PriceFull....xml
```
