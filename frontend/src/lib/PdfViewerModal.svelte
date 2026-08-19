<script lang="ts">
  import { sheetResourceViewUrl } from './api'
  import Modal from './Modal.svelte'

  let { resourceId, onClose }: { resourceId: number | null; onClose: () => void } = $props()
</script>

<Modal open={resourceId !== null} title="Sheet preview" size="large" onClose={onClose}>
  {#if resourceId !== null}
    <iframe class="pdf-frame" src={sheetResourceViewUrl(resourceId)} title="Sheet music PDF preview"
    ></iframe>
  {/if}
</Modal>

<style>
  .pdf-frame {
    display: block;
    width: 100%;
    height: calc(100vh - 12rem);
    border: none;
  }
</style>
