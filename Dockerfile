FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN python -m pip install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

EXPOSE 8080

ENV TZ=Asia/Shanghai

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]