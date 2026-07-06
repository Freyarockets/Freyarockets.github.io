FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r stardust_avatar/requirements.txt
ENV PORT=5000
EXPOSE 5000
CMD ["gunicorn", "stardust_avatar.app:app", "-b", "0.0.0.0:5000", "--workers", "3"]
