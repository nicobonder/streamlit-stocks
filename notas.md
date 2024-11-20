# Trabajo con el virtual enviroment. Para eso hago:

python -m venv .venv
.\.venv\Scripts\activate

- Y hay que elegir el interprete:

* Selecciona Python: Select Interpreter y elige el intérprete dentro de .venv (debería ser algo como .venv\Scripts\python.exe

- Aunque tengo ambiente virtual, para instalar algo tengo que hacer:
  pip install yfinance
- E importo con:
  import yfinance as yf

# Para salir del ambiente virtual:

deactivate
