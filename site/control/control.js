(() => {
"use strict";
const REPO = "Pershore/PetTraffic" + String.fromCharCode(45,65,73);
const GH = "https://api.github.com/repos/" + REPO;
const WORKER = "https://pettraffic-control-api.pauliusgrubliauskis.workers.dev";
const SITE = "https://pettraffic-ai.pages.dev";
const TZ = "Europe/Vilnius";
const $ = (id) => document.getElementById(id);
const state = { runs: [], prs: [], commit: null, issue: null, health: null, site: null, analytics: null, topics: null, loadedAt: null, loading: false };
const archiveCache = { analytics: { checkedAt: 0, value: null }, "topic-radar": { checkedAt: 0, value: null } };
const workflowDefinitions = [
 {key:"site",title:"Svetainės patikra",file:"site-check.yml",match:"site checks",cadence:"Kasdien 07:37 LT + push / PR",desc:"HTML, vidinės nuorodos, SEO, sitemap, Python testai"},
 {key:"daily",title:"Daily-suite",file:"daily-suite.yml",match:"daily automation suite",cadence:"Kasdien 08:10 LT",desc:"GA4 / GSC, temų radaras ir gyvos svetainės patikra"},
 {key:"control",title:"Control Center",file:"control-center.yml",match:"central control center",cadence:"Kasdien 10:40 LT",desc:"Sujungia workflow įrodymus, rizikas ir rekomendacijas"},
 {key:"analytics",title:"Analytics snapshot",file:"analytics-snapshot.yml",match:"analytics snapshot",cadence:"Daily-suite dalis / push / manual",desc:"GA4 ir Search Console agreguoti duomenys"},
 {key:"topics",title:"Topic radar",file:"daily-topic-radar.yml",match:"daily topic radar",cadence:"Daily-suite dalis / push / manual",desc:"Viešos Google News RSS antraštės"},
 {key:"lighthouse",title:"Lighthouse",file:"lighthouse-audit.yml",match:"lighthouse audits",cadence:"Pirmadieniais 09:27 LT + site push",desc:"5 puslapiai × mobile ir desktop"},
 {key:"sync",title:"D1 snapshot sync",file:"sync-control-api.yml",match:"sync pettraffic snapshots",cadence:"Po workflow įvykių / manual",desc:"GitHub OIDC, agreguotų snapshot įrašymas ir readback"},
 {key:"bridge",title:"Saugus dispatch bridge",file:"dispatch-daily-suite.yml",match:"secure workflow dispatch",cadence:"Tik owner komanda issue #145",desc:"Dedup, ribotas workflow_dispatch, nėra savavališkų komandų"},
 {key:"worker",title:"Worker deploy",file:"deploy-control-api.yml",match:"deploy pettraffic control api",cadence:"Worker failų push / manual",desc:"Worker testai, Cloudflare validacija, deploy ir /health"},
 {key:"monitor",title:"Live-site monitor",file:"live-site-monitor.yml",match:"live-site monitor",cadence:"Daily-suite dalis / workflow",desc:"Viešos svetainės ir sveikatos signalai"},
 {key:"termux",title:"Termux bridge CI",file:"termux-bridge-check.yml",match:"termux bridge",cadence:"Pagal kodo pakeitimus",desc:"Android / Ubuntu bootstrap scenarijų CI testai"},
 {key:"worklog",title:"Work-log",file:"work-log.yml",match:"work-log",cadence:"Po main pakeitimų",desc:"Automatinis GitHub darbo žurnalo įrašas"},
 {key:"workercron",title:"Worker cron diagnostika",file:"worker-cron-diagnostic.yml",match:"worker cron diagnostic",cadence:"Pagal workflow",desc:"Worker heartbeat ir agentų ciklo diagnostika"},
 {key:"indexnow",title:"IndexNow",file:"indexnow.yml",match:"indexnow",cadence:"Pagal svetainės pakeitimus",desc:"Paieškos sistemų URL pranešimas"}
];
const escapeHtml = (value) => String(value ?? "").replace(/[&<>"']/g, ch => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[ch]));
const dateLT = value => value ? new Intl.DateTimeFormat("lt-LT",{dateStyle:"medium",timeStyle:"short",timeZone:TZ}).format(new Date(value)) : "—";
const fmt = value => new Intl.NumberFormat("lt-LT",{maximumFractionDigits:0}).format(Number(value)||0);
const localDate = () => new Intl.DateTimeFormat("en-CA",{timeZone:TZ,year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
const localMinutes = () => { const p=new Intl.DateTimeFormat("en-GB",{timeZone:TZ,hour:"2-digit",minute:"2-digit",hourCycle:"h23"}).formatToParts(new Date()); return Number(p.find(x=>x.type==="hour").value)*60+Number(p.find(x=>x.type==="minute").value); };
const statusClass = run => run?.status === "in_progress" || run?.status === "queued" ? "warn" : run?.conclusion === "success" ? "good" : run?.conclusion === "failure" || run?.conclusion === "cancelled" || run?.conclusion === "timed_out" ? "bad" : "unknown";
const statusText = run => !run ? "Nėra duomenų" : run.status !== "completed" ? (run.status === "in_progress" ? "Vyksta" : "Eilėje") : run.conclusion === "success" ? "Sėkmingas" : run.conclusion === "failure" ? "Nesėkmingas" : run.conclusion || "Baigtas";
const badge = (label, cls="unknown") => '<span class="state '+cls+'">'+escapeHtml(label)+'</span>';
const toast = message => { const el=$("toast");el.textContent=message;el.classList.add("show");setTimeout(()=>el.classList.remove("show"),2400); };
async function getJson(url, timeout=12000) {
 const controller = new AbortController(); const timer=setTimeout(()=>controller.abort(),timeout);
 try { const response=await fetch(url,{cache:"no-store",signal:controller.signal,headers:{accept:"application/json"}}); if(!response.ok) throw new Error("HTTP "+response.status); return await response.json(); }
 finally { clearTimeout(timer); }
}
async function getText(url, timeout=10000) {
 const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),timeout);
 try { const response=await fetch(url,{cache:"no-store",signal:controller.signal,method:"GET"});if(!response.ok)throw new Error("HTTP "+response.status);return response.text(); }
 finally {clearTimeout(timer);}
}
function setState(id,text,cls){const el=$(id);if(el){el.textContent=text;el.className="state "+cls;}}
function latestFor(file){const d=workflowDefinitions.find(x=>x.file===file);return state.runs.find(r=>(r.path||"").includes(file)||(d?.match&&String(r.name||"").toLowerCase().includes(d.match)))||null;}
function latestEvent(file,event){const d=workflowDefinitions.find(x=>x.file===file);return state.runs.find(r=>r.event===event&&((r.path||"").includes(file)||(d?.match&&String(r.name||"").toLowerCase().includes(d.match))))||null;}
function renderStats(){
 const site=state.site;const h=state.health;const latestRuns=state.runs.slice(0,100);const failed=latestRuns.filter(r=>r.status==="completed"&&r.conclusion!=="success").length;const open=state.prs.length;
 $("stat-site").textContent=site?.ok?"HTTP 200":"Neatsako";$("stat-site").className=site?.ok?"good-text":"bad-text";$("stat-site-detail").textContent=site?.url||SITE;
 $("stat-actions").textContent=latestRuns.length?String(latestRuns.length):"—";$("stat-actions-detail").textContent="main "+(state.commit?.sha||"").slice(0,7)+" · "+failed+" nesėkmingų iš "+latestRuns.length+" run";
 $("stat-worker").textContent=h?.preview_blocked?"Tik produkcijos domene":h?.ok&&h?.database==="connected"?"Prisijungęs":"Nežinoma";$("stat-worker").className=h?.ok?"good-text":"warn-text";$("stat-worker-detail").textContent=h?.preview_blocked?"Preview CORS ribojamas oficialiu domenu":h?.control_core_schema==="connected"?"D1 + Control Core prijungti":"Nepatvirtinta";
 $("stat-prs").textContent=String(open);$("stat-prs-detail").textContent="Atviri PR main šakai";
 const ai=aiCycleStatus();$("stat-ai").textContent=ai.label;$("stat-ai").className=ai.cls==="good"?"good-text":ai.cls==="bad"?"bad-text":"warn-text";$("stat-ai-detail").textContent=ai.detail;
 $("connection-state").textContent=site?.ok&&h?.ok?"Sistemos pasiekiamos":"Dalis sistemų nepasiekiama";
}
function aiCycleStatus(){
 const run=state.health?.agent_orchestration;if(!run||!run.started_at)return {label:"Nežinoma",cls:"unknown",detail:"Worker nepateikė agentų ciklo"};
 const today=localDate();const runDate=String(run.run_date||"").slice(0,10);const start=new Date(run.started_at);const mins=Number(new Intl.DateTimeFormat("en-GB",{timeZone:TZ,hour:"2-digit",hourCycle:"h23"}).format(start))*60+Number(new Intl.DateTimeFormat("en-GB",{timeZone:TZ,minute:"2-digit"}).format(start));
 if(runDate!==today)return {label:"SENA",cls:"bad",detail:"Paskutinio ciklo data "+runDate};
 if(run.status==="failed")return {label:"KLAIDA",cls:"bad",detail:run.error_code||"agentų ciklas nepavyko"};
 if(localMinutes()<13*60+20&&mins<13*60+20)return {label:"LAUKIA",cls:"warn",detail:"Dienos ciklas tikslinis 13:20 LT"};
 if(mins<13*60+20)return {label:"STALE",cls:"bad",detail:"Šiandienos ciklas pradėtas iki 13:20 LT"};
 if(run.status==="completed"&&Number(run.ai_calls)>=5&&run.error_code==null)return {label:"ATLIKTA",cls:"good",detail:"5 agentų kvietimai, klaidos nėra"};
 return {label:String(run.status||"Nežinoma").toUpperCase(),cls:"warn",detail:Number(run.ai_calls||0)+" agentų kvietimų"};
}
function renderAttention(){
 const items=[];const daily=latestEvent("daily-suite.yml","schedule");const cc=latestEvent("control-center.yml","schedule");const ai=aiCycleStatus();
 if(!daily||new Date(daily.created_at).toDateString()!==new Date().toDateString())items.push({title:"Daily-suite schedule įrodymas",detail:daily?"Paskutinis schedule: "+dateLT(daily.created_at):"Naujausio sąrašo schedule paleidimo nerasta",cls:"warn"});
 if(!cc||new Date(cc.created_at).toDateString()!==new Date().toDateString())items.push({title:"Control Center schedule įrodymas",detail:cc?"Paskutinis schedule: "+dateLT(cc.created_at):"Naujausio sąrašo schedule paleidimo nerasta",cls:"warn"});
 if(ai.cls!=="good")items.push({title:"Worker agentų ciklas: "+ai.label,detail:ai.detail,cls:ai.cls});
 const bad=state.runs.filter(r=>r.status==="completed"&&r.conclusion!=="success").slice(0,3);
 bad.forEach(r=>items.push({title:r.name+" · "+r.conclusion,detail:"#"+r.run_number+" · "+dateLT(r.created_at),cls:"bad",url:r.html_url}));
 if(state.prs.length)items.push({title:state.prs.length+" atviri PR",detail:state.prs.slice(0,3).map(p=>"#"+p.number+" "+p.title).join(" · "),cls:"warn",url:state.prs[0].html_url});
 if(state.issue?.state==="open")items.push({title:"Pagrindinis alert #145 atviras",detail:state.issue.title||"Reikia Control Center recovery įrodymo",cls:"warn",url:state.issue.html_url});
 if(!items.length)items.push({title:"Kritinių signalų iš gautų šaltinių nėra",detail:"Tai nėra pilnas visų paskyrų ar paslapčių auditas.",cls:"good"});
 $("attention-list").innerHTML=items.slice(0,8).map(x=>'<div class="attention-item '+(x.cls==="good"?"good":"")+'"><span class="signal"></span><div><strong>'+escapeHtml(x.title)+'</strong><small>'+escapeHtml(x.detail)+' '+(x.url?'<a href="'+escapeHtml(x.url)+'" target="_blank" rel="noopener">Atverti ↗</a>':"")+'</small></div></div>').join("");
}
function renderWorkflowSummary(){
 const selected=["site-check.yml","daily-suite.yml","control-center.yml","analytics-snapshot.yml","daily-topic-radar.yml","lighthouse-audit.yml"];
 $("workflow-summary").innerHTML=selected.map(file=>{const d=workflowDefinitions.find(x=>x.file===file);const r=latestFor(file);return '<div class="workflow-row"><div><strong>'+escapeHtml(d?.title||file)+'</strong><small>'+(r?escapeHtml(r.event)+" · "+escapeHtml(dateLT(r.created_at)):"Vykdymo nėra")+'</small></div>'+badge(statusText(r),statusClass(r))+'</div>';}).join("");
 $("workflow-grid").innerHTML=workflowDefinitions.map(d=>{
 const r=latestFor(d.file);const schedule=latestEvent(d.file,"schedule");
 const isScheduled=["site-check.yml","daily-suite.yml","control-center.yml","lighthouse-audit.yml"].includes(d.file);
 const schedText=isScheduled?(schedule?"Paskutinis schedule: "+dateLT(schedule.created_at):"Schedule įrodymo sąraše nėra"):"Grafikas pagal workflow konfigūraciją";
 return '<article class="workflow-card"><h3>'+escapeHtml(d.title)+'</h3><p>'+escapeHtml(d.desc)+'</p><p><b>Numatyta:</b> '+escapeHtml(d.cadence)+'</p><div class="workflow-meta">'+badge(statusText(r),statusClass(r))+(isScheduled?badge(schedule?"schedule rastas":"schedule nepatvirtintas",schedule?"good":"warn"):badge("workflow", "unknown"))+'</div><p>Latest: '+escapeHtml(r?dateLT(r.created_at):"nėra vykdymo")+' · '+escapeHtml(r?.event||"—")+'</p><a href="https://github.com/'+REPO+'/actions/workflows/'+encodeURIComponent(d.file)+'" target="_blank" rel="noopener">Atverti workflow ↗</a>'+(r?' · <a href="'+escapeHtml(r.html_url)+'" target="_blank" rel="noopener">Run #'+escapeHtml(r.run_number)+' ↗</a>':"")+'</article>';
 }).join("");
}
function renderRuns(filter="all"){
 let list=state.runs.slice(0,40);
 if(filter==="schedule"||filter==="workflow_dispatch")list=list.filter(r=>r.event===filter);
 if(filter==="failure")list=list.filter(r=>r.status==="completed"&&r.conclusion!=="success");
 $("runs-table").innerHTML='<table class="runs-table"><thead><tr><th>LAIKAS (LT)</th><th>WORKFLOW</th><th>EVENT</th><th>BŪSENA</th><th>RUN</th></tr></thead><tbody>'+list.slice(0,30).map(r=>'<tr><td>'+escapeHtml(dateLT(r.created_at))+'</td><td>'+escapeHtml(r.name)+'</td><td>'+escapeHtml(r.event)+'</td><td>'+badge(statusText(r),statusClass(r))+'</td><td><a href="'+escapeHtml(r.html_url)+'" target="_blank" rel="noopener">#'+escapeHtml(r.run_number)+' ↗</a></td></tr>').join("")+'</tbody></table>'+(list.length?"":'<p class="muted">Pagal pasirinktą filtrą vykdymų nerasta.</p>');
}
function renderHistory(){
 $("history-count").textContent=state.runs.length+" įrašų gauta";
 $("history-list").innerHTML=state.runs.slice(0,25).map(r=>'<div class="history-item"><time>'+escapeHtml(dateLT(r.created_at))+'</time><div><strong>'+escapeHtml(r.name)+'</strong><small>'+escapeHtml(r.event)+' · '+escapeHtml(r.head_branch||"—")+' · '+escapeHtml(r.head_sha?.slice(0,7)||"")+'</small></div><div>'+badge(statusText(r),statusClass(r))+' <a href="'+escapeHtml(r.html_url)+'" target="_blank" rel="noopener">↗</a></div></div>').join("");
}
function latestSnapshot(archive){
 const snapshots=Array.isArray(archive?.snapshots)?archive.snapshots:[];
 let latest=null;let latestTime=-Infinity;
 for(const snapshot of snapshots){
  if(!snapshot||typeof snapshot!=="object")continue;
  const timestamp=Date.parse(snapshot.generated_at||"");
  if(Number.isFinite(timestamp)&&timestamp>=latestTime){latest=snapshot;latestTime=timestamp;}
 }
 return latest||(snapshots.length?snapshots[snapshots.length-1]:null);
}
function renderAnalytics(){
 const s=latestSnapshot(state.analytics);const m=s?.metrics;const gsc=s?.search_console_details;
 if(m){
 $("metric-stack").innerHTML=[["Aktyvūs naudotojai",fmt(m.active_users)],["Sesijos",fmt(m.sessions)],["Puslapių peržiūros",fmt(m.page_views)]].map(x=>'<div class="metric-line"><span>'+x[0]+'</span><strong>'+x[1]+'</strong></div>').join("");
 $("analytics-panel").innerHTML='<article class="analytics-card"><h3>Google Analytics 4</h3><p>Laikotarpis: '+escapeHtml(s.ga4_period||"nenurodytas")+' · surinkta '+escapeHtml(dateLT(s.generated_at))+'</p><div class="analytics-numbers">'+[['Aktyvūs naudotojai',m.active_users],['Nauji naudotojai',m.new_users],['Sesijos',m.sessions],['Puslapių peržiūros',m.page_views]].map(x=>'<div class="analytics-number"><span>'+x[0]+'</span><strong>'+fmt(x[1])+'</strong></div>').join("")+'</div><div class="analytics-note">Patvirtintos organinės sesijos: '+fmt(m.organic_sessions_verified)+' · GA4 statusas: '+escapeHtml(s.ga4_status)+'</div></article><article class="analytics-card"><h3>Google Search Console</h3><p>Laikotarpis: '+escapeHtml(s.search_console_period||"nenurodytas")+'</p><div class="analytics-numbers">'+[['Parodymai',m.search_impressions],['Paspaudimai',m.search_clicks],['CTR',Number(m.search_ctr||0).toFixed(2)+"%"],['Vid. pozicija',Number(m.average_position||0).toFixed(1)]].map(x=>'<div class="analytics-number"><span>'+x[0]+'</span><strong>'+((typeof x[1]==="string")?escapeHtml(x[1]):fmt(x[1]))+'</strong></div>').join("")+'</div><div class="analytics-note">Sitemap: '+escapeHtml(gsc?.sitemap?.status||"nežinoma")+' · pending: '+(gsc?.sitemap?.is_pending?"taip":"nežinoma")+'. 0 parodymų nėra indeksavimo diagnozė.</div></article>';
 }else{
 $("metric-stack").innerHTML='<p class="muted">Naujausias GA4/GSC agreguotas archyvas šiuo metu nepasiekiamas. Nulis nelaikomas duomenimis.</p>';
 $("analytics-panel").innerHTML='<article class="analytics-card"><h3>GA4 + Search Console</h3><p>Duomenų būsena</p><span class="state warn">Archyvas nerastas / neprieinamas</span><div class="analytics-note">Patikrink analytics workflow ir jo artefaktą. Paslaptys šiame dashboard nerodomos.</div></article>';
 }
 const t=latestSnapshot(state.topics);
 $("topics-panel").innerHTML=t?'<p class="muted">Google News RSS · '+escapeHtml(dateLT(t.generated_at))+' · '+fmt(t.unique_article_links)+' unikalių antraščių nuorodų · '+fmt(t.total_topic_checks)+' temų patikrų</p>'+Object.entries(t.topic_counts||{}).sort((a,b)=>b[1]-a[1]).map(([name,count])=>'<div class="bar-row"><span>'+escapeHtml(name)+'</span><div class="bar-track"><div class="bar-fill" style="width:'+Math.min(100,(count/Math.max(1,...Object.values(t.topic_counts)))*100)+'%"></div></div><b>'+fmt(count)+'</b></div>').join(""):'<p class="muted">Temų archyvas šiuo metu nepasiekiamas.</p>';
 const lh=state.runs.find(r=>r.name.toLowerCase().includes("lighthouse")&&r.conclusion==="success");
 $("lighthouse-panel").innerHTML=lh?'<div class="metric-line"><span>Paskutinis sėkmingas auditas</span><strong>'+escapeHtml(dateLT(lh.updated_at||lh.created_at))+'</strong></div><div class="metric-line"><span>Vykdymas</span><a href="'+escapeHtml(lh.html_url)+'" target="_blank" rel="noopener">#'+escapeHtml(lh.run_number)+' ↗</a></div><div class="analytics-note">Pilni HTML/JSON rezultatai laikomi GitHub Actions artefakte. Dashboard nekuria išvestinių Lighthouse balų.</div>':'<p class="muted">Nerasta sėkmingo Lighthouse vykdymo paskutinių 100 run sąraše.</p>';
}
function renderAgents(){
 const h=state.health;const orchestration=h?.agent_orchestration||{};const core=h?.control_core||{};const ai=aiCycleStatus();
 const cards=[
  {title:"Worker orchestration",value:ai.label,detail:ai.detail,cls:ai.cls},
  {title:"Control Core",value:core.status||"Nežinoma",detail:"Run: "+(core.run_date||"—")+" · JSON: "+(core.decision_json_status||"—"),cls:core.status==="reviewed"?"good":core.status==="needs_evidence"?"warn":"unknown"},
  {title:"D1 atmintis",value:core.memory_status||"Nežinoma",detail:"Atnaujinta: "+dateLT(core.memory_updated_at),cls:core.memory_status==="present"?"good":"warn"},
  {title:"Rekomendacijos",value:fmt(core.recommendation_count),detail:"Patariamosios, ne automatiniai veiksmai",cls:"unknown"},
  {title:"Įrodymų spragos",value:fmt(core.evidence_gap_count),detail:"Kategorijos: "+Object.entries(core.evidence_gap_categories||{}).map(([k,v])=>k+" "+v).join(" · "),cls:Number(core.evidence_gap_count)>0?"warn":"good"},
  {title:"Paskutinis agentų ciklas",value:orchestration.status||"Nežinoma",detail:"Data: "+(orchestration.run_date||"—")+" · pradžia: "+dateLT(orchestration.started_at)+" · kvietimai: "+fmt(orchestration.ai_calls),cls:ai.cls}
 ];
 $("agent-panel").innerHTML=cards.map(x=>'<div class="agent-card"><strong>'+escapeHtml(x.title)+'</strong><small>'+escapeHtml(x.detail)+'</small>'+badge(x.value,x.cls)+'</div>').join("");
 const specialists=Object.entries(core.specialist_statuses||{});
 if(specialists.length)$("agent-panel").innerHTML+='<div class="specialist-list">'+specialists.map(([name,status])=>{const value=String(status);const cls=/^(ok|complete|completed|reviewed)$/i.test(value)?"good":/error|fail|invalid/i.test(value)?"bad":"warn";return '<div class="specialist"><strong>'+escapeHtml(name)+'</strong><small>'+escapeHtml(value)+'</small></div>';}).join("")+'</div>';
}
function renderPrs(){
 $("pr-count").textContent=state.prs.length+" atviri";
 $("prs-list").innerHTML=state.prs.length?state.prs.map(p=>'<div class="pr-row"><div><strong>#'+escapeHtml(p.number)+' · '+escapeHtml(p.title)+'</strong><small>'+escapeHtml(p.head?.ref||"")+' → '+escapeHtml(p.base?.ref||"main")+' · atnaujinta '+escapeHtml(dateLT(p.updated_at))+'</small></div><a href="'+escapeHtml(p.html_url)+'" target="_blank" rel="noopener">Peržiūrėti ↗</a></div>').join(""):'<p class="muted">Atvirų PR nėra.</p>';
}
function renderTools(){
 const h=state.health;
 setState("tool-pages",state.site?.ok?"Vieša svetainė HTTP 200":"Vieša svetainė nepatvirtinta",state.site?.ok?"good":"bad");
 setState("tool-worker",h?.preview_blocked?"CORS: tik oficialus domenas":h?.ok?"Worker /health HTTP 200":"Worker neprieinamas",h?.ok?"good":h?.preview_blocked?"warn":"bad");
 setState("tool-d1",h?.database==="connected"?"D1 prijungta":"D1 nepatvirtinta",h?.database==="connected"?"good":"bad");
 const ai=aiCycleStatus();setState("tool-ai",ai.label+" · "+ai.detail,ai.cls);
}
function renderAll(){
 renderStats();renderAttention();renderWorkflowSummary();renderRuns($("run-filter")?.value||"all");renderHistory();renderAnalytics();renderTools();renderAgents();renderPrs();
 setState("pages-status",state.site?.ok?"HTTP 200 · gyva":"Nepasiekiama",state.site?.ok?"good":"bad");
 setState("worker-arch-status",state.health?.preview_blocked?"Preview CORS ribojimas":state.health?.ok?"HTTP 200":"Neatsako",state.health?.ok?"good":state.health?.preview_blocked?"warn":"bad");
 setState("d1-status",state.health?.database==="connected"?"Connected":"Nežinoma",state.health?.database==="connected"?"good":"warn");
 setState("ai-arch-status",aiCycleStatus().label,aiCycleStatus().cls);
 setState("actions-status",state.runs.length?"Run istorija gauta":"Neprieinama",state.runs.length?"good":"warn");
 setState("coordinator-status","ChatGPT automation · gyvas API statusas neprieinamas","protected");
}
async function loadAnalyticsArchive(kind){
 const today=localDate();const dates=[];
 for(let i=0;i<7;i++){const d=new Date(today+"T12:00:00Z");d.setUTCDate(d.getUTCDate()-i);dates.push(d.toISOString().slice(0,10));}
 for(const date of dates){try{return await getJson("https://raw.githubusercontent.com/"+REPO+"/automation-history/reports/history/"+kind+"/"+date+".json",8000);}catch(e){}}
 return null;
}
async function refresh(){
 if(state.loading)return;state.loading=true;$("refresh-button").disabled=true;$("connection-state").textContent="Atnaujinama…";
 const sources = {
 runs: getJson(GH+"/actions/runs?per_page=100").then(x=>x.workflow_runs||[]),
 prs: getJson(GH+"/pulls?state=open&per_page=50"),
 commit: getJson(GH+"/commits/main"),
 health: getJson(WORKER+"/health"),
 site: fetch(SITE,{method:"HEAD",cache:"no-store"}).then(r=>({ok:r.ok,status:r.status,url:SITE})),
 analytics: loadAnalyticsArchive("analytics"),
 topics: loadAnalyticsArchive("topic-radar"),
 issue: getJson(GH+"/issues/145")
 };
 const sourceKeys=Object.keys(sources);
 const results=await Promise.allSettled(Object.values(sources));
 results.forEach((result,index)=>{if(result.status==="fulfilled")state[sourceKeys[index]]=result.value;});
 state.loadedAt=new Date();renderAll();
 const failed=results.filter(x=>x.status==="rejected").length;
 $("last-updated").textContent="Atnaujinta "+dateLT(state.loadedAt);
 $("connection-state").textContent=failed===0?"Visi šaltiniai atsakė":"Šaltiniai: "+(8-failed)+"/8";
 $("global-alert").hidden=failed===0;
 $("global-alert").textContent=failed?("Nepavyko pasiekti "+failed+" iš 8 duomenų šaltinių. Nepasiekiami duomenys žymimi kaip nežinomi, ne kaip nulis."): "";
 $("refresh-button").disabled=false;state.loading=false;
}
function showView(name){
 document.querySelectorAll(".view-panel").forEach(el=>el.classList.toggle("active",el.id==="view-"+name));
 document.querySelectorAll(".nav-item").forEach(el=>el.classList.toggle("active",el.dataset.view===name));
 const titles={overview:"Apžvalga",architecture:"Architektūra",automations:"Automatizacijos",analytics:"Analitika ir SEO",tools:"Įrankiai ir prieigos",history:"Vykdymų istorija"};
 $("view-title").textContent=titles[name]||"Apžvalga";
 $("page-title").textContent=name==="overview"?"Visas projektas vienoje vietoje":titles[name];
 $("page-subtitle").textContent=name==="overview"?"Tikri GitHub, Worker ir viešos svetainės duomenys. Būsenos atnaujinamos atidarius puslapį ir paspaudus „Atnaujinti“.":"Gyva projekto informacija iš viešų ir autorizuotų agreguotų šaltinių.";
}
document.querySelectorAll(".nav-item").forEach(btn=>btn.addEventListener("click",()=>showView(btn.dataset.view)));
document.querySelectorAll("[data-go]").forEach(btn=>btn.addEventListener("click",()=>showView(btn.dataset.go)));
$("refresh-button").addEventListener("click",refresh);
$("run-filter").addEventListener("change",e=>renderRuns(e.target.value));
refresh();
setInterval(refresh,300000);
})();