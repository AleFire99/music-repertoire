<script lang="ts">
  import type { Snippet } from 'svelte'

  let {
    title,
    dek,
    actions,
  }: { title: string; dek?: string; actions?: Snippet } = $props()
</script>

<header class="section-header">
  <h2>{title}</h2>
  {#if dek}
    <p class="dek">{dek}</p>
  {/if}
  <hr class="rule" />
  {#if actions}
    <div class="actions-row">{@render actions()}</div>
  {/if}
</header>

<style>
  .section-header {
    margin-bottom: var(--space-5);
  }
  .rule {
    margin-top: var(--space-4);
  }
  .actions-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--space-4);
    padding-top: var(--space-3);
  }
</style>
