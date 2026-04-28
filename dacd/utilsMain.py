import hashlib

def php_style_md5(string):
    """
    Calcula el hash MD5 de una cadena, retornándolo en mayúsculas
    para compatibilidad con el sistema de base de datos y el proceso de login.
    """
    if not string:
        return ""
    return hashlib.md5(string.encode('utf-8')).hexdigest().upper()
