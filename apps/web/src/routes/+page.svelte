<script lang="ts">
  import { createAssessment, generateReport } from '$lib/api';
  import type { AssessmentCreate } from '$lib/types';

  let assessment: any = null;
  let loading = false;
  let exportLoading = false;
  let error = '';
  let reportUrl = '';

  let form: AssessmentCreate = {
    jurisdiction: 'US',
    profile: {
      product_name: 'DentalVision AI',
      company_name: 'DentalVision AI',
      intended_use:
        'AI-enabled software that assists clinicians with early detection of oral disease patterns from dental images.',
      target_users: ['dentists'],
      jurisdictions: ['US'],
      delivery_model: 'web',
      clinical_decision_support: true,
      provides_diagnosis: true,
      provides_treatment_recommendation: false,
      stores_phi: true,
      integrates_with_ehr: false,
      uses_ml_models: true,
      human_in_the_loop: true,
      software_lifecycle_stage: 'prototype'
    }
  };

  async function submitAssessment() {
    loading = true;
    error = '';
    reportUrl = '';

    try {
      assessment = await createAssessment(form);
    } catch (err: any) {
      error = err?.message || 'Assessment failed. Please review the form and try again.';
    } finally {
      loading = false;
    }
  }

  async function exportReport() {
    if (!assessment?.id) return;

    exportLoading = true;
    error = '';

    try {
      const report = await generateReport(assessment.id);
      if (report?.storage_url) {
        reportUrl = report.storage_url;
        window.open(report.storage_url, '_blank');
      } else {
        error = 'Report generation completed, but no downloadable file URL was returned.';
      }
    } catch (err: any) {
      error = err?.message || 'Could not generate the PDF report.';
    } finally {
      exportLoading = false;
    }
  }

  function resetForm() {
    assessment = null;
    reportUrl = '';
    error = '';
  }
</script>

<svelte:head>
  <title>RegIntel | Regulatory Intelligence Engine</title>
  <meta
    name="description"
    content="Assess medical software concepts using deterministic rules, regulatory retrieval, and reproducible PDF reporting."
  />
</svelte:head>

<div class="min-h-screen bg-slate-50 text-slate-900">
  <div class="mx-auto max-w-7xl px-6 py-8 lg:px-8">
    <section class="grid gap-8 rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200 lg:grid-cols-[1.2fr,0.8fr]">
      <div>
        <div class="inline-flex items-center rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-200">
          Regulatory Intelligence Engine
        </div>

        <h1 class="mt-4 text-4xl font-semibold tracking-tight text-slate-900">
          Evaluate medical software concepts before development risk compounds.
        </h1>

        <p class="mt-4 max-w-2xl text-base leading-7 text-slate-600">
          This workbench combines deterministic regulatory rules, retrieval from relevant standards and guidance,
          and reproducible report generation to help early-stage medical software teams understand likely
          classification, compliance implications, and evidence-backed reasoning.
        </p>

        <div class="mt-6 grid gap-4 sm:grid-cols-3">
          <div class="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
            <div class="text-sm font-semibold text-slate-900">Deterministic classification</div>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              Rules drive the decision path first, reducing black-box behavior.
            </p>
          </div>

          <div class="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
            <div class="text-sm font-semibold text-slate-900">Grounded evidence</div>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              Retrieved clauses and guidance excerpts support the generated output.
            </p>
          </div>

          <div class="rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
            <div class="text-sm font-semibold text-slate-900">Exportable report</div>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              Generate a downloadable regulatory report after assessment.
            </p>
          </div>
        </div>
      </div>

      <div class="rounded-2xl bg-slate-900 p-6 text-slate-50">
        <h2 class="text-lg font-semibold">What this first deployment does</h2>
        <ul class="mt-4 space-y-3 text-sm leading-6 text-slate-200">
          <li>Assesses a medical software concept against the current backend rule flow</li>
          <li>Surfaces explainable classification output and supporting evidence</li>
          <li>Previews the resulting regulatory assessment on-page</li>
          <li>Generates a downloadable PDF report</li>
        </ul>

        <div class="mt-6 rounded-2xl bg-slate-800 p-4 ring-1 ring-white/10">
          <div class="text-xs uppercase tracking-wide text-slate-400">Deployment mode</div>
          <div class="mt-1 text-sm font-medium text-white">Authentication removed for first deployment UX</div>
          <p class="mt-2 text-sm leading-6 text-slate-300">
            The interface now prioritizes direct assessment flow instead of sign-in-first behavior.
          </p>
        </div>
      </div>
    </section>

    <div class="mt-8 grid gap-8 lg:grid-cols-[1.05fr,0.95fr]">
      <section class="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 class="text-2xl font-semibold text-slate-900">Product intake form</h2>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              Describe the software concept so the backend can evaluate intended use, workflow role,
              diagnosis behavior, PHI handling, and oversight model.
            </p>
          </div>

          {#if assessment}
            <button
              class="rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              onclick={resetForm}
            >
              Start over
            </button>
          {/if}
        </div>

        <div class="mt-6 grid gap-5">
          <div class="grid gap-2">
            <label for="product_name" class="text-sm font-medium text-slate-700">Product name</label>
            <input
              id="product_name"
              bind:value={form.profile.product_name}
              class="rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              placeholder="e.g. DentalVision AI"
            />
          </div>

          <div class="grid gap-2">
            <label for="company_name" class="text-sm font-medium text-slate-700">Company name</label>
            <input
              id="company_name"
              bind:value={form.profile.company_name}
              class="rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              placeholder="e.g. DentalVision AI Ltd."
            />
          </div>

          <div class="grid gap-2">
            <label for="jurisdiction" class="text-sm font-medium text-slate-700">Jurisdiction</label>
            <select
              id="jurisdiction"
              bind:value={form.jurisdiction}
              class="rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            >
              <option value="US">United States</option>
              <option value="EU">European Union</option>
              <option value="UK">United Kingdom</option>
            </select>
          </div>

          <div class="grid gap-2">
            <label for="intended_use" class="text-sm font-medium text-slate-700">Intended use</label>
            <textarea
              id="intended_use"
              bind:value={form.profile.intended_use}
              class="min-h-40 rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              placeholder="Describe what the software does, who uses it, whether it influences diagnosis or treatment, and how outputs are used."
            ></textarea>
          </div>

          <div class="grid gap-2 sm:grid-cols-2">
            <div class="grid gap-2">
              <label for="delivery_model" class="text-sm font-medium text-slate-700">Delivery model</label>
              <select
                id="delivery_model"
                bind:value={form.profile.delivery_model}
                class="rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              >
                <option value="web">Web</option>
                <option value="desktop">Desktop</option>
                <option value="mobile">Mobile</option>
                <option value="api">Cloud API</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>

            <div class="grid gap-2">
              <label for="software_lifecycle_stage" class="text-sm font-medium text-slate-700">Lifecycle stage</label>
              <select
                id="software_lifecycle_stage"
                bind:value={form.profile.software_lifecycle_stage}
                class="rounded-xl border border-slate-300 px-4 py-3 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              >
                <option value="idea">Idea</option>
                <option value="design">Design</option>
                <option value="prototype">Prototype</option>
                <option value="pre-market">Pre-market</option>
                <option value="market">Market</option>
              </select>
            </div>
          </div>

          <div class="grid gap-3 sm:grid-cols-2">
            <label class="flex items-center gap-3 rounded-2xl border border-slate-200 p-4">
              <input type="checkbox" bind:checked={form.profile.clinical_decision_support} />
              <span class="text-sm text-slate-700">Clinical decision support</span>
            </label>

            <label class="flex items-center gap-3 rounded-2xl border border-slate-200 p-4">
              <input type="checkbox" bind:checked={form.profile.provides_diagnosis} />
              <span class="text-sm text-slate-700">Provides diagnosis-related output</span>
            </label>

            <label class="flex items-center gap-3 rounded-2xl border border-slate-200 p-4">
              <input type="checkbox" bind:checked={form.profile.provides_treatment_recommendation} />
              <span class="text-sm text-slate-700">Provides treatment recommendation</span>
            </label>

            <label class="flex items-center gap-3 rounded-2xl border border-slate-200 p-4">
              <input type="checkbox" bind:checked={form.profile.stores_phi} />
              <span class="text-sm text-slate-700">Stores protected health information</span>
            </label>

            <label class="flex items-center gap-3 rounded-2xl border border-slate-200 p-4">
              <input type="checkbox" bind:checked={form.profile.integrates_with_ehr} />
              <span class="text-sm text-slate-700">Integrates with EHR systems</span>
            </label>

            <label class="flex items-center gap-3 rounded-2xl border border-slate-200 p-4">
              <input type="checkbox" bind:checked={form.profile.uses_ml_models} />
              <span class="text-sm text-slate-700">Uses machine learning models</span>
            </label>

            <label class="flex items-center gap-3 rounded-2xl border border-slate-200 p-4 sm:col-span-2">
              <input type="checkbox" bind:checked={form.profile.human_in_the_loop} />
              <span class="text-sm text-slate-700">Human oversight remains in the decision workflow</span>
            </label>
          </div>

          <div class="pt-2">
            <button
              onclick={submitAssessment}
              disabled={loading}
              class="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {#if loading}
                Processing assessment...
              {:else}
                Run regulatory assessment
              {/if}
            </button>
          </div>

          {#if error}
            <div class="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          {/if}
        </div>
      </section>

      <section class="rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-2xl font-semibold text-slate-900">Assessment result</h2>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              The result section appears after the backend completes evaluation.
            </p>
          </div>
        </div>

        {#if !assessment?.result && !loading}
          <div class="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center">
            <div class="text-base font-medium text-slate-800">No result yet</div>
            <p class="mt-2 text-sm leading-6 text-slate-600">
              Submit the intake form to generate a classification summary, evidence trace, and exportable report.
            </p>
          </div>
        {/if}

        {#if loading}
          <div class="mt-6 space-y-4">
            <div class="h-24 animate-pulse rounded-2xl bg-slate-100"></div>
            <div class="h-32 animate-pulse rounded-2xl bg-slate-100"></div>
            <div class="h-48 animate-pulse rounded-2xl bg-slate-100"></div>
          </div>
        {/if}

        {#if assessment?.result}
          <div class="mt-6 space-y-5">
            <div class="rounded-2xl border border-slate-200 p-5">
              <div class="text-sm text-slate-500">Likely classification</div>
              <div class="mt-2 text-2xl font-semibold text-slate-900">
                {assessment.result.classification}
              </div>
              <div class="mt-2 inline-flex rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                Confidence: {assessment.result.confidence_band}
              </div>
            </div>

            <div class="rounded-2xl border border-slate-200 p-5">
              <div class="text-base font-semibold text-slate-900">Executive summary</div>
              <p class="mt-3 text-sm leading-7 text-slate-700">
                {assessment.result.explanation?.executive_summary}
              </p>
            </div>

            {#if assessment.result.explanation?.key_obligations?.length}
              <div class="rounded-2xl border border-slate-200 p-5">
                <div class="text-base font-semibold text-slate-900">Key obligations</div>
                <div class="mt-3 space-y-2">
                  {#each assessment.result.explanation.key_obligations as obligation}
                    <div class="rounded-xl bg-slate-50 px-4 py-3 text-sm text-slate-700">
                      {obligation}
                    </div>
                  {/each}
                </div>
              </div>
            {/if}

            <div class="rounded-2xl border border-slate-200 p-5">
              <div class="flex items-center justify-between gap-4">
                <div>
                  <div class="text-base font-semibold text-slate-900">Regulatory document preview</div>
                  <p class="mt-1 text-sm text-slate-600">
                    Preview of the assessment output and supporting citations before download.
                  </p>
                </div>
              </div>

              <div class="mt-4 rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
                <div class="text-sm font-semibold text-slate-900">
                  {form.profile.product_name} - Regulatory Assessment Preview
                </div>
                <div class="mt-3 grid gap-3 text-sm text-slate-700">
                  <div>
                    <span class="font-medium">Company:</span> {form.profile.company_name}
                  </div>
                  <div>
                    <span class="font-medium">Jurisdiction:</span> {form.jurisdiction}
                  </div>
                  <div>
                    <span class="font-medium">Intended use:</span> {form.profile.intended_use}
                  </div>
                  <div>
                    <span class="font-medium">Classification:</span> {assessment.result.classification}
                  </div>
                  <div>
                    <span class="font-medium">Confidence:</span> {assessment.result.confidence_band}
                  </div>
                </div>
              </div>
            </div>

            <div class="rounded-2xl border border-slate-200 p-5">
              <div class="text-base font-semibold text-slate-900">Evidence trace</div>
              <div class="mt-4 space-y-3">
                {#each assessment.result.evidence as item}
                  <div class="min-w-0 rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
                    <div class="flex min-w-0 flex-wrap items-center gap-2">
                      <div class="min-w-0 break-words text-sm font-semibold text-slate-900">{item.framework}</div>
                      <div class="max-w-full break-words rounded-full bg-white px-2 py-0.5 text-xs text-slate-500 ring-1 ring-slate-200">
                        {item.citation}
                      </div>
                      <div class="rounded-full bg-white px-2 py-0.5 text-xs text-slate-500 ring-1 ring-slate-200">
                        score {item.score.toFixed(3)}
                      </div>
                    </div>
                    <p class="mt-3 whitespace-pre-line break-words text-sm leading-6 text-slate-700">{item.excerpt}</p>
                  </div>
                {/each}
              </div>
            </div>

            <div class="flex flex-wrap gap-3 pt-2">
              <button
                onclick={exportReport}
                disabled={exportLoading}
                class="inline-flex items-center justify-center rounded-xl bg-slate-900 px-5 py-3 font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {#if exportLoading}
                  Generating PDF...
                {:else}
                  Download PDF report
                {/if}
              </button>

              {#if reportUrl}
                <a
                  href={reportUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  class="inline-flex items-center justify-center rounded-xl border border-slate-300 px-5 py-3 font-medium text-slate-700 transition hover:bg-slate-50"
                >
                  Open generated report
                </a>
              {/if}
            </div>
          </div>
        {/if}
      </section>
    </div>
  </div>
</div>
