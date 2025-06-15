FROM python:3.12-slim
WORKDIR /app
COPY ./avocado_bot /app/avocado_bot
RUN pip install --no-cache-dir -r avocado_bot/requirements.txt
CMD ["python","-m","avocado_bot.bot"]