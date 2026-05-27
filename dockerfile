FROM python:3.12

#Don't create .pyc files or __pycache__ directories.
ENV PYTHONDONTWRITEBYTECODE=1 

#to make debugging easier as the output that is buffered can be seen immediately and if not used and ,
#if code crashes then the output stays in buffer only and wont be in the output
ENV PYTHONUNBUFFERED=1

WORKDIR /authentication

RUN pip install uv

COPY authentication/pyproject.toml authentication/uv.lock ./

#--frozen in uv is basically a “do not change anything, just install exactly what is locked” switch.
RUN uv sync --frozen

RUN adduser --disabled-password appuser

COPY . .

USER appuser

CMD ["uv", "run", "uvicorn", "authentication.main:app", "--host", "0.0.0.0", "--port", "8000"]
