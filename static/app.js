const logEl = document.getElementById('log')
const userEl = document.getElementById('username')
const passEl = document.getElementById('password')

function append(msg){
  logEl.textContent += msg + "\n"
  logEl.scrollTop = logEl.scrollHeight
}

async function postJSON(path, body){
  const res = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)})
  return res.json()
}

document.getElementById('btn-clear').addEventListener('click', ()=> logEl.textContent='')

document.getElementById('btn-register').addEventListener('click', async ()=>{
  append('== Registro ==')
  const r = await postJSON('/api/register',{username:userEl.value, password:passEl.value})
  if(r.error) append('Erro: '+r.error)
  else{
    append('salt: '+r.salt)
    append('v: '+r.v.slice(0,80)+'...')
  }
})

document.getElementById('btn-client-step1').addEventListener('click', async ()=>{
  append('== Cliente passo 1 ==')
  const r = await postJSON('/api/client_step1',{})
  if(r.error) append('Erro: '+r.error)
  else{
    append('a (privado) hex: '+r.a)
    append('A (pub) hex: '+r.A.slice(0,120)+'...')
  }
})

document.getElementById('btn-server-step1').addEventListener('click', async ()=>{
  append('== Servidor passo 1 ==')
  const r = await postJSON('/api/server_step1',{})
  if(r.error) append('Erro: '+r.error)
  else{
    append('b (privado) hex: '+r.b)
    append('B (pub) hex: '+r.B.slice(0,120)+'...')
  }
})

document.getElementById('btn-compute').addEventListener('click', async ()=>{
  append('== Calcular sessões ==')
  const r = await postJSON('/api/compute_sessions',{username:userEl.value,password:passEl.value})
  if(r.error) append('Erro: '+r.error)
  else{
    append('u_c: '+r.u_c)
    append('S_c: '+(r.S_c||'') .slice(0,120)+'...')
    append('S_s: '+(r.S_s||'') .slice(0,120)+'...')
    append('K_c: '+(r.K_c||'') .slice(0,80)+'...')
    append('K_s: '+(r.K_s||'') .slice(0,80)+'...')
    append('S equal: '+r.S_equal)
  }
})

document.getElementById('btn-proofs').addEventListener('click', async ()=>{
  append('== Gerar provas ==')
  const r = await postJSON('/api/proofs',{username:userEl.value})
  if(r.error) append('Erro: '+r.error)
  else{
    append('M1: '+(r.M1||'') )
    append('M2: '+(r.M2||'') )
    append('M1 ok: '+r.M1_ok)
    append('M2 ok: '+r.M2_ok)
  }
})

document.getElementById('btn-full').addEventListener('click', async ()=>{
  append('== Demo completo ==')
  const r = await postJSON('/api/full_demo',{username:userEl.value,password:passEl.value})
  if(r.error) append('Erro: '+r.error)
  else{
    for(const line of r.logs) append(line)
  }
})
