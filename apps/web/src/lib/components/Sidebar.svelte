<script lang="ts">
  const items = [
    'Dashboard',
    'New Assessment',
    'Assessments',
    'Document Library',
    'Rules Explorer',
    'Reports',
    'Admin'
  ];
</script>

<aside class="hidden w-72 shrink-0 border-r border-slate-200 bg-white lg:block">
  <div class="px-6 py-6">
    <div class="text-sm font-semibold uppercase tracking-wide text-brand-700">RegIntel</div>
    <div class="mt-2 text-2xl font-bold text-slate-900">Workbench</div>
  </div>
  <nav class="space-y-1 px-3 pb-6">
    {#each items as item}
      <a
        href={item === 'New Assessment' ? '/' : '#'}
        class="block rounded-xl px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
      >
        {item}
      </a>
    {/each}
  </nav>
</aside>
