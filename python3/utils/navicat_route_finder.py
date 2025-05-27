import platform
import winreg
import logging

logging.basicConfig(level=logging.INFO)

def enumerate_subkeys(hive, key_path):
    """
    Enumeran los subkeys de una clave del registro de Windows.
    Devuelve una lista de nombres de subkeys.
    """
    subkeys_list = []
    try:
        with winreg.OpenKeyEx(hive, key_path, 0, winreg.KEY_READ) as hkey:
            index = 0
            while True:
                try:
                    subkey_name = winreg.EnumKey(hkey, index)
                    subkeys_list.append(subkey_name)
                    index += 1
                except OSError:
                    break
        return subkeys_list

    except FileNotFoundError:
        logging.error("Error: La clave '%s' no fue encontrada en el hive especificado.", key_path)
        return []
    except PermissionError:
        logging.error("Error: Permiso denegado para acceder a la clave '%s'.", key_path)
        return []
    except OSError as e:
        logging.error("Ocurrió un error inesperado al acceder a '%s': %s", key_path, e)
        return []


def find_projects_recursive(hive, current_path, target="Profiles"):
    """
    Busca recursivamente el directorio 'Projects' y retorna la ruta completa
    junto con sus contenidos.
    """
    results = []

    try:
        subkeys = enumerate_subkeys(hive, current_path)
        for subkey in subkeys:
            subkey_path = current_path + '\\' + subkey
            if subkey == target:
                projects_content = enumerate_subkeys(hive, subkey_path)
                results.append({
                    'path': subkey_path,
                    'contents': projects_content
                })

            else:
                recursive_results = find_projects_recursive(hive, subkey_path, target)
                results.extend(recursive_results)

    except (OSError, PermissionError, FileNotFoundError, RecursionError) as e:
        logging.error("Error al buscar en la clave '%s': %s", current_path, e)

    return results


def find_value_if_exists(registry_key, search_value):
    """
    Busca un valor en el registro de Windows y devuelve su contenido.
    Si no se encuentra el valor, devuelve None.
    """
    try:
        return winreg.QueryValueEx(registry_key, search_value)[0]
    except (OSError, FileNotFoundError):
        return None
