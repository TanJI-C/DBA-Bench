(function(){
    "use strict";
    const REFRESH_MS=10000;
    let timer=null;
    document.addEventListener("DOMContentLoaded",init);

    async function init(){
        document.getElementById("result-set-select").addEventListener("change",load);
        document.getElementById("results-refresh").addEventListener("click",load);
        const matrixSection=document.getElementById("matrix-section");
        matrixSection.addEventListener("mouseover",event=>{
            const th=event.target.closest("th.num");
            if(th){showMatrixTooltip(th);return;}
            const td=event.target.closest("td.cell-analyzed");
            if(td){showAnalysisTooltip(td);return;}
            hideMatrixTooltip();
        });
        matrixSection.addEventListener("mouseleave",hideMatrixTooltip);
        const sets=await fetchJson("/api/result-sets");
        const select=document.getElementById("result-set-select");
        sets.forEach(item=>select.appendChild(new Option(item.result_set_id,item.result_set_id)));
        const requested=new URLSearchParams(location.search).get("result_set");
        if(requested){select.value=requested;await load()}
    }

    async function load(){
        clearTimeout(timer);
        const id=document.getElementById("result-set-select").value;
        if(!id)return;
        try{
            const resultSet=await fetchJson(`/api/result-sets/${encodeURIComponent(id)}`);
            const categories=await Promise.all(resultSet.categories.map(item=>fetchJson(item.url)));
            const analysis=await fetchJson(`/api/result-sets/${encodeURIComponent(id)}/analysis`);
            render(resultSet,categories,analysis);
            document.getElementById("results-error").hidden=true;
            const url=new URL(location.href);url.searchParams.set("result_set",id);history.replaceState(null,"",url);
        }catch(error){
            const box=document.getElementById("results-error");box.textContent=error.message;box.hidden=false;
        }finally{
            timer=setTimeout(load,REFRESH_MS);
        }
    }

    let analysisByRun={};
    function render(resultSet,categories,analysis){
        const loaded=categories.reduce((sum,item)=>sum+item.runs.length,0);
        document.getElementById("result-set-summary").textContent=
            `${resultSet.state} · ${loaded}/${resultSet.expected_runs} runs · ${new Date().toLocaleString()}`;
        const blocks=document.getElementById("category-blocks");
        const prevScrolls=[...blocks.querySelectorAll(".table-wrap")].map(w=>w.scrollLeft);
        blocks.replaceChildren(...categories.map(renderCategory));
        if(window.TableTools)TableTools.enhanceAll(blocks);
        [...blocks.querySelectorAll(".table-wrap")].forEach((w,i)=>{if(prevScrolls[i])w.scrollLeft=prevScrolls[i];});
        renderMatrix(resultSet,categories,analysis);
    }

    function renderCategory(payload){
        const section=document.createElement("section");section.className="category-block";
        const title=payload.category.title||payload.category.id;
        section.innerHTML=`<div class="category-head"><h2>${escapeHtml(title)}</h2><div class="category-meta">${payload.cases.length} Cases · ${payload.runs.length} Runs</div></div>`;
        section.appendChild(heading("ScenarioCase"));
        section.appendChild(caseTable(payload));
        section.appendChild(heading("Run 明细"));
        section.appendChild(runTable(payload));
        section.appendChild(heading("难度聚合"));
        section.appendChild(aggregateTable(payload));
        return section;
    }

    function renderMatrix(resultSet,categories,analysis){
        const section=document.getElementById("matrix-section");section.hidden=false;
        const prevScroll=section.querySelector(".matrix-scroll")?.scrollLeft??0;
        analysisByRun=analysis?(analysis.analyses||{}):{};
        const marks=new Map();
        const runMap=new Map();
        const rates={};
        categories.forEach(payload=>{
            const diffOf=new Map(payload.cases.map(c=>[`${c.scenario_id}/${c.case_id}`,c.difficulty]));
            rates[payload.category.id]={};
            payload.runs.forEach(run=>{
                const key=`${payload.category.id}|${run.scenario_id}/${run.case_id}|${run.model.agent_id}`;
                if(run.evaluation&&run.evaluation.superseded){
                    if(!marks.has(key))marks.set(key,"s");
                    if(!runMap.has(key))runMap.set(key,run);
                }
                else{
                    runMap.set(key,run);
                    if(run.evaluation&&run.evaluation.valid_for_aggregate===true){
                        marks.set(key,run.evaluation.OutcomePass===true?"T":"F");
                        const bucket=(rates[payload.category.id][run.model.agent_id]??={easy:[0,0],hard:[0,0]})[diffOf.get(`${run.scenario_id}/${run.case_id}`)];
                        if(bucket){bucket[1]++;if(run.evaluation.OutcomePass===true)bucket[0]++;}
                    }
                }
            });
        });
        const rateText=b=>b&&b[1]?`${b[0]},${b[1]},${(b[0]/b[1]*100).toFixed(1)}%`:"";
        let catRow=`<th class="model-col corner" rowspan="2"></th>`;
        let numRow="";
        const cellsByModel={};
        resultSet.models.forEach(m=>{cellsByModel[m.id]="";});
        categories.forEach(payload=>{
            const cat=payload.category.id;
            catRow+=`<th class="cat-head cat-${escapeHtml(cat)} cat-start" colspan="${payload.cases.length}">${escapeHtml(payload.category.title||cat)} · ${payload.cases.length}</th><th class="rate-gap" colspan="2">OP 通过率</th>`;
            payload.cases.forEach((item,i)=>{
                numRow+=`<th class="num cat-${escapeHtml(cat)}${item.difficulty==="hard"?" num-hard":""}${String(item.difficulty).toLowerCase()==="unknown"?" num-unknown":""}${i===0?" cat-start":""}" data-name="${escapeHtml(item.case_name)}" data-case="${escapeHtml(item.case_id)}" data-scenario="${escapeHtml(item.scenario_id)}" data-difficulty="${escapeHtml(capitalize(item.difficulty))}" data-depth="${item.diagnostic_depth??""}" data-complex="${formatNumber(item.environmental_complexity)}">${String(item.alias).padStart(2,"0")}</th>`;
            });
            numRow+=`<th class="rate">easy</th><th class="rate">hard</th>`;
            resultSet.models.forEach(m=>{
                cellsByModel[m.id]+=payload.cases.map((item,i)=>{
                    const cellKey=`${cat}|${item.scenario_id}/${item.case_id}|${m.id}`;
                    const hit=marks.get(cellKey);
                    const run=runMap.get(cellKey);
                    const rec=run&&hit!=="s"?analysisByRun[run.run_key]:null;
                    const staleTitle=hit==="s"?' title="场景增强前的旧结果，已作废待重跑"':"";
                    return `<td class="cell cat-${escapeHtml(cat)}${i===0?" cat-start":""}${rec?" cell-analyzed":""}"${rec?` data-run-key="${escapeHtml(run.run_key)}"`:""}${staleTitle}>${hit?`<span class="mark mark-${hit.toLowerCase()}">${hit}</span>`:""}</td>`;
                }).join("");
                const b=rates[cat][m.id]||{};
                cellsByModel[m.id]+=`<td class="rate">${rateText(b.easy)}</td><td class="rate">${rateText(b.hard)}</td>`;
            });
        });
        const body=resultSet.models.map(m=>`<tr><th class="model-col">${escapeHtml(m.name)}</th>${cellsByModel[m.id]}</tr>`).join("");
        section.innerHTML=`<div class="matrix-head"><h2>模型 × Case 覆盖矩阵</h2><div class="matrix-meta">T = 有效判定且 OP 通过 · F = 有效判定但 OP 未通过 · S = 场景增强前的旧结果已作废 · 空白 = 无有效结果 · 列号带下划线 = Hard · 列号带中划线 = Unknown · 单元格下划线 = 该 run 已人工分析（悬浮查看结论；作废 run 不显示）· 每类末尾 easy/hard 列为该难度 OP 通过率（分子,分母,百分比）· 悬浮列号查看 Case 名称</div></div><div class="matrix-scroll"><table class="matrix-table"><thead><tr>${catRow}</tr><tr>${numRow}</tr></thead><tbody>${body}</tbody></table></div>`;
        const sc=section.querySelector(".matrix-scroll");
        if(sc&&prevScroll)sc.scrollLeft=prevScroll;
    }

    let matrixTooltip=null;
    function showMatrixTooltip(th){
        if(!matrixTooltip){matrixTooltip=document.createElement("div");matrixTooltip.className="matrix-tooltip";document.body.appendChild(matrixTooltip);}
        const depth=th.dataset.depth||"—",complex=th.dataset.complex||"—";
        matrixTooltip.innerHTML=`<div class="t-name">${escapeHtml(th.dataset.case||"")}</div><div class="t-sub">${escapeHtml(th.dataset.scenario||"")}</div><div class="t-sub">${escapeHtml(th.dataset.name||"")}</div><div class="t-sub">${escapeHtml(th.dataset.difficulty||"")} · 诊断深度 ${escapeHtml(depth)} · 环境复杂度 ${escapeHtml(complex)}</div>`;
        matrixTooltip.style.display="block";
        const rect=th.getBoundingClientRect(),w=matrixTooltip.offsetWidth,h=matrixTooltip.offsetHeight;
        const left=Math.max(8,Math.min(rect.left+rect.width/2-w/2,window.innerWidth-w-8));
        let top=rect.top-h-8;if(top<8)top=rect.bottom+8;
        matrixTooltip.style.left=`${left}px`;matrixTooltip.style.top=`${top}px`;
    }
    function hideMatrixTooltip(){if(matrixTooltip)matrixTooltip.style.display="none";}
    function showAnalysisTooltip(td){
        const rec=analysisByRun[td.dataset.runKey];
        if(!rec)return;
        if(!matrixTooltip){matrixTooltip=document.createElement("div");matrixTooltip.className="matrix-tooltip";document.body.appendChild(matrixTooltip);}
        const labels=(rec.dominant_labels||[]).join(", ")||"无";
        const artifact=rec.measurement_artifact
            ?`<div class="t-sub">评测伪影：${escapeHtml(rec.measurement_artifact.kind||"")}${rec.measurement_artifact.check?` · ${escapeHtml(rec.measurement_artifact.check)}`:""}<br>${escapeHtml(rec.measurement_artifact.detail||"")}</div>`
            :"";
        matrixTooltip.innerHTML=`<div class="t-name">Run 分析 · ${escapeHtml(String(rec.analyzed_at||"").replace("T"," ").slice(0,16))}</div><div class="t-sub">主导标签：${escapeHtml(labels)}</div><div class="t-body">${escapeHtml(rec.verdict||"")}</div>${artifact}`;
        matrixTooltip.style.display="block";
        const rect=td.getBoundingClientRect(),w=matrixTooltip.offsetWidth,h=matrixTooltip.offsetHeight;
        const left=Math.max(8,Math.min(rect.left+rect.width/2-w/2,window.innerWidth-w-8));
        let top=rect.bottom+8;if(top+h>window.innerHeight-8)top=rect.top-h-8;
        matrixTooltip.style.left=`${left}px`;matrixTooltip.style.top=`${top}px`;
    }

    function heading(text){const h=document.createElement("h3");h.className="section-title";h.textContent=text;return h}

    function caseTable(payload){
        const id=`${payload.result_set_id}:${payload.category.id}:cases`;
        const rows=payload.cases.map(item=>`<tr><td class="number" data-sort-value="${item.alias}">${item.alias}</td><td data-filter-value="${escapeHtml(item.scenario_id)}">${escapeHtml(item.scenario_name)}</td><td data-filter-value="${escapeHtml(item.case_id)}">${escapeHtml(item.case_name)}</td><td>${escapeHtml(capitalize(item.difficulty))}</td><td class="number">${item.diagnostic_depth}</td><td class="number">${formatNumber(item.environmental_complexity)}</td></tr>`).join("");
        return table(`<table class="results-table" data-table-id="${id}"><thead><tr><th class="number">别名</th><th data-filter>Scenario</th><th data-filter>ScenarioCase</th><th>难度</th><th class="number">诊断深度</th><th class="number">环境复杂度</th></tr></thead><tbody>${rows}</tbody></table>`);
    }

    function runTable(payload){
        const id=`${payload.result_set_id}:${payload.category.id}:runs`;
        const cases=new Map(payload.cases.map(item=>[`${item.scenario_id}/${item.case_id}`,item]));
        const rows=[...payload.runs].sort((a,b)=>{
            const aa=cases.get(`${a.scenario_id}/${a.case_id}`).alias;
            const ba=cases.get(`${b.scenario_id}/${b.case_id}`).alias;
            return aa-ba||a.model.agent_id.localeCompare(b.model.agent_id)||a.repetition-b.repetition;
        }).map(run=>{
            const item=cases.get(`${run.scenario_id}/${run.case_id}`),evaluation=run.evaluation||{},timing=run.timing||{};
            const trace=run.provenance&&run.provenance.trace_path?`<a class="trace-link" href="/${escapeHtml(run.provenance.trace_path)}">Trace</a>`:"-";
            return `<tr><td class="number" data-sort-value="${item.alias}">${item.alias}</td><td data-filter-value="${escapeHtml(item.scenario_id)}">${escapeHtml(item.scenario_name)}</td><td data-filter-value="${escapeHtml(item.case_id)}">${escapeHtml(item.case_name)}</td><td data-filter-value="${escapeHtml(run.model.agent_id)}">${escapeHtml(run.model.model_name)}</td><td><span class="status ${escapeHtml(run.execution.status)}">${escapeHtml(run.execution.status)}</span>${run.evaluation&&run.evaluation.superseded?'<div class="run-sub">旧结果已作废</div>':""}</td><td class="number" data-sort-value="${sortNum(run.interaction&&run.interaction.iterations)}">${show(run.interaction&&run.interaction.iterations)}</td><td class="number" data-sort-value="${sortNum(run.interaction&&run.interaction.tool_calls)}">${show(run.interaction&&run.interaction.tool_calls)}</td><td class="number" data-sort-value="${sortNum(run.tokens&&run.tokens.input)}">${show(run.tokens&&run.tokens.input)}</td><td class="number" data-sort-value="${sortNum(run.tokens&&run.tokens.cache_input)}">${show(run.tokens&&run.tokens.cache_input)}</td><td class="number" data-sort-value="${sortNum(run.tokens&&run.tokens.output)}">${show(run.tokens&&run.tokens.output)}</td><td class="center" data-sort-value="${passSort(evaluation.DiagnosisPass)}">${pass(evaluation.DiagnosisPass)}</td><td class="center" data-sort-value="${passSort(evaluation.OutcomePass)}">${pass(evaluation.OutcomePass)}</td><td class="center" data-sort-value="${passSort(evaluation.SafePass)}">${pass(evaluation.SafePass)}</td><td class="number" data-sort-value="${sortNum(timing.container_start_seconds)}">${seconds(timing.container_start_seconds)}</td><td class="number" data-sort-value="${sortNum(timing.preparation_seconds)}">${seconds(timing.preparation_seconds)}</td><td class="number" data-sort-value="${sortNum(timing.agent_interaction_seconds)}">${seconds(timing.agent_interaction_seconds)}</td><td class="number" data-sort-value="${sortNum(timing.evaluation_seconds)}">${seconds(timing.evaluation_seconds)}</td><td class="number" data-sort-value="${sortNum(timing.cleanup_seconds)}">${seconds(timing.cleanup_seconds)}</td><td class="number" data-sort-value="${sortNum(run.execution.duration_seconds)}">${seconds(run.execution.duration_seconds)}</td><td class="center" data-sort-value="${run.fault_snapshot&&run.fault_snapshot.used?1:0}">${run.fault_snapshot&&run.fault_snapshot.used?"是":"否"}</td><td>${trace}</td></tr>`;
        }).join("");
        const body=rows||`<tr class="empty-row"><td colspan="21" class="empty">暂无 Run</td></tr>`;
        return table(`<table class="results-table run-table" data-table-id="${id}"><thead><tr><th class="number">Case</th><th data-filter>Scenario</th><th data-filter>ScenarioCase</th><th data-filter>模型</th><th>状态</th><th class="number">轮数</th><th class="number">工具</th><th class="number">Input</th><th class="number">Cache input</th><th class="number">Output</th><th class="center">DP</th><th class="center">OP</th><th class="center">SP</th><th class="number">容器</th><th class="number">准备</th><th class="number">交互</th><th class="number">评估</th><th class="number">清理</th><th class="number">总时长</th><th class="center">Snapshot</th><th>溯源</th></tr></thead><tbody>${body}</tbody></table>`);
    }

    function aggregateTable(payload){
        const id=`${payload.result_set_id}:${payload.category.id}:aggregate`;
        const caseDifficulty=new Map(payload.cases.map(item=>[`${item.scenario_id}/${item.case_id}`,item.difficulty.toLowerCase()]));
        const rows=["easy","hard"].map(difficulty=>{
            const caseCount=payload.cases.filter(item=>item.difficulty.toLowerCase()===difficulty).length;
            const expected=caseCount*payload.models.length*payload.repetitions;
            const valid=payload.runs.filter(run=>caseDifficulty.get(`${run.scenario_id}/${run.case_id}`)===difficulty&&run.evaluation&&run.evaluation.valid_for_aggregate===true);
            return `<tr><td>${capitalize(difficulty)}</td><td class="number">${expected}</td><td class="number">${valid.length}</td><td class="number" data-sort-value="${rateSort(valid,"DiagnosisPass",true)}">${rate(valid,"DiagnosisPass",true)}</td><td class="number" data-sort-value="${rateSort(valid,"OutcomePass",false)}">${rate(valid,"OutcomePass",false)}</td><td class="number" data-sort-value="${rateSort(valid,"SafePass",false)}">${rate(valid,"SafePass",false)}</td></tr>`;
        }).join("");
        return table(`<table class="results-table" data-table-id="${id}"><thead><tr><th>难度</th><th class="number">预期 Runs</th><th class="number">有效 Runs</th><th class="number">DP 通过率</th><th class="number">OP 通过率</th><th class="number">SP 通过率</th></tr></thead><tbody>${rows}</tbody></table>`);
    }

    function rate(runs,key,excludeNull){
        const values=runs.map(run=>run.evaluation[key]).filter(value=>!excludeNull||value!==null);
        if(!values.length)return "-";
        const passed=values.filter(Boolean).length;
        return `${passed}/${values.length} · ${(passed/values.length*100).toFixed(1)}%`;
    }
    function rateSort(runs,key,excludeNull){
        const values=runs.map(run=>run.evaluation[key]).filter(value=>!excludeNull||value!==null);
        if(!values.length)return "";
        return String(values.filter(Boolean).length/values.length);
    }
    function sortNum(value){return value===null||value===undefined?"":value}
    function passSort(value){return value===null||value===undefined?"":value?1:0}
    function table(html){const wrap=document.createElement("div");wrap.className="table-wrap";wrap.innerHTML=html;return wrap}
    function pass(value){return value===null||value===undefined?"-":value?'<span class="pass">P</span>':'<span class="fail">F</span>'}
    function seconds(value){return value===null||value===undefined?"-":`${Number(value).toFixed(1)}s`}
    function show(value){return value===null||value===undefined?"-":Number(value).toLocaleString()}
    function formatNumber(value){return value===null?"-":Number(value).toFixed(6).replace(/0+$/,"").replace(/\.$/,"")}
    function capitalize(value){return value.charAt(0).toUpperCase()+value.slice(1)}
    async function fetchJson(url){const response=await fetch(`${url}${url.includes("?")?"&":"?"}_=${Date.now()}`,{cache:"no-store"});if(!response.ok)throw new Error(`${url}: ${response.status} ${await response.text()}`);return response.json()}
    function escapeHtml(value){return String(value).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c])}
}());
