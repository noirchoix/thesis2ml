<script lang="ts">
  export let title: string;
  export let items: any[] | string | undefined = [];

  $: normalized = Array.isArray(items) ? items.filter(Boolean) : items ? [items] : [];
</script>

<section class="block">
  <h3>{title}</h3>
  {#if normalized.length === 0}
    <p class="muted">No output returned.</p>
  {:else}
    <ul>
      {#each normalized as item}
        <li>{typeof item === 'string' ? item : JSON.stringify(item)}</li>
      {/each}
    </ul>
  {/if}
</section>

