from django.contrib.auth import authenticate
from djoser.serializers import (TokenCreateSerializer, UserCreateSerializer,
                                UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (Amount, Favorite, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Subscription, User


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(subscriber=user, user=obj).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("__all__",)


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = Amount
        fields = ("id", "name", "measurement_unit", "amount")


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = Amount
        fields = ("id", "amount")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ("__all__",)


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True,
        source='ingredient_recipe'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = "__all__"

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        user = request.user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=request.user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        user = request.user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = AmountSerializer(many=True)
    cooking_time = serializers.IntegerField(required=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "ingredients",
            "tags",
            "name",
            "text",
            "cooking_time",
            "image"
        )

    def validate(self, data):
        ingredients = data["ingredients"]
        if not ingredients:
            raise serializers.ValidationError(
                {"ingredient:": "Список ингридиентов не может быть пустым."}
            )
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredient': 'Ингредиенты должны быть уникальными.'
                })
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount':
                    'Количество ингредиентов должно быть больше нуля.'
                })
        if data["cooking_time"] < 0:
            raise serializers.ValidationError({
                "cooking_time":
                "Время приготовления не может быть отрицательным."
            })
        name = data["name"]
        author = self.context.get("request").user
        if (
            Recipe.objects.filter(name=name, author=author).exists()
            and self.context.get("request").method != 'PATCH'
        ):
            raise serializers.ValidationError({
                "validation_error:":
                "Вы уже создавали рецепт с таким названием."
            })
        return data

    @staticmethod
    def create_amounts(recipe, amounts):
        Amount.objects.bulk_create(
            [
                Amount(
                    recipe=recipe,
                    ingredient=amount["id"],
                    amount=amount["amount"],
                )
                for amount in amounts
            ]
        )

    def create(self, validated_data):
        user = self.context.get("request").user
        amounts = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(**validated_data, author=user)
        recipe.tags.set(tags)
        self.create_amounts(recipe, amounts)
        return recipe

    def update(self, instance, validated_data):
        amounts = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        Amount.objects.filter(recipe=instance).delete()
        instance.tags.clear()
        instance.tags.set(tags)
        self.create_amounts(instance, amounts)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return RecipeListSerializer(instance, context=context).data


class SmallRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class CustomSerializer(serializers.ModelSerializer):
    model_class = None
    attr_string_list = ['user', 'recipe']
    error = None

    def validate(self, data):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        attrs = {}
        for i in range(len(self.attr_string_list)):
            attrs[self.attr_string_list[i]] = data[self.attr_string_list[i]]
        if self.model_class.objects.filter(**attrs).exists():
            raise serializers.ValidationError(
                {self.attr_string_list[0]: self.error}
            )
        return data

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return SmallRecipeSerializer(instance.recipe, context=context).data


class FavoriteSerializer(CustomSerializer):
    model_class = Favorite
    error = 'Рецепт уже добавлен в избранное.'

    class Meta:
        model = Favorite
        fields = ("user", "recipe")


class ShoppingCartSerializer(CustomSerializer):
    model_class = ShoppingCart
    error = "Вы уже добавили рецепт в список покупок."

    class Meta:
        model = ShoppingCart
        fields = ("user", "recipe")


class SubscriptionSerializer(CustomSerializer):
    model_class = Subscription
    attr_string_list = ['subscriber', 'user']
    error = 'Вы уже подписаны на этого пользователя.'

    class Meta:
        model = Subscription
        fields = ("subscriber", "user")

    def to_representation(self, instance):
        request = self.context.get("request")
        context = {"request": request}
        return SubscriptionListSerializer(instance.user, context=context).data


class SubscriptionListSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.only("id", "name", "image", "cooking_time")
        return SmallRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CustomTokenCreateSerializer(TokenCreateSerializer):
    email = serializers.CharField(
        required=False,
        style={"input_type": "email"}
    )

    def validate(self, attrs):
        password = attrs.get("password")
        params = {'email': attrs.get('email')}
        self.user = authenticate(
            request=self.context.get("request"), **params, password=password
        )
        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user and self.user.is_active:
            return attrs
        self.fail("invalid_credentials")
