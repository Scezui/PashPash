import os
from cryptography.fernet import Fernet
from kivy.utils import platform


SECURE_STORAGE_KEY = 'encryption_key'

def get_non_android_secure_storage_path():
    return os.path.expanduser('~/.secure_storage')

def get_non_android_encryption_key():
    secure_storage_path = get_non_android_secure_storage_path()
    if not os.path.exists(secure_storage_path):
        key = Fernet.generate_key()
        with open(secure_storage_path, 'wb') as f:
            f.write(key)
    else:
        with open(secure_storage_path, 'rb') as f:
            key = f.read()
    return key

def get_cipher_suite():
    if platform == 'android':
        
        from android.storage import app_storage_path

        def get_secure_storage_path():
            return os.path.join(app_storage_path(), 'secure_storage')

        def get_encryption_key():
            secure_storage_path = get_secure_storage_path()
            if not os.path.exists(secure_storage_path):
                key = Fernet.generate_key()
                with open(secure_storage_path, 'wb') as f:
                    f.write(key)
            else:
                with open(secure_storage_path, 'rb') as f:
                    key = f.read()
            return key

        def get_secure_storage_path():
            return get_non_android_secure_storage_path()

    def get_encryption_key():
        return get_non_android_encryption_key()

    key = get_encryption_key()
    return Fernet(key)

