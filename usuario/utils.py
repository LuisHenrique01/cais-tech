from django.core.exceptions import ValidationError


def validar_cpf(cpf: str, raise_exception: bool = True) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito_1 = (soma * 10) % 11
    if digito_1 == 10:
        digito_1 = 0

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito_2 = (soma * 10) % 11
    if digito_2 == 10:
        digito_2 = 0

    if cpf[-2:] == f'{digito_1}{digito_2}':
        return True

    if raise_exception:
        raise ValidationError(f"O CPF {cpf} é inválido.")
    return False


def validar_cnpj(cnpj: str, raise_exception: bool = True) -> bool:
    cnpj = ''.join(filter(str.isdigit, cnpj))

    if (not cnpj) or (len(cnpj) < 14):
        return False

    # Pega apenas os 12 primeiros dígitos do CNPJ e gera os 2 dígitos que faltam
    inteiros = list(map(int, cnpj))
    novo = inteiros[:12]

    prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    while len(novo) < 14:
        r = sum([x*y for (x, y) in zip(novo, prod)]) % 11
        if r > 1:
            f = 11 - r
        else:
            f = 0
        novo.append(f)
        prod.insert(0, 6)

    # Se o número gerado coincidir com o número original, é válido
    if novo == inteiros:
        return True

    if raise_exception:
        raise ValidationError(f"O CNPJ {cnpj} é inválido.")
    return False
