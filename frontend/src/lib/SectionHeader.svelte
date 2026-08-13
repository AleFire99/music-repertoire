<script lang="ts">
  import type { Snippet } from 'svelte'

  let { eyebrow, title, right }: { eyebrow: string; title: string; right?: Snippet } = $props()
</script>

<header class="section-header">
  <div class="row">
    <div>
      <p class="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
    </div>
    {#if right}
      <div class="right">{@render right()}</div>
    {/if}
  </div>
</header>

<style>
  .section-header {
    padding-bottom: var(--space-4);
    margin-bottom: var(--space-4);
    border-bottom: 1px solid var(--border);
  }
  .row {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: var(--space-4);
    flex-wrap: wrap;
  }
  .eyebrow {
    margin: 0 0 0.2rem;
    color: var(--accent-strong);
    font-size: var(--text-xs);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .right {
    font-family: var(--font-sans);
    display: flex;
    align-items: center;
    gap: var(--space-3);
  }
</style>
