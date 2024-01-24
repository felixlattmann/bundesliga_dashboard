from io import BytesIO

current_round = "Hello! This is a round!"

buf = BytesIO(bytes(current_round, encoding="utf-8"))
print(buf.read())
