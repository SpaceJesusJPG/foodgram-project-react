from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, FavoriveViewSet, IngredientViewSet,
                    RecipeViewSet, ShoppingCartViewSet, SubscriptionViewSet,
                    TagViewSet)

app_name = "api"

router = routers.DefaultRouter()

router.register("tags", TagViewSet, basename="tags")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register(
    r"recipes/(?P<id>[\d]+)/favorite", FavoriveViewSet, basename="favorite"
)
router.register("users", CustomUserViewSet, basename="users")
router.register(
    r"users/(?P<id>[\d]+)/subscribe", SubscriptionViewSet, basename="subscribe"
)
router.register(
    r"recipes/(?P<id>[\d]+)/shopping_cart",
    ShoppingCartViewSet,
    basename="shopping_cart"
)

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
