## <h1 align="center"> Проект Foodgram </h1>


## Описание
Проект Foodgram предостовляет возможность публиковать рецепты, подписываться на любимых авторов, добавлять рецепты в избранное и список покупок, который так же позволяет скачать список всех необходимых ингридиентов для рецептов, находяшихся в этом списке.


### Используемые технологии:

* Python 3.7
* Django 3.2.15
* Django Rest Framework 3.13
* Djoser
* nginx
* Docker
* Docker-Compose

### Посмотреть уже развернутый проект:

[Foodgram](http://51.250.105.244/)

Примеры запросов к API и документацию можно посмотреть [тут](http://51.250.105.244/api/docs/)


### Как развернуть проект локально:

Клонировать репозиторий и перейти в папку с инструкциями в командной строке: 
``` 
git clone git@github.com:SpaceJesusJPG/foodgram-project-react.git
``` 
```
cd foodgram-project-react/infra 
``` 
Собрать контейнер, выполнить миграции и собрать статику: 
``` 
docker-compose up -d
``` 
``` 
docker-compose exec web python manage.py migrate 
``` 
``` 
docker-compose exec web python manage.py collectstatic --no-input 
``` 
### Автор: 

* [Никита Гладышев](https://github.com/SpaceJesusJPG) 