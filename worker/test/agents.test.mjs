import test from "node:test";
import assert from "node:assert/strict";
import { runAgentOrchestration, isVilniusAgentRunTime, isAgentScheduledEvent, isAgentCatchUpEvent, shouldRunAgentOrchestration, parseResult, extractResponseText, callModel } from "../src/agents.mjs";
function mockEnv({ai=true,existingRun=false,reserveErrorAt=0,reserveErrorBeforeCommit=false,reserveReadbackError=false,invalidEventPayload=false,modelResponse=null,modelResponses=null,modelResponder=null}={}) {
 const state={inserted:false,aiCalls:0,updates:[],reservationErrorThrown:false};
 const env={FETCH:async()=>new Response("<html><body><p>Test content</p></body></html>",{status:200}),DB:{prepare(sql){return {
  bind(...values){return {
   run:async()=>{if(sql.includes("INSERT OR IGNORE INTO agent_runs")){if(state.inserted||existingRun)return{meta:{changes:0}};state.inserted=true;return{meta:{changes:1}};}state.updates.push({sql,values});return{meta:{changes:1}};},
   first:async()=>{if(sql.includes("UPDATE agent_runs SET ai_calls")){const next=state.aiCalls+1;if(reserveErrorAt===next&&!state.reservationErrorThrown){state.reservationErrorThrown=true;if(!reserveErrorBeforeCommit)state.aiCalls=next;throw new SyntaxError("Unexpected_end_of_JSON_input");}state.aiCalls=next;return state.aiCalls<=5?{ai_calls:state.aiCalls}:null;}if(sql.includes("SELECT ai_calls FROM agent_runs")){if(reserveReadbackError)throw new SyntaxError("Unexpected_end_of_JSON_input");return{ai_calls:state.aiCalls};}return null;},
   all:async()=>({results:[]}),
  };},
  all:async()=>({results:invalidEventPayload?[{kind:"analytics_snapshot",payload_json:"{truncated",created_at:"2026-11-13T00:00:00.000Z"}]:[]}),
 };}}};
 if(ai)env.AI={run:async(model,options)=>({response:typeof modelResponder==="function"?modelResponder(options,state):(Array.isArray(modelResponses)?(modelResponses[state.aiCalls-1]??JSON.stringify({status:"reviewed",findings:[],recommendations:[],evidence_gaps:[]})):(modelResponse??JSON.stringify({status:"reviewed",findings:[],recommendations:[],evidence_gaps:[]})))})};
 return{env,state};
}
test("orchestrator performs five capped AI calls and stores a read-only report",async()=>{const{env,state}=mockEnv();const result=await runAgentOrchestration(env);assert.equal(result.completed,true);assert.equal(result.ai_calls,5);assert.equal(state.aiCalls,5);assert.ok(state.updates.some(x=>x.sql.includes("status='completed'")));});
test("orchestrator is idempotent per UTC day",async()=>{const{env,state}=mockEnv({existingRun:true});const result=await runAgentOrchestration(env);assert.equal(result.skipped,true);assert.equal(result.reason,"daily_run_already_started");assert.equal(state.aiCalls,0);});
test("orchestrator refuses to run without Workers AI binding",async()=>{const{env,state}=mockEnv({ai:false});const result=await runAgentOrchestration(env);assert.equal(result.skipped,true);assert.equal(result.reason,"ai_binding_missing");assert.equal(state.aiCalls,0);});

test("agent schedule stays at 13:20 Europe/Vilnius in winter and summer", () => {
 assert.equal(isVilniusAgentRunTime(new Date("2026-11-13T11:20:00.000Z")), true);
 assert.equal(isVilniusAgentRunTime(new Date("2026-06-13T10:20:00.000Z")), true);
 assert.equal(isVilniusAgentRunTime(new Date("2026-11-13T11:19:00.000Z")), false);
});

test("agent cron uses the correct winter UTC trigger for 13:20 Vilnius", () => {
 assert.equal(isAgentScheduledEvent({
  cron: "20 10,11 * * *",
  scheduledTime: Date.parse("2026-11-14T11:20:00.000Z"),
 }), true);
});

test("agent cron uses the correct summer UTC trigger for 13:20 Vilnius", () => {
 assert.equal(isAgentScheduledEvent({
  cron: "20 10,11 * * *",
  scheduledTime: Date.parse("2026-06-14T10:20:00.000Z"),
 }), true);
});

test("agent cron ignores the old 10:20 Vilnius winter trigger", () => {
 assert.equal(isAgentScheduledEvent({
  cron: "20 10,11 * * *",
  scheduledTime: Date.parse("2026-11-14T08:20:00.000Z"),
 }), false);
});


test("incomplete model JSON is converted to a bounded evidence gap",()=>{
 const result=parseResult('{"status":"reviewed"');
 assert.equal(result.status,"invalid_json");
 assert.match(result.evidence_gaps[0],/incomplete JSON/);
 assert.equal(result.requires_human_approval,true);
});

test("reservation reconciles a D1 response error after the counter was committed",async()=>{
 const{env,state}=mockEnv({reserveErrorAt:2});
 const result=await runAgentOrchestration(env);
 assert.equal(result.completed,true);
 assert.equal(state.aiCalls,5);
 assert.ok(state.updates.some(x=>x.sql.includes("status='completed'")));
});

test("reservation retries once when D1 failed before committing the counter",async()=>{
 const{env,state}=mockEnv({reserveErrorAt:2,reserveErrorBeforeCommit:true});
 const result=await runAgentOrchestration(env);
 assert.equal(result.completed,true);
 assert.equal(state.aiCalls,5);
 assert.ok(state.updates.some(x=>x.sql.includes("status='completed'")));
});

test("unrecoverable reservation readback preserves partial control memory",async()=>{
 const{env,state}=mockEnv({reserveErrorAt:2,reserveReadbackError:true});
 const result=await runAgentOrchestration(env);
 assert.equal(result.completed,false);
 assert.match(result.error,/reserve_topics:reservation_readback_failed/);
 assert.equal(result.memory_persisted,true);
 const failure=state.updates.find(x=>x.sql.includes("status='failed'"));
 assert.match(failure.values[0],/^reserve_topics:/);
 const memory=state.updates.find(x=>x.sql.includes("control_core_memory"));
 assert.ok(memory,"partial failed run should still persist long-term memory");
 assert.match(memory.values[1],/partial/);
});

test("orchestrator skips malformed stored event JSON and preserves an evidence gap",async()=>{
 const{env,state}=mockEnv({invalidEventPayload:true});
 const result=await runAgentOrchestration(env);
 assert.equal(result.completed,true);
 const completed=state.updates.find(x=>x.sql.includes("status='completed'"));
 const report=JSON.parse(completed.values[0]);
 assert.equal(report.data_quality.invalid_event_payload_count,1);
 assert.ok(report.coordinator.evidence_gaps.some(x=>x.includes("invalid stored event payload")));
});

test("model JSON with missing schema fields is preserved as needs_evidence",()=>{
 const partial=parseResult('{"status":"reviewed"}');
 assert.equal(partial.status,"needs_evidence");
 assert.equal(partial.partial_schema,true);
 assert.match(partial.evidence_gaps[0],/findings, recommendations, evidence_gaps/);
 assert.equal(parseResult('{"status":"reviewed","findings":[],"recommendations":[],"evidence_gaps":[]}').status,"reviewed");
});

test("model statuses are normalized to the control-core status contract",()=>{
 const noData=parseResult(JSON.stringify({status:"no data",findings:["There is no verified topic demand."],recommendations:[],evidence_gaps:["No search-volume evidence."]}));
 assert.equal(noData.status,"needs_evidence");
 assert.equal(noData.evidence_gaps[0],"No search-volume evidence.");
 const monitor=parseResult(JSON.stringify({status:"monitor",findings:[],recommendations:[],evidence_gaps:[]}));
 assert.equal(monitor.status,"needs_evidence");
 assert.match(monitor.evidence_gaps[0],/needs additional evidence/);
 const unknown=parseResult(JSON.stringify({status:"observe",findings:[],recommendations:[],evidence_gaps:[]}));
 assert.equal(unknown.status,"needs_evidence");
 assert.match(unknown.evidence_gaps[0],/unsupported status/);
 const completed=parseResult(JSON.stringify({status:"completed",findings:[],recommendations:[],evidence_gaps:[]}));
 assert.equal(completed.status,"reviewed");
});

test("model output is bounded to one short item per array",()=>{
 const result=parseResult(JSON.stringify({status:"reviewed",findings:["first","second"],recommendations:["first","second"],evidence_gaps:["first","second"]}));
 assert.deepEqual(result.findings,["first"]);
 assert.deepEqual(result.recommendations,["first"]);
 assert.deepEqual(result.evidence_gaps,["first"]);
});

test("partial JSON schema is preserved as needs_evidence and counted as degraded",async()=>{
 const valid=JSON.stringify({status:"reviewed",findings:[],recommendations:[],evidence_gaps:[]});
 const partial='{"status":"reviewed","findings":["Bounded finding"],"recommendations":[]}';
 const{env,state}=mockEnv({modelResponder:options=>options.input?.some(item=>typeof item.content==="string"&&item.content.includes("Peržiūrėk viešų puslapių tekstą ir struktūrą."))?partial:valid});
 const result=await runAgentOrchestration(env);
 assert.equal(result.completed,true);
 assert.equal(result.ai_calls,5);
 const completed=state.updates.find(x=>x.sql.includes("status='completed'"));
 const report=JSON.parse(completed.values[0]);
 const specialist=report.specialists["content-review"];
 assert.equal(specialist.status,"needs_evidence");
 assert.equal(specialist.partial_schema,true);
 assert.match(specialist.evidence_gaps[0],/evidence_gaps/);
 assert.equal(report.data_quality.partial_schema_specialist_count,1);
 assert.equal(report.data_quality.degraded_specialist_count,1);
 assert.ok(report.coordinator.evidence_gaps.some(x=>x.includes("content-review")));
});

test("invalid specialist output is retained as an evidence gap and does not stop the daily cycle",async()=>{
 const valid=JSON.stringify({status:"reviewed",findings:[],recommendations:[],evidence_gaps:[]});
 const{env,state}=mockEnv({modelResponses:[valid,valid,valid,'{"status":"reviewed"',valid]});
 const result=await runAgentOrchestration(env);
 assert.equal(result.completed,true);
 assert.equal(state.aiCalls,5);
 const completed=state.updates.find(x=>x.sql.includes("status='completed'"));
 assert.ok(completed);
 const report=JSON.parse(completed.values[0]);
 assert.equal(report.specialists["content-review"].status,"invalid_json");
 assert.equal(report.data_quality.degraded_specialist_count,1);
 assert.ok(report.coordinator.evidence_gaps.some(x=>x.includes("content-review")));
 assert.ok(state.updates.some(x=>x.sql.includes("control_core_memory")));
});

test("invalid coordinator output uses deterministic read-only aggregation",async()=>{
 const valid=JSON.stringify({status:"reviewed",findings:["Patikrintas faktas"],recommendations:["Peržiūrėti įrodymus"],evidence_gaps:[]});
 const{env,state}=mockEnv({modelResponses:[valid,valid,valid,valid,'{"status":"reviewed"']});
 const result=await runAgentOrchestration(env);
 assert.equal(result.completed,true);
 assert.equal(state.aiCalls,5);
 const completed=state.updates.find(x=>x.sql.includes("status='completed'"));
 const report=JSON.parse(completed.values[0]);
 assert.equal(report.coordinator.status,"fallback");
 assert.ok(report.coordinator.findings.includes("analytics: Patikrintas faktas"));
 assert.ok(report.coordinator.evidence_gaps.some(x=>x.includes("deterministic aggregation")));
});

test("repeated invalid model outputs use deterministic fallback and persist evidence-aware memory",async()=>{
 const{env,state}=mockEnv({modelResponse:'{"status":"reviewed"'});
 const result=await runAgentOrchestration(env);
 assert.equal(result.completed,true);
 assert.equal(result.ai_calls,4,"return the actual reserved call count when coordinator is skipped");
 assert.equal(state.aiCalls,4,"skip the coordinator call when no specialist produced usable evidence");
 const completed=state.updates.find(x=>x.sql.includes("status='completed'"));
 assert.ok(completed);
 const report=JSON.parse(completed.values[0]);
 assert.equal(report.ai_calls,4);
 assert.equal(report.coordinator.status,"fallback");
 assert.ok(Object.values(report.specialists).every(item=>item.status==="invalid_json"));
 assert.ok(report.coordinator.evidence_gaps.length>0);
 assert.ok(state.updates.some(x=>x.sql.includes("control_core_memory")));
 assert.equal(state.updates.some(x=>x.sql.includes("status='failed'")),false);
});

test("Workers AI receives enough output budget for the complete JSON response",async()=>{
 let received;
 const env={AI:{run:async(model,options)=>{received={model,options};return{response:JSON.stringify({status:"reviewed",findings:[],recommendations:[],evidence_gaps:[]})};}}};
 const result=await callModel(env,"Return only compact JSON.","bounded test input");
 assert.equal(result.status,"reviewed");
 assert.equal(received.model,"@cf/openai/gpt-oss-20b");
 assert.equal(received.options.max_output_tokens,1024);
 assert.equal(received.options.reasoning.effort,"low");
});


test("agent cron uses Cloudflare scheduledTime even when invocation is delayed",()=>{
 const controller={cron:"20 10,11 * * *",scheduledTime:Date.parse("2026-11-14T11:20:00.000Z")};
 assert.equal(isAgentScheduledEvent(controller),true);
});
test("agent cron ignores the old 10:20 Vilnius winter trigger",()=>{
 const controller={cron:"20 10,11 * * *",scheduledTime:Date.parse("2026-11-14T08:20:00.000Z")};
 assert.equal(isAgentScheduledEvent(controller),false);
});
test("agent cron ignores heartbeat events and missing scheduled timestamps",()=>{
 assert.equal(isAgentScheduledEvent({cron:"*/15 * * * *",scheduledTime:Date.parse("2026-11-14T11:20:00.000Z")}),false);
 assert.equal(isAgentScheduledEvent({cron:"20 10,11 * * *"}),false);
});


test("model prompt constrains JSON size to reduce truncated specialist responses",async()=>{let prompt="";const env={AI:{run:async(model,options)=>{prompt=options.input[0].content;return{response:JSON.stringify({status:"reviewed",findings:[],recommendations:[],evidence_gaps:[]})};}}};await callModel(env,"Base role.","Short input");assert.match(prompt,/vieną JSON objektą be Markdown/);assert.match(prompt,/status \(tiksliai „reviewed“ arba „needs_evidence“\)/);assert.match(prompt,/daugiausia po 1 trumpą įrašą/);assert.match(prompt,/iki 120 simbolių/);});


test("heartbeat catch-up opens at 13:20 Vilnius in both winter and summer", () => {
 const winter = { cron: "*/15 * * * *", scheduledTime: Date.parse("2026-11-14T11:30:00.000Z") };
 const summer = { cron: "*/15 * * * *", scheduledTime: Date.parse("2026-06-14T10:30:00.000Z") };
 const before = { cron: "*/15 * * * *", scheduledTime: Date.parse("2026-11-14T11:15:00.000Z") };
 assert.equal(isAgentCatchUpEvent(winter), true);
 assert.equal(isAgentCatchUpEvent(summer), true);
 assert.equal(isAgentCatchUpEvent(before), false);
 assert.equal(isAgentCatchUpEvent({ cron: "20 10,11 * * *", scheduledTime: winter.scheduledTime }), false);
});

test("daily orchestration waits for a same-day analytics or topic snapshot", async () => {
 const controller = { cron: "*/15 * * * *", scheduledTime: Date.parse("2026-11-15T11:30:00.000Z") };
 const makeEnv = ({existingRun=null,rows=[]}={}) => ({
  DB: { prepare(sql) {
   return {
    bind() { return { first: async () => sql.includes("FROM agent_runs") ? existingRun : null }; },
    all: async () => ({results: rows}),
   };
  } },
 });
 const today = makeEnv({rows:[{kind:"analytics_snapshot",created_at:"2026-11-15T13:51:00.000Z"}]});
 const yesterday = makeEnv({rows:[{kind:"topic_snapshot",created_at:"2026-11-14T13:51:00.000Z"}]});
 const none = makeEnv();
 assert.equal(await shouldRunAgentOrchestration(today,controller), true);
 assert.equal(await shouldRunAgentOrchestration(yesterday,controller), false);
 assert.equal(await shouldRunAgentOrchestration(none,controller), false);
});

test("daily orchestration never starts a second time after a run was reserved", async () => {
 const controller = { cron: "20 10,11 * * *", scheduledTime: Date.parse("2026-11-15T11:20:00.000Z") };
 const env = {
  DB: { prepare() { return { bind() { return {
   first: async () => ({run_date:"2026-11-15"}),
   all: async () => { throw new Error("snapshot lookup should not run after an existing daily run"); },
  }; } }; } },
 };
 assert.equal(await shouldRunAgentOrchestration(env,controller), false);
});
