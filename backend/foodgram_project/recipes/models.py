from django.db import models

from users.models import User

COLOR_CHOICES = (
    ("#E26C2D", "Оранжевый"),
    ("#eb4034", "Зеленый"),
    ("#8908a3", "Фиолетовый"),
)


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name="Название ингридиента"
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name="Единица измерения"
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название тэга")
    color = models.CharField(max_length=200, choices=COLOR_CHOICES)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название рецепта")
    text = models.TextField(verbose_name="Описание рецепта")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор рецепта",
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="Amount", blank=True
    )
    tags = models.ManyToManyField(Tag, verbose_name="Тэги")
    cooking_time = models.PositiveIntegerField(
        default=1, verbose_name="Время приготовления"
    )
    image = models.ImageField(
        "Картинка", upload_to="recipes/", blank=True, null=True
    )

    def __str__(self):
        return self.name


class Amount(models.Model):
    amount = models.IntegerField(default=0, verbose_name="Количество")
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amout',
        verbose_name="Ингридиент"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe',
        verbose_name="Рецепт"
    )

    def __str__(self):
        return f"{self.recipe.name}-{self.ingredient.name}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепт",
    )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепт",
    )
