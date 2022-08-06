from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from recipes.models import (Amount, Favorite, Ingredient, Recipe, ShoppingCart,
                            Tag)
from users.models import Subscription, User

from .filters import IngredientSearchFilter, RecipeFilter
from .mixins import CreateDestroyViewSet, ListRetrieveViewSet
from .pagination import CustomPageNumberPagination
from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          FavoriteSerializer, IngredientSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionListSerializer,
                          SubscriptionSerializer, TagSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create":
            return CustomUserCreateSerializer
        if self.action == "me":
            return CustomUserSerializer
        if self.action == "subscriptions":
            return SubscriptionListSerializer
        return super().get_serializer_class()

    @action(
        methods=[
            "GET",
        ],
        url_path="subscriptions",
        detail=False,
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing_to__subscriber=user)
        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RecipeListSerializer
        return RecipeSerializer

    @action(
        methods=[
            "GET",
        ],
        url_path="download_shopping_cart",
        detail=False
    )
    def download_shopping_cart(self, request):
        shopping_list = {}
        user = request.user
        recipe_queryset = Recipe.objects.filter(shopping_cart__user=user)
        for recipe in recipe_queryset:
            amount_queryset = Amount.objects.filter(recipe=recipe)
            for amount in amount_queryset:
                if (
                    f'{amount.ingredient}'
                    f'({amount.ingredient.measurement_unit})'
                ) in shopping_list:
                    amount_int = shopping_list[
                        f'{amount.ingredient} '
                        f'({amount.ingredient.measurement_unit})'
                    ]
                    amount_sum = amount_int + amount.amount
                    shopping_list[
                        f'{amount.ingredient} '
                        f'({amount.ingredient.measurement_unit})'
                    ] = amount_sum
                else:
                    shopping_list[
                        f'{amount.ingredient} '
                        f'({amount.ingredient.measurement_unit})'
                    ] = amount.amount
        text = []
        for key, value in shopping_list.items():
            text += f'{key} - {value}\n'
        response = HttpResponse(text, content_type='text/plain')
        return response


class FavoriveViewSet(CreateDestroyViewSet):
    model_class = Recipe
    model_string = 'recipe'
    queryset_model = Favorite
    serializer = FavoriteSerializer
    error = "Такого избранного не существует."


class ShoppingCartViewSet(CreateDestroyViewSet):
    model_class = Recipe
    model_string = 'recipe'
    queryset_model = ShoppingCart
    serializer = ShoppingCartSerializer
    error = "Этот рецепт не был добавлен в список покупок."


class SubscriptionViewSet(CreateDestroyViewSet):
    model_class = User
    model_string = 'user'
    error = "Такой подписки не существует."

    def get_queryset(self):
        user = self.request.user
        return Subscription.objects.filter(subscriber=user)

    def get_serializer(self, id):
        return SubscriptionSerializer(
            data={
                "subscriber": self.request.user.id,
                "user": id,
            },
            context={
                "request": self.request,
            },
        )
