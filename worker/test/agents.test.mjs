import test from "node:test";
import assert from "node:assert/strict";
import { runAgentOrchestration, isVilniusAgentRunTime } from "../src/agents.mjs";
function mockEnv({ai=true,existingRun=false}={}) {
 const state={inserted:false,aiCalls:0,updates:[]};
 const env={FETCH:async()=>new Response("<html><body><p>Test content</p></body></html>",{status:200}),DB:{prepare(sql){return {
  bind(...values){return {
   run:async()=>{if(sql.includes("INSERT OR IGNORE INTO agent_runs")){if(state.inserted||existingRun)return{meta:{changes:0}};state.inserted=true;return{meta:{changes:1}};}state.updates.push({sql,values});return{meta:{changes:1}};},
   first:async()=>{if(sql.includes("UPDATE agent_runs SET ai_calls")){state.aiCalls++;return state.aiCalls<=5?{ai_calls:state.aiCalls}:null;}return null;},
   all:async()=>({results:[]}),
  };},
  all:async()=>({results:[]}),
 };}}};
 if(ai)env.AI={run:async()=>({response:JSON.stringify({status:"reviewed",findings:[],recommendations:[],evidence_gaps:[]})})};
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
