# Мини-апп для личных финансов: что есть и стоит ли

**1. Можно ли переиспользовать готовое?** Готового приложения под твой случай нет, но готовые движки учёта и Telegram-боты для ввода есть, и их можно взять за основу.
*Что изменит вывод:* появление готового продукта, который уже импортирует выписки George (личный счёт) и monobank и держит EUR, UAH и USD.

**2. Стоит ли идти в Mini App?** Да, как эксперимент и для опыта, но как витрину и экран ввода поверх отдельного хранилища, а не как единственное место учёта.
*Что изменит вывод:* «не стоит», если пробный прототип окажется нестабильным на iPhone (в исследовании этого не проверяли) или ввод через Mini App выйдет медленнее, чем одной фразой в бот.

**3. Что можно изучать?** Идеи, интерфейсы и модели данных из открытого кода и публичных документов изучать можно, а копировать чужой код без лицензии нельзя; декомпилировать (разбирать программу до кода) чужие приложения можно только ради совместимости.
*Что изменит вывод:* проверка австрийского закона об авторском праве (UrhG), которую в исследовании не делали.

Похожие проекты есть, но разнесены по частям: движки учёта с API, боты для ввода и Mini App-дашборд поверх Firefly III (miguel-bm, MIT). Ни один найденный продукт не сводит вместе EUR, UAH и USD, счета, активы и импорт твоих банков; поддержку UAH в движках мы не проверяли. Erste возможен через посредника Enable Banking, но личный доступ не проверен. Для monobank есть официальный личный API, для PrivatBank личного API не нашли. Telegram-хранилища слишком малы и не гарантируют сохранность, поэтому учёт должен лежать в движке или базе, которые контролируешь ты.

## Движки учёта готовы, но без Telegram и без твоих банков
**Надёжность: высокая.** Данные GitHub и документации API проверены на 31 октября 2026 года; сценарии с валютами проверены не везде.

Движок учёта - готовая программа, которую ставят на свой сервер. Звёзды GitHub - аналог лайков. Ниже проекты, по которым проверены данные GitHub и документация.

| Движок | Что умеет | Подключение программно | Лицензия, популярность | Оговорка |
|---|---|---|---|---|
| [Firefly III](https://github.com/firefly-iii/firefly-iii) | счета, бюджеты, валюты | API; вход по разрешению (OAuth2) или личный токен (ключ доступа) | AGPL-3.0; 25 045 звёзд | конвертация по курсам не проверена |
| [Sure](https://github.com/we-promise/sure) | счета, чистая стоимость, держания и сделки, несколько валют | API с описанием OpenAPI; ключ или OAuth2 | AGPL-3.0; 10 736 звёзд | продолжение Maybe Finance |
| [Securo](https://github.com/securo-finance/securo) | счета, банки через Enable Banking, пересчёт валют | публичного API нет; вход по логину | AGPL-3.0; создан в марте 2026 | без ключа курсов суммы в другой валюте считаются по курсу 1:1 |
| [ezBookkeeping](https://github.com/mayswind/ezbookkeeping) | мультивалютность с курсами; импорт Firefly III и Camt.053 (формат банковских выписок) | API не проверяли | MIT; 5 893 звёзд | банковского подключения нет |
| [Actual Budget](https://github.com/actualbudget/actual) | бюджеты, Enable Banking | HTTP-API нет, только клиент для Node.js | MIT; 29 879 звёзд | нужна своя обёртка |

Лицензии: MIT почти ничем не ограничивает; AGPL требует открыть изменённую версию, если её дают по сети, а GPL - если её передают другим людям. Для личного учёта это не важно, для продажи клиентам важно. [Maybe Finance](https://github.com/maybe-finance/maybe) (54 206 звёзд) в архиве с июля 2025 года и не годится за основу.

У Firefly III описан API ([документация](https://docs.firefly-iii.org/api/)), поэтому он и Sure ближе всего к роли основы; у Sure подтверждены баланс, держания и сделки ([описание API](https://github.com/we-promise/sure/tree/main/docs/api)). Ни в одном проверенном движке нет импорта monobank или PrivatBank: проверены документации Firefly III, Actual и Securo. Готовый монобанк-импортер для Firefly III последний раз обновлялся в январе 2024 года и без лицензии (только читать, не форкать без разрешения автора; форк - своя копия кода) ([репозиторий](https://github.com/mariko357/fireflyiii-monobank-importer)).

## Erste через посредника, monobank через свой код, PrivatBank вручную
**Надёжность: средняя.** Условия посредника и правила ЕС проверены; доступ к личным счетам George и PrivatBank - нет.

PSD2 - европейское правило открытого банкинга: банк открывает данные счёта стороннему сервису с согласия клиента. Посредник Enable Banking подключает банки. Его условия от 9 января 2026 года делают панель управления и API бесплатными, а боевой доступ открывают для личного использования. Число подключённых счетов «может быть ограничено» и не опубликовано, бизнес-счета не покрыты ([условия](https://enablebanking.com/terms/)). Erste Bank стоит первой в списке главных австрийских банков, интеграция поддерживается (обновление в журнале изменений за июнь 2026) ([Enable Banking AT](https://enablebanking.com/docs/markets/at/)). Подключение твоего George мы не проверяли: нужен аккаунт в панели Enable Banking. Повторное подтверждение доступа требуется, когда прошло более 180 дней; так устроено правило с 25 июля 2023 года ([EUR-Lex](https://eur-lex.europa.eu/eli/reg_del/2022/2360/oj)). Выгрузка George в CSV, Excel и JSON описана только для George Business ([Sparkasse](https://www.sparkasse.at/en/george-help/george-business/transactions-and-search/print-and-export/download---export-your-account-history)); для личного счёта это не подтверждено.

GoCardless, другой посредник из открытых проектов, закрыл регистрацию новых аккаунтов; официальное уведомление есть, даты в нём нет ([GoCardless](https://bankaccountdata.gocardless.com/new-signups-disabled)).

monobank даёт официальный личный API ([документация](https://api.monobank.ua/docs/)). Токен выдают в личном кабинете, выписка отдаётся за период до 31 дня и 1 часа, запросы не чаще раза в 60 секунд. Есть вебхук: сервис сам присылает новые операции. Личный API рассчитан на себя и семью; для сервиса, которым пользуются другие люди, по тексту документации нужен корпоративный доступ.

PrivatBank: личного API для выписок не нашли; найденные клиенты рассчитаны на бизнес-версию Privat24 (по поиску, не проверено). Рабочий путь - ручная выгрузка из приложения, её формат надо проверить самим. Надёжность по PrivatBank низкая.

## Telegram-продукты продают ввод расходов, но не счета и активы
**Надёжность: средняя.** Страницы продуктов проверены; выручку называют сами сервисы.

| Продукт | Тип | Цена (как на сайте) | Что важно | Сигнал |
|---|---|---|---|---|
| Cointry | бот | Free $0; Premium $2.5 в месяц при годовой оплате | бюджеты, мультивалютность, голос - в Premium; запущен в 2022 ([Product Hunt](https://www.producthunt.com/products/cointry)) | не показан |
| Tabby | бот + веб | Free $0; Pro $24.99 в год; 14 дней без карты | мультивалютность по курсу в Free; к банкам не подключается ([сайт](https://tabbyfinance.app)) | не показан |
| Kopilo | Mini App | 7 дней бесплатно; платная цена не найдена | 50+ валют, общие бюджеты; один разработчик | 7 подписчиков и 0 отзывов на Product Hunt |
| TeleExpense Tracker | бот + Google Sheets | не указана | читает банковские уведомления, банки не названы | 29 активных подписок, MRR $68 (выручка подтверждена Stripe, по [TrustMRR](https://trustmrr.com/startup/teleexpense-tracker)) |
| FinNotes | Mini App | не указана | только расходы; экспорт в Excel и Notion | автор: 30 000-50 000 руб. в месяц (со слов автора) |

В найденных продуктах счетов и активов не видно: все они про расходы. Cointry - самый полный по функциям, но бюджеты, мультивалютность и голос у него платные, а запущен он в 2022 году, не в 2026 ([Product Hunt](https://www.producthunt.com/products/cointry)).

## Mini App учит Telegram, но не держит деньги
**Надёжность: средняя** для платформы (официальные страницы проверены); **низкая** для спроса и карьеры.

Mini App - веб-страница, которую Telegram открывает внутри себя. Её хранилища маленькие: облачное хранилище держит 1 024 записи по 4 096 символов, на устройстве - 5 МБ, защищённое - 10 записей ([Telegram](https://core.telegram.org/bots/webapps)). Условия разработчика возлагают на тебя безопасное хранение данных и активов, Telegram не гарантирует сохранность облачных данных, а при утрате аккаунта созданные им приложения могут быть закрыты ([условия](https://telegram.org/tos/bot-developers)). Значит, учёт нельзя держать только в Telegram.

Telegram Serverless (страница обновлена 6 октября 2026 года) - хостинг, где код запускает сам Telegram: Mini App-хостинг, функции на JavaScript и база SQLite (база в одном файле). В документации есть раздел «Building with AI» ([Serverless](https://core.telegram.org/bots/serverless)). Цена, статус бета или открытой версии, место хранения и шифрование не указаны. Условия разработчика пока описывают хостинг на собственных серверах. Внутри Serverless нет библиотек npm (склад готового кода на JavaScript), а в сеть код ходит только через встроенный `fetch` из SDK (набора инструментов для разработчика). Запросы к API банков технически возможны, но подключение Enable Banking там нужно проверить отдельно.

Правила меняются часто: версия 10.2 (14 июля 2026) запрещает Mini App вызывать методы из чужих доменов, с 20 июля это включено для всех ([changelog](https://core.telegram.org/bots/api-changelog)). Альтернатива - PWA, сайт на экране телефона; на iPhone он получает уведомления только после установки на экран ([WebKit](https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/)).

Гибрид уже существует: miguel-bm связывает бота и Mini App-дашборд поверх Firefly III (не запускали, 0 звёзд). Kopilo, Mini App-only учёт одного разработчика, пишет, что баг чёрного экрана в WebKit (движке, который показывает веб-страницы на iPhone) «съел» два дня ([Indie Hackers](https://www.indiehackers.com/post/building-a-liquid-glass-finance-tracker-for-telegram-solo-dev-xBgVJgRvdITLGUgOrepV)). Сроки в кейсах - самоотчёты: агентство заявляет 7 рабочих дней и цену менее 300 000 руб. против от 600 000 руб. у нативного приложения, без базы сравнения ([Vibes](https://www.sostav.ru/blogs/280723/58933)). Adjust: через 30 дней в межотраслевых данных остаётся 7% пользователей, отдельной цифры для финансов нет ([Adjust](https://www.adjust.com/blog/what-makes-a-good-retention-rate/)).

Украина. Ограничение, принятое в сентябре 2024 года, касается служебных устройств госорганов, военных и критической инфраструктуры ([DOU](https://dou.ua/lenta/news/regulation-telegram-in-ukraine/)). Законопроект 11115 комитет рекомендовал к первому чтению в марте 2026 года; блокировки он не предусматривает ([Ligazakon](https://biz.ligazakon.net/news/243127_komitet-vr-odobril-zakonoproekt-o-regulirovanii-telegram-chto-izmenitsya-dlya-polzovateley-i-biznesa)). Утверждение, что прямой запрет для частных пользователей не предусмотрен, принадлежит депутату, главе комитета Рады, а не правительству ([Mezha](https://mezha.net/eng/news/ukraine_will_not/)). Для личного приложения риск низкий, но служебный телефон может попасть под ограничение.

Карьера и продажи: подтверждённого спроса мы не нашли. Есть только вендорские цены: фриланс-разработка Mini App от $2 000 до $15 000, без методики ([CyberPanel](https://cyberpanel.net/blog/how-to-hire-telegram-mini-app-developers-in-2025)). Данных о спросе малого бизнеса на Mini App или AI-автоматизацию в Австрии, ЕС и Украине нет. Mini App учит в основном особенностям Telegram; связка бота, таблицы или базы и ИИ-агента ближе к процессам, которые можно продавать. Это вывод из источников, уверенность средняя.

## Идеи изучать можно, чужой код без лицензии - нет
**Надёжность: высокая** для правовых норм (тексты ЕС проверены); **средняя** для описаний репозиториев.

| Проект | Что изучать | Лицензия | Как использовать |
|---|---|---|---|
| [miguel-bm/firefly-iii-telegram-bot](https://github.com/miguel-bm/firefly-iii-telegram-bot) | ввод фразой и голосом; Mini App-дашборд | MIT | можно форкать; 0 звёзд, не запускали |
| [ilramdhan/dompetku](https://github.com/ilramdhan/dompetku) | чистая стоимость, счета, учёт чеков по фото через ИИ | MIT | можно форкать; валюты IDR и USD, не Mini App |
| [cyxou/firefly-iii-telegram-bot](https://github.com/cyxou/firefly-iii-telegram-bot) | полный набор команд к Firefly III; файлы правил для ИИ-агентов | GPL-3.0 | 70 звёзд; голосового ввода нет; производные работы - под GPL |
| [bbharathbala/actual-budget-telegram-bot](https://github.com/bbharathbala/actual-budget-telegram-bot) | учёт чеков без языковых моделей | MIT | можно форкать; 18 звёзд |
| [sofiy_qwen](https://github.com/xetus476/sofiy_qwen); [KidCoderT/beancounter](https://github.com/KidCoderT/beancounter); [quicktrack-expenses-mini-app](https://github.com/AdoniasMulugeta/quicktrack-expenses-mini-app) | экраны бюджета и аналитики; Mini App по адресу /app (только просмотр); простой Mini App без фреймворка | нет | только читать, не форкать без разрешения автора |
| ZenMoney | модель данных: валюта, банк, счёт, категория, получатель; синхронизация по изменениям | коммерческое | идеи, без кода; 199 руб. в месяц, 1 490 руб. в год |
| YNAB, Copilot, Monarch, Kubera | UX и сценарии чистой стоимости; API YNAB: 200 запросов в час на токен | коммерческие | пользоваться как клиент; ориентир: YNAB и Copilot $109 в год, Monarch Core $99.99 в год |

Директива ЕС 2009/24/EC разрешает изучать работу программы, пока ты её законно используешь (ст. 5(3)). Идеи и принципы, в том числе лежащие в основе интерфейсов, не защищены (ст. 1(2)). Декомпилировать код можно только ради совместимости (ст. 6), и договор не может этого отменить (ст. 8) ([EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024)). Значит, изучаешь поведение, структуру и модели данных, но не копируешь тексты, иконки, код и наборы данных. Скрипты, которые входят в банк по логину и паролю, не берём: это риск и по условиям банка, и по безопасности.

## Что это меняет
Главный сдвиг: нужна сборка из уже существующих частей (движок учёта, бот для ввода, витрина, посредник для банка), а не одна готовая вещь. Учебная польза Mini App - в навыке соединять эти части, а не в интерфейсе. Самое неясное место - банки: Erste возможен через посредника с ограничениями, monobank требует собственного кода, PrivatBank - ручной выгрузки.

**Надёжность: средняя.** Выводы опираются на проверенные факты; вывод о карьерной ценности - инференция из источников.

## Что взять на этап выбора стека

**Надёжность: средняя.** Пункты взяты из разделов выше; ни один вариант здесь не выбран.

1. Где лежит учёт: готовый движок (Firefly III, Sure, Securo, ezBookkeeping), собственная база или Telegram Serverless. Решают хранение, выгрузка и условия Telegram.
2. Статус Telegram Serverless: бета или открытая версия, цена, место хранения и шифрование. Спросить у Telegram или проверить в настройках BotFather.
3. Erste: личный доступ через Enable Banking на твоём George; лимит счетов не опубликован, подтверждение нужно раз в 180 дней.
4. George: API через посредника или ручная выгрузка CSV.
5. monobank: собственный импортёр через личный API (1 запрос в минуту, до 31 дня за запрос) или через вебхук.
6. PrivatBank: ручная выгрузка из Privat24 (формат проверить) или ввод вручную.
7. Ввод: только бот или бот плюс Mini App-дашборд.
8. Валюты: как считать EUR, UAH и USD. Securo без ключа курсов даёт курс 1:1; у Firefly III конвертация не проверена.
9. Лицензии: AGPL у Firefly III, Sure и Securo - проверить до продажи клиентам.
10. Конфиденциальность: условия требуют политику конфиденциальности в @BotFather даже для Mini App; применимость GDPR к личному приложению не проверяли.
11. SDK (набор инструментов для разработчика) Mini App: @tma.js актуален, четыре пакета @telegram-apps помечены как устаревшие.

## Приложение. Источники, ограничения и что не проверено

**Надёжность приложения:** официальные страницы Telegram, EUR-Lex и данные GitHub - высокая; цены и выручка со слов сервисов - средняя. Утверждения, которые нашли только в поисковой выдаче, в отчёт как факты не вошли.

**Источники**

Telegram и условия:
1. https://core.telegram.org/bots/webapps
2. https://core.telegram.org/bots/api-changelog
3. https://core.telegram.org/bots/serverless
4. https://telegram.org/tos/bot-developers
5. https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/

Право и банки:
6. https://eur-lex.europa.eu/eli/reg_del/2022/2360/oj
7. https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32009L0024
8. https://enablebanking.com/terms/
9. https://enablebanking.com/docs/markets/at/
10. https://github.com/actualbudget/actual
11. https://bankaccountdata.gocardless.com/new-signups-disabled
12. https://www.sparkasse.at/en/george-help/george-business/transactions-and-search/print-and-export/download---export-your-account-history
13. https://api.monobank.ua/docs/

Движки и открытый код:
14. https://docs.firefly-iii.org/api/
15. https://github.com/firefly-iii/firefly-iii
16. https://github.com/we-promise/sure
17. https://github.com/we-promise/sure/tree/main/docs/api
18. https://github.com/securo-finance/securo
19. https://github.com/mayswind/ezbookkeeping
20. https://actualbudget.org/docs/api/
21. https://github.com/maybe-finance/maybe
22. https://github.com/mariko357/fireflyiii-monobank-importer
23. https://github.com/miguel-bm/firefly-iii-telegram-bot
24. https://github.com/ilramdhan/dompetku
25. https://github.com/cyxou/firefly-iii-telegram-bot
26. https://github.com/bbharathbala/actual-budget-telegram-bot
27. https://github.com/xetus476/sofiy_qwen
28. https://github.com/KidCoderT/beancounter
29. https://github.com/AdoniasMulugeta/quicktrack-expenses-mini-app
30. https://www.npmjs.com/package/@tma.js/sdk
31. https://www.npmjs.com/package/@telegram-apps/bridge

Продукты и рынок:
32. https://cointry.io
33. https://www.producthunt.com/products/cointry
34. https://tabbyfinance.app
35. https://www.producthunt.com/products/kopilo
36. https://trustmrr.com/startup/teleexpense-tracker
37. https://t-j.ru/we-started-telegram-mini-app-for-financial-accounting/
38. https://www.indiehackers.com/post/building-a-liquid-glass-finance-tracker-for-telegram-solo-dev-xBgVJgRvdITLGUgOrepV
39. https://hackernoon.com/building-a-business-app-on-telegram-4-lessons-we-learned-the-hard-way
40. https://www.sostav.ru/blogs/280723/58933
41. https://cyberpanel.net/blog/how-to-hire-telegram-mini-app-developers-in-2025
42. https://www.adjust.com/blog/what-makes-a-good-retention-rate/
43. https://dou.ua/lenta/news/regulation-telegram-in-ukraine/
44. https://biz.ligazakon.net/news/243127_komitet-vr-odobril-zakonoproekt-o-regulirovanii-telegram-chto-izmenitsya-dlya-polzovateley-i-biznesa
45. https://mezha.net/eng/news/ukraine_will_not/

Коммерческие приложения:
46. https://www.ynab.com/pricing
47. https://api.ynab.com/
48. https://www.copilot.money/pricing
49. https://www.monarch.com/pricing
50. https://kubera.com/
51. https://zenmoney.ru/a/

**Не подтверждено или не проверено**
- Статус, цена, место хранения и шифрование Telegram Serverless: на странице их нет; сообщения о раннем доступе из поиска не подтверждены.
- Личный доступ к счёту Erste через Enable Banking, лимит счетов, личный экспорт George.
- Выписки PrivatBank и личный API PrivatBank: только поиск, страницы не открывались.
- Дата закрытия GoCardless «июль 2025»: указана только в документации Actual.
- Cointry: в бесплатном тарифе написано «поддержка любой валюты», но конвертация в бесплатном тарифе не подтверждена.
- Поддержка UAH и конвертация курсов в Firefly III и Sure; API Securo и ezBookkeeping.
- Работа miguel-bm, dompetku и cyxou: описания и README прочитаны, код не запускали.
- Австрийский закон UrhG, GDPR для личных финансов, налоговые вопросы.
- Рейтинги в Google Play не собирались.

**Ограничения**
- Аккаунты в банках и сервисах не создавали, ничего не запускали и не клонировали. Данные GitHub и тарифов актуальны на 31 октября 2026 года.
- Два репозитория из первичных заметок отвечают 404, в отчёт они не вошли.
- В одном поисковом сниппете страницы документации Monobank был текст, адресованный ИИ-инструментам; на самой странице такого текста не нашли, и инструкции из него не выполнялись.
- Значения взяты после проверки всех шести файлов заметок: исправленные значения стоят вместо прежних, неподтверждённые убраны или помечены «не подтверждено».
