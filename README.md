# BTR  Behave-TestRail-Reporter
Это сервис для:
-
* Cоздания тест-кейсов на основе BDD(Behave) в TestRail
* Поиска тест-кейсов на основе BDD(Behave) в TestRail
* Отправки результатов тест-кейсов на основе BDD(Behave) в TestRail

Для начала работы нужно:
-
* Создать фаил testrail.yml в папке feature
* Заполнить фаил testrail.yml в формате:
    * base_url : '' (адрес Вашего сервера TestRail **без http://**) 
    * username : '' 
    * password : ''
    * project_id : int (id проекта в TestRail)
    

* Добвить в before_all строки: 
    "reporter = TReporter()"
    "context.config.reporters.append(reporter)"
    
**Может понадобится создать секцию в TestRail**