<script lang="ts">
  import {
    analyzeDocument,
    getChemistryDatasets,
    listDocuments,
    queryDocument,
    uploadDocument,
    type DocumentRecord
  } from '$lib/api';
  import Block from '$lib/Block.svelte';
  import { onMount } from 'svelte';

  let documents: DocumentRecord[] = [];
  let selectedDocumentId = '';
  let selectedFile: File | null = null;
  let field = 'chemistry';
  let query =
    'Find practical ML, product, and commercialization pathways for this chemistry thesis.';
  let status = 'Ready';
  let activeTab: 'roadmap' | 'ml' | 'product' | 'commercial' | 'trace' = 'roadmap';
  let analysis: any = null;
  let searchTrace: any = null;
  let catalogue: any = null;
  let loading = false;

  const formatNumber = (value: number) => new Intl.NumberFormat().format(value || 0);

  async function refresh() {
    const [docs, chem] = await Promise.all([listDocuments(), getChemistryDatasets()]);
    documents = docs.documents;
    catalogue = chem;
    if (!selectedDocumentId && documents.length) {
      selectedDocumentId = documents[0].id;
    }
  }

  async function handleUpload() {
    if (!selectedFile) return;
    loading = true;
    status = 'Indexing thesis';
    try {
      const result = await uploadDocument(selectedFile, field);
      selectedDocumentId = result.document.id;
      selectedFile = null;
      await refresh();
      status = 'Thesis indexed';
    } catch (error) {
      status = error instanceof Error ? error.message : 'Upload failed';
    } finally {
      loading = false;
    }
  }

  async function runAnalysis() {
    if (!selectedDocumentId) return;
    loading = true;
    status = 'Running specialist agents';
    try {
      const result = await analyzeDocument(selectedDocumentId, query);
      analysis = result;
      searchTrace = result.trace;
      activeTab = 'roadmap';
      status = 'Analysis complete';
    } catch (error) {
      status = error instanceof Error ? error.message : 'Analysis failed';
    } finally {
      loading = false;
    }
  }

  async function runSearch() {
    if (!selectedDocumentId) return;
    loading = true;
    status = 'Retrieving thesis context';
    try {
      searchTrace = await queryDocument(selectedDocumentId, query);
      activeTab = 'trace';
      status = 'Retrieval trace updated';
    } catch (error) {
      status = error instanceof Error ? error.message : 'Retrieval failed';
    } finally {
      loading = false;
    }
  }

  $: selectedDocument = documents.find((doc) => doc.id === selectedDocumentId);

  onMount(() => {
    refresh();
  });
</script>

<svelte:head>
  <meta
    name="description"
    content="Chemistry-first thesis to ML planning workbench with RAG and specialist-agent orchestration."
  />
</svelte:head>

<main class="shell">
  <aside class="left">
    <div class="brand">
      <span class="mark">T2</span>
      <div>
        <strong>Thesis2ML</strong>
        <small>Chemistry workbench</small>
      </div>
    </div>

    <section class="panel">
      <h2>Ingest thesis</h2>
      <label>
        Field schema
        <select bind:value={field}>
          <option value="chemistry">Chemistry</option>
          <option value="materials">Materials chemistry</option>
          <option value="analytical">Analytical chemistry</option>
          <option value="organic">Organic chemistry</option>
        </select>
      </label>
      <label class="file-picker">
        <input
          type="file"
          accept=".pdf,.txt,.md"
          on:change={(event) => {
            selectedFile = event.currentTarget.files?.[0] ?? null;
          }}
        />
        <span>{selectedFile ? selectedFile.name : 'Choose PDF, TXT, or MD'}</span>
      </label>
      <button class="primary" disabled={!selectedFile || loading} on:click={handleUpload}>
        Upload and index
      </button>
    </section>

    <section class="panel documents">
      <h2>Indexed theses</h2>
      {#if documents.length === 0}
        <p class="muted">No documents indexed yet.</p>
      {:else}
        {#each documents as document}
          <button
            class:active={document.id === selectedDocumentId}
            on:click={() => (selectedDocumentId = document.id)}
          >
            <span>{document.title}</span>
            <small>{document.status} · {formatNumber(document.char_count)} chars</small>
          </button>
        {/each}
      {/if}
    </section>
  </aside>

  <section class="workspace">
    <header class="topbar">
      <div>
        <p class="eyebrow">Agentic research-to-ML pipeline</p>
        <h1>{selectedDocument ? selectedDocument.title : 'Upload a chemistry thesis'}</h1>
      </div>
      <div class="status" class:busy={loading}>{status}</div>
    </header>

    <section class="query">
      <textarea bind:value={query} rows="4"></textarea>
      <div class="actions">
        <button class="secondary" disabled={!selectedDocumentId || loading} on:click={runSearch}>
          Inspect retrieval
        </button>
        <button class="primary" disabled={!selectedDocumentId || loading} on:click={runAnalysis}>
          Run full analysis
        </button>
      </div>
    </section>

    <nav class="tabs">
      <button class:active={activeTab === 'roadmap'} on:click={() => (activeTab = 'roadmap')}>Roadmap</button>
      <button class:active={activeTab === 'ml'} on:click={() => (activeTab = 'ml')}>ML plan</button>
      <button class:active={activeTab === 'product'} on:click={() => (activeTab = 'product')}>Product</button>
      <button class:active={activeTab === 'commercial'} on:click={() => (activeTab = 'commercial')}>Commercial</button>
      <button class:active={activeTab === 'trace'} on:click={() => (activeTab = 'trace')}>Trace</button>
    </nav>

    <section class="output">
      {#if !analysis && activeTab !== 'trace'}
        <div class="empty">
          <h2>Run analysis to generate a structured thesis-to-ML plan.</h2>
          <p>
            The backend uses separate specialists for extraction, ML mapping, product strategy, and commercialization.
          </p>
        </div>
      {:else if activeTab === 'roadmap'}
        <div class="summary-grid">
          <article>
            <span>Field</span>
            <strong>{analysis?.result?.extraction?.field ?? 'Pending'}</strong>
          </article>
          <article>
            <span>ML readiness</span>
            <strong>{analysis?.result?.extraction?.ml_readiness ?? 'Review'}</strong>
          </article>
          <article>
            <span>Feasibility</span>
            <strong>{analysis?.result?.ml_plan?.feasibility_score ?? 'n/a'}</strong>
          </article>
        </div>
        <Block title="Research question" items={[analysis?.result?.extraction?.research_question]} />
        <Block title="Data assets" items={analysis?.result?.extraction?.data_assets} />
        <Block title="Next steps" items={analysis?.result?.commercialization?.next_steps} />
      {:else if activeTab === 'ml'}
        {#each analysis?.result?.ml_plan?.recommended_tracks ?? [] as track}
          <div class="record">
            <h2>{track.track}</h2>
            <p><b>Baseline:</b> {track.baseline_experiment}</p>
            <Block title="Algorithms" items={track.algorithms} />
            <Block title="Dataset matches" items={track.dataset_matches} />
            <Block title="Data needed" items={track.data_needed ?? track.thesis_data_to_extract} />
            <p class="risk">{track.risk}</p>
          </div>
        {/each}
      {:else if activeTab === 'product'}
        {#each analysis?.result?.product_strategy?.products ?? [] as product}
          <div class="record">
            <h2>{product.name}</h2>
            <p>{product.problem}</p>
            <dl>
              <dt>User</dt><dd>{product.user}</dd>
              <dt>Workflow</dt><dd>{product.workflow}</dd>
              <dt>MVP</dt><dd>{product.build_scope}</dd>
              <dt>Monetization</dt><dd>{product.monetization}</dd>
            </dl>
          </div>
        {/each}
      {:else if activeTab === 'commercial'}
        <Block title="Commercialization paths" items={analysis?.result?.commercialization?.commercialization_paths} />
        <Block title="Research paths" items={analysis?.result?.commercialization?.research_paths} />
        <Block title="Data readiness checklist" items={analysis?.result?.commercialization?.data_readiness_checklist} />
        <Block title="Cautions" items={analysis?.result?.commercialization?.cautions} />
      {:else}
        <pre>{JSON.stringify(searchTrace ?? analysis?.trace ?? {}, null, 2)}</pre>
      {/if}
    </section>
  </section>

  <aside class="right">
    <section class="panel">
      <h2>Agent pipeline</h2>
      <ol class="pipeline">
        <li>Thesis extractor</li>
        <li>Chemistry ML mapper</li>
        <li>Product strategist</li>
        <li>Commercialization analyst</li>
      </ol>
    </section>

    <section class="panel">
      <h2>Chemistry catalogue</h2>
      {#each catalogue?.categories ?? [] as category}
        <details>
          <summary>{category.name}</summary>
          <p>{category.use_when}</p>
        </details>
      {/each}
    </section>
  </aside>
</main>
