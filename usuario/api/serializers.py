from rest_framework import serializers
from django.contrib.auth import get_user_model
from usuario.models import Carteira, HistoricoTransacao
from django.core.exceptions import ValidationError

Usuario = get_user_model()


class CarteiraSerializer(serializers.ModelSerializer):

    class Meta:
        model = Carteira
        fields = ['saldo', 'bloqueado']


class UsuarioSerializer(serializers.ModelSerializer):

    carteira = CarteiraSerializer(read_only=True)
    # cpf_cnpj_mascarado = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nome', 'cpf_cnpj', 'telefone', 'password', 'carteira', 'telefone_formatado', 'cpf_cnpj_formatado']
        read_only_fields = ['id', 'telefone_formatado', 'cpf_cnpj_formatado']
        extra_kwargs = {'password': {'write_only': True}, 'cpf_cnpj': {'write_only': True},
                        'telefone': {'write_only': True}}

    # def get_cpf_cnpj_mascarado(self, obj):
    #     if len(self.cpf_cnpj) > 11:
    #         return f'***.{self.cpf_cnpj[3:6]}.{self.cpf_cnpj[6:9]}-**' 
    #     return f'***.{self.cpf_cnpj[2:5]}.{self.cpf_cnpj[5:8]}/{self.cpf_cnpj[8:12]}-**'


class HistoricoTransacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = HistoricoTransacao
        fields = '__all__'
