<script lang="ts">
  import type { Snippet } from 'svelte'

  let {
    kicker,
    title,
    subtitle,
    actions,
  }: { kicker?: string; title: string; subtitle?: string; actions?: Snippet } = $props()
</script>

<header class="section-header">
  <div class="heading">
    {#if kicker}
      <div class="kicker">{kicker}</div>
    {/if}
    <h1>{title}</h1>
    {#if subtitle}
      <p class="subtitle">{subtitle}</p>
    {/if}
  </div>
  {#if actions}
    <div class="actions-row">{@render actions()}</div>
  {/if}
</header>

<style>
  .section-header {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: var(--space-5) var(--space-6);
    padding-bottom: var(--space-5);
    margin-bottom: var(--space-6);
    border-bottom: var(--border-width-strong) solid var(--border);
  }
  .heading {
    flex: 1 1 20rem;
    min-width: 0;
  }
  .actions-row {
    flex: none;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--space-3);
    margin-left: auto;
  }
</style>
