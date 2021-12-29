# 
## Тестовое задание
На схеме вы видите навигационную схему приложения для работы с корпоративными картами.
Система не должна быть интегрирована ни с какими внешними продуктами, мы разрабатываем ее целиком с нуля, и внешние данные в нее просто будут импортировать сразу в бд.
Необходимо написать документацию для REST API такого приложения. В формате "метод - список параметров - формат результата".

## Зависимости

- Docker
- docker-compose

## Технологии

- [Django] - python фреймоворк для быстрого прототипирования
- [django-restframework] - REST API интерфейс
- [markdown] - Описание

## Установка и запуск

Установка и запуск происходит с помощью docker.

```sh
docker-compose up --build
```
открыть в браузере
<http://127.0.0.1:8010/>

## Структура url
- <http://127.0.0.1:8010/swagger/> swagger
- <http://127.0.0.1:8010/redoc/> redoc
- <http://127.0.0.1:8010/api/> RestAPI
    - <http://127.0.0.1:8010/api/login/> 
        - POST авторизация по логину и паролю:
            - Параметры тела запроса:
                - username: <string> - обязательный параметр
                - passsword: <string> - обязательный параметр
            - Response:
                - 200 успешная авторизация
                - 400 ошибка авторизации
    - <http://127.0.0.1:8010/api/login/code/> 
        - POST авторизация по пинкоду или отпечатку пальца 
            - Параметры:
                - token: <string> - обязательный параметр
                - pincode: <string> - pincode или fingerprint обязательный параметр
                - fingerprint: <string> - pincode или fingerprint обязательный параметр
            - Response:
                - 200 успешная авторизация
                - 400 ошибка авторизации
    - <http://127.0.0.1:8010/api/logout/> 
        - POST выход из системы 
            - Response:
                - 200 успешный выход из системы
                - 403 пользователь не авторизован
    - <http://127.0.0.1:8010/api/recovery/> 
        - GET запрос восстановления пароля 
            - Параметры:
                - username: <string> - Опционально обязательный параметр ( или first_name last_name patronymic birth_date - обязательны)
                - first_name: <string> - Опционально обязательный параметр ( или username обязателен)
                - last_name: <string> - Опционально обязательный параметр ( или username обязателен)
                - patronymic: <string> - Опционально обязательный параметр ( или username обязателен)
                - birth_date: <string> - Опционально обязательный параметр ( или username обязателен)
            - Response:
                - 201 В случае успеха создаётся обращение
                    - application/json:
                        - recoverytoken: string
                - 400 Ошибка валидации, пользователь с такими данными не идентифицирован 
        - POST сброс пароля 
            - Параметры:
                - recoverytoken: <string> - обязательный параметр
                - code: <string> - обязательный параметр
                - new_password: <string> - обязательный параметр
            - Response:
                - 200 В случае успеха установка нового пароля
                - 400 Ошибка валидации, пользователь с такими данными не найден
    - <http://127.0.0.1:8010/api/profile/> 
        - GET Получение данных пользователя
            - Response:
                - 200
                    - application/json:
                        - id: int - уникальный идентификатор пользователя
                        - bank_card: object Банковская карта по-умолчанию
                            - id: int - уникальный идентификатор банковской карты
                            - card_number: <string> номер карты
                            - month: <int> срок действия (номер месяца)
                            - year: <int> срок действия (номер года)  
                            - first_name: <string> имя владельца карта  
                            - last_name: <string> фамилия владельца карта  
                            - status: <string> статус (choice: 'NEW', 'ACTIVE', 'BLOCKED')
                            - is_default: bool карта по умолчанию
                        - first_name: <string> - имя пользователя
                        - last_name: <string> - фамилия пользователя
                        - patronymic: <string> - отчество пользователя
                        - birth_date: <date> - дата рождения пользователя
                        - is_pincode: <bool> - пользователь создал пинкод
                        - is_fingerprint: <bool> - пользователь создал отпечаток пальца
                        - total_amount_limit: <decimal> - Общий доступный лимит
                        - cash_amount_limit: <decimal> - доступный лимит снятия наличных
                        - buy_amount_limit: <decimal> - доступный лимит покупок
        - PATCH обновление данных пользователя
            - Параметры:
                - first_name: <string> - не обязательный параметр
                - last_name: <string> - не обязательный параметр
                - patronymic: <string> - не обязательный параметр
                - birth_date: <string> - не обязательный параметр
                - pincode: <string> - не обязательный параметр
                - fingerprint: <string> - не обязательный параметр
            
            - Response:
                - 200 В случае успешного обновления
                - 400 Ошибка валидации
    - <http://127.0.0.1:8010/api/operations/> 
        - GET Получение списка операций пользователя по всем картам отсортированный по дате создания
            - Параметры:
                - bankd_card: <int> - необязательный параметр, уничкальный идентификатор банковской карты
                - is_default: <bool> - необязательный параметр, операции по карте которая задана по умолчанию
            - Response:
                - 200
                    - application/json:
                        - nextpage: <int> - номер следующей страницы
                        - nextpage: <int> - номер предыдущей страницы
                        - count:  <int> - кол-во записей всего
                        - results: <array> - список операции по карте 
                            - id: int - уникальный идентификатор операции
                            - title: <string> - краткое описание операции
                            - amount: <decimal> - сумма операции
                            - created_dt: <date> - дата создания операции
                            - updated_dt: <date> - дата последнего обоновления операции
                            - status: <string> - статус операции (choice: 'NEW', 'PROCESS', 'BLOCKED', 'CLOSED', 'CANCEL')
                            
    - <http://127.0.0.1:8010/api/operations/<int:id>/> 
        - GET Получение операции пользователя по уникальному идентификатору карты
            - Url-Параметры:
                - id: <int> - обязательный параметр, уникальный идентификатор операции
            - Response:
                - 200 
                    - application/json:
                        - id: int - уникальный идентификатор операции
                        - title: <string> - краткое описание операции
                        - bank_card: Банковская карта
                            - id: <int> - уникальный идентификатор банковской карты
                            - card_number: <string> номер карты
                            - month: <int> срок действия (номер месяца)
                            - year: <int> срок действия (номер года)  
                            - first_name: <string> имя владельца карта  
                            - last_name: <string> фамилия владельца карта  
                            - status: <string> статус (choice: 'NEW', 'ACTIVE', 'BLOCKED')
                            - is_default: bool карта по умолчанию
                        - amount: <decimal> - сумма операции
                        - created_dt: <date> - дата создания операции
                        - updated_dt: <date> - дата последнего обоновления операции
                        - status: <string> - статус операции (choice: 'NEW', 'PROCESS', 'BLOCKED', 'CLOSED', 'CANCEL')
    - <http://127.0.0.1:8010/api/bankcards/> 
        - GET Получение списка бакновских кард привязанных к авторизованному пользотвателю
            - Параметры:
                - is_default: <bool> - необязательный параметр, карта по умолчанию
            - Response:
                - 200
                    - application/json:
                        - nextpage: <int> - номер следующей страницы
                        - nextpage: <int> - номер предыдущей страницы
                        - count:  <int> - кол-во операций всего
                        - results: <array> - список записей по карте 
                            - id: <int> - уникальный идентификатор банковской карты
                            - card_number: <string> номер карты
                            - month: <int> срок действия (номер месяца)
                            - year: <int> срок действия (номер года)  
                            - first_name: <string> имя владельца карта  
                            - last_name: <string> фамилия владельца карта  
                            - status: <string> статус (choice: 'NEW', 'ACTIVE', 'BLOCKED')
                            - is_default: bool карта по умолчанию
        - POST Добавлени новой карты для авторизованного пользователя
            - Параметры:
                - first_name: <string> - обязательный параметр, имя владельца карты
                - last_name: <string> - обязательный параметр, фамилия владельца карты
                - card_number: <string> - обязательный параметр, номер карты
                - month: <int> - обязательный параметр, срок действия карты месяц (range(1, 12))
                - year: <int> - обязательный параметр, срок действия карты год
                - is_default: <bool> - необязательный параметр, сделать карту по умолчанию
            - Response:
                - 201 В случае успешного добавления новой карты
                - 400 Ошибка валидации
    - <http://127.0.0.1:8010/api/bankcards/<int:id>/> 
        - GET Получение банковской карты пользователя по уникальному идентификатору карты
            - Url-Параметры:
                - id: <int> - обязательный параметр, уникальный идентификатор карты
            - Response:
                - id: <int> - уникальный идентификатор банковской карты
                - card_number: <string> номер карты
                - month: <int> срок действия (номер месяца)
                - year: <int> срок действия (номер года)  
                - first_name: <string> имя владельца карта  
                - last_name: <string> фамилия владельца карта  
                - status: <string> статус (choice: 'NEW', 'ACTIVE', 'BLOCKED')
                - is_default: bool карта по умолчанию
                - total_amount_limit: <decimal> - доступный лимит по карте
                - cash_amount_limit: <decimal> - доступный лимит снятия наличных по карте
                - buy_amount_limit: <decimal> - доступный лимит покупок по карте
        - PATCH Обновление информации банковской карты пользователя по уникальному идентификатору карты
            - Url-Параметры:
                - id: <int> - обязательный параметр, уникальный идентификатор карты
            - Параметры:
                - is_default: <bool> обязательный параметр, сделать карту по умолчанию
            - Response:
                - 200 В случае успешного обновления данных карты
                - 400 Ошибка валидации
    - <http://127.0.0.1:8010/api/profile/rate/>  
        - GET Получение данных пользователя об оценке приложения
            - Response:
                - 200 
                    - application/json:
                        - rate: <int> - оценка пользователя (defualt: 0 нет оценки)
                        - msg: <string> текстовый комментарий от пользоватея
        - POST Обновление данных пользователя об оценке приложения
            - Параметры:
                - rate: <int> - оценка пользователя (defualt: 0 нет оценки)
                - msg: <string> текстовый комментарий от пользоватея
            - Response:
                - 200 
                    - application/json:
                        - rate: <int> - оценка пользователя (defualt: 0 нет оценки)
                        - msg: <string> текстовый комментарий от пользоватея
    - <http://127.0.0.1:8010/api/feedbacks/>  
        - GET Получение списка обращений пользователя
            - Параметры:
                - feedback_type: <string> - необязательный параметр, тип обращения (choice: 'QUEST', 'PROBLEM', 'OPERATION', 'RECOVERY')
                    - QUEST - Обращение
                    - PROBLEM - Проблема
                    - OPERATION - Спорная операция
                    - RECOVERY - Востановление пароля
            - Response:
                - 200 
                    - application/json:
                        - nextpage: <int> - номер следующей страницы
                        - nextpage: <int> - номер предыдущей страницы
                        - count:  <int> - кол-во записей всего
                        - results: <array> - список операции по карте 
                            - id: <int> - уникальный идентификатор обращения
                            - feedback_type: <string> - тип обращения (choice: 'QUEST', 'PROBLEM', 'OPERATION', 'RECOVERY')
                            - status: <string> - cтатус обращения (choice: 'NEW', 'PROCESS', 'CLOSE' )
                            - created_dt: <datetime> - дата и время создания обращения
                            - updated_dt: <datetime> - дата и время последнего обновления
        - POST Создание обращения с типом  обращения QUEST
            - Параметры:
                - msg: <string> текстовый комментарий от пользователя
            - Response:
                - 201 
                    - application/json:
                        - id: <int> - уникальный идентификатор обращения
                        - feedback_type: <string> - тип обращения (choice: 'QUEST', 'PROBLEM', 'OPERATION', 'RECOVERY')
                        - status: <string> - cтатус обращения (choice: 'NEW', 'PROCESS', 'CLOSE' )
                        - created_dt: <datetime> - дата и время создания обращения
                        - updated_dt: <datetime> - дата и время последнего обновления
    - <http://127.0.0.1:8010/api/feedbacks/<int:id>/>  
        - GET Получение обращения пользователя по уникальному идентификатору
            - Url-Параметры:
                - id: <int> - обязательный параметр, уникальный идентификатор обращения
            - Response:
                - 200 
                    - application/json:
                        - id: <int> - уникальный идентификатор обращения
                        - feedback_type: <string> - тип обращения (choice: 'QUEST', 'PROBLEM', 'OPERATION', 'RECOVERY')
                        - status: <string> - cтатус обращения (choice: 'NEW', 'PROCESS', 'CLOSE' )
                        - created_dt: <datetime> - дата и время создания обращения
                        - updated_dt: <datetime> - дата и время последнего обновления
                        - msg: <string> - текстовый комментарий от пользователя
                        - answer: <string> - ответ на обращение
                        - bank_card: object(default: null) Банковская карта по которой было обращение 
                            - id: int - уникальный идентификатор банковской карты
                            - card_number: <string> номер карты
                            - month: <int> срок действия (номер месяца)
                            - year: <int> срок действия (номер года)  
                            - first_name: <string> имя владельца карта  
                            - last_name: <string> фамилия владельца карта  
                            - status: <string> статус (choice: 'NEW', 'ACTIVE', 'BLOCKED')
                            - is_default: bool карта по умолчанию
                        - bank_card: object(default: null) Банковская карта по которой было обращение 
                            - id: int - уникальный идентификатор банковской карты
                            - card_number: <string> номер карты
                            - month: <int> срок действия (номер месяца)
                            - year: <int> срок действия (номер года)  
                            - first_name: <string> имя владельца карта  
                            - last_name: <string> фамилия владельца карта  
                            - status: <string> статус (choice: 'NEW', 'ACTIVE', 'BLOCKED')
                            - is_default: bool карта по умолчанию
                        - operation: object(default: null) операция по которой было обращение
                            - id: int - уникальный идентификатор операции
                            - title: <string> - краткое описание операции
                            - amount: <decimal> - сумма операции
                            - created_dt: <date> - дата создания операции
                            - updated_dt: <date> - дата последнего обоновления операции
                            - status: <string> - статус операции (choice: 'NEW', 'PROCESS', 'BLOCKED', 'CLOSED', 'CANCEL')
    - <http://127.0.0.1:8010/api/bankcards/<int:bank_card_id>/feedbacks/>  
        - POST создание обращения по банковской карте
            - Url-Параметры:
                - bank_card_id: <int> - обязательный параметр, уникальный идентификатор банковской карты
            - Response:
                - 201 
                    - application/json:
                        - id: <int> - уникальный идентификатор обращения
                        - feedback_type: <string> - тип обращения (choice: 'QUEST', 'PROBLEM', 'OPERATION', 'RECOVERY')
                        - status: <string> - cтатус обращения (choice: 'NEW', 'PROCESS', 'CLOSE' )
                        - created_dt: <datetime> - дата и время создания обращения
                        - updated_dt: <datetime> - дата и время последнего обновления
                        - bank_card: object Банковская карта по которой было обращение 
                            - id: int - уникальный идентификатор банковской карты
                            - card_number: <string> номер карты
                            - month: <int> срок действия (номер месяца)
                            - year: <int> срок действия (номер года)  
                            - first_name: <string> имя владельца карта  
                            - last_name: <string> фамилия владельца карта  
                            - status: <string> статус (choice: 'NEW', 'ACTIVE', 'BLOCKED')
                            - is_default: bool карта по умолчанию
    - <http://127.0.0.1:8010/api/operations/<int:operation_id>/feedbacks/>  
        - POST создание обращения по операции
            - Url-Параметры:
                - operation_id: <int> - обязательный параметр, уникальный идентификатор операции
            - Response:
                - 201 
                    - application/json:
                        - id: <int> - уникальный идентификатор обращения
                        - feedback_type: <string> - тип обращения (choice: 'QUEST', 'PROBLEM', 'OPERATION', 'RECOVERY')
                        - status: <string> - cтатус обращения (choice: 'NEW', 'PROCESS', 'CLOSE' )
                        - created_dt: <datetime> - дата и время создания обращения
                        - updated_dt: <datetime> - дата и время последнего обновления
                        - operation: object Банковская карта по которой было обращение 
                            - id: int - уникальный идентификатор операции
                            - title: <string> - краткое описание операции
                            - amount: <decimal> - сумма операции
                            - created_dt: <date> - дата создания операции
                            - updated_dt: <date> - дата последнего обоновления операции
                            - status: <string> - статус операции (choice: 'NEW', 'PROCESS', 'BLOCKED', 'CLOSED', 'CANCEL')

## Структура Приложения и запросов
- Авторизация
    - по логину и паролю - <http://127.0.0.1:8010/api/login/> 
    - по тouchID или пинкоду - <http://127.0.0.1:8010/api/login/code/>
- Главный экран
    - Данные профиля <http://127.0.0.1:8010/api/profile/>
    - Список операций <http://127.0.0.1:8010/api/operations/>
- Блокировка карты
    - создать обращение <http://127.0.0.1:8010/api/bankcards/<int:bank_card_id>/feedbacks/> 
    - список карт <http://127.0.0.1:8010/api/bankcards/> 
- Оценка приложения
    - получить или создать оценку <http://127.0.0.1:8010/api/profile/rate/>
- Обращения
    - список всех обращений <http://127.0.0.1:8010/api/feedbacks/>
