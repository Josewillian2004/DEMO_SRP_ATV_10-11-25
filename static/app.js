const logEl = document.getElementById('log')
const userEl = document.getElementById('username')
const passEl = document.getElementById('password')

function timeNow(){ return new Date().toLocaleTimeString() }

function append(msg, cls){
  const t = `[${timeNow()}] `
  const line = document.createElement('div')
  if(cls) line.className = cls
  line.textContent = t + msg
  logEl.appendChild(line)
  logEl.scrollTop = logEl.scrollHeight
}

async function postJSON(path, body){
  try{
    const res = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)} )
    if(!res.ok){
      const txt = await res.text().catch(()=>res.statusText)
      throw new Error(`${res.status} ${res.statusText} - ${txt}`)
    }
    return await res.json()
  }catch(err){
    throw err
  }
}

function setButtonsDisabled(disabled){
  document.querySelectorAll('button').forEach(b=>b.disabled = disabled)
}

document.getElementById('btn-clear').addEventListener('click', ()=> logEl.innerHTML='')
document.getElementById('btn-copy-log').addEventListener('click', ()=>{
  navigator.clipboard.writeText(logEl.innerText).then(()=>append('Log copiado para a área de transferência','ok')).catch(()=>append('Falha ao copiar','err'))
})

document.getElementById('btn-register').addEventListener('click', async ()=>{
  append('Iniciando registro...')
  setButtonsDisabled(true)
  try{
    const r = await postJSON('/api/register',{username:userEl.value, password:passEl.value})
    if(r.error) append('Erro: '+r.error,'err')
    else{
      append('salt: '+r.salt,'ok')
      append('v: '+(r.v||'').slice(0,80)+'...')
    }
  }catch(e){ append('Erro de rede: '+e.message,'err') }
  setButtonsDisabled(false)
})

document.getElementById('btn-client-step1').addEventListener('click', async ()=>{
  append('Gerando A (cliente)...')
  setButtonsDisabled(true)
  try{
    const r = await postJSON('/api/client_step1',{})
    if(r.error) append('Erro: '+r.error,'err')
    else{
      append('a (privado) hex: '+r.a)
      append('A (pub) hex: '+(r.A||'').slice(0,120)+'...')
    }
  }catch(e){ append('Erro de rede: '+e.message,'err') }
  setButtonsDisabled(false)
})

document.getElementById('btn-server-step1').addEventListener('click', async ()=>{
  append('Gerando B (servidor)...')
  setButtonsDisabled(true)
  try{
    const r = await postJSON('/api/server_step1',{})
    if(r.error) append('Erro: '+r.error,'err')
    else{
      append('b (privado) hex: '+r.b)
      append('B (pub) hex: '+(r.B||'').slice(0,120)+'...')
    }
  }catch(e){ append('Erro de rede: '+e.message,'err') }
  setButtonsDisabled(false)
})

document.getElementById('btn-compute').addEventListener('click', async ()=>{
  append('Calculando sessões...')
  setButtonsDisabled(true)
  try{
    const r = await postJSON('/api/compute_sessions',{username:userEl.value,password:passEl.value})
    if(r.error) append('Erro: '+r.error,'err')
    else{
      append('u_c: '+r.u_c)
      append('S_c: '+(r.S_c||'').slice(0,120)+'...')
      append('S_s: '+(r.S_s||'').slice(0,120)+'...')
      append('K_c: '+(r.K_c||'').slice(0,80)+'...')
      append('K_s: '+(r.K_s||'').slice(0,80)+'...')
      append('S equal: '+r.S_equal, r.S_equal ? 'ok' : 'err')
    }
  }catch(e){ append('Erro de rede: '+e.message,'err') }
  setButtonsDisabled(false)
})

document.getElementById('btn-proofs').addEventListener('click', async ()=>{
  append('Gerando provas...')
  setButtonsDisabled(true)
  try{
    const r = await postJSON('/api/proofs',{username:userEl.value})
    if(r.error) append('Erro: '+r.error,'err')
    else{
      append('M1: '+(r.M1||''))
      append('M2: '+(r.M2||''))
      append('M1 ok: '+r.M1_ok, r.M1_ok ? 'ok':'err')
      append('M2 ok: '+r.M2_ok, r.M2_ok ? 'ok':'err')
    }
  }catch(e){ append('Erro de rede: '+e.message,'err') }
  setButtonsDisabled(false)
})

document.getElementById('btn-full').addEventListener('click', async ()=>{
  append('Executando demo completo...')
  setButtonsDisabled(true)
  try{
    const r = await postJSON('/api/full_demo',{username:userEl.value,password:passEl.value})
    if(r.error) append('Erro: '+r.error,'err')
    else{
      for(const line of r.logs) append(line)
    }
  }catch(e){ append('Erro de rede: '+e.message,'err') }
  setButtonsDisabled(false)
})
