class BaseException(Exception):

    @property
    def serializer(self):
        return {
            'message': getattr(self, 'message', 'Problema interno.')
        }


class UsuarioBloqueadoException(BaseException):

    def __init__(self, message="Usuário bloqueado."):
        self.message = message
        super().__init__(self.message)


class SaldoInvalidoException(BaseException):

    def __init__(self, message="Saldo inválido."):
        self.message = message
        super().__init__(self.message)


class LogistaException(BaseException):

    def __init__(self, message="Você não pode realizar essa transferência."):
        self.message = message
        super().__init__(self.message)


class TransferenciaException(BaseException):

    def __init__(self, message="Falha ao realizar essa transferência."):
        self.message = message
        super().__init__(self.message)