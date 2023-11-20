FROM python:3.11-bullseye as builder

run apt-get update && apt-get install -y \
    build-essential libgdbm6 libgdbm-dev

COPY requirements.txt .
RUN pip install --root="/install" -r requirements.txt

# runtime
FROM python:3.11-slim-bullseye

COPY --from=builder /install /
COPY . .

CMD  ["/bin/sleep", "10000"]
