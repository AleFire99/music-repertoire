<script lang="ts">
  import { deleteSheetResource, sheetResourceFileUrl, type SheetResource } from './api'
  import Icon from './Icon.svelte'

  let {
    resources,
    onDeleted,
  }: {
    resources: SheetResource[]
    onDeleted: (id: number) => void
  } = $props()

  let deletingId = $state<number | null>(null)
  let deleteError = $state<string | null>(null)

  async function handleDelete(resource: SheetResource): Promise<void> {
    if (!window.confirm(`Delete this sheet resource? This cannot be undone.`)) return
    deletingId = resource.id
    deleteError = null
    try {
      await deleteSheetResource(resource.id)
      onDeleted(resource.id)
    } catch (err) {
      deleteError = err instanceof Error ? err.message : String(err)
    } finally {
      deletingId = null
    }
  }
</script>

{#if deleteError}
  <p class="error">{deleteError}</p>
{/if}

{#if resources.length === 0}
  <p class="empty">No sheet resources yet.</p>
{:else}
  <div class="resource-grid">
    {#each resources as resource (resource.id)}
      <div class="resource-row">
        <span class="icon-wrap">
          <Icon name="sheet" size={17} />
        </span>
        <div class="body">
          <div class="reference">{resource.reference}</div>
          <div class="meta-line">
            <span>{resource.kind}</span>
            {#if resource.label}<span>{resource.label}</span>{/if}
          </div>
          {#if resource.notes}
            <p class="notes">{resource.notes}</p>
          {/if}
        </div>
        {#if resource.kind === 'uploaded'}
          <a
            class="icon-btn always"
            href={sheetResourceFileUrl(resource.id)}
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Download"
          >
            <Icon name="download" size={16} />
          </a>
        {/if}
        <button
          type="button"
          class="icon-btn danger always"
          onclick={() => handleDelete(resource)}
          disabled={deletingId === resource.id}
          aria-label="Delete"
        >
          <Icon name="delete" size={16} />
        </button>
      </div>
    {/each}
  </div>
{/if}

<style>
  .resource-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0 var(--space-6);
  }
  .resource-row {
    display: flex;
    gap: var(--space-3);
    padding: var(--space-3) 0;
    border-bottom: var(--border-width) solid var(--border);
  }
  .icon-wrap {
    flex: none;
    width: 2.375rem;
    height: 2.375rem;
    display: grid;
    place-items: center;
    background: var(--surface);
    border: var(--border-width) solid var(--border);
    color: var(--ink-soft);
  }
  .body {
    flex: 1;
    min-width: 0;
  }
  .reference {
    color: var(--ink);
    font-size: var(--text-sm);
    overflow-wrap: break-word;
  }
  .notes {
    margin: var(--space-1) 0 0;
    color: var(--ink-soft);
    font-size: var(--text-xs);
  }
  a.icon-btn {
    text-decoration: none;
  }
</style>
