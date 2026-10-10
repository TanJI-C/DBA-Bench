(function(){
    "use strict";
    let experiments=[];
    let timer=null;
    document.addEventListener("DOMContentLoaded",init);

    async function init(){
        bind();
        experiments=await fetchJson("/api/experiments");
        const select=document.getElementById("experiment-select");
        experiments.forEach(item=>select.appendChild(new Option(item.experiment_id,item.experiment_id)));
        const requested=new URLSearchParams(location.search).get("experiment");
        if(requested){select.value=requested;await loadRuns();}
    }
    function bind(){
        document.getElementById("experiment-select").addEventListener("change",loadRuns);
        document.getElementById("run-search").addEventListener("input",()=>{clearTimeout(timer);timer=setTimeout(loadRuns,220)});
        ["run-scenario","run-agent","run-status"].forEach(id=>document.getElementById(id).addEventListener("change",loadRuns));
        document.getElementById("run-refresh").addEventListener("click",async()=>{experiments=await fetchJson("/api/experiments");await loadRuns()});
    }
    async function loadRuns(){
        const id=document.getElementById("experiment-select").value;
        if(!id)return;
        const params=new URLSearchParams();
        const values={q:value("run-search"),scenario:value("run-scenario"),agent:value("run-agent"),status:value("run-status")};
        Object.entries(values).forEach(([key,val])=>{if(val)params.set(key,val)});
        const payload=await fetchJson(`/api/experiments/${encodeURIComponent(id)}/runs?${params}`);
        fill("run-scenario",payload.filters.scenarios,"全部场景");fill("run-agent",payload.filters.agents,"全部 Agent");fill("run-status",payload.filters.statuses,"全部状态");
        render(id,payload);
        const url=new URL(location.href);url.searchParams.set("experiment",id);history.replaceState(null,"",url);
    }
    function render(id,payload){
        const table=document.getElementById("experiment-runs-table");
        table.dataset.tableId=`experiment-runs:${id}`;
        const root=document.getElementById("run-rows");root.replaceChildren(...payload.items.map(run=>{
            const row=document.createElement("tr");
            const scored=run.outcome_pass!==null&&run.outcome_pass!==undefined;
            const score=scored?`DP:${passMark(run.diagnosis_pass)} OP:${passMark(run.outcome_pass)} SP:${passMark(run.safe_pass)}`:"--";
            const sortScore=scored?[run.diagnosis_pass,run.outcome_pass,run.safe_pass].filter(Boolean).length:"";
            const modelText=`${run.agent_id}${run.model?" · "+run.model:""}`;
            const links=[];
            if(run.trace_path){const file=run.trace_path.split("/").pop();links.push(`<a href="/raw-traces?file=${encodeURIComponent(file)}">JSON</a>`,`<a href="/?file=${encodeURIComponent(file)}">Trace</a>`)}
            if(run.evaluator_path)links.push(`<a href="/${escapeHtml(run.evaluator_path)}">Evaluator</a>`);
            if(run.stdout_path)links.push(`<a href="/${escapeHtml(run.stdout_path)}">stdout</a>`);
            row.innerHTML=`<td><div class="run-id">${escapeHtml(run.run_id)}</div><div class="run-sub">rep ${run.repetition} · seed ${run.seed} · attempt ${run.attempt}</div></td>`
                +`<td data-filter-value="${escapeHtml(run.scenario_id)}">${escapeHtml(run.scenario_id)}</td>`
                +`<td data-filter-value="${escapeHtml(run.case_id||"")}">${escapeHtml(run.case_id||"--")}</td>`
                +`<td data-filter-value="${escapeHtml(modelText)}">${escapeHtml(modelText)}</td>`
                +`<td data-sort-value="${escapeHtml(run.status)}"><span class="status ${escapeHtml(run.status)}">${escapeHtml(run.status)}</span>${run.failure_category?`<div class="run-sub">${escapeHtml(run.failure_category)}</div>`:""}</td>`
                +`<td data-sort-value="${sortScore}">${score}</td>`
                +`<td data-sort-value="${run.duration_seconds===null||run.duration_seconds===undefined?"":run.duration_seconds}">${run.duration_seconds===null||run.duration_seconds===undefined?"--":Number(run.duration_seconds).toFixed(1)+"s"}</td>`
                +`<td data-sort-value="${escapeHtml(run.started_at||"")}">${formatTime(run.started_at)}</td>`
                +`<td><div class="artifacts">${links.join("")}</div></td>`;
            return row;
        }));
        document.getElementById("run-empty").style.display=payload.items.length?"none":"block";
        if(window.TableTools)TableTools.enhance(table);
        const info=experiments.find(item=>item.experiment_id===payload.experiment_id);
        document.getElementById("experiment-summary").textContent=`${payload.experiment_id} · ${payload.total} 条匹配 · 全部 ${info?.runs??"--"} · 成功 ${info?.succeeded??"--"} · 异常 ${info?.failed??"--"}`;
    }
    function fill(id,values,label){const el=document.getElementById(id),current=el.value;el.replaceChildren(new Option(label,""),...values.map(v=>new Option(v,v)));el.value=current}
    function value(id){return document.getElementById(id).value.trim()}
    async function fetchJson(url){const response=await fetch(url);if(!response.ok)throw new Error(`${url}: ${response.status}`);return response.json()}
    function formatTime(value){return value?new Date(value).toLocaleString():"--"}
    function passMark(value){return value===null||value===undefined?"N/A":value?"P":"F"}
    function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c])}
}());
