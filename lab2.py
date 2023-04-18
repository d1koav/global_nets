from typing import List
from math import log2, ceil
from random import randrange
from crc64iso.crc64iso import crc64

def __hamming_common(src: List[List[int]], s_num: int, encode=True) -> int:
    s_range = range(s_num)
    errors = 0
    for i in src:
        sindrome = 0
        for s in s_range:
            sind = 0
            for p in range(2 ** s, len(i) + 1, 2 ** (s + 1)):
                for j in range(2 ** s):
                    if (p + j) > len(i):
                        break
                    sind ^= i[p + j - 1]
            if encode:
                i[2 ** s - 1] = sind
            else:
                sindrome += (2 ** s * sind)
        if (not encode) and sindrome:
            try:
                i[sindrome - 1] = int(not i[sindrome - 1])
            except IndexError:
                errors += 1
    return errors


def hamming_encode(msg: str, mode: int = 8) -> str:
    result = ""
    msg_b = msg.encode("utf8")
    s_num = ceil(log2(log2(mode + 1) + mode + 1))
    bit_seq = []
    for byte in msg_b:
        bit_seq += list(map(int, f"{byte:08b}"))
    res_len = ceil((len(msg_b) * 8) / mode)
    bit_seq += [0] * (res_len * mode - len(bit_seq))
    to_hamming = []
    for i in range(res_len):
        code = bit_seq[i * mode:i * mode + mode]
        for j in range(s_num):
            code.insert(2 ** j - 1, 0)
        to_hamming.append(code)
    errors = __hamming_common(to_hamming, s_num, True)
    for i in to_hamming:
        result += "".join(map(str, i))
    return result


def hamming_decode(msg: str, mode: int = 8):
    result = ""
    s_num = ceil(log2(log2(mode + 1) + mode + 1))
    res_len = len(msg) // (mode + s_num)
    code_len = mode + s_num
    to_hamming = []
    for i in range(res_len):
        code = list(map(int, msg[i * code_len:i * code_len + code_len]))
        to_hamming.append(code)
    errors = __hamming_common(to_hamming, s_num, False)
    for i in to_hamming:
        for j in range(s_num):
            i.pop(2 ** j - 1 - j)
        result += "".join(map(str, i))
    msg_l = []
    for i in range(len(result) // 8):
        val = "".join(result[i * 8:i * 8 + 8])
        msg_l.append(int(val, 2))
    try:
        result = bytes(msg_l).decode("utf8")
    except UnicodeDecodeError:
        pass
    return result, errors


def noizer(msg: str, mode: int) -> str:
    seq = list(map(int, msg))
    s_num = ceil(log2(log2(mode + 1) + mode + 1))
    code_len = mode + s_num
    cnt = len(msg) // code_len
    result = ""
    for i in range(cnt):
        to_noize = seq[i * code_len:i * code_len + code_len]
        noize = randrange(code_len)
        to_noize[noize] = int(not to_noize[noize])
        result += "".join(map(str, to_noize))
    return result


def noizer2(msg: str, mode: int) -> str:
    seq = list(map(int, msg))
    s_num = ceil(log2(log2(mode + 1) + mode + 1))
    code_len = mode + s_num
    cnt = len(msg) // code_len
    result = ""
    for i in range(0, cnt, 4):
        to_noize = seq[i * code_len:i * code_len + code_len]
        noize1 = randrange(code_len)
        noize2 = randrange(code_len)
        to_noize[noize1] = int(not to_noize[noize1])
        to_noize[noize2] = int(not to_noize[noize2])
        result += "".join(map(str, to_noize))
    return result


if __name__ == '__main__':
    MODE = 47 # Всего 53. Исключаем 1,2,4,8,16,32. Остается 47
    msg = 'ETag или entity tag — один из регламентируемых спецификацией RFC 7232, служебных заголовков протокола HTTP/1.1, который может быть установлен веб-сервером в фазе формирования ответа, на полученный от клиента запрос. Содержимое заголовка ETag является идентификатором, значение которого прямо зависит от состояния загружаемого клиентом ресурса. В дальнейшем, этот идентификатор, используется с целью актуализации состояния загруженного ресурса его оригиналу, расположенному на Веб-сервере. Что достигается путём отправки серверу HTTP/1.1 запроса с указанием ETag идентификатора как значении заголовка - If-None-Match. Сервер, обнаружив такой заголовок, на основании сравнения его значения с текущим состоянием ресурса сообщает клиенту о том, что копия, хранящаяся в кэше клиента, актуальна т.е. необходимости в повторной загрузке нет, или, в противном случае, необходима загрузка актуальной версии.  ETag — это закрытый идентификатор, присвоенный веб-сервером на определённую версию ресурса, найденного на URL. Если содержание ресурса для этого адреса меняется на новое, назначается и новый ETag. Использование в таком ключе ETags аналогично использованию отпечатков пальцев, можно быстро сравнить и определить, являются ли две версии ресурса одинаковыми или нет. Сравнение ETag имеет смысл только c Etag с одного и того же URL, идентификаторы, полученные из разных URL-адресов, могут быть равны, а могут быть нет, вне зависимости от ресурсов, так что их сравнение не имеет какого-либо смысла.  Использование ETags в заголовке HTTP не является обязательным (как и некоторые другие поля заголовка HTTP 1.1). Метод, с помощью которого ETags генерируются, никогда не был указан в спецификации HTTP.  Общие методы создания ETag включают использование устойчивой к коллизиям хеш-функции содержимого ресурса, хеш последнего времени изменения или даже только номер версии.  Для того, чтобы избежать использования устаревших данных кэша, методы, используемые для генерации ETags, должны гарантировать (настолько, насколько это практично), что каждый ETag является уникальным. Тем не менее, функция создания Etag может быть оценена как «полезная», если может быть доказано (математически), что создание одинаковых ETags «приемлемо редко», даже если оно может или будет происходить.  Некоторые ранние контрольные функции, например, CRC32 и CRC64, как известно, страдают от этой проблемы коллизий. По этой причине они не являются хорошими кандидатами для использования в генерации ETag.'
    print(f'Начальное сообщение:\n{msg}')
    checksum = crc64(msg)
    print(f'Контрольная сумма: {checksum}')
    print()
    print('Отправка без ошибок')
    enc_msg = hamming_encode(msg, MODE)
    print(f'Кодированное сообщение:\n{enc_msg}')
    dec_msg, err = hamming_decode(enc_msg, MODE)
    dec_msg = dec_msg[:-1:]
    print(f'Декодированное сообщение:\n{dec_msg}')
    print(f'Контрольная сумма: {crc64(dec_msg)} ')
    print(f'Значения сумм совпадают:{crc64(dec_msg) == checksum}')
    print(f'Совпадение текстов: {msg == dec_msg}')
    print()
    print('Отправка не более 1 ошибки на слово')
    noize_msg = noizer(enc_msg, MODE)
    print(f'Кодированное сообщение с ошибками:\n{noize_msg}')
    dec_msg, err = hamming_decode(noize_msg, MODE)
    dec_msg = dec_msg[:-1:]
    print(f'Декодированное сообщение:\n{dec_msg}')
    print(f'Контрольная сумма: {crc64(dec_msg)} ')
    print(f'Значения сумм совпадают:{crc64(dec_msg) == checksum}')
    print(f'Совпадение текстов: {msg == dec_msg}')
    print()
    print('Отправка до двух ошибок на каждое 4-ое слово')
    noize_msg = noizer2(enc_msg, MODE)
    print(f'Кодированное сообщение с ошибками:\n{noize_msg}')
    dec_msg, err = hamming_decode(noize_msg, MODE)
    dec_msg = dec_msg[:-1:]
    print(f'Декодированное сообщение:\n{dec_msg}')
    print(f'Контрольная сумма: {crc64(dec_msg)} ')
    print(f'Значения сумм совпадают:{crc64(dec_msg) == checksum}')
    print(f'Количество обнаруженных ошибок: {err}')
