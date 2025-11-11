# SRP-6a Demo — Web GUI

Interface web (HTML/CSS/JS) que consome um backend Flask usando o módulo `demo.py` (implementação educacional SRP-6a).

Como executar:

1. Crie um ambiente virtual (recomendado) e instale dependências:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Execute o servidor:

# SRP-6a Demo — Web GUI

Pequeno demo educacional do protocolo SRP-6a com UI web (HTML/CSS/JS) e backend em Flask.
O backend usa o módulo `demo.py` para executar registro, geração de A/B, cálculo de sessão e provas.

IMPORTANTE: este código é somente para estudo. Não use em produção.

## Como preparar o ambiente

1) (opcional, recomendado) Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2) Instale dependências:

```bash
pip install -r requirements.txt
```

## Como executar o servidor (porta 8080)

O projeto foi configurado para rodar com Flask. Para iniciar no modo desenvolvimento na porta 8080:

```bash
PORT=8080 python3 web_app.py
```

Abra no navegador: http://127.0.0.1:8080

Se preferir executar em background (Linux/macOS):

```bash
# Rodar em background (stdout/stderr ainda vão para o terminal)
PORT=8080 nohup python3 web_app.py &

# Ou usar tmux/screen; para parar:
pkill -f web_app.py
```

## Testando a interface (passos rápidos)

- Abra a página e use os botões: Registrar → Gerar A → Gerar B → Calcular Sessões → Gerar Provas.
- O log no painel mostra os hex e resultados (truncados para legibilidade).

## Testes via API (curl)

Exemplos de chamadas HTTP para testar endpoints diretamente:

1. Registrar (POST /api/register)

```bash
curl -s -X POST http://127.0.0.1:8080/api/register \
	-H 'Content-Type: application/json' \
	-d '{"username":"alice","password":"senha"}' | jq
```

2. Gerar A (cliente)

```bash
curl -s -X POST http://127.0.0.1:8080/api/client_step1 -H 'Content-Type: application/json' | jq
```

3. Gerar B (servidor)

```bash
curl -s -X POST http://127.0.0.1:8080/api/server_step1 -H 'Content-Type: application/json' | jq
```

4. Calcular sessões

```bash
curl -s -X POST http://127.0.0.1:8080/api/compute_sessions \
	-H 'Content-Type: application/json' \
	-d '{"username":"alice","password":"senha"}' | jq
```

5. Gerar provas (M1/M2)

```bash
curl -s -X POST http://127.0.0.1:8080/api/proofs -H 'Content-Type: application/json' -d '{}' | jq
```

6. Demo completo

```bash
curl -s -X POST http://127.0.0.1:8080/api/full_demo -H 'Content-Type: application/json' -d '{"username":"alice","password":"senha"}' | jq
```

## Resolução de problemas comuns

- Erro de conexão / refused: verifique se o servidor está rodando e na porta correta (o valor `PORT` ambiente é usado). Use `ss -ltnp | grep 8080` ou `ps aux | grep web_app.py`.
- 404 em `/static/*.css` ou `/static/*.js`: o servidor serve os estáticos a partir da pasta `static/`. Garanta que o servidor esteja executando no diretório do projeto.
- CORS / requests bloqueadas no console do navegador: o backend já adiciona cabeçalhos CORS básicos para desenvolvimento. Se você ainda vê bloqueio, confirme a URL (mesmo host/porta) e desative extensões que possam bloquear requests.
- Erros inesperados no log do Flask: abra o terminal onde o servidor foi iniciado para ver tracebacks. O servidor está em modo debug por padrão para facilitar o desenvolvimento.

## Validação rápida (smoke test)

No workspace você pode executar um teste rápido para confirmar que o backend importa sem erro:

```bash
python3 -c "import web_app; print('import ok')"
```

## Notas finais

- Arquivos importantes:
	- `demo.py` — implementação educacional do protocolo SRP usada pelo backend
	- `web_app.py` — servidor Flask + endpoints
	- `static/index.html`, `static/styles.css`, `static/app.js` — frontend
- Estado: o servidor mantém estado em memória (uma única sessão). Reiniciar o servidor limpa esse estado.

Se quiser, posso:
- adicionar testes automatizados (pytest) para `demo.py`;
- empacotar em Dockerfile para facilitar execução consistente; ou
- melhorar ainda mais a UI (visualização dos valores hex completos com copy, histórico, etc.).
