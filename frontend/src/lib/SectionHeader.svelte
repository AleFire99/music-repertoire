<script lang="ts">
  import type { Snippet } from 'svelte'

  let { title, right }: { title: string; right?: Snippet } = $props()
</script>

<header class="section-header">
  <div class="row">
    <h2><span class="barline" aria-hidden="true">‖</span> {title}</h2>
    {#if right}
      <div class="right">{@render right()}</div>
    {/if}
  </div>
  <div class="staff" aria-hidden="true"></div>
</header>

<style>
  .section-header {
    margin-bottom: var(--space-4);
  }
  .row {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: var(--space-3);
    flex-wrap: wrap;
  }
  h2 {
    display: flex;
    align-items: baseline;
    gap: var(--space-2);
  }
  .barline {
    color: var(--brass);
    font-weight: 400;
  }
  .right {
    font-family: var(--font-body);
  }
  .staff {
    margin-top: var(--space-3);
    height: 13px;
    background-image: linear-gradient(
      to bottom,
      var(--line) 0,
      var(--line) 1px,
      transparent 1px,
      transparent 3px,
      var(--line) 3px,
      var(--line) 4px,
      transparent 4px,
      transparent 6px,
      var(--line) 6px,
      var(--line) 7px,
      transparent 7px,
      transparent 9px,
      var(--line) 9px,
      var(--line) 10px,
      transparent 10px,
      transparent 12px,
      var(--line) 12px,
      var(--line) 13px
    );
    background-repeat: no-repeat;
    opacity: 0.9;
  }
</style>
