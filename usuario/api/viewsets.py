from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated

from django.contrib.auth import get_user_model

from usuario.models import HistoricoTransacao
from .serializers import UsuarioSerializer, HistoricoTransacaoSerializer
from usuario.custom_exception import *


Usuario = get_user_model()


class HistoricoView(APIView):

    def get_queryset(self):
        return HistoricoTransacao.objects.filter(carteira=self.request.user.carteira)

    def get(self, request):
        queryset = self.get_queryset()
        serializer = HistoricoTransacaoSerializer(queryset, many=True)
        return Response(serializer.data)


class UsuarioViewSet(ViewSet):

    queryset = Usuario.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)

    def create(self, request):
        serializer = UsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):
        if request.user.id == int(pk):
            serializer = UsuarioSerializer(request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    def destroy(self, request, pk):
        instance = request.user
        if instance.id == int(pk):
            instance.carteira.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(methods=['POST'], detail=False, url_path='transferir', url_name='transferir')
    def transferir(self, request):
        try:
            data = request.data
            destinatario = get_object_or_404(self.queryset, cpf_cnpj=data['cpf_cnpj'])
            user = request.user
            user.transferir(valor=data['valor'], destinatario=destinatario)
            return Response({'messagem': 'Authorized'}, status=status.HTTP_200_OK)
        except (UsuarioBloqueadoException, SaldoInvalidoException, LogistaException, TransferenciaException) as e:
            return Response(e.serializer, status=status.HTTP_400_BAD_REQUEST)
