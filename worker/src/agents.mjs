export function isVilniusAgentRunTime(date = new Date()) {
  const localTime = new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/Vilnius", hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(date);
  return localTime === "10:20";
}

import { buildControlDecision, persistControlDecision } from "./control-core.mjs";
const MODEL = "@cf/openai/gpt-oss-20b";
const MAX_DAILY_CALLS = 5;
const MAX_INPUT_CHARS = 6000;
const MAX_OUTPUT_TOKENS = 192;
const SITE = "https://pettraffic-ai.pages.dev";
const CONTENT_PATHS = ["/articles/kada-kreiptis-i-veterinara.html", "/articles/kate-negali-pasislapinti-skubi-pagalba.html", "/articles/kate-viduriuoja-ka-daryti.html", "/articles/suo-viduriuoja-ka-daryti.html"];
const AGENTS = [
 { id:"analytics", label:"Analitikos agentas", kinds:["analytics_snapshot"], task:"Įvertink tik GA4 ir Search Console suvestines. Atskirk faktus nuo prielaidų, nurodyk duomenų trūkumus ir tik palyginamais laikotarpiais pagrįstas tendencijas." },
 { id:"topics", label:"Temų agentas", kinds:["topic_snapshot"], task:"Įvertink temų radaro išvestį. Nelaikyk temų patvirtinta paklausa be skaičių ir šaltinių. Atrink daugiausia tris temas papildomam tyrimui." },
 { id:"technical-seo", label:"Techninio SEO agentas", kinds:["control_center_snapshot","recommendation_snapshot"], task:"Įvertink kontrolės centro ir rekomendacijų suvestines. Ieškok tik konkrečių, patikrinamų techninių problemų. Nekeisk kodo, DNS ar infrastruktūros." },
 { id:"content-review", label:"Turinio peržiūros agentas", kinds:[], task:"Peržiūrėk viešų puslapių tekstą ir struktūrą. Pažymėk galimai neparemtus veterinarinius teiginius, trūkstamas autoritetingas nuorodas ir aiškumo problemas. Netvirtink medicininių faktų be šaltinių." },
];
function parseResult(raw) {
 if(typeof raw!=="string") throw new Error("invalid_model_response");
 const cleaned=raw.trim().replace(/^\x60{3}(?:json)?\s*/i,"").replace(/\s*\x60{3}$/i,"");
 const value=JSON.parse(cleaned);
 if(!value||typeof value!=="object"||Array.isArray(value)) throw new Error("invalid_model_json");
 const strings=k=>Array.isArray(value[k])?value[k].filter(x=>typeof x==="string").slice(0,5).map(x=>x.slice(0,400)):[];
 return {status:typeof value.status==="string"?value.status.slice(0,40):"reviewed",findings:strings("findings"),recommendations:strings("recommendations"),evidence_gaps:strings("evidence_gaps"),requires_human_approval:true};
}
async function callModel(env,system,input) {
 const result=await env.AI.run(MODEL,{messages:[{role:"system",content:system},{role:"user",content:input.slice(0,MAX_INPUT_CHARS)}],max_tokens:MAX_OUTPUT_TOKENS,temperature:0.2});
 return parseResult(typeof result?.response==="string"?result.response:"");
}
async function getEvents(env) {
 const rows=await env.DB.prepare("SELECT kind,payload_json,created_at FROM events ORDER BY created_at DESC LIMIT 30").all();
 return (rows.results||[]).map(row=>({kind:row.kind,created_at:row.created_at,payload:JSON.parse(row.payload_json)}));
}
async function getPublicContent(env) {
 const pages=[]; const fetcher=env.FETCH||fetch;
 for(const path of CONTENT_PATHS) {
  try {
   const response=await fetcher(SITE+path,{headers:{"user-agent":"PetTraffic-AgentContentReview/1.0"},redirect:"follow"});
   if(!response.ok){pages.push({path,status:response.status,text:""});continue;}
   const html=await response.text();
   const text=html.replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi," ").replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi," ")
    .replace(/<[^>]+>/g," ").replace(/&nbsp;/gi," ").replace(/&amp;/gi,"&").replace(/&lt;/gi,"<").replace(/&gt;/gi,">")
    .replace(/&quot;/gi,'"').replace(/&#39;/gi,"'").replace(/\s+/g," ").trim();
   pages.push({path,status:response.status,text:text.slice(0,900)});
  } catch { pages.push({path,status:0,text:""}); }
 }
 return pages;
}
async function reserveCall(env,date) {
 const row=await env.DB.prepare("UPDATE agent_runs SET ai_calls=ai_calls+1 WHERE run_date=? AND ai_calls<? RETURNING ai_calls").bind(date,MAX_DAILY_CALLS).first();
 return Boolean(row);
}
export async function runAgentOrchestration(env) {
 if(!env.DB||!env.AI)return {skipped:true,reason:!env.DB?"database_not_bound":"ai_binding_missing"};
 const date=new Date().toISOString().slice(0,10);
 const inserted=await env.DB.prepare("INSERT OR IGNORE INTO agent_runs (run_date,status,ai_calls,started_at) VALUES (?,'running',0,?)").bind(date,new Date().toISOString()).run();
 if(!inserted.meta?.changes)return {skipped:true,reason:"daily_run_already_started"};
 try {
  const events=await getEvents(env); const pages=await getPublicContent(env); const specialists={};
  for(const agent of AGENTS) {
   const source=agent.id==="content-review"?{public_pages:pages}:{verified_snapshots:events.filter(e=>agent.kinds.includes(e.kind))};
   if(!(await reserveCall(env,date)))throw new Error("daily_ai_call_cap_reached");
   specialists[agent.id]={label:agent.label,...await callModel(env,"Tu esi Pet traffic projekto read-only specialistas. Atsakyk tik validžiu JSON: {status:string,findings:string[],recommendations:string[],evidence_gaps:string[]}. Naudok tik pateiktus duomenis. Nekeisk svetainės ir neprašyk publikuoti. Jei duomenų nepakanka, aiškiai pasakyk.",JSON.stringify({task:agent.task,source}))};
  }
  if(!(await reserveCall(env,date)))throw new Error("daily_ai_call_cap_reached");
  const coordinator=await callModel(env,"Tu esi Pet traffic centrinis koordinatorius. Sujunk keturių specialistų rezultatus į trumpą prioritetinę ataskaitą. Atsakyk tik validžiu JSON: {status:string,findings:string[],recommendations:string[],evidence_gaps:string[]}. Nespėliok. Jokio publikavimo, kodo keitimo ar infrastruktūros veiksmų; rekomendacijoms būtinas žmogaus patvirtinimas.",JSON.stringify({date_utc:date,specialist_results:specialists}));
  const report={date_utc:date,generated_at:new Date().toISOString(),model:MODEL,ai_calls:MAX_DAILY_CALLS,specialists,coordinator,read_only:true,publication_enabled:false};
  const decision=buildControlDecision(report);
  await persistControlDecision(env,decision);
  await env.DB.prepare("UPDATE agent_runs SET status='completed',report_json=?,completed_at=? WHERE run_date=?").bind(JSON.stringify({...report,control_decision:decision}),new Date().toISOString(),date).run();
  return {completed:true,run_date:date,ai_calls:MAX_DAILY_CALLS,control_core_version:decision.core_version};
 } catch(error) {
  await env.DB.prepare("UPDATE agent_runs SET status='failed',error_code=?,completed_at=? WHERE run_date=?").bind(String(error?.message||"agent_run_failed").slice(0,80),new Date().toISOString(),date).run();
  return {completed:false,run_date:date,error:String(error?.message||"agent_run_failed").slice(0,80)};
 }
}
