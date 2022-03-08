from rsa import PublicKey, PrivateKey

width = 400
height = 400
white = (255, 255, 255)
black = (0, 0, 0)

red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

yellow = (255, 255, 0)
cyan = (0, 255, 255)
magenta = (255, 0, 255)

orange = (255, 165, 0)
brown = (139, 69, 19)
pink = (255, 20, 147)

CORES_MATRIX = [[red, green, blue], [yellow, cyan, magenta], [orange, brown, pink]]
CORES_MATRIX_NAME = [
    ["Vermelho", "Verde", "Azul"],
    ["Amarelo", "Ciano", "Magenta"],
    ["Laranja", "Marrom", "Rosa"],
]

SIZE_CIRCLE_GAME = 15
SIZE_CIRCLE_COLOR = 50
LINE_HEIGHT = int(SIZE_CIRCLE_GAME / 2)
CHARSET = "abcdefghijklmnopqrstuvyxwz1234567890?!.,"
FPS = 30

MAX_CHAR_MSG = 50

DEFAULT_ENCODING = "utf-8"
ENDERECO = "127.0.0.1"
PORTA = 5051

import rsa
(PUBLIC_KEY, PRIVATE_KEY) = rsa.newkeys(2048)
# PUBLIC_KEY = PublicKey.load_pkcs1(
#     b"-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEApns5jkxWvqx0XxlhcrbtDHBVrgD3gRZEb28lq9laKKko3EDBLqR2\n0yNMMXz+IKBpO3uzDnvLMd99FmnS+e6loFDBqqK4cJvHvRYTfcON0JsSrsk4S01p\nFFZFImmVbl5HUXcoHkEuDiDTbFk+VfHYN+dZzRrQsyI0jxUNlA9KzPwf9FImU3nH\n/U59ZfMD9SCUdieNNQ27gB6Aff70oQhEi0VXFinaYXAmd96XUqckF4mWWVZdrP4s\nm2S5ZmZBkufGBmVFWkPr1X2KpZeJqRU+zeGQS/KWwPxLluRq8Y0KdFUAdO3fE0iJ\ncldmh/Qvf0ufeOmumLiYDbniiE9rVjT73QIDAQAB\n-----END RSA PUBLIC KEY-----\n"
# )
# PRIVATE_KEY = PrivateKey.load_pkcs1(
#     b"-----BEGIN RSA PRIVATE KEY-----\nMIIEqgIBAAKCAQEApns5jkxWvqx0XxlhcrbtDHBVrgD3gRZEb28lq9laKKko3EDB\nLqR20yNMMXz+IKBpO3uzDnvLMd99FmnS+e6loFDBqqK4cJvHvRYTfcON0JsSrsk4\nS01pFFZFImmVbl5HUXcoHkEuDiDTbFk+VfHYN+dZzRrQsyI0jxUNlA9KzPwf9FIm\nU3nH/U59ZfMD9SCUdieNNQ27gB6Aff70oQhEi0VXFinaYXAmd96XUqckF4mWWVZd\nrP4sm2S5ZmZBkufGBmVFWkPr1X2KpZeJqRU+zeGQS/KWwPxLluRq8Y0KdFUAdO3f\nE0iJcldmh/Qvf0ufeOmumLiYDbniiE9rVjT73QIDAQABAoIBAGwzNksXrmEqcE/G\njSEjZplpASagFjxdnojWMiOolgJLPvU3WNbZqSi8ji6zz+6gkwRH9y34oy181S2W\nBbrOsfKpydT/AOSfOofYKz7Xs/nab6ANw3qdiyfekfw1pxseRzfZO8e+ERK5nu+S\naQMutZpP0HuPbAigt/tHORi8wbLYSA7Ne8olawA8rrmYt7Vg1WdLH2Gwdo5BvDUF\nwqxjY/WHc1z99CH2PDvWQVtbI/GAKmp7+7eDw4RJeRO4GCaRA1cEz8RxoMXll9eP\n7VeFP84m0ZsNrSTe3ASKyjSmwdJlwnztaaSeBADGLTLrRL4PTWwL/C3WPVuFP4CY\nlbJyRgECgYkA3vN3MMJuQGGrGMs0TuBqyCofxr3p3Kk9QmMLDJuSUU/ihdVxBrIj\nXosXfqSPQcoVU00QhmxLxAgUdKn8C4YdZkmI6XoyLPAXEJYLR/rGxuC4/aNPPDVU\neqKW8+t/3gTbmjPcgcYPEUHeCZ7upkkrjVcVdoJznRw1WLNpUnPHijsZNQXUrn8r\nnQJ5AL8o2bC8lnYlWkEGQhMT1IUDTzbxWVE8NAcKtg6JVIAhEc0zdlEJ/a3W4tgG\nyHRZ1IowtY43lCrOnCLGw3WHb3u9faSyAh4Hd2Zawi9PB+re50/6u4AeUtZs/XQv\n6vAlJzV7vwqHNr+8RxPnGFwv6Nkmcums5hi9QQKBiQDB2CM4hMRBO+n8K6l2Lw8I\nq/9m1/Z+gbMehmiz9It6IR/Nxy93Z+jyqbKqzL81r1NtUuLcTUpuzaujZ6waBOiI\n58SfYzw+8BzNsfdrBPJRNlABTz10FtY1rinbOFW7nrOk1hSRzLeLBJ7d9I6Ai7vP\nLvkdSfzljAIh9hPLuZizagDXphMuCKnNAngdGqEaMXxO/JzjLYq90NUYc0qKOPC6\nV4osUEsrp2kAIQjOzzkCWZ0P7JmY/l9ip5Kef5AE2R1r7w0ClnSH3ljw5AbPHnMI\nE2bwZH0QKt4vukRJfwkxFmzSTMHCANGqQl3X3MFXXwLM6mN/+j1RO9IdzabNQQ+/\nUIECgYkAhGyWFHbTbRV3nz/x78w8z2dv7Rz8H7zZOxGgPVrM7OIRarsYjzNBRWRd\nTdXkVdwkW/d18Ap/F10ZjF39Kv+W3IEeVelR3Knjnv7X5/b02jYkQwAeaYZqdeZ0\nu/AQyDVkcDs0SJNNSqXeVZ5lRX2AhqsE9qUZvDu7NrN3DY8tzc9omV+HyOgtgA==\n-----END RSA PRIVATE KEY-----\n"
# )
