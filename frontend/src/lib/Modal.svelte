<script lang="ts">
  import type { Snippet } from 'svelte'
  import Icon from './Icon.svelte'

  let {
    open,
    title,
    size = 'medium',
    onClose,
    children,
  }: {
    open: boolean
    title: string
    size?: 'small' | 'medium' | 'large'
    onClose: () => void
    children: Snippet
  } = $props()

  let dialogEl = $state<HTMLDialogElement | undefined>()

  $effect(() => {
    if (!dialogEl) return
    if (open && !dialogEl.open) {
      dialogEl.showModal()
    } else if (!open && dialogEl.open) {
      dialogEl.close()
    }
  })

  $effect(() => {
    if (!open) return
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previousOverflow
    }
  })

  function handleDialogClick(event: MouseEvent): void {
    if (event.target === dialogEl) onClose()
  }
</script>

<dialog
  bind:this={dialogEl}
  data-size={size}
  onclose={onClose}
  onclick={handleDialogClick}
  aria-labelledby="modal-title"
>
  <div class="panel">
    <header>
      <h2 id="modal-title">{title}</h2>
      <button type="button" class="close" onclick={onClose} aria-label="Close"><Icon name="close" size={16} /></button>
    </header>
    <div class="body">
      {@render children()}
    </div>
  </div>
</dialog>

<style>
  .panel {
    background: var(--surface-container-high);
    border-radius: var(--radius-xl);
    box-shadow: var(--elevation-4);
    max-height: calc(100vh - 4rem);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--space-3);
    padding: var(--space-4) var(--space-5);
    border-bottom: var(--border-width) solid var(--outline-variant);
    flex: none;
  }
  h2 {
    margin: 0;
    font-size: var(--text-lg);
  }
  .close {
    flex: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.75rem;
    height: 1.75rem;
    padding: 0;
    color: var(--ink-soft);
    background: transparent;
    border: none;
    border-radius: var(--radius-full);
    transition: background 120ms ease, color 120ms ease;
  }
  .close:hover {
    background: color-mix(in srgb, var(--ink) calc(var(--state-hover) * 100%), transparent);
    color: var(--ink);
  }
  .body {
    padding: var(--space-5);
    overflow-y: auto;
  }
</style>
