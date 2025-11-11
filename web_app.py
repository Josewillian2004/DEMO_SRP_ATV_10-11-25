from flask import Flask, request, jsonify, send_from_directory
import binascii
import os
import demo

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Estado em memória (demo simples, apenas para interface educacional)
state = {
    'salt': None,  # bytes
    'v': None,      # int
    'a': None, 'A': None,
    'b': None, 'B': None,
    'u_c': None, 'S_c': None, 'K_c': None,
    'u_s': None, 'S_s': None, 'K_s': None,
    'M1': None, 'M2': None,
}

def to_hex(x):
    if x is None:
        return None
    if isinstance(x, bytes):
        return binascii.hexlify(x).decode()
    if isinstance(x, int):
        return format(x, 'x')
    return str(x)


@app.after_request
def add_cors_headers(response):
    # Permitir chamadas do frontend (útil durante desenvolvimento)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


@app.before_request
def log_request():
    app.logger.debug(f"{request.method} {request.path} from {request.remote_addr}")


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    # Servir arquivos estáticos explicitamente — evita 404 em alguns ambientes
    return send_from_directory('static', filename)


@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json or {}
    username = data.get('username', 'alice')
    password = data.get('password', '')
    salt, v = demo.register(username, password)
    state['salt'] = salt
    state['v'] = v
    return jsonify({'salt': to_hex(salt), 'v': to_hex(v)})


@app.route('/api/client_step1', methods=['POST'])
def api_client_step1():
    a, A = demo.client_step1()
    state['a'] = a
    state['A'] = A
    # Por clareza do demo, retornamos A e também a (privado) — não faça isso em produção
    return jsonify({'a': to_hex(a), 'A': to_hex(A)})


@app.route('/api/server_step1', methods=['POST'])
def api_server_step1():
    if state.get('v') is None:
        return jsonify({'error': 'user not registered'}), 400
    b, B = demo.server_step1(state['v'])
    state['b'] = b
    state['B'] = B
    return jsonify({'b': to_hex(b), 'B': to_hex(B)})


@app.route('/api/compute_sessions', methods=['POST'])
def api_compute_sessions():
    data = request.json or {}
    username = data.get('username', 'alice')
    password = data.get('password', '')
    a = state.get('a'); A = state.get('A')
    b = state.get('b'); B = state.get('B')
    salt = state.get('salt'); v = state.get('v')
    if None in (a, A, b, B, salt, v):
        return jsonify({'error': 'missing values - generate A/B and register first'}), 400
    u_c, S_c, K_c = demo.compute_session_client(a, salt, username, password, A, B)
    u_s, S_s, K_s = demo.compute_session_server(b, salt, v, A, B)
    state.update({'u_c': u_c, 'S_c': S_c, 'K_c': K_c, 'u_s': u_s, 'S_s': S_s, 'K_s': K_s})
    equal = (S_c == S_s)
    return jsonify({
        'u_c': to_hex(u_c), 'S_c': to_hex(S_c), 'K_c': to_hex(K_c),
        'u_s': to_hex(u_s), 'S_s': to_hex(S_s), 'K_s': to_hex(K_s),
        'S_equal': equal
    })


@app.route('/api/proofs', methods=['POST'])
def api_proofs():
    data = request.json or {}
    username = data.get('username', 'alice')
    A = state.get('A'); B = state.get('B')
    K_c = state.get('K_c'); K_s = state.get('K_s')
    salt = state.get('salt')
    if None in (A, B, K_c, K_s, salt):
        return jsonify({'error': 'missing session values'}), 400
    M1 = demo.client_proof(username, salt, A, B, K_c)
    expected_M1 = demo.client_proof(username, salt, A, B, K_s)
    ok1 = (M1 == expected_M1)
    M2 = None
    ok2 = False
    if ok1:
        M2 = demo.server_proof(A, M1, K_s)
        expected_M2 = demo.server_proof(A, M1, K_c)
        ok2 = (M2 == expected_M2)
    state['M1'] = M1; state['M2'] = M2
    return jsonify({'M1': to_hex(M1), 'M2': to_hex(M2) if M2 else None, 'M1_ok': ok1, 'M2_ok': ok2})


@app.route('/api/full_demo', methods=['POST'])
def api_full_demo():
    data = request.json or {}
    username = data.get('username', 'alice')
    password = data.get('password', '')
    logs = []
    # Registro
    salt, v = demo.register(username, password)
    state['salt'] = salt; state['v'] = v
    logs.append(f"registered: salt={to_hex(salt)} v={to_hex(v)[:80]}...")
    # Client/Server steps
    a, A = demo.client_step1(); state['a']=a; state['A']=A
    b, B = demo.server_step1(v); state['b']=b; state['B']=B
    logs.append(f"A={to_hex(A)[:80]}...")
    logs.append(f"B={to_hex(B)[:80]}...")
    # Sessions
    u_c, S_c, K_c = demo.compute_session_client(a, salt, username, password, A, B)
    u_s, S_s, K_s = demo.compute_session_server(b, salt, v, A, B)
    state.update({'u_c': u_c, 'S_c': S_c, 'K_c': K_c, 'u_s': u_s, 'S_s': S_s, 'K_s': K_s})
    logs.append(f"S_c={to_hex(S_c)[:80]}...")
    logs.append(f"S_s={to_hex(S_s)[:80]}...")
    logs.append("session keys equal="+str(S_c==S_s))
    # Proofs
    M1 = demo.client_proof(username, salt, A, B, K_c)
    expected_M1 = demo.client_proof(username, salt, A, B, K_s)
    if M1 == expected_M1:
        M2 = demo.server_proof(A, M1, K_s)
        expected_M2 = demo.server_proof(A, M1, K_c)
        ok = (M2 == expected_M2)
        logs.append('M1 verified, M2='+('ok' if ok else 'FAIL'))
    else:
        logs.append('M1 verification failed')
    return jsonify({'logs': logs})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
