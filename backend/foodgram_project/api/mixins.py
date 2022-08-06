from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response


class CreateDestroyViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    model_class = None
    model_string = None
    serializer = None
    queryset_model = None

    def get_queryset(self):
        user = self.request.user
        return self.queryset_model.objects.filter(user=user)

    def get_serializer(self, id):
        return self.serializer(
            data={
                "user": self.request.user.id,
                "recipe": id,
            },
            context={
                "request": self.request,
            },
        )

    def create(self, request, id):
        serializer = self.get_serializer(id)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        obj = {
            str(self.model_string):
            get_object_or_404(self.model_class, id=id)
        }
        queryset = self.get_queryset()
        if queryset:
            filtered_queryset = queryset.filter(**obj)
            filtered_queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {
                "errors": f"{self.error}",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class ListRetrieveViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    pass
