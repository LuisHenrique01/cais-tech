from django.test import TestCase
from decimal import Decimal
from .models import Carteira, Usuario
from .custom_exception import SaldoInvalidoException, UsuarioBloqueadoException, LogistaException

class CarteiraTestCase(TestCase):

    def setUp(self):
        self.carteira = Carteira.objects.create(saldo=100)
        self.usuario = Usuario.objects.create(email='luisrocha@gmail.com', cpf_cnpj='23296820000', nome='Luis Henrique',
                                              telefone='89994619853', carteira=self.carteira)

    def test_transferencia_valida_saldo_suficiente(self):
        # Teste quando há saldo suficiente na carteira
        valor = Decimal('50')
        self.assertTrue(self.carteira.transferencia_valida(valor, saida=True))

    def test_transferencia_valida_saldo_insuficiente(self):
        # Teste quando há saldo insuficiente na carteira
        valor = Decimal('150')
        self.assertFalse(self.carteira.transferencia_valida(valor, saida=True))

    def test_transferencia_valida_carteira_bloqueada(self):
        # Teste quando a carteira está bloqueada
        self.carteira.bloqueado = True
        self.carteira.save()
        valor = Decimal('50')
        with self.assertRaises(UsuarioBloqueadoException):
            self.carteira.transferencia_valida(valor, saida=True, raise_exception=True)

    def test_sacar(self):
        # Teste para o método sacar
        valor = Decimal('50')
        saldo_esperado = Decimal('50')
        self.assertEqual(self.carteira.sacar(valor), saldo_esperado)

    def test_sacar_saldo_insuficiente(self):
        # Teste para o método sacar com saldo insuficiente
        valor = Decimal('150')
        with self.assertRaises(SaldoInvalidoException):
            self.carteira.sacar(valor)

    def test_depositar(self):
        # Teste para o método depositar
        valor = Decimal('50')
        saldo_esperado = Decimal('150')
        self.assertEqual(self.carteira.depositar(valor), saldo_esperado)

    def test_depositar_carteira_bloqueada(self):
        # Teste para o método depositar com a carteira bloqueada
        self.carteira.bloqueado = True
        self.carteira.save()
        valor = Decimal('50')
        with self.assertRaises(UsuarioBloqueadoException):
            self.carteira.depositar(valor)



class UsuarioTestCase(TestCase):
    def setUp(self):
        self.usuario_origem = Usuario.objects.create(email='origem@example.com', cpf_cnpj='12345678900', nome='Origem', telefone='1234567890')
        self.usuario_destino = Usuario.objects.create(email='destino@example.com', cpf_cnpj='98765432100', nome='Destino', telefone='0987654321')
        self.carteira_origem = self.usuario_origem.carteira
        self.carteira_destino = self.usuario_destino.carteira
        self.carteira_origem.saldo = Decimal(100)
        self.carteira_origem.save()

    def test_cpf_cnpj_formatado_cpf(self):
        # Teste do método cpf_cnpj_formatado para CPF
        self.usuario_origem.cpf_cnpj = '12345678900'
        self.assertEqual(self.usuario_origem.cpf_cnpj_formatado, '123.456.789-00')

    def test_cpf_cnpj_formatado_cnpj(self):
        # Teste do método cpf_cnpj_formatado para CNPJ
        self.usuario_origem.cpf_cnpj = '12345678000123'
        self.assertEqual(self.usuario_origem.cpf_cnpj_formatado, '12.345.678/0001-23')

    def test_telefone_formatado(self):
        # Teste do método telefone_formatado
        self.assertEqual(self.usuario_origem.telefone_formatado, '(12) 34567-890')

    def test_is_logista_true(self):
        # Teste do método is_logista quando é logista (CNPJ)
        self.usuario_origem.cpf_cnpj = '21782849000134'
        self.assertTrue(self.usuario_origem.is_logista)

    def test_is_logista_false(self):
        # Teste do método is_logista quando não é logista (CPF)
        self.assertFalse(self.usuario_destino.is_logista)

    def test_transferir_sucesso(self):
        # Teste do método transferir com sucesso
        valor = Decimal('50')
        self.assertTrue(self.usuario_origem.transferir(valor, self.usuario_destino))
        self.assertEqual(self.carteira_origem.saldo, Decimal('50'))
        self.assertEqual(self.carteira_destino.saldo, Decimal('50'))

    def test_transferir_saldo_insuficiente(self):
        # Teste do método transferir com saldo insuficiente na carteira de origem
        valor = Decimal('150')
        with self.assertRaises(SaldoInvalidoException):
            self.usuario_origem.transferir(valor, self.usuario_destino)

    def test_transferir_carteira_bloqueada(self):
        # Teste do método transferir com carteira bloqueada
        self.carteira_origem.bloqueado = True
        self.carteira_origem.save()
        valor = Decimal('50')
        with self.assertRaises(UsuarioBloqueadoException):
            self.usuario_origem.transferir(valor, self.usuario_destino)
