from decimal import Decimal
from uuid import uuid4
import requests
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction

from usuario.utils import validar_cnpj, validar_cpf
from .custom_exception import UsuarioBloqueadoException, SaldoInvalidoException, LogistaException, TransferenciaException

class BaseModel(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)

    class Meta:
        abstract = True


class Carteira(BaseModel):

    saldo = models.DecimalField('Saldo', max_digits=9, decimal_places=2, default=0)
    bloqueado = models.BooleanField('Carteira bloqueada', default=False)

    def transferencia_valida(self, valor: Decimal, *, saida: bool = True, raise_exception: bool = False) -> bool:
        if self.bloqueado:
            if raise_exception:
                raise UsuarioBloqueadoException()
            return False
        if saida:
            if self.saldo < valor:
                if raise_exception:
                    raise SaldoInvalidoException()
                return False
            if self.usuario.is_logista:
                if raise_exception:
                    raise LogistaException()
                return False
        return True

    @transaction.atomic
    def sacar(self, valor: Decimal) -> Decimal:
        if self.transferencia_valida(valor, raise_exception=True):
            self.saldo -= valor
            print(self.saldo)
            self.save()
            HistoricoTransacao.objects.create(valor=valor, carteira=self, saida=True)
            return self.saldo

    @transaction.atomic
    def depositar(self, valor: Decimal) -> Decimal:
        if self.transferencia_valida(valor, saida=False, raise_exception=True):
            self.saldo += valor
            self.save()
            HistoricoTransacao.objects.create(valor=valor, carteira=self, saida=False)
            return self.saldo

    def __str__(self) -> str:
        return f'Saldo: {self.saldo}'


class Usuario(AbstractUser):
    username = None

    email = models.EmailField("E-mail", unique=True)
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=14, validators=[validar_cnpj, validar_cpf], unique=True)
    nome = models.CharField('Nome', max_length=250)
    telefone = models.CharField('Nome', max_length=11)
    carteira = models.OneToOneField(Carteira, on_delete=models.CASCADE, related_name='usuario')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def cpf_cnpj_formatado(self) -> str:
        if len(self.cpf_cnpj) == 11:
            return f'{self.cpf_cnpj[:3]}.{self.cpf_cnpj[3:6]}.{self.cpf_cnpj[6:9]}-{self.cpf_cnpj[9:]}' 
        return f'{self.cpf_cnpj[:2]}.{self.cpf_cnpj[2:5]}.{self.cpf_cnpj[5:8]}/{self.cpf_cnpj[8:12]}-{self.cpf_cnpj[12:]}'

    @property
    def telefone_formatado(self) -> str:
        return f'({self.telefone[:2]}) {self.telefone[2:7]}-{self.telefone[7:]}'

    @property
    def is_logista(self) -> bool:
        return validar_cnpj(self.cpf_cnpj, raise_exception=False)

    @transaction.atomic
    def transferir(self, valor: Decimal, destinatario):
        response = requests.post('https://run.mocky.io/v3/8fafdd68-a090-496f-8c9a-3442cf30dae6', json=
                                 {'valor': str(valor), 'cpfCnpjDestino': destinatario.cpf_cnpj,
                                  'cpfCnpjOrigem': self.cpf_cnpj})
        if response.status_code == 200:
            self.carteira.sacar(valor)
            destinatario.carteira.depositar(valor)
            print('AQUI')
            return True
        raise TransferenciaException()

    def save(self, **kwargs) -> None:
        if self._state.adding:
            self.set_password(self.password)
            self.carteira = Carteira.objects.create()
        return super().save(**kwargs)

    def __str__(self) -> str:
        return self.nome


class HistoricoTransacao(BaseModel):

    valor = models.DecimalField('Valor', max_digits=9, decimal_places=2)
    carteira = models.ForeignKey(Carteira, on_delete=models.CASCADE, related_name='historico_transacao')
    saida = models.BooleanField('Saida', default=False)

    def __str__(self) -> str:
        return str(self.valor)
    