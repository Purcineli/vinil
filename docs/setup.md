# Setup — Configuração Local

## Pré-requisitos

- Python 3.12+
- pip

## Passos

```bash
# 1. Criar e ativar virtualenv
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Aplicar migrations
python manage.py migrate

# 4. Criar superusuário (opcional, para acessar o Django Admin)
python manage.py createsuperuser

# 5. Rodar o servidor
python manage.py runserver
```

O projeto estará disponível em `http://localhost:8000`.
O Django Admin estará em `http://localhost:8000/admin/`.

## Dependências

| Pacote | Versão | Uso |
|---|---|---|
| Django | 6.0.3 | Framework principal |
| django-simple-history | 3.11.0 | Histórico de alterações nos models |
| Pillow | 12.1.1 | Processamento de imagens (QR Code) |
| qrcode | 8.2 | Geração de QR Codes |
| tzdata | 2025.3 | Dados de timezone |

## Banco de dados

SQLite padrão do Django. O arquivo `db.sqlite3` é gerado na raiz do projeto após o `migrate`.

## Variáveis de ambiente

Por ora o projeto usa `settings.py` direto, sem `.env`. O `DEBUG` está `True` e `ALLOWED_HOSTS = ['*']` para desenvolvimento local.
