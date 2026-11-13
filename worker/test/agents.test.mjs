import test from "node:test";
import assert from "node:assert/strict";
import { runAgentOrchestration, isVilniusAgentRunTime, parseResult, extractResponseText } from "../src/agents.mjs";
function mockEnv({ai=true,existingRun=false,reserveErrorAt=0,reserveErrorBeforeCommit=false,reserveReadbackError=false,invalidEventPayload=false,modelResponse=null}={}) {
 const state={inserted:false,aiCalls:0,updates:[],reservationErrorThrown:false};
 const env={FETCH:async()=>new Response("<html><body><p>Test content</p></body></html>",{status:200}),DB:{prepare(sql){return {
  bind(...values){return {
   run:async()=>{if(sql.includes("INSERT OR IGNORE INTO agent_runs")){if(state.inserted||existingRun)return{meta:{changes:0}};state.inserted=true;return{meta:{changes:1}};}state.updates.push({sql,values});return{meta:{changes:1}};},
   first:async()=>{if(sql.includes("UPDATE agent_runs SET ai_calls")){const next=state.aiCalls+1;if(reserveErrorAt===next&&!state.reservationErrorThrown){state.reservationErrorThrown=true;if(!reserveErrorBeforeCommit)state.aiCalls=next;throw new SyntaxError("Unexpected_end_of_JSON_input");}state.aiCalls=next;return state.aiCalls<=5?{ai_calls:state.aiCalls}:null;}if(sql.includes("SELECT ai_calls FROM agent_runs")){if(reserveReadbackError)throw new SyntaxError("Unexpected_end_of_JSON_input");return{ai_calls:state.aiCalls};}return null;},
   all:async()=>({results:[]}),
  };},
  all:async()=>({results:invalidEventPayload?[{kind:"analytics_snapshot",payload_json:"{truncated",created_at:"2026-11-13T00:00:00.000Z"}]:[]}),
 };}}};
 if(ai)env.AI={run:async()=>({response:modelResponse??JSON.stringify({status:"reviewed",findings:[],recommendations:[],evidence_gaps:[]})})};
 return{env,state};
}
test("orchestrator performs five capped AI calls and stores a read-only report",async()=>{const{env,state}=mockEnv();const result=await runAgentOrchestration(env);assert.equal(result.completed,true);assert.equal(result.ai_calls,5);assert.equal(state.aiCalls,5);assert.ok(state.updates.some(x=>x.sql.includes("status='completed'")));});
test("orchestrator is idempotent per UTC day",async()=>{const{env,state}=mockEnv({existingRun:true});const result=await runAgentOrchestration(env);assert.equal(result.skipped,true);assert.equal(result.reason,"daily_run_already_started");assert.equal(state.aiCalls,0);});
test("orchestrator refuses to run without Workers AI binding",async()=>{const{env,state}=mockEnv({ai:false});const result=await runAgentOrchestration(env);assert.equal(result.skipped,true);assert.equal(result.reason,"ai_binding_missing");assert.equal(state.aiCalls,0);});

test("agent schedule stays at 10:20 Europe/Vilnius in winter and summer", () => {
 assert.equal(isVilniusAgentRunTime(new Date("2026-11-13T08:20:00.000Z")), true);
 assert.equal(isVilniusAgentRunTime(new Date("2026-06-13T07:20:00.000Z")), true);
 assert.equal(isVilniusAgentRunTime(new Date("2026-11-13T08:19:00.000Z")), false);
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

test("model JSON must contain every required schema field",()=>{
 assert.equal(parseResult('{"status":"reviewed"}').status,"invalid_json");
 assert.equal(parseResult('{"status":"reviewed","findings":[],"recommendations":[],"evidence_gaps":[]}').status,"reviewed");
});

test("invalid model output fails the orchestration and persists partial memory",async()=>{
 const{env,state}=mockEnv({modelResponse:'{"status":"reviewed"'});
 const result=await runAgentOrchestration(env);
 assert.equal(result.completed,false);
 assert.match(result.error,/model_analytics:model_output_invalid_json/);
 assert.equal(result.memory_persisted,true);
 assert.ok(state.updates.some(x=>x.sql.includes("status='failed'")));
 assert.ok(state.updates.some(x=>x.sql.includes("control_core_memory")));
 assert.equal(state.updates.some(x=>x.sql.includes("status='completed'")),false);
});
